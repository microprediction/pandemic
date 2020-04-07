import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="pandemic",
    version="0.1.7",
    description="Orstein-Uhlenbeck pandemic simulation",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/microprediction/pandemic",
    author="microprediction",
    author_email="info@microprediction.org",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=['pandemic'],
    test_suite='pytest',
    tests_require=['pytest','deepdiff'],
    include_package_data=True,
    install_requires=["numpy","pathlib","matplotlib","contexttimer","requests","python-geohash","deepdiff"],
    entry_points={
        "console_scripts": [
            "pandemic=pandemic.__main__:main",
        ]
     },
     )
