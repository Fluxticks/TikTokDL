from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read()

with open("README.md") as f:
    readme = f.read()

setup(
    name="tiktokdl",
    version="1.0.0",
    url="https://github.com/Fluxticks/TikTokDL",
    author="Fluxticks",
    packages=find_packages(),
    install_requires=requirements,
    long_description=readme,
    long_description_content_type="text/markdown",
    description="A package to dowload TikTok videos via URL"
)