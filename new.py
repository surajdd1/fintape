import streamlit as st
import datetime
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from yahoo_fin import stock_info
import seaborn as sns
    
from yahoo_fin.stock_info import get_analysts_info

# from textblob import TextBlob


# # Set page configuration
# st.set_page_config(page_title="Stock Market Information", layout="wide")

# # Title and description
# st.title("Stock Market Information")
# st.write("This app provides live stock market information and news.")

st.set_page_config(
    page_title="FinTape",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Stock icon images
# stock_images = {
#     symbol : 'https://logo.clearbit.com/{}.com'.format(symbol),
#     'MSFT': 'https://logo.clearbit.com/microsoft.com',
#     'AMZN': 'https://logo.clearbit.com/amazon.com'

# }

st.title("FinTape")
st.write("This app provides live stock market information and news.")


# Set theme
sns.set_palette("Set2")
sns.set_style("whitegrid")
sns.set_context("paper")


# Sidebar inputs
with st.sidebar:
    st.subheader("Select Stock Exchange")
    stock_exchange = st.radio("Exchange", ("sp500","NASDAQ", "DOW", "NSE"))

    if stock_exchange == "NSE":
        st.subheader("Select NSE Stock")
        nse_tickers = stock_info.tickers_nifty50()
        nse_symbol = st.selectbox("Symbol", nse_tickers)
        symbol = nse_symbol 
    else:
        st.subheader(f"Select {stock_exchange} Stock")
        exchange_tickers = getattr(stock_info, f"tickers_{stock_exchange.lower()}")()
        symbol = st.selectbox("Symbol", exchange_tickers)
        stock_images = {
            symbol : 'https://logo.clearbit.com/{}.com'.format(symbol),
            'MSFT': 'https://logo.clearbit.com/microsoft.com',
            'AMZN': 'https://logo.clearbit.com/amazon.com'
            }


    start_date = st.date_input("From Date", datetime.date.today() - datetime.timedelta(30))
    end_date = st.date_input("To Date", datetime.date.today())

# Retrieve stock data
data = yf.download(tickers=symbol, start=start_date, end=end_date)
if symbol in stock_images:
         st.subheader(f"{symbol}:")
         st.write(f'<img src="{stock_images[symbol]}" style="max-width:50px;">', unsafe_allow_html=True)

# Display stock data
if not data.empty:
    info = yf.Ticker(symbol).info
    # string_name = info.get['longName']
    long_name = info['longName']
    st.header('**%s**' %  long_name ) 
    st.subheader(f"{symbol} Historical Data")
    st.subheader(f"{long_name} ({symbol})")
    st.dataframe(data)

    # recommendation_df = info.get_analysts_info(symbol)
    # recommendation_summary = recommendation_df.groupby('To Grade').count()['Firm'].to_dict()
    # buy_count = recommendation_summary.get('Buy', 0)
    # sell_count = recommendation_summary.get('Sell', 0)
    # st.subheader(f"{buy_count} ({symbol})")
    # st.subheader(f"{sell_count} ({symbol})")
    



    

    # Display logo
    logo_url = info.get('logo_url')
    if logo_url:
        response = requests.get(logo_url)
        st.image(response.content, use_column_width=True)
    else:
        st.write("No logo available")

    # Display dividend
    dividend_yield = info.get('trailingAnnualDividendYield')
    # get_dividends(symbol)dividend_yield
    if dividend_yield:
        st.subheader(f"{symbol} Dividend Yield")
        st.write(f"{dividend_yield*100:.2f}%")
    else:
        st.write("No dividend information available")

    

    # Plot candlestick chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'],
                                 name="Market Data"))

    fig.update_layout(title=f"{symbol} Live Share Price Evolution",
                      yaxis_title="Stock Price",
                      xaxis_rangeslider_visible=True)

    st.plotly_chart(fig)

    # Additional analytics options
    st.subheader("Analytics")
    st.write("Select the analytics option you would like to see.")

    if st.checkbox("Moving Average"):
        st.write("Moving Average")
        ma_period = st.slider("Select the period for Moving Average", min_value=5, max_value=50, value=20)
        data['MA'] = data['Close'].rolling(ma_period).mean()
        fig_ma = go.Figure()
        fig_ma.add_trace(go.Candlestick(x=data.index,
                                        open=data['Open'],
                                        high=data['High'],
                                        low=data['Low'],
                                        close=data['Close'],
                                        name="Market Data"))
        fig_ma.add_trace(go.Scatter(x=data.index, y=data['MA'], name=f"{ma_period}-day Moving Average"))
        fig_ma.update_layout(title=f"{symbol} Live Share Price Evolution with Moving Average",
                             yaxis_title="Stock Price",
                             xaxis_rangeslider_visible=True)
        st.plotly_chart(fig_ma)

    if st.checkbox("Relative Strength Index (RSI)"):
        st.write("Relative Strength Index (RSI)")
        rsi_period = st.slider("Select the period for RSI", min_value=5, max_value=50, value=14)
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(rsi_period).mean()
        avg_loss = loss.rolling(rsi_period).mean()
        rs = avg_gain / avg_loss
        
        # Plot RSI
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=data.index, y=rs, name="RSI"))
        fig_rsi.update_layout(title=f"{symbol} Relative Strength Index (RSI)",
                              yaxis_title="RSI",
                              xaxis_rangeslider_visible=True)
        st.plotly_chart(fig_rsi)



    st.title('Market Mood Index Calculator')

    # Get user input for stock symbol and date range
    symbol = st.text_input('Enter stock symbol (e.g. AAPL)')
    start_date = st.date_input('Enter start date')
    end_date = st.date_input('Enter end date')

    # Fetch stock data
    data = yf.download(symbol, start=start_date, end=end_date)

    # Calculate market mood index
    period = 10
    data['Close_shifted'] = data['Close'].shift(1)
    data['Change'] = data['Close'] - data['Close_shifted']
    data['Direction'] = data['Change'].apply(lambda x: 1 if x >= 0 else -1)
    data['Abs_Change'] = data['Change'].apply(abs)
    data['MMI'] = data['Abs_Change'].rolling(period).sum() / data['Abs_Change'].rolling(period).sum().shift(1)
    data.drop(['Close_shifted', 'Change', 'Direction', 'Abs_Change'], axis=1, inplace=True)

    # Display MMI chart
    st.line_chart(data['MMI'])



    # Define stock symbol
    import streamlit as st
    import yfinance as yf
    import plotly.graph_objs as go

    # Define stock symbol
    symbol = "AAPL"

    # Fetch stock data
    stock_data = yf.Ticker(symbol).history(period="max")

    # Calculate percentage of buying and selling
    total_trades = stock_data.shape[0]
    buy_trades = stock_data[stock_data["Close"] > stock_data["Open"]].shape[0]
    sell_trades = stock_data[stock_data["Close"] < stock_data["Open"]].shape[0]

    buy_percentage = buy_trades / total_trades * 100
    sell_percentage = sell_trades / total_trades * 100

    # Define colors for the pie chart
    colors = ["green", "red"]

    # Create a pie chart using plotly
    fig = go.Figure(data=[go.Pie(labels=['Buying', 'Selling'],
                                 values=[buy_percentage, sell_percentage],
                                 marker=dict(colors=colors))])

    # Set chart title and formatting
    fig.update_layout(title=f"Percentage of buying and selling for {symbol}",
                      title_font_size=20,
                      title_font_family="Arial",
                      title_font_color="black",
                      title_x=0.5,
                      legend_font_size=14,
                      legend_font_family="Arial")

    # Set color for the buying percentage slice of the chart
    fig.data[0].marker.colors[0] = "green"

    # Set color for the selling percentage slice of the chart
    fig.data[0].marker.colors[1] = "red"

    # Display chart using streamlit
    st.plotly_chart(fig)
