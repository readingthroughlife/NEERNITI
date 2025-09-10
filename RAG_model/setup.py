from setuptools import setup, find_packages

setup(
    name="neerniti-rag",
    version="0.1.0",
    description="Retrieval-Augmented Generation system for querying Gujarat district and taluk data",
    author="NEERNITI Team",
    author_email="",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.8.0",
        "cohere>=5.0.0",
        "chromadb>=0.4.18",
        "tqdm>=4.66.0",
        "numpy>=1.24.0",
        "PyPDF2>=3.0.0",
    ],
    python_requires=">=3.8",
)
