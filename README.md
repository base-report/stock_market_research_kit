# Stock Market Research Kit

Please note that this is currently very much a work in progress.

The Stock Market Research Kit is an open-source Python project brought to you by [base.report](https://base.report). It allows you to conduct systematic backtesting and analysis of the stock market. This research kit is designed to be flexible and extensible, enabling you to customize and improve upon the provided tools and methods.

## Prerequisites

Before getting started, ensure that you have the following tools installed on your system:

- Conda: A package and environment manager for Python ([https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html))
- SQLite: A small, fast, self-contained, high-reliability, full-featured, SQL database engine (https://sqlite.org)

## Installation

1.  Clone the repository using Git:

```bash
git clone https://github.com/base-report/stock_market_research_kit.git
```

2.  Navigate to the project directory:

```bash
cd stock_market_research_kit
```

3.  Create a Conda environment for the project:

```bash
conda create --name smrk python=3.x
```

Replace `3.x` with the desired Python 3 version (e.g., 3.11.3). This command will create a new Conda environment named `smrk` with the specified Python version.

4.  Activate the Conda environment:

```bash
conda activate smrk
```

5.  Install the required dependencies:

```bash
conda install --file requirements.txt
```

This command installs all the necessary packages specified in the `requirements.txt` file.

## Usage

Follow the instructions below to set up the database, download stock data, and download the timeseries data.

1. Get an API key from Financial Modeling Prep (FMP) and add it to a `.env` file in the root folder of the project:

```
FMP_API_KEY=your_api_key_here
```

2. Set up the database by running the `setup_db.py` script:

```bash
python scripts/setup_db.py
```

3. Download the stock data by running the `download_stock_data.py` script:

```bash
python scripts/download_stock_data.py
```

4. Download the timeseries data by running the `download_timeseries.py` script:

```bash
python scripts/download_timeseries.py
```

The SQLite database `stock_market_research.db` will be created and populated with stock data and the timeseries data.

## Contributing

Contributions to the Stock Market Research Kit are welcome. If you have ideas for improvements or new features, please open an issue on GitHub or submit a pull request with your proposed changes.