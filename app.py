from flask import Flask, render_template, request
import yfinance as yf
import riskfolio as rp
import pandas as pd
import plotly.graph_objs as go
import json
import plotly

app = Flask(__name__)

# Function to optimize portfolio
def optimize_portfolio(data, model='MV'):
    # Ensure the input data is a DataFrame
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Stock data must be a DataFrame.")

    # Step 1: Calculate the daily returns from the adjusted close prices
    returns = data.pct_change().dropna()

    # Ensure returns is a DataFrame
    if not isinstance(returns, pd.DataFrame):
        raise ValueError("Returns must be a DataFrame.")

    # Step 2: Build a Portfolio object with the returns
    port = rp.Portfolio(returns=returns)

    # Step 3: Estimate the inputs for the optimization
    port.assets_stats(method_mu='hist', method_cov='ledoit')

    # Step 4: Perform the optimization based on the selected model
    if model == 'MV':
        weights = port.optimization(model='Classic', rm='MV', obj='Sharpe')
    elif model == 'CVaR':
        weights = port.optimization(model='Classic', rm='CVaR', obj='Sharpe')
    elif model == 'MAD':
        weights = port.optimization(model='Classic', rm='MAD', obj='Sharpe')
    else:
        raise ValueError("Invalid model selected.")

    return weights

# Function to plot portfolio performance
def plot_portfolio_performance(data, weights):
    returns = data.pct_change().dropna()
    portfolio_return = (returns * weights).sum(axis=1)

    # Create cumulative return plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=portfolio_return.index, 
                             y=(1 + portfolio_return).cumprod(), 
                             mode='lines', name='Portfolio'))
    fig.update_layout(title='Portfolio Performance',
                      xaxis_title='Date', yaxis_title='Cumulative Returns')
    
    return fig

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the user input (tickers, date range, and model)
        tickers = request.form.get('tickers').split(',')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        model = request.form.get('model')

        # Fetch stock data (Adjusted Close prices) using yfinance
        data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']

        # Ensure data is in a DataFrame
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Stock data must be a DataFrame.")

        # Optimize portfolio based on the selected model
        weights = optimize_portfolio(data, model=model)

        # Generate portfolio performance plot
        performance_chart = plot_portfolio_performance(data, weights)

        # Send the plot to the result template
        graph_json = json.dumps(performance_chart, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('result.html', weights=weights.to_dict(), graph_data=graph_json)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
