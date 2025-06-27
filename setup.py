from setuptools import setup, find_packages

setup(
    name="pluseposter",
    version="0.1.0",
    description="A Python automation tool for social media posting",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Kofidell4545",
    url="https://github.com/Kofidell4545/PlusePoster",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=open("requirements.txt").readlines(),
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "pluseposter=pluseposter.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
