#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="proxy-sales-bot",
    version="1.0.0",
    author="Proxy Bot Developer",
    author_email="developer@example.com",
    description="بوت تيليجرام متكامل لبيع البروكسيات مع إدارة أدمن شاملة ونظام إحالات",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/proxy-sales-bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "proxy-bot=simpl_bot:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt"],
    },
    keywords="telegram bot proxy sales admin management referral system",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/proxy-sales-bot/issues",
        "Source": "https://github.com/yourusername/proxy-sales-bot",
        "Documentation": "https://github.com/yourusername/proxy-sales-bot#readme",
    },
)