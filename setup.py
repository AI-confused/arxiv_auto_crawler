import setuptools

# with open("./README.org", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="arxiv_auto_crawler",
    version="0.0.5",
    author="black_tears",
    author_email="21860437@zju.edu.cn",
    description="Used for crawling arxiv papers automatically.",
    long_description='Used for crawling arxiv papers automatically.',
    long_description_content_type="text/markdown",
    url="https://github.com/AI-confused/arxiv_scrawl",
    project_urls={
        "Bug Tracker": "https://github.com/AI-confused/arxiv_scrawl/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)