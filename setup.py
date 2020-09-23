from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name = 's3Review',
    version = '0.1.0',
    packages = ['S3CLI'],
    entry_points = {
        'console_scripts': [
            's3cli = S3CLI.__main__:main'
        ]
    },
    install_requires=required
)