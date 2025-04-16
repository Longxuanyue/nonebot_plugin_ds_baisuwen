from setuptools import setup, Extension

module = Extension(
    'core',
    sources=['core.c'],
)

setup(
    name='monotonic_align',
    ext_modules=[module],
    # 如果使用包结构，可能需要指定package_dir
    package_dir={'nonebot_plugin_baisuwen.monotonic_align': '.'},
)