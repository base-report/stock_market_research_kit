# Stock Market Research Kit

Please note that this is currently very much a work in progress.

The Stock Market Research Kit is an open-source Python project brought to you by [base.report](https://base.report). It allows you to conduct systematic backtesting and analysis of the stock market. This research kit is designed to be flexible and extensible, enabling you to customize and improve upon the provided tools and methods.

## Prerequisites

### Financial Modeling Prep

Currently, the stock data is retrieved from Financial Modeling Prep. As of April 2023, you will need at least the [Professional plan](https://site.financialmodelingprep.com/developer/docs/pricing) to be able to use the bulk endpoint for fetching all profiles.

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

## Basic Usage

### Set up database

Set up the database by running the `setup_db.py` script:

```bash
python scripts/setup_db.py
```

### Download stock data

1. Get an API key from Financial Modeling Prep and add it to a `.env` file in the root folder of the project:

```
FMP_API_KEY=your_api_key_here
```

2. Download the stock data by running the `download_stock_data.py` script:

```bash
python scripts/download_stock_data.py
```

_Please note that only the `NASDAQ`, `NYSE`, and `AMEX` exchanges are selected. To target different exchanges, update the `VALID_EXCHANGES` list in the `scripts/download_stock_data.py` file._

3. Download the timeseries data by running the `download_timeseries.py` script:

```bash
python scripts/download_timeseries.py
```

_Please note the code currently is setup to handle 10 simultaneous downloads. Depending on the Financial Modeling Prep plan you have, you might want to adjust the `max_workers` number in the `scripts/download_timeseries.py` file. With 10 concurrent workers, this step takes ~30 minutes to complete._

The SQLite database `stock_market_research.db` will be created and the `stock_data` table will be populated with stock data and the timeseries data.

### Run backtest

To run the backtest for all of the results we have in the `stock_data` table, run the `run_backtest.py` script:

```bash
python scripts/run_backtest.py
```

_This should popoulate the `trades` table. With the default parameters and data as of early April 2023, there should be ~27,000 trades. This step should take ~3-5 minutes (possibly shorter or longer depending on the machine you are running this on)._

### Data Cleaning

After running the backtest, make sure to look for potentiall inaccurate data. For example, as of April 2023, the tickers `CBIO` and `VATE` contain some price data where some `adjClose` (adjusted close) are negative. As of result, any rows associated with these tickers will need to be deleted from the `trades` and `stock_data` tables.

### Analysis

To analyze data based on different factors like seasonality or ADR%, run the `analyze_trades.py` script:

```bash
python scripts/analyze_trades.py
```

This should create a series of CSV files in the `data/csv/` folder.

## ML Usage

### Plot stock charts

To plot a stock chart of the 200 daily candles prior to each trade entry, run the `plot_stock_charts.py` script:

```bash
python scripts/plot_stock_charts.py
```

_Please note that this loads all of the timeseries data into memory and uses 10 background workers to process the trades in parallel. This steps takes ~20 minutes to complete. Feel free to adjust the number of workers in `plot_stock_charts.py` to your machine's capabilities._

## Contributing

Contributions to the Stock Market Research Kit are welcome. If you have ideas for improvements or new features, please open an issue on GitHub or submit a pull request with your proposed changes.
