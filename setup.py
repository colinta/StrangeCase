import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
        name="StrangeCase",
        version="v2.1.1",
        author="Colin Thomas-Arnold",
        author_email="colinta.com",
        url="https://github.com/colinta/StrangeCase",

        description="A straightforward python static site generator.",
        long_description=read("README.md"),

        packages=["strange_case"],
        keywords="strange_case static site generator",
        platforms="any",
        license="BSD",
        classifiers=[
            "Programming Language :: Python",
            "Development Status :: 4 - Beta",
            "Environment :: Other Environment",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Text Processing",
        ],
        )
