from setuptools import setup, find_packages

setup(
    name="tiktok-dlpy",
    version="1.2.0",
    url="https://github.com/Fluxticks/TikTokDL",
    download_url="https://github.com/Fluxticks/TikTokDL/archive/v1.2.0.tar.gz",
    author="Fluxticks",
    packages=find_packages(),
    install_requires=[
        "bs4",
        "lxml",
        "playwright",
        "numpy",
        "opencv-python",
    ],
    description="A package to dowload TikTok videos via URL",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10"
    ],
    keywords=["tiktok",
              "playwright",
              "async"],
)