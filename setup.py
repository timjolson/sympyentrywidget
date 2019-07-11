from setuptools import setup, find_packages


setup(
    name='sympyEntryWidget',
    version="0.7",
    packages = find_packages(),
    install_requires = ['PyQt5', 'sympy'],
    dependency_links=[
        'https://github.com/timjolson/qt_utils.git',
        'https://github.com/timjolson/entrywidget.git'
        ],
    tests_require = ['pytest', 'pytest-qt'],
)