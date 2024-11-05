from setuptools import setup, find_packages

setup(
    name='mysql_wrapper',
    version='0.4',
    packages=find_packages(),
    install_requires=[
        'mysql-connector-python'
    ],
    author='Ahmed Sharief',
    description='A generic MySQL wrapper for database operations.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    url='https://github.com/ahmed-sharief5/mysql-wrapper-package.git',
)
