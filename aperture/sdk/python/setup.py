from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aperture-ai",
    version="0.1.0",
    author="Aperture Team",
    author_email="hello@aperture.dev",
    description="Official Python SDK for Aperture - User Intelligence for AI Apps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aperture",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="ai llm user-intelligence analytics conversational-ai",
    project_urls={
        "Documentation": "https://docs.aperture.dev",
        "Source": "https://github.com/yourusername/aperture",
        "Bug Reports": "https://github.com/yourusername/aperture/issues",
    },
)
