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
    
    # Pull stock data
    stock_list = tickers.split(',')
    data = yf.download(stock_list, period="1y")['Adj Close']
    
    # Portfolio Optimization
    Y = data.pct_change().dropna()
    port = rp.Portfolio(returns=Y)
    
    # Optimization Models
    if model == 'Mean-Variance':
        w = port.optimization(model='Classic', rm='MV', obj='Sharpe', rf=0, l=0)
    elif model == 'Risk-Parity':
        w = port.optimization(model='Classic', rm='MV', obj='MinRisk', rf=0, l=0)
    elif model == 'Max-Sharpe':
        w = port.optimization(model='Classic', rm='MV', obj='Sharpe', rf=0, l=0)
    elif model == 'Efficient-Frontier':
        w = port.efficient_frontier(model='Classic', points=50, rf=0)
    
    weights_dict = w.to_dict()

    # Bar Chart for Portfolio Weights
    fig = go.Figure([go.Bar(x=list(weights_dict.keys()), y=list(weights_dict.values()))])
    fig.update_layout(title='Portfolio Weights', xaxis_title='Stocks', yaxis_title='Weights')
    
    # Convert plotly figure to JSON for rendering
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('results.html', tickers=tickers, model=model, weights=weights_dict, graphJSON=graphJSON)

if __name__ == '__main__':
    app.run(debug=True)
