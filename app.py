from flask import Flask, render_template, request
import yfinance as yf
import riskfolio as rp
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import json
import plotly

app = Flask(__name__)

# Function to optimize portfolio
def optimize_portfolio(data, model='MV'):
    # Ensure input data is a DataFrame
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Stock data must be a DataFrame.")
    if data.empty:
        raise ValueError("Stock data is empty. Check tickers or date range.")

    # Calculate daily returns
    returns = data.pct_change().dropna()

    # Debug: print the returns DataFrame
    print("Returns DataFrame: ", returns)

    # Ensure the returns DataFrame is not empty
    if returns.empty:
        raise ValueError("Returns are empty after processing.")

    # Create a Portfolio object
    port = rp.Portfolio(returns=returns)

    # Estimate portfolio inputs (mean, covariance)
    port.assets_stats(method_mu='hist', method_cov='ledoit')

    # Perform optimization based on the selected model
    if model == 'MV':
        weights = port.optimization(model='Classic', rm='MV', obj='Sharpe')
    elif model == 'CVaR':
        weights = port.optimization(model='Classic', rm='CVaR', obj='Sharpe')
    elif model == 'MAD':
        weights = port.optimization(model='Classic', rm='MAD', obj='Sharpe')
    else:
        raise ValueError("Invalid model selected.")
    
    print("Optimized Weights: ", weights)  # Debug: print optimized weights
    
    return weights


# Function to plot portfolio performance
def plot_portfolio_performance(data, weights):
    # 1. Create a weighted portfolio return series
    returns = data.pct_change().dropna()
    portfolio_return = (returns * weights).sum(axis=1)

    # 2. Plot Portfolio Performance (Line chart)
    performance_trace = go.Scatter(x=portfolio_return.index, y=(1 + portfolio_return).cumprod(),
                                   mode='lines', name='Portfolio Value',
                                   line=dict(color='blue', width=2))

    # 3. Plot Asset Allocation (Pie chart)
    allocation_pie = go.Figure(go.Pie(
        labels=weights.index, 
        values=weights.values,
        hoverinfo='label+percent',
        textinfo='label+value',
        marker=dict(colors=px.colors.qualitative.Plotly, line=dict(color='#000000', width=1))
    ))
    
    allocation_pie.update_layout(
        title="Portfolio Asset Allocation",
        showlegend=True,
        margin=dict(t=40, b=0, l=0, r=0)
    )

    # 4. Risk vs Return Plot
    port = rp.Portfolio(returns=returns)
    port.assets_stats(method_mu='hist', method_cov='ledoit')
    
    mu = port.mu
    sigma = port.sigma

    risk_return_trace = go.Scatter(x=sigma, y=mu, mode='markers+text', text=mu.index,
                                   marker=dict(size=10, color='green'),
                                   textposition='top center')

    risk_return_layout = go.Layout(
        title='Risk vs. Return of Individual Assets',
        xaxis=dict(title='Risk (Standard Deviation)'),
        yaxis=dict(title='Expected Return'),
        hovermode='closest'
    )
    
    risk_return_chart = go.Figure(data=[risk_return_trace], layout=risk_return_layout)

    # Create combined layout for performance and risk-return plots
    layout = go.Layout(
        title="Portfolio Performance",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Cumulative Returns"),
        showlegend=True
    )
    
    performance_chart = go.Figure(data=[performance_trace], layout=layout)

    return {
        'performance_chart': performance_chart,
        'allocation_pie': allocation_pie,
        'risk_return_chart': risk_return_chart
    }

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

        print(data)

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
