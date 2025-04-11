# setup.py
from setuptools import setup, find_packages

setup(
    name="FileMetaLib",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        # No hard dependencies
    ],
    extras_require={
        "image": ["Pillow"],
        "all": ["Pillow"],
    },
    author="Srinivas Sarkar",
    author_email="srinivassarkar07@gmail.com",
    description="A library for attaching, indexing, and querying metadata for files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/srinivassarkar/FileMetaLib",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
