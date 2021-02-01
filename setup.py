from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
setup(
    name='simple_socket',
    version='0.0.8',
    # 0.0.8 - Bug fix .ListenIPAddress was returning wrong value
    # 0.0.7 - Bug fix in _BaseTCPServer, timeout was set incorrectly causing long pauses
    # 0.0.6 - Added 'listenAddress' parameter
    # 0.0.5 - Added README.rst
    # 0.0.3 - Added SSL server/client
    # 0.0.2 - Added readme.md
    # 0.0.1 - init release
    packages=['simple_socket'],
    url='https://github.com/GrantGMiller/simple_socket',
    long_description=long_description,
    license='MIT',
    author='Grant Miller',
    author_email='grant@grant-miller.com',
    description='Simple event-based socket objects'
)

# python -m setup.py sdist bdist_wheel
# twine upload dist/*
