FROM ubuntu:22.04
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

RUN apt update
RUN pip3 install playwright && playwright install --with-deps