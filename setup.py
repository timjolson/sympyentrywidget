from setuptools import setup, find_packages


setup(
    name='sympyentrywidget',
    version="0.9",
    packages = find_packages(),
    install_requires = ['PyQt5', 'sympy'],
    dependency_links=[
        'https://github.com/timjolson/qt_utils.git',
        'https://github.com/timjolson/entrywidget.git'
        ],
    tests_require = ['pytest', 'pytest-qt'],
)