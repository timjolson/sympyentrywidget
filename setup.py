from setuptools import setup, find_packages


setup(
    name='sympyEntryWidget',
    version="0.6",
    packages = find_packages(),
    install_requires = ['PyQt5', 'sympy'],
    dependency_links=[
        'https://github.com/timjolson/entrywidget.git',
        'https://github.com/timjolson/qt_utils.git'
        ],
    tests_require = ['pytest'],
)