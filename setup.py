from distutils.core import setup
import setuptools

setup(
    name='VcdExtMessageWorker',
    version='0.1',
    author="Ludovic Rivallain",
    author_email='ludovic.rivallain@gmail.com',
    packages=['vcdextmessageworker'],
    license='MIT',
    description='RabbitMQ message worker for vCloud Director Extensibility SDK',
    long_description=open('README.txt').read(),
    install_requires=[
        "kombu",
    ],
)
