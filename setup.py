from pathlib import Path

from setuptools import find_packages, setup

requirements = Path("requirements.txt").read_text().splitlines()

setup(
    name="E-commerce LLMOPS-Agent",
    version="0.1.0",
    author="ridabayi",
    author_email="bayi.rida@gmail.com",
    packages=find_packages(),
    install_requires=requirements,
)
