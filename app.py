from flask import Flask, render_template, request, redirect, url_for
import plotly
import yfinance as yf
import riskfolio as rp
import pandas as pd
import plotly.graph_objs as go
import json
import numpy as np

app = Flask(__name__)

# Home route to input tickers and select a model
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        tickers = request.form['tickers']
        model = request.form['model']
        return redirect(url_for('results', tickers=tickers, model=model))
    return render_template('index.html')

# Results route for optimization
@app.route('/results')
def results():
    tickers = request.args.get('tickers')
    model = request.args.get('model')

    # Split tickers string into a list of symbols
    stock_list = [ticker.strip() for ticker in tickers.split(',')]

    # Download stock data from Yahoo Finance
    try:
        data = yf.download(stock_list, period="1y")['Adj Close']

        # Handle the case where a single stock is provided
        if isinstance(data, pd.Series):
            data = pd.DataFrame(data)  # Convert Series to DataFrame
            data.columns = [stock_list[0]]  # Rename the column with the stock ticker

        # Check if data is returned
        if data.empty:
            return f"No data available for the given tickers: {tickers}. Please check the ticker symbols."
    except Exception as e:
        return f"An error occurred while fetching data: {str(e)}"

    # Clean data: Ensure all values are numeric and remove any missing values
    data = data.dropna()  # Drop rows with missing values
    data = data.apply(pd.to_numeric, errors='coerce')  # Ensure data is numeric, convert invalid entries to NaN
    data = data.dropna()  # Drop any rows with NaNs after conversion

    # Check again if the data is now valid
    if data.empty:
        return "No valid data after cleaning. Please check the stock tickers or try different tickers."

    # Calculate returns (percentage change in prices)
    returns = data.pct_change().dropna()

    # Ensure returns DataFrame is fully numeric
    returns.replace([np.inf, -np.inf], np.nan, inplace=True)  # Replace infinite values with NaN
    returns = returns.dropna()  # Drop any rows with NaN values

    # Check if the returns data is valid and properly formatted
    if returns.empty or len(returns.columns) < len(stock_list):
        return "Insufficient data to calculate returns. Please check your tickers."

    # Standardize column names and index
    returns.columns = [ticker for ticker in stock_list]  # Ensure proper column names
    returns.index = pd.to_datetime(returns.index)  # Ensure proper datetime index

    # Check data structure for debugging
    print(f"Shape of returns DataFrame: {returns.shape}")
    print(f"First few rows of returns DataFrame: \n{returns.head()}")

    # Convert returns DataFrame to a numpy array (workaround to avoid object arrays issue)
    returns_array = returns.to_numpy()

    # Attempt to create Portfolio object and optimize
    try:
        port = rp.Portfolio(returns=pd.DataFrame(returns_array, columns=returns.columns))
    except Exception as e:
        return f"Error creating portfolio object: {str(e)}"

    # Choose the optimization model based on user input
    try:
        if model == 'Mean-Variance':
            w = port.optimization(model='Classic', rm='MV', obj='Sharpe', rf=0, l=0)
        elif model == 'Risk-Parity':
            w = port.optimization(model='Classic', rm='MV', obj='MinRisk', rf=0, l=0)
        elif model == 'Max-Sharpe':
            w = port.optimization(model='Classic', rm='MV', obj='Sharpe', rf=0, l=0)
        elif model == 'Efficient-Frontier':
            w = port.efficient_frontier(model='Classic', points=50, rf=0)
        else:
            return "Model not recognized. Please select a valid model."
    except Exception as e:
        # Capture specific errors during optimization
        return f"An error occurred during optimization: {str(e)}"

    # Check optimization output
    print(f"Optimized weights: \n{w}")

    # Prepare weights dictionary for output
    weights_dict = w.to_dict()

    # Plotly Bar Chart for Portfolio Weights
    fig = go.Figure([go.Bar(x=list(weights_dict.keys()), y=list(weights_dict.values()))])
    fig.update_layout(title='Portfolio Weights', xaxis_title='Stocks', yaxis_title='Weights')

    # Convert plotly figure to JSON for rendering
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('results.html', tickers=tickers, model=model, weights=weights_dict, graphJSON=graphJSON)

if __name__ == '__main__':
    app.run(debug=True)
