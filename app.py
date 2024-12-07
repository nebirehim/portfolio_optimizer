from flask import Flask, render_template, request, jsonify
from plotly.subplots import make_subplots
import yfinance as yf
import pandas as pd
import riskfolio as rp
import plotly.graph_objs as go
import json
import plotly
import numpy as np

class SP500Fetcher:
    @staticmethod
    def fetch_sp500_tickers():
        # URL for Wikipedia's S&P 500 constituents
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        sp500_table = tables[0]  # First table contains the data we need
        tickers = sp500_table['Symbol'].tolist()
        return tickers

class StockDataFetcher:
    @staticmethod
    def fetch_data(tickers, start_date, end_date):
        stock_data = yf.download(tickers, start=start_date, end=end_date)
        stock_data = stock_data['Adj Close']
        
        if isinstance(stock_data, pd.Series):
            stock_data = stock_data.to_frame()

        if stock_data.empty:
            raise ValueError("No stock data was returned. Please check the tickers and date range.")
        
        return stock_data


class PortfolioOptimizer:
    def __init__(self, data):
        self.data = data
        self.returns = data.pct_change().dropna()

    def optimize(self, model='MV'):
        port = rp.Portfolio(returns=self.returns)
        port.assets_stats(method_mu='hist', method_cov='ledoit')

        if model == 'MV':
            weights = port.optimization(model='Classic', rm='MV', obj='Sharpe')
        elif model == 'CVaR':
            weights = port.optimization(model='Classic', rm='CVaR', obj='Sharpe')
        elif model == 'MAD':
            weights = port.optimization(model='Classic', rm='MAD', obj='Sharpe')
        elif model == 'MDD':
            weights = port.optimization(model='Classic', rm='MDD', obj='Sharpe')
        else:
            raise ValueError("Invalid model selected.")
        
        return weights

    def plot_efficient_frontier(self, is_dark_mode):
        mean_returns = self.returns.mean()
        cov_matrix = self.returns.cov()

        # Generate random portfolios
        num_portfolios = 10000
        results = np.zeros((3, num_portfolios))
        for i in range(num_portfolios):
            weights = np.random.random(len(self.data.columns))
            weights /= np.sum(weights)

            portfolio_return = np.dot(weights, mean_returns)
            portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

            results[0, i] = portfolio_return
            results[1, i] = portfolio_std_dev
            results[2, i] = (portfolio_return - 0.02) / portfolio_std_dev  # Sharpe ratio

        background_color = 'rgba(240, 240, 240, 0.9)' if not is_dark_mode else 'rgba(40, 40, 40, 1)'
        text_color = '#000' if not is_dark_mode else '#FFF'

        # Create efficient frontier figure
        frontier_fig = go.Figure()
        frontier_fig.add_trace(go.Scatter(
            x=results[1, :], 
            y=results[0, :], 
            mode='markers',
            marker=dict(color=results[2, :], colorscale='Viridis', showscale=True),
            text=['Sharpe: ' + str(round(x, 2)) for x in results[2, :]]
        ))
        frontier_fig.update_layout(
            title='Efficient Frontier',
            xaxis_title='Standard Deviation',
            yaxis_title='Expected Return',
            plot_bgcolor=background_color,
            font=dict(color=text_color)
        )

        return frontier_fig


class PlotGenerator:
    @staticmethod
    def plot_performance(data, weights, is_dark_mode):
        returns = data.pct_change().dropna()
        portfolio_return = (returns * weights).sum(axis=1)
        cumulative_returns = (1 + portfolio_return).cumprod()

        # Create price trend traces
        price_traces = []
        for ticker in data.columns:
            price_traces.append(go.Scatter(x=data.index, y=data[ticker], mode='lines', name=f'{ticker} Price'))

        # Create cumulative return trace
        price_traces.append(go.Scatter(x=cumulative_returns.index, y=cumulative_returns, mode='lines',
                                       name='Cumulative Portfolio Return', line=dict(color='blue', width=2)))

        background_color = 'rgba(240, 240, 240, 0.9)' if not is_dark_mode else 'rgba(40, 40, 40, 1)'
        text_color = '#000' if not is_dark_mode else '#FFF'

        # Create price figure
        price_fig = go.Figure(data=price_traces)
        price_fig.update_layout(title='Stock Prices and Portfolio Cumulative Returns',
                                 xaxis_title='Date',
                                 yaxis_title='Price',
                                 legend_title='Legend',
                                 hovermode='x unified',
                                 plot_bgcolor=background_color,
                                 font=dict(color=text_color))

        # Create weights pie chart
        weights_fig = go.Figure(data=[go.Pie(labels=weights.index, values=weights.values.flatten(), hole=0.4)])
        weights_fig.update_layout(title='Portfolio Weights Allocation',
                                   plot_bgcolor=background_color,
                                   paper_bgcolor=background_color,
                                   font=dict(color=text_color))

        return price_fig, weights_fig


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_sp500_tickers', methods=['GET'])
def get_sp500_tickers():
    try:
        tickers = SP500Fetcher.fetch_sp500_tickers()
        return jsonify(tickers=tickers)
    except Exception as e:
        return jsonify(error=str(e)), 400


@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json
    tickers = data['tickers']
    start_date = data['start_date']
    end_date = data['end_date']
    model = data['model']
    is_dark_mode = data['is_dark_mode']

    try:
        # Fetch stock data
        stock_data = StockDataFetcher.fetch_data(tickers, start_date, end_date)

        # Optimize portfolio
        optimizer = PortfolioOptimizer(stock_data)
        weights = optimizer.optimize(model)

        # Correlation Matrix
        correlation_matrix = stock_data.pct_change().dropna().corr()

        # Create text for the heatmap (correlation values as strings)
        text_matrix = correlation_matrix.applymap(lambda x: f'{x:.2%}' if pd.notnull(x) else '')

        # Plot correlation matrix
        correlation_fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale='Viridis',
            colorbar=dict(title='Correlation'),
            text=text_matrix.values,  # Set the correlation coefficient values as text
            hoverinfo='text',  # Display the text (correlation coefficients) on hover
            hoverongaps=False  # Avoid gaps showing on hover
        ))

        correlation_fig.update_layout(
            title='Correlation Matrix',
            xaxis=dict(title='Assets'),
            yaxis=dict(title='Assets'),
            plot_bgcolor='rgba(240,240,240,0.9)' if not is_dark_mode else 'rgba(40,40,40,1)',
            font=dict(color='#000' if not is_dark_mode else '#FFF'),
            xaxis_tickangle=45,
            yaxis_tickangle=-45
        )

        # Convert the correlation graph to JSON for rendering
        correlation_graph_json = json.dumps(correlation_fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Generate other plots (e.g., performance and efficient frontier)
        price_fig, weights_fig = PlotGenerator.plot_performance(stock_data, weights, is_dark_mode)
        frontier_fig = optimizer.plot_efficient_frontier(is_dark_mode)

        # Convert other figures to JSON for rendering
        price_graph_json = json.dumps(price_fig, cls=plotly.utils.PlotlyJSONEncoder)
        weights_graph_json = json.dumps(weights_fig, cls=plotly.utils.PlotlyJSONEncoder)
        frontier_graph_json = json.dumps(frontier_fig, cls=plotly.utils.PlotlyJSONEncoder)

        return jsonify(weights=weights.to_dict(),
                       price_graph=price_graph_json,
                       weights_graph=weights_graph_json,
                       frontier_graph=frontier_graph_json,
                       correlation_graph=correlation_graph_json)
    except Exception as e:
        return jsonify(error=str(e)), 400



if __name__ == "__main__":
    app.run(debug=True)
