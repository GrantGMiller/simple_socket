from setuptools import setup

setup(
    name='simple_socket',
    version='0.0.2',
    # 0.0.2 - Added readme.md
    # 0.0.1 - init release
    packages=['simple_socket'],
    url='https://github.com/GrantGMiller/simple_socket',
    license='MIT',
    author='Grant Miller',
    author_email='grant@grant-miller.com',
    description='Simple event-based socket objects'
)

# python -m setup.py sdist bdist_wheel
# twine upload dist/*