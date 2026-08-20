from setuptools import setup, Extension

snapshot_module = Extension(
    'snapshot',
    sources=['src/c_bridge/snapshot.c'],
)

setup(
    name='ProteusOS-C',
    version='1.0',
    description='C extensions for ProteusOS',
    ext_modules=[snapshot_module],
)
