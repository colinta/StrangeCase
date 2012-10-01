import os
from setuptools import setup
from setuptools import find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
        name="StrangeCase",
        version="v4.5.21",
        author="Colin Thomas-Arnold",
        author_email="colinta@gmail",
        url="https://github.com/colinta/StrangeCase",
        install_requires=['Jinja2', 'PyYAML', 'watchdog'],  # 'PIL', 'markdown2', 'clevercss', 'pyScss', 'pytest', 'python-dateutil', 'unidecode'

        entry_points={
            'console_scripts': [
                'scase = strange_case.__main__:run'
            ]
        },

        description="A straightforward python static site generator.",
        long_description=read("README.rst"),

        packages=find_packages(),
        keywords="strange_case static site generator",
        platforms="any",
        license="BSD",
        classifiers=[
            "Programming Language :: Python",
            "Development Status :: 4 - Beta",
            'Environment :: Console',
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",

            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',

            "Topic :: Text Processing",
            'Topic :: Software Development',
            'Topic :: Software Development :: Build Tools',
            'Topic :: Software Development :: Code Generators',
            'Topic :: Internet',
            'Topic :: Internet :: WWW/HTTP :: Site Management',
        ],
    )
