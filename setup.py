#!/usr/bin/env python

import setuptools

application_dependencies = []
test_dependencies = ["pytest", "pytest-env", "pytest-cov", "pytz"]
lint_dependencies = ["flake8", "flake8-docstrings", "black", "isort", "mypy"]
docs_dependencies = []
deploy_dependencies = ["requests", "twine"]
dev_dependencies = test_dependencies + lint_dependencies + docs_dependencies + deploy_dependencies + ["ipdb"]


with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION", "r") as buf:
    version = buf.read()

setuptools.setup(
    name="jsonmarshal",
    version=version,
    description="Marshal JSON to/from python dataclasses.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mike Wooster",
    author_email="",
    url="https://github.com/MikeWooster/jsonmarshal",
    python_requires=">=3.6",
    packages=["jsonmarshal"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    install_requires=application_dependencies,
    extras_require={
        "test": test_dependencies,
        "lint": lint_dependencies,
        "docs": dev_dependencies,
        "dev": dev_dependencies,
        "deploy": deploy_dependencies,
    },
    include_package_data=True,
    zip_safe=False,
)
