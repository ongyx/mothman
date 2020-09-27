from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    install_requires = f.read().split("\n")

setup(
    name="cidercellar",
    version="1.0.0a1",
    author="Ong Yong Xin",
    author_email="ongyongxin2020+github@gmail.com",
    description="Cydia/Sileo repository builder and configurator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ongyx/cidercellar",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    python_requires=">=3.6",
    install_requires=install_requires,
)
