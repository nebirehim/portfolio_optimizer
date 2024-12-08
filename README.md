# Portfolio Optimization Application

This repository contains a Flask-based web application for portfolio optimization, visualization, and analysis of financial data. The app uses data from Yahoo Finance and S&P 500 constituent data from Wikipedia to provide advanced portfolio optimization capabilities using the **Riskfolio-Lib** library.

---

## Features

- **Fetch S&P 500 Tickers**  
  Retrieve a list of S&P 500 constituent stock tickers from Wikipedia.

- **Stock Data Retrieval**  
  Automatically fetch adjusted closing price data for a list of selected stocks over a specified date range using Yahoo Finance.

- **Portfolio Optimization**  
  Optimize portfolio allocation based on models such as:
  - Mean-Variance (MV)
  - Conditional Value-at-Risk (CVaR)
  - Mean Absolute Deviation (MAD)
  - Maximum Drawdown (MDD)

- **Visualizations**  
  - **Efficient Frontier**: Displays the trade-off between risk (standard deviation) and return.
  - **Portfolio Performance**: Shows individual stock prices and cumulative portfolio returns.
  - **Portfolio Weights Allocation**: Pie chart of the optimized portfolio weights.
  - **Correlation Matrix**: Heatmap of the correlation between the selected stocks.

- **Dark Mode Support**  
  Dynamic visualization adjustments for both light and dark modes.

---

## Installation

### Prerequisites

Ensure you have the following installed on your system:
- Python 3.8+
- Pip (Python package manager)

### Steps

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/portfolio-optimization-app.git
   cd portfolio-optimization-app

	2.	Install required Python libraries:

pip install -r requirements.txt


	3.	Run the application:

python app.py


	4.	Open your web browser and navigate to:

http://127.0.0.1:5000/

API Endpoints

1. /get_sp500_tickers
	•	Method: GET
	•	Description: Fetches the list of S&P 500 tickers.
	•	Response: JSON object containing the list of tickers.

2. /optimize
	•	Method: POST
	•	Description: Optimizes a portfolio based on user inputs.
	•	Request Payload:

{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "start_date": "2022-01-01",
  "end_date": "2023-01-01",
  "model": "MV",
  "is_dark_mode": true
}


	•	Response: JSON object with:
	•	weights: Optimized portfolio weights.
	•	price_graph: Stock performance graph in JSON.
	•	weights_graph: Portfolio weights pie chart in JSON.
	•	frontier_graph: Efficient frontier graph in JSON.
	•	correlation_graph: Correlation matrix heatmap in JSON.

Project Structure

portfolio-optimization-app/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html         # Frontend HTML template
├── static/                # Static assets (CSS, JS)
├── requirements.txt       # Python dependencies
└── README.md              # Documentation

Technologies Used
	•	Backend: Flask, Pandas, Riskfolio-Lib, Yahoo Finance (via yfinance)
	•	Frontend: Plotly, HTML, CSS
	•	Visualization: Plotly Graphs
	•	Data Sources:
	•	Yahoo Finance API
	•	Wikipedia (S&P 500 tickers)

Usage
	1.	Access the web interface.
	2.	Select S&P 500 tickers or manually input a list of stocks.
	3.	Specify the date range and optimization model.
	4.	Click Optimize to generate portfolio weights and visualizations.

Example Screenshots

Efficient Frontier

Correlation Matrix

Contributing

We welcome contributions to improve this project. Please fork the repository, make changes, and submit a pull request.

License

This project is licensed under the MIT License. See LICENSE for more details.

Acknowledgments
	•	Yahoo Finance for stock price data.
	•	Wikipedia for S&P 500 constituent data.
	•	Riskfolio-Lib for portfolio optimization functionality.
	•	Plotly for advanced data visualization.

