import re
from .japanese import japanese_to_romaji_with_accent, japanese_to_ipa, japanese_to_ipa2, japanese_to_ipa3
from .korean import latin_to_hangul, number_to_hangul, divide_hangul, korean_to_lazy_ipa, korean_to_ipa
from .mandarin import number_to_chinese, chinese_to_bopomofo, latin_to_bopomofo, chinese_to_romaji, chinese_to_lazy_ipa, chinese_to_ipa, chinese_to_ipa2
from .sanskrit import devanagari_to_ipa
from .english import english_to_lazy_ipa, english_to_ipa2, english_to_lazy_ipa2
from .thai import num_to_thai, latin_to_thai
from pypinyin import Style, pinyin
# from text.shanghainese import shanghainese_to_ipa
# from text.cantonese import cantonese_to_ipa
# from text.ngu_dialect import ngu_dialect_to_ipa


def japanese_cleaners(text):
    text = japanese_to_romaji_with_accent(text)
    text = re.sub(r'([A-Za-z])$', r'\1.', text)
    return text


def japanese_cleaners2(text):
    return japanese_cleaners(text).replace('ts', 'ʦ').replace('...', '…')


def korean_cleaners(text):
    '''Pipeline for Korean text'''
    text = latin_to_hangul(text)
    text = number_to_hangul(text)
    text = divide_hangul(text)
    text = re.sub(r'([\u3131-\u3163])$', r'\1.', text)
    return text


def chinese_cleaners(text):
    # 保留中文、常用标点和基本拉丁字符
    text = re.sub(r'[^\u4e00-\u9fff，。！？、a-zA-Z0-9\s]', '', text)
    
    # 分割文本为汉字和标点
    segments = re.split(r'([，。！？、])', text)
    phones = []
    
    for seg in segments:
        if not seg:
            continue
        if seg in ['，', '。', '！', '？', '、']:
            # 将中文标点映射为对应符号
            phones.append({
                '，': ',', 
                '。': '.', 
                '！': '!', 
                '？': '?', 
                '、': ','
            }[seg])
        else:
            # 处理中文部分
            seg_phones = pinyin(seg, style=Style.TONE3)
            phones.extend([p[0] for p in seg_phones])
    
    # 添加句子结束标点
    if phones and phones[-1] not in ['.', '!', '?']:
        phones.append('.')
    
    return ' '.join(phones)


def zh_ja_mixture_cleaners(text):
    # 保留中文、常用标点和基本拉丁字符
    text = re.sub(r'[^\u4e00-\u9fff，。！？、a-zA-Z0-9\s]', '', text)
    
    # 分割文本为汉字和标点
    segments = re.split(r'([，。！？、])', text)
    phones = []
    
    for seg in segments:
        if not seg:
            continue
        if seg in ['，', '。', '！', '？', '、']:
            # 将中文标点映射为对应符号
            phones.append({
                '，': ',', 
                '。': '.', 
                '！': '!', 
                '？': '?', 
                '、': ','
            }[seg])
        else:
            # 处理中文部分
            seg_phones = pinyin(seg, style=Style.TONE3)
            phones.extend([p[0] for p in seg_phones])
    
    # 添加句子结束标点
    if phones and phones[-1] not in ['.', '!', '?']:
        phones.append('.')
    
    return ' '.join(phones)


def sanskrit_cleaners(text):
    text = text.replace('॥', '।').replace('ॐ', 'ओम्')
    text = re.sub(r'([^।])$', r'\1।', text)
    return text


def cjks_cleaners(text):
    text = re.sub(r'\[ZH\](.*?)\[ZH\]',
                  lambda x: chinese_to_lazy_ipa(x.group(1))+' ', text)
    text = re.sub(r'\[JA\](.*?)\[JA\]',
                  lambda x: japanese_to_ipa(x.group(1))+' ', text)
    text = re.sub(r'\[KO\](.*?)\[KO\]',
                  lambda x: korean_to_lazy_ipa(x.group(1))+' ', text)
    text = re.sub(r'\[SA\](.*?)\[SA\]',
                  lambda x: devanagari_to_ipa(x.group(1))+' ', text)
    text = re.sub(r'\[EN\](.*?)\[EN\]',
                  lambda x: english_to_lazy_ipa(x.group(1))+' ', text)
    text = re.sub(r'\s+$', '', text)
    text = re.sub(r'([^\.,!\?\-…~])$', r'\1.', text)
    return text


