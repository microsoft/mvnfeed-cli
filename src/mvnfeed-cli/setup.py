from setuptools import setup, find_packages

NAME = 'mvnfeed-cli'
VERSION = '0.0.1'

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    'knack==0.5.1',
    'mvnfeed-cli-common==' + VERSION,
    'mvnfeed-cli-transfer==' + VERSION,
]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'License :: OSI Approved :: MIT License',
]

setup(
    name=NAME,
    version=VERSION,
    license='MIT',
    description="MvnFeed Command Line Interface",
    author="Vladimir Ritz Bossicard",
    author_email="vlritz@microsoft.com",
    url="",
    keywords=["Maven", "MvnFeed", "CLI"],
    install_requires=REQUIRES,
    packages=find_packages(),
    classifiers=CLASSIFIERS,
    entry_points={
        'console_scripts': [
            'mvnfeed = mvnfeed.cli.__main__:main'
        ]
    },
    include_package_data=True,
    long_description="""\
    """
)
