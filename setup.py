from setuptools import setup, find_packages

setup(
    name="pybacktest",  # Replace with your package name
    version="0.1.0",  # Start with an initial version
    packages=find_packages(),  # Automatically find packages in your project
    install_requires=[
        "dash == 2.18.2",
        "ipykernel == 6.29.5",
        "matplotlib == 3.10.0",
        "pandas-datareader == 0.10.0",
        "tinycss2 == 1.4.0",
        "yfinance == 0.2.52",
    ],
    author="Carlo Teufel",
    description="A comprehensive backtesting framework for financial trading strategies with interactive dashboard",
    long_description=open("README.md").read(),  # Ensure you have a README.md file
    long_description_content_type="text/markdown",  # For Markdown README files
    url="https://github.com/cteufel13/backtest",  # Replace with your repository URL if available
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Replace with your license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11.8",  # Specify the Python versions supported
)
