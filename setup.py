"""Setup module for EcoWitt."""
from pathlib import Path

from setuptools import find_packages, setup

PROJECT_DIR = Path(__file__).parent.resolve()
README_FILE = PROJECT_DIR / "README.md"
VERSION = "2022.08.2"


setup(
    name="aioecowitt",
    version=VERSION,
    url="https://github.com/home-assistant-libs/aioecowitt",
    download_url="https://github.com/home-assistant-libs/aioecowitt",
    author="Home Assistant Team",
    author_email="hello@home-assistant.io",
    description="Python wrapper for EcoWitt Protocol",
    long_description=README_FILE.read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["test.*", "test", "misc"]),
    package_data={"aioecowitt": ["py.typed"]},
    python_requires=">=3.9",
    install_requires=["aiohttp>3", "meteocalc>=1.1.0"],
    entry_points={"console_scripts": ["ecowitt-testserver = aioecowitt.__main__:main"]},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Home Automation",
    ],
)
