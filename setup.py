from setuptools import setup, find_packages

setup(
    name="sympyEntryWidget",
    version="0.5",
    packages = find_packages(),
    install_requires = ['PyQt5', 'sympy'],
)