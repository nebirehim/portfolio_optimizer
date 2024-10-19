from flask import Flask, render_template, request, redirect, url_for
import plotly
import yfinance as yf
import riskfolio as rp
import pandas as pd
import plotly.graph_objs as go
import json

app = Flask(__name__)

# Home route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        tickers = request.form['tickers']
        model = request.form['model']
        return redirect(url_for('results', tickers=tickers, model=model))
    return render_template('index.html')

# Results route
@app.route('/results')
def results():
    tickers = request.args.get('tickers')
    model = request.args.get('model')
    
    # Split tickers string into a list of symbols
    stock_list = [ticker.strip() for ticker in tickers.split(',')]
    
    # Download stock data from Yahoo Finance
    try:
        data = yf.download(stock_list, period="1y")['Adj Close']
        
        # Convert to DataFrame if only one ticker is provided
        if isinstance(data, pd.Series):
            data = pd.DataFrame(data)

        # Check if data is returned
        if data.empty:
            return f"No data available for the given tickers: {tickers}. Please check the ticker symbols."
    except Exception as e:
        return f"An error occurred while fetching data: {str(e)}"
    
    # Calculate returns - percentage change in prices
    returns = data.pct_change().dropna()

    # Ensure all data is numeric and there are no 'object' columns
    returns = returns.apply(pd.to_numeric, errors='coerce')  # Convert non-numeric values to NaN
    returns = returns.dropna()  # Drop any rows with NaN values

    # Ensure the DataFrame is not empty after cleaning
    if returns.empty or len(returns.columns) < len(stock_list):
        return "Insufficient data to calculate returns. Please check the stock tickers or try with different tickers."

    # Create Portfolio object with the returns DataFrame
    port = rp.Portfolio(returns=returns)
    
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
        return f"An error occurred during optimization: {str(e)}"

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
