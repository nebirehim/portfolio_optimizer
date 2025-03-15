import yfinance as yf

ticker = "AAPL"
start_date = "2023-01-02"
end_date = "2024-03-14"

try:
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    print(data.columns)  # Print the column names to debug
    print(data.head())   # Print the first few rows to check the data

    if 'Adj Close' in data.columns:
        adj_close_data = data['Adj Close']
        print(adj_close_data.head())
    else:
        print("Error: 'Adj Close' column not found.")
except Exception as e:
    print(f"Error fetching data: {e}")
