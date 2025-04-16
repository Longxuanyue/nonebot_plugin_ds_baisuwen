import asyncio
import os
import time
import numpy as np
import torch
import requests
import soundfile as sf
import subprocess
from pathlib import Path
from nonebot import get_driver, logger
from typing import Optional, Tuple
import tempfile
from . import commons
from . import utils
from .models import SynthesizerTrn
from .text import text_to_sequence
from .redis_handler import redis_client
from .config_loader import load_character_config

class VoiceService:
    def __init__(self):
        driver = get_driver()
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.config = load_character_config()
        
        # API配置
        self.api_url = "http://127.0.0.1:7860/run/predict"
        self.timeout = 15  # API超时时间
        
        # 保持旧模型加载逻辑作为备用
        self._load_backup_model()

    def _load_backup_model(self):
        """备用模型加载（防止API服务未启动）"""
        try:
            self.vits_model_path = Path(self.config["vits_model_path"])
            self.vits_config_path = Path(self.config["vits_config_path"])
            self.hps = utils.get_hparams_from_file(str(self.vits_config_path))
            self.net_g = SynthesizerTrn(
                len(self.hps.symbols),
                self.hps.data.filter_length // 2 + 1,
                self.hps.train.segment_size // self.hps.data.hop_length,
                n_speakers=self.hps.data.n_speakers,
                **self.hps.model
            ).to(self.device)
            utils.load_checkpoint(str(self.vits_model_path), self.net_g, None)
            self.net_g.eval()
            logger.warning("备用模型已加载，建议优先使用API模式")
        except Exception as e:
            logger.error(f"备用模型加载失败: {str(e)}")

    async def text_to_speech(self, text: str) -> Optional[Path]:
        """双模式语音生成（优先API模式）"""
        # 尝试API模式
        clean_text = text.replace("\n", " ").strip()
        print(clean_text)
        result = await self._try_api_generate(text)
        if result: return result
        
        # 回退本地模型
        logger.warning("API调用失败，使用备用模型生成")
        return await self._local_generate(clean_text)

    async def _try_api_generate(self, text: str, retry=3) -> Optional[Path]:
        """调用本地VITS API服务（增强错误处理）"""
        for attempt in range(retry):
            try:
                # 构造符合Gradio API的请求格式
                payload = {
                    "fn_index": 0,
                    "data": [
                        text, 
                        "rosmontic", 
                        "简体中文",
                        1.0
                    ]
                }
                
                # 发送请求并记录原始响应
                response = requests.post(self.api_url, json=payload, timeout=self.timeout)
                logger.debug(f"API原始响应: {response.text[:500]}")  # 截取前500字符避免日志过长
                
                if response.status_code != 200:
                    raise ConnectionError(f"HTTP错误: {response.status_code}")

                result = response.json()
                logger.debug(f"解析后的响应结构: {str(result)[:500]}")  # 关键日志
                
                # 增强响应结构验证
                if not isinstance(result, dict) or "data" not in result:
                    raise ValueError("无效的API响应格式")
                    
                # 解析音频路径（兼容新版Gradio）
                audio_data = result["data"]
                if len(audio_data) < 2 or not isinstance(audio_data[1], (list, dict)):
                    raise ValueError("音频数据缺失")
                    
                # 处理不同格式的音频路径
                if isinstance(audio_data[1], list):
                    # 格式1: [采样率, 文件路径]
                    audio_path = self._parse_gradio_path(audio_data[1][1])
                elif isinstance(audio_data[1], dict):
                    # 格式2: {"name": "路径", "data": ...}
                    audio_path = self._parse_gradio_path(audio_data[1].get("name", ""))
                else:
                    raise ValueError("未知的音频格式")

                logger.debug(f"解析后的音频路径: {audio_path}")
                if not audio_path or not audio_path.exists():
                    raise FileNotFoundError(f"音频文件不存在: {audio_path}")

                return await self._process_remote_audio(audio_path)

            except Exception as e:
                logger.error(f"API尝试 {attempt+1}/{retry} 失败详情:", exc_info=True)  # 打印完整堆栈
                await asyncio.sleep(1)
        return None

    def _parse_gradio_path(self, path_str: str) -> Optional[Path]:
        """增强路径解析（处理Windows特殊字符和URL编码）"""
        from urllib.parse import unquote
        try:
            # 处理含URL编码的路径
            if "file=" in path_str:
                decoded_path = unquote(path_str.split("file=")[1].split("&")[0])
                decoded_path = decoded_path.strip('"')
                return Path(decoded_path)
            
            # 处理直接路径
            clean_path = unquote(path_str).replace("\\", "/")
            return Path(clean_path) if Path(clean_path).exists() else None
        except Exception as e:
            logger.error(f"路径解析失败: {path_str} -> {str(e)}")
        return None

    async def _process_remote_audio(self, audio_path: Path) -> Optional[Path]:
        """处理远程生成的音频文件"""
        try:
            # 读取音频数据
            audio, sr = sf.read(str(audio_path))
            
            # 转换为SILK格式
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
                sf.write(tmp_wav.name, audio, sr, subtype='PCM_16')
                return await self._convert_to_silk(audio)
        
        except Exception as e:
            logger.error(f"远程音频处理失败: {str(e)}")
            return None

    async def _local_generate(self, text: str) -> Optional[Path]:
        """备用本地模型生成"""
        try:
            text = "[ZH]" + text + "[ZH]"  # 强制中文标记
            stn_tst = self._get_text(text)
            with torch.no_grad():
                x_tst = stn_tst.unsqueeze(0).to(self.device)
                x_tst_lengths = torch.LongTensor([stn_tst.size(0)]).to(self.device)
                sid = torch.LongTensor([0]).to(self.device)
                audio = self.net_g.infer(x_tst, x_tst_lengths, sid=sid)[0][0,0].cpu().numpy()
            return await self._convert_to_silk(audio)
        except Exception as e:
            logger.error(f"本地生成失败: {str(e)}")
            return None

    def _get_text(self, text: str):
        # """文本处理逻辑（增强校验）"""
        # text = "[ZH]" + text + "[ZH]"
        logger.debug(f"原始文本: {text}")
        text_norm = text_to_sequence(
            text, 
            self.hps.symbols, 
            self.hps.data.text_cleaners
        )
        
        # 长度校验
        if len(text_norm) < 3:
            raise ValueError(f"符号序列过短（{len(text_norm)}）")
        
        logger.debug(f"处理后的符号序列长度: {len(text_norm)}")
        if self.hps.data.add_blank:
            text_norm = commons.intersperse(text_norm, 0)
        return torch.LongTensor(text_norm)

    async def _convert_to_silk(self, audio: np.ndarray) -> Optional[Path]:
        temp_dir = Path(r"D:\gocq\data\record")
        encoder_path = Path(r"D:\silk-v3-decoder-master\silk-v3-decoder-master\windows\silk_v3_encoder.exe").resolve()
        
        # 初始化所有路径变量为 None
        temp_wav = temp_pcm = temp_silk = None
        
        try:
            # ==== 1. 验证目录和编码器 ====
            if not temp_dir.exists():
                temp_dir.mkdir(parents=True, exist_ok=True)
            if not encoder_path.exists():
                raise FileNotFoundError(f"SILK编码器不存在: {encoder_path}")

            # ==== 2. 生成唯一时间戳 ====
            timestamp = int(time.time() * 1000)
            temp_wav = temp_dir / f"temp_{timestamp}.wav"
            temp_pcm = temp_dir / f"temp_{timestamp}.pcm"
            temp_silk = temp_dir / f"temp_{timestamp}.silk"

            # ==== 3. 保存WAV文件 ====
            logger.debug(f"保存WAV文件到: {temp_wav}")
            sf.write(str(temp_wav), audio, self.hps.data.sampling_rate, subtype='PCM_16')

            # ==== 4. 转换PCM ====
            logger.debug("开始转换WAV到PCM...")
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-i", str(temp_wav),
                "-ar", "24000",
                "-ac", "1",
                "-f", "s16le",
                "-loglevel", "error",
                str(temp_pcm)
            ]
            subprocess.run(
                ffmpeg_cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=15
            )

            # ==== 5. 验证PCM文件 ====
            if not temp_pcm.exists():
                raise RuntimeError("PCM文件生成失败")

            # ==== 6. SILK编码 ====
            logger.debug("开始SILK编码...")
            cmd = [
                str(encoder_path),
                str(temp_pcm),
                str(temp_silk),
                "-Fs_API", "24000",
                "-rate", "24000",
                "-tencent",
                "-quiet"
            ]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=15,
                check=True,
                shell=False
            )

            # ==== 7. 验证SILK文件 ====
            retry_count = 0
            while not temp_silk.exists() and retry_count < 10:
                logger.debug(f"等待文件生成，重试次数: {retry_count}")
                await asyncio.sleep(0.5)
                retry_count += 1

            if not temp_silk.exists():
                raise FileNotFoundError(f"SILK文件未生成: {temp_silk}")
            if temp_silk.stat().st_size < 1024:
                raise ValueError(f"SILK文件大小异常: {temp_silk.stat().st_size}字节")

            return temp_silk

        except subprocess.CalledProcessError as e:
            error_msg = f"""
            子进程错误[code={e.returncode}]
            命令: {' '.join(e.cmd)}
            错误输出: {e.stderr.decode('gbk', errors='ignore')}
            """
            logger.error(error_msg)
            return None
        except Exception as e:
            logger.error(f"编码失败: {str(e)}")
            return None
        finally:
            # 安全清理中间文件
            for f in [temp_wav, temp_pcm]:
                if f and f.exists():
                    try:
                        f.unlink(missing_ok=True)
                    except Exception as e:
                        logger.warning(f"清理失败 {f}: {str(e)}")

voice_service = VoiceService()