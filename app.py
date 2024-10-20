from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
import riskfolio as rp
import plotly.graph_objs as go
import json
import plotly

app = Flask(__name__)

# Function to fetch stock data from Yahoo Finance
def get_stock_data(tickers, start_date, end_date):
    stock_data = yf.download(tickers, start=start_date, end=end_date)
    stock_data = stock_data['Adj Close']
    
    if isinstance(stock_data, pd.Series):
        stock_data = stock_data.to_frame()

    if stock_data.empty:
        raise ValueError("No stock data was returned. Please check the tickers and date range.")
    
    return stock_data

# Function to optimize portfolio using Riskfolio-Lib
def optimize_portfolio(data, model='MV'):
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Stock data must be a DataFrame.")

    returns = data.pct_change().dropna()
    
    if returns.empty:
        raise ValueError("Returns are empty after processing.")
    
    port = rp.Portfolio(returns=returns)
    port.assets_stats(method_mu='hist', method_cov='ledoit')

    if model == 'MV':
        weights = port.optimization(model='Classic', rm='MV', obj='Sharpe')
    elif model == 'CVaR':
        weights = port.optimization(model='Classic', rm='CVaR', obj='Sharpe')
    elif model == 'MAD':
        weights = port.optimization(model='Classic', rm='MAD', obj='Sharpe')
    else:
        raise ValueError("Invalid model selected.")
    
    return weights

# Function to plot performance of the portfolio
# Function to plot performance of the portfolio
def plot_performance(data, weights):
    returns = data.pct_change().dropna()
    portfolio_return = (returns * weights).sum(axis=1)
    cumulative_returns = (1 + portfolio_return).cumprod()

    # Create price trend traces
    price_traces = []
    for ticker in data.columns:
        price_traces.append(go.Scatter(x=data.index, y=data[ticker], mode='lines', name=f'{ticker} Price'))

    # Create cumulative return trace
    price_traces.append(go.Scatter(x=cumulative_returns.index, y=cumulative_returns, mode='lines', name='Cumulative Portfolio Return', line=dict(color='blue', width=2)))

    # Create price figure
    price_fig = go.Figure(data=price_traces)
    price_fig.update_layout(title='Stock Prices and Portfolio Cumulative Returns',
                             xaxis_title='Date',
                             yaxis_title='Price',
                             legend_title='Legend',
                             hovermode='x unified',
                             plot_bgcolor='rgba(240, 240, 240, 0.9)')  # Light gray background

    # Ensure weights are properly formatted for the pie chart
    weights_values = weights.values.flatten().tolist()
    weights_labels = weights.index.tolist()

    # Check for non-zero weights (to avoid empty pie chart)
    if sum(weights_values) == 0:
        weights_values = [1] * len(weights_values)  # Temporary fix for displaying empty portfolios

    # Create pie chart for weights
    weights_fig = go.Figure(data=[go.Pie(labels=weights_labels, values=weights_values, hole=0.4)])
    weights_fig.update_layout(title='Portfolio Weights Allocation',
                               plot_bgcolor='rgba(240, 240, 240, 0.9)',
                               paper_bgcolor='rgba(240, 240, 240, 0.9)')

    return price_fig, weights_fig


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json
    tickers = data['tickers']
    start_date = data['start_date']
    end_date = data['end_date']
    model = data['model']

    # Fetch stock data
    stock_data = get_stock_data(tickers, start_date, end_date)

    # Optimize portfolio
    weights = optimize_portfolio(stock_data, model)

    # Plot performance
    price_fig, weights_fig = plot_performance(stock_data, weights)

    # Convert figures to JSON for rendering
    price_graph_json = json.dumps(price_fig, cls=plotly.utils.PlotlyJSONEncoder)
    weights_graph_json = json.dumps(weights_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return jsonify(weights=weights.to_dict(), price_graph=price_graph_json, weights_graph=weights_graph_json)

if __name__ == "__main__":
    app.run(debug=True)
