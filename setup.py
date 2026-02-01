from setuptools import setup, find_packages


setup(
    name='sympyentrywidget',
    version="0.9",
    packages = find_packages(),
    # Dependencies are now managed in requirements.txt
    tests_require=['pytest', 'pytest-qt'],
)
