from setuptools import setup

setup(
    name='simple_socket',
    version='0.0.1',
    packages=['simple_socket'],
    url='https://github.com/GrantGMiller/simple_socket',
    license='MIT',
    author='Grant Miller',
    author_email='grant@grant-miller.com',
    description='Simple event-based socket objects'
)

# python -m setup.py sdist bdist_wheel
# twine upload dist/*