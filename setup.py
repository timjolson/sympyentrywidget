from setuptools import setup, find_packages


setup(
    name='sympyentrywidget',
    version="0.9",
    packages = find_packages(),
    install_requires=['PyQt5==5.9', 'sympy'],
    dependency_links=[
        'https://github.com/timjolson/generalutils.git',
        'https://github.com/timjolson/qt_utils.git',
        ],
    tests_require=['pytest', 'pytest-qt'],
)
