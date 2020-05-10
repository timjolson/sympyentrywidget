from setuptools import setup, find_packages


setup(
    name='sympyentrywidget',
    version="0.9",
    packages = find_packages(),
    install_requires=['PyQt5==5.9', 'sympy'],
    tests_require=['pytest', 'pytest-qt'],
)