def cjke_cleaners(text):
    text = re.sub(r'\[ZH\](.*?)\[ZH\]', lambda x: chinese_to_lazy_ipa(x.group(1)).replace(
        'ʧ', 'tʃ').replace('ʦ', 'ts').replace('ɥan', 'ɥæn')+' ', text)
    text = re.sub(r'\[JA\](.*?)\[JA\]', lambda x: japanese_to_ipa(x.group(1)).replace('ʧ', 'tʃ').replace(
        'ʦ', 'ts').replace('ɥan', 'ɥæn').replace('ʥ', 'dz')+' ', text)
    text = re.sub(r'\[KO\](.*?)\[KO\]',
                  lambda x: korean_to_ipa(x.group(1))+' ', text)
    text = re.sub(r'\[EN\](.*?)\[EN\]', lambda x: english_to_ipa2(x.group(1)).replace('ɑ', 'a').replace(
        'ɔ', 'o').replace('ɛ', 'e').replace('ɪ', 'i').replace('ʊ', 'u')+' ', text)
    text = re.sub(r'\s+$', '', text)
    text = re.sub(r'([^\.,!\?\-…~])$', r'\1.', text)
    return text


def cjke_cleaners2(text):
    text = re.sub(r'\[ZH\](.*?)\[ZH\]',
                  lambda x: chinese_to_ipa(x.group(1))+' ', text)
    text = re.sub(r'\[JA\](.*?)\[JA\]',
                  lambda x: japanese_to_ipa2(x.group(1))+' ', text)
    text = re.sub(r'\[KO\](.*?)\[KO\]',
                  lambda x: korean_to_ipa(x.group(1))+' ', text)
    text = re.sub(r'\[EN\](.*?)\[EN\]',
                  lambda x: english_to_ipa2(x.group(1))+' ', text)
    text = re.sub(r'\s+$', '', text)
    text = re.sub(r'([^\.,!\?\-…~])$', r'\1.', text)
    return text


def thai_cleaners(text):
    text = num_to_thai(text)
    text = latin_to_thai(text)
    return text


# def shanghainese_cleaners(text):
#     text = shanghainese_to_ipa(text)
#     text = re.sub(r'([^\.,!\?\-…~])$', r'\1.', text)
#     return text


# def chinese_dialect_cleaners(text):
#     text = re.sub(r'\[ZH\](.*?)\[ZH\]',
#                   lambda x: chinese_to_ipa2(x.group(1))+' ', text)
#     text = re.sub(r'\[JA\](.*?)\[JA\]',
#                   lambda x: japanese_to_ipa3(x.group(1)).replace('Q', 'ʔ')+' ', text)
#     text = re.sub(r'\[SH\](.*?)\[SH\]', lambda x: shanghainese_to_ipa(x.group(1)).replace('1', '˥˧').replace('5',
#                   '˧˧˦').replace('6', '˩˩˧').replace('7', '˥').replace('8', '˩˨').replace('ᴀ', 'ɐ').replace('ᴇ', 'e')+' ', text)
#     text = re.sub(r'\[GD\](.*?)\[GD\]',
#                   lambda x: cantonese_to_ipa(x.group(1))+' ', text)
#     text = re.sub(r'\[EN\](.*?)\[EN\]',
#                   lambda x: english_to_lazy_ipa2(x.group(1))+' ', text)
#     text = re.sub(r'\[([A-Z]{2})\](.*?)\[\1\]', lambda x: ngu_dialect_to_ipa(x.group(2), x.group(
#         1)).replace('ʣ', 'dz').replace('ʥ', 'dʑ').replace('ʦ', 'ts').replace('ʨ', 'tɕ')+' ', text)
#     text = re.sub(r'\s+$', '', text)
#     text = re.sub(r'([^\.,!\?\-…~])$', r'\1.', text)
#     return text
