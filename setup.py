from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read()

with open("README.md") as f:
    readme = f.read()

setup(
    name="tiktok-dlpy",
    version="1.1.0",
    url="https://github.com/Fluxticks/TikTokDL",
    download_url="https://github.com/Fluxticks/TikTokDL/archive/v1.1.0.tar.gz",
    author="Fluxticks",
    packages=find_packages(),
    install_requires=requirements,
    long_description=readme,
    long_description_content_type="text/markdown",
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