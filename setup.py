import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyCommandsTool",
    version="2.0.1",
    author="Haven Selph",
    author_email="havenselph@gmail.com",
    description="A simple and easy-to-use module that streamlines the whole user-input side of your script.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HavenSelph/PyCommands",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)