from setuptools import find_packages, setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="autoplaywright-python",
    version="1.0.3",
    description="Automating Playwright steps using ChatGPT(OpenAI) or DeepSeek in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nohet/autoplaywright-python",
    author="Nohet",
    author_email="igorczupryniak503@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="playwright automation, autoplaywright, playwright ai, playwright with ai, ChatGPT playwright",
    include_package_data=True,
    packages=find_packages(),
    install_requires=["pydantic", "openai", "bs4"],
)