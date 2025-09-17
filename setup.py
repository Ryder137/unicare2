from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="unicare",
    version="0.1.0",
    author="UNICARE Team",
    author_email="contact@example.com",
    description="A mental health support platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/unicare",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask>=2.0.1",
        "Flask-Login>=0.5.0",
        "Flask-PyMongo>=2.3.0",
        "Flask-Limiter>=2.4.0",
        "python-dotenv>=0.19.0",
        "pymongo>=3.12.0",
        "bcrypt>=3.2.0",
        "email-validator>=1.1.3",
        "Flask-Mail>=0.9.1",
        "python-jose>=3.3.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
