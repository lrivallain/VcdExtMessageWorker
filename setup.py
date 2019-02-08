from distutils.core import setup # pylint: disable=no-name-in-module,import-error
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='VcdExtMessageWorker',
    version='0.3',
    author="Ludovic Rivallain",
    author_email='ludovic.rivallain@gmail.com',
    packages=setuptools.find_packages(),
    license='MIT',
    description='RabbitMQ message worker for vCloud Director Extensibility SDK',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "kombu",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/lrivallain/VcdExtMessageWorker",
)