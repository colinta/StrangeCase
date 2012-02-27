import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
        name="StrangeCase",
        version="v2.0.1",
        packages=["strange_case"],
        author="Colin Thomas-Arnold",
        author_email="colinta.com",
        keywords="strange_case static site generator",
        description="A straightforward python static site generator.",
        long_description=read("README.md"),
        url="https://github.com/colinta/StrangeCase",
        platforms="any",
        license="BSD",
        install_requires=['Jinja2', 'MarkupSafe', 'PIL', 'PyYAML', 'markdown2', 'pymongo'],
        )
