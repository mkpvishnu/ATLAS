from setuptools import setup, find_namespace_packages
import os

# Read the contents of README.md
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="lsada",
    version="1.5.0",
    packages=find_namespace_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "lsada.pool": ["*.json"],
    },
    include_package_data=True,
    install_requires=[
        "openai>=1.0.0",
        "anthropic>=0.3.0",
        "python-dotenv>=0.19.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
        "flask>=2.0.0",  # For web server functionality
        "requests>=2.25.0",  # For HTTP requests
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=0.900",
            "flake8>=4.0.0",
            "pytest-cov>=3.0.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    python_requires=">=3.8",
    author="M K P Vishnu",
    author_email="mkpvishnu@gmail.com",
    description="A flexible evaluation framework for content using LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mkpvishnu/atlas",
    project_urls={
        "Bug Tracker": "https://github.com/mkpvishnu/atlas/issues",
        "Documentation": "https://github.com/mkpvishnu/atlas/wiki",
        "Source Code": "https://github.com/mkpvishnu/atlas",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Operating System :: OS Independent",
    ],
    keywords="llm, evaluation, content-analysis, machine-learning, nlp",
)
