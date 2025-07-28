from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='FLIPKART LLMOPS-Agent',
    version='0.1.0',
    author='ridabayi',
    author_email='bayi.rida@gmail.com',
    packages=find_packages(),
    install_requires=requirements,
)