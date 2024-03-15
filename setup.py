from setuptools import setup, find_packages

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="tiktok-dlpy",
    version="1.6.0",
    url="https://github.com/Fluxticks/TikTokDL",
    download_url="https://github.com/Fluxticks/TikTokDL/archive/v1.6.0.tar.gz",
    author="Fluxticks",
    packages=find_packages(),
    install_requires=[
        "playwright",
        "numpy",
        "opencv-python",
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    description=
    "A package to download TikTok videos or slideshows by URL without needing to login",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ],
    keywords=["tiktok", "playwright", "async"],
)
