import pathlib
from setuptools import setup, find_packages
from gitsync import __version__

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="git-sync",
    version=__version__,
    python_requires=">=3.6, <4",
    packages=find_packages(),
    install_requires=[
        "gitpython==3.1.40",
    ],
    extras_require={
        "dev": [],
        "test": [
            "black",
            "coverage",
            "pylint",
            "flake8",
            "pytest",
        ],
    },
    description="A daemon for keeping git repo sync",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/e7h4n/git-sync",
    author="e7h4n",
    author_email="ethan.pw@icloud.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Accounting",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="daemon, git sync",
    package_dir={"git-sync": "gitsync"},
    entry_points={
        "console_scripts": [
            "git-sync=gitsync.service:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/e7h4n/git-sync/issues",
        "Source": "https://github.com/e7h4n/git-sync/",
    },
)
