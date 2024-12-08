import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from riskfolio import Portfolio

# Class for fetching SP500 tickers
class SP500Fetcher:
    @staticmethod
    def fetch_sp500_tickers():
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        sp500_table = tables[0]
        tickers = sp500_table['Symbol'].tolist()
        return tickers

# Class for fetching stock data
class StockDataFetcher:
    @staticmethod
    def fetch_data(tickers, start_date, end_date):
        data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
        if isinstance(data, pd.Series):
            data = data.to_frame()
        if data.empty:
            raise ValueError("No data fetched. Check tickers or date range.")
        return data

# Class for portfolio optimization
class PortfolioOptimizer:
    def __init__(self, data):
        self.data = data
        self.returns = data.pct_change().dropna()

    def optimize(self, model='MV'):
        port = Portfolio(returns=self.returns)
        port.assets_stats(method_mu='hist', method_cov='ledoit')
        weights = port.optimization(model="Classic", rm=model, obj="Sharpe")
        return weights

# Class for visualizations
class Visualizer:
    @staticmethod
    def plot_efficient_frontier(data, returns, is_dark_mode):
        mean_returns = returns.mean()
        cov_matrix = returns.cov()

        # Generate random portfolios
        num_portfolios = 10000
        results = np.zeros((3, num_portfolios))
        for i in range(num_portfolios):
            weights = np.random.random(len(data.columns))
            weights /= np.sum(weights)

            portfolio_return = np.dot(weights, mean_returns)
            portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

            results[0, i] = portfolio_return
            results[1, i] = portfolio_std_dev
            results[2, i] = (portfolio_return - 0.02) / portfolio_std_dev

        # Plot efficient frontier
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=results[1, :],
            y=results[0, :],
            mode='markers',
            marker=dict(color=results[2, :], colorscale='Viridis', showscale=True),
            text=[f"Sharpe: {x:.2f}" for x in results[2, :]]
        ))
        fig.update_layout(
            title="Efficient Frontier",
            xaxis_title="Standard Deviation",
            yaxis_title="Expected Return",
            template="plotly_dark" if is_dark_mode else "plotly_white"
        )
        return fig

    @staticmethod
    def plot_correlation_matrix(data, is_dark_mode):
        correlation_matrix = data.pct_change().dropna().corr()
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale="Viridis",
            colorbar=dict(title="Correlation")
        ))
        fig.update_layout(
            title="Correlation Matrix",
            template="plotly_dark" if is_dark_mode else "plotly_white"
        )
        return fig

    @staticmethod
    def plot_weights_pie(weights, is_dark_mode):
        fig = go.Figure(data=[go.Pie(labels=weights.index, values=weights.values.flatten(), hole=0.4)])
        fig.update_layout(
            title="Portfolio Weights Allocation",
            template="plotly_dark" if is_dark_mode else "plotly_white"
        )
        return fig

    @staticmethod
    def plot_cumulative_returns(data, weights, is_dark_mode):
        returns = data.pct_change().dropna()
        portfolio_return = (returns * weights).sum(axis=1)
        cumulative_returns = (1 + portfolio_return).cumprod()

        # Plot cumulative returns
        fig = go.Figure()
        for ticker in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index, y=data[ticker], mode='lines', name=f"{ticker} Price"
            ))
        fig.add_trace(go.Scatter(
            x=cumulative_returns.index, y=cumulative_returns, mode='lines', name="Portfolio Cumulative Return",
            line=dict(color='blue', width=2)
        ))
        fig.update_layout(
            title="Stock Prices and Portfolio Cumulative Returns",
            template="plotly_dark" if is_dark_mode else "plotly_white"
        )
        return fig

# Streamlit App
st.set_page_config(layout="wide", page_title="Portfolio Optimization")

st.title("Portfolio Optimization Dashboard")

# Dark mode toggle
is_dark_mode = st.checkbox("Enable Dark Mode")

# Input Section
st.sidebar.header("Input Options")

# Fetch tickers
tickers = SP500Fetcher.fetch_sp500_tickers()
selected_tickers = st.sidebar.multiselect("Select Stocks", tickers, default=tickers[:5])

start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2015-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2023-01-01"))

model = st.sidebar.selectbox("Optimization Model", options=["MV", "CVaR", "MAD", "MDD"], index=0)

if st.sidebar.button("Optimize Portfolio"):
    try:
        # Fetch stock data
        stock_data = StockDataFetcher.fetch_data(selected_tickers, start_date, end_date)

        # Optimize portfolio
        optimizer = PortfolioOptimizer(stock_data)
        weights = optimizer.optimize(model)

        # Visualize results
        vis = Visualizer()

        st.subheader("Portfolio Weights")
        st.table(weights)

        st.subheader("Efficient Frontier")
        st.plotly_chart(vis.plot_efficient_frontier(stock_data, optimizer.returns, is_dark_mode), use_container_width=True)

        st.subheader("Correlation Matrix")
        st.plotly_chart(vis.plot_correlation_matrix(stock_data, is_dark_mode), use_container_width=True)

        st.subheader("Portfolio Weights Pie Chart")
        st.plotly_chart(vis.plot_weights_pie(weights, is_dark_mode), use_container_width=True)

        st.subheader("Cumulative Returns")
        st.plotly_chart(vis.plot_cumulative_returns(stock_data, weights, is_dark_mode), use_container_width=True)
    except Exception as e:
        st.error(f"Error: {str(e)}")
