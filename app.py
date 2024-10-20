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
    # Calculate returns
    returns = data.pct_change().dropna()
    
    # Build Portfolio object
    port = rp.Portfolio(returns=returns)
    
    # Estimate inputs for optimization
    port.assets_stats(method_mu='hist', method_cov='ledoit')

    # Optimization based on selected model
    if model == 'MV':
        weights = port.optimization(model='Classic', rm='MV', obj='Sharpe')
    elif model == 'CVaR':
        weights = port.optimization(model='Classic', rm='CVaR', obj='Sharpe')
    elif model == 'MAD':
        weights = port.optimization(model='Classic', rm='MAD', obj='Sharpe')
    
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
        tickers = request.form.get('tickers').split(',')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        model = request.form.get('model')

        # Fetch stock data
        data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
        
        # Optimize portfolio based on selected model
        weights = optimize_portfolio(data, model=model)

        # Generate portfolio performance plot
        performance_chart = plot_portfolio_performance(data, weights)
        
        # Render results template with data and chart
        graph_json = json.dumps(performance_chart, cls=plotly.utils.PlotlyJSONEncoder)  # Use Plotly's JSON encoder
        return render_template('result.html', weights=weights.to_dict(), graph_data=graph_json)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
