import os
from setuptools import setup
from setuptools import find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
        name="StrangeCase",
        version="4.6.6",
        author="Colin T.A. Gray",
        author_email="colinta@gmail.com",
        url="https://github.com/colinta/StrangeCase",
        install_requires=['Jinja2', 'PyYAML', 'watchdog'],
        # optional: 'Pillow', 'misaka', 'clevercss', 'pyScss', 'pytest', 'python-dateutil', 'unidecode', 'plywood'
        python_requires='>3.0.0',

        entry_points={
            'console_scripts': [
                'scase = strange_case.__main__:run'
            ]
        },

        description="A straightforward python static site generator.",
        long_description=read("README.rst"),

        packages=find_packages(exclude=['strange_case.tests']),
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
