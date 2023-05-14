import streamlit as st

try:
    import datetime
    import matplotlib.pyplot as plt
    import plotly.express as px
    import yfinance as yf
    from yahoo_fin import stock_info
    from PIL import Image
    import pandas as pd
    from pandas_datareader import data as pdr
    import plotly.graph_objs as ago
    from links import links_r
    import seaborn as sns


except ModuleNotFoundError as e:
    st.error(
        f"Looks like requirements are not installed: '{e}'. Run the following command to install requirements"
    )

    st.code(  
        "pip install streamlit matplotlib yfinance yahoo_fin pillow pandas"
    )
else:

    def Nifty50():
        with st.sidebar:
            st.write("Nifty50 Inputs")
            symbol = st.selectbox("Select Symbol",stock_info.tickers_nifty50())
            a = st.date_input("From date", datetime.date.today() - datetime.timedelta(30)) 
            b = st.date_input("To Date", datetime.date.today())     
        cdata = yf.download(tickers=symbol, start=a, end=b)
        tickerData = yf.Ticker(symbol)
        string_name = tickerData.info['longName']
        st.header('**%s**' % string_name)  
        try:
            pe_ratio = tickerData.info["trailingPE"]
        except KeyError:
            print("")
        else :
            pe_ratio = tickerData.info["trailingPE"]
            st.write(f"{symbol} P/E Ratio: {pe_ratio}")        
        # pe_ratio = tickerData.info["trailingPE"]
        # st.write(f"{symbol} P/E Ratio: {pe_ratio}")
        fig = ago.Figure()
        fig.add_trace(ago.Candlestick(x=cdata.index,open=cdata['Open'],high=cdata['High'],low=cdata['Low'],close=cdata['Close'], name = 'market data'))
        fig.update_layout(title=' live share price evolution',yaxis_title='Stock Price (INR per Shares)')
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=15, label="15m", step="minute", stepmode="backward"),
                    dict(count=45, label="45m", step="minute", stepmode="backward"),
                    dict(count=1, label="HTD", step="hour", stepmode="todate"),
                    dict(count=3, label="3h", step="hour", stepmode="backward"),
                    dict(step="all")])))
        st.write(fig)
        string_summary = tickerData.info['longBusinessSummary']
        st.info(string_summary)

        string_summary1 = tickerData.news
        news_links = links_r(string_summary1)
        news_links = news_links[:1]
        a=news_links[0]
        a=a[:-2]
        st.info(a)
        st.markdown(f'''<a href={a}><button style="background-color:Green;">Today on {string_name}</button></a>''',unsafe_allow_html=True)
        st.subheader("Analytics")
        st.write("Select the analytics option you would like to see.")

        if st.checkbox("Moving Average"):
            st.write("Moving Average")
            ma_period = st.slider("Select the period for Moving Average", min_value=5, max_value=50, value=20)
            cdata['MA'] = cdata['Close'].rolling(ma_period).mean()
            fig_ma = ago.Figure()
            fig_ma.add_trace(ago.Candlestick(x=cdata.index,
                                            open=cdata['Open'],
                                            high=cdata['High'],
                                            low=cdata['Low'],
                                            close=cdata['Close'],
                                            name="Market Data"))
            fig_ma.add_trace(ago.Scatter(x=cdata.index, y=cdata['MA'], name=f"{ma_period}-day Moving Average"))
            fig_ma.update_layout(title=f"{symbol} Live Share Price Evolution with Moving Average",
                                 yaxis_title="Stock Price",
                                 xaxis_rangeslider_visible=True)
            st.plotly_chart(fig_ma)

        if st.checkbox("Relative Strength Index (RSI)"):
            st.write("Relative Strength Index (RSI)")
            rsi_period = st.slider("Select the period for RSI", min_value=5, max_value=50, value=14)
            delta = cdata['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(rsi_period).mean()
            avg_loss = loss.rolling(rsi_period).mean()
            rs = avg_gain / avg_loss
            
            # Plot RSI
            fig_rsi = ago.Figure()
            fig_rsi.add_trace(ago.Candlestick(x=cdata.index,
                                            open=cdata['Open'],
                                            high=cdata['High'],
                                            low=cdata['Low'],
                                            close=cdata['Close'],
                                            name="Market Data"))
            fig_rsi.add_trace(ago.Scatter(x=cdata.index, y=rs, name="RSI"))
            fig_rsi.update_layout(title=f"{symbol} Relative  Index (RSI)",
                                  yaxis_title="RSI",
                                  xaxis_rangeslider_visible=True)
            st.plotly_chart(fig_rsi)
        if st.checkbox("Market Mood Index (MMI)"):
            st.write("Market Mood Index (MMI)")
            mmi_period = st.slider("Select the period for MMI", min_value=5, max_value=50, value=14)
            mmi_period = 10
            cdata['Close_shifted'] = cdata['Close'].shift(1)
            cdata['Change'] = cdata['Close'] - cdata['Close_shifted']
            cdata['Direction'] = cdata['Change'].apply(lambda x: 1 if x >= 0 else -1)
            cdata['Abs_Change'] = cdata['Change'].apply(abs)
            cdata['MMI'] = cdata['Abs_Change'].rolling(mmi_period).sum() / cdata['Abs_Change'].rolling(mmi_period).sum().shift(1)
            cdata.drop(['Close_shifted', 'Change', 'Direction', 'Abs_Change'], axis=1, inplace=True)

            # Display MMI chart
            st.line_chart(cdata['MMI'])
        stock_data = yf.Ticker(symbol).history(period="max")
        total_trades = stock_data.shape[0]
        buy_trades = stock_data[stock_data["Close"] > stock_data["Open"]].shape[0]
        sell_trades = stock_data[stock_data["Close"] < stock_data["Open"]].shape[0]
        buy_percentage = buy_trades / total_trades * 100
        sell_percentage = sell_trades / total_trades * 100
        # colors = ["green", "red"]
        fig_pc = ago.Figure(data=[ago.Pie(labels=['Buying', 'Selling'],
                                     values=[buy_percentage, sell_percentage])])
        # fig_pc.data[0].marker.colors[0] = "green"

        # # Set color for the selling percentage slice of the chart
        # fig_pc.data[0].marker.colors[1] = "red"
        fig_pc.update_layout(title=f"Percentage of buying and selling for {symbol}")
        st.plotly_chart(fig_pc)


    def NSE():

        with st.sidebar:
            st.write("NSE Inputs")
            tickers = pd.read_html('https://ournifty.com/stock-list-in-nse-fo-futures-and-options.html#:~:text=NSE%20F%26O%20Stock%20List%3A%20%20%20%20SL,%20%201000%20%2052%20more%20rows%20')[0]
            tickers = tickers[4:]
            tickers = tickers.SYMBOL.to_list()
            for count in range(len(tickers)):
                tickers[count] = tickers[count]
            symbol = st.selectbox("Select Symbol", tickers)
            
            a = st.date_input("From date", datetime.date.today() - datetime.timedelta(30)) 
            b = st.date_input("To Date", datetime.date.today())

        cdata = yf.download(tickers=symbol  + ".NS", start=a, end=b)
        # Ticker information
        tickerData = yf.Ticker(symbol + ".ns")
        # string_logo = '<img src=%s>' % tickerData.info['logo_url']
        # st.markdown(string_logo, unsafe_allow_html=True)
        # string_name = tickerData.info['longName']
        # st.header('**%s**' % string_name)
        string_name = tickerData.info['longName']
        st.header('**%s**' % string_name) 
        try:
            pe_ratio = tickerData.info["trailingPE"]
        except KeyError:
            print("")
        else :
            pe_ratio = tickerData.info["trailingPE"]
            st.write(f"{symbol} P/E Ratio: {pe_ratio}")
        # pe_ratio = tickerData.info["trailingPE"]
        # st.write(f"{symbol} P/E Ratio: {pe_ratio}")
        fig = ago.Figure()
        fig.add_trace(ago.Candlestick(x=cdata.index,open=cdata['Open'],high=cdata['High'],low=cdata['Low'],close=cdata['Close'], name = 'market data'))
        fig.update_layout(title='live share price evolution',yaxis_title='Stock Price (INR per Shares)')
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=15, label="15m", step="minute", stepmode="backward"),
                    dict(count=45, label="45m", step="minute", stepmode="backward"),
                    dict(count=1, label="HTD", step="hour", stepmode="todate"),
                    dict(count=3, label="3h", step="hour", stepmode="backward"),
                    dict(step="all")])))
        # st.write(fig)
        # string_summary = tickerData.info['long_Business_Summary']
        # string_summary = stock_info.get_analysts_info(symbol)
        # st.info(string_summary)
        # print(string_summary)
        st.write(fig)
        string_summary = tickerData.info['longBusinessSummary']
        st.info(string_summary)

        string_summary1 = tickerData.news
        news_links = links_r(string_summary1)
        news_links = news_links[:1]
        a=news_links[0]
        a=a[:-2]
        st.info(a)
        st.markdown(f'''<a href={a}><button style="background-color:Green;">Today on {string_name}</button></a>''',unsafe_allow_html=True)
        st.subheader("Analytics")
        st.write("Select the analytics option you would like to see.")

        if st.checkbox("Moving Average"):
            st.write("Moving Average")
            ma_period = st.slider("Select the period for Moving Average", min_value=5, max_value=50, value=20)
            cdata['MA'] = cdata['Close'].rolling(ma_period).mean()
            fig_ma = ago.Figure()
            fig_ma.add_trace(ago.Candlestick(x=cdata.index,
                                            open=cdata['Open'],
                                            high=cdata['High'],
                                            low=cdata['Low'],
                                            close=cdata['Close'],
                                            name="Market Data"))
            fig_ma.add_trace(ago.Scatter(x=cdata.index, y=cdata['MA'], name=f"{ma_period}-day Moving Average"))
            fig_ma.update_layout(title=f"{symbol} Live Share Price Evolution with Moving Average",
                                 yaxis_title="Stock Price",
                                 xaxis_rangeslider_visible=True)
            st.plotly_chart(fig_ma)

        if st.checkbox("Relative Strength Index (RSI)"):
            st.write("Relative Strength Index (RSI)")
            rsi_period = st.slider("Select the period for RSI", min_value=5, max_value=50, value=14)
            delta = cdata['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(rsi_period).mean()
            avg_loss = loss.rolling(rsi_period).mean()
            rs = avg_gain / avg_loss
            
            # Plot RSI
            fig_rsi = ago.Figure()
            fig_rsi.add_trace(ago.Candlestick(x=cdata.index,
                                            open=cdata['Open'],
                                            high=cdata['High'],
                                            low=cdata['Low'],
                                            close=cdata['Close'],
                                            name="Market Data"))
            fig_rsi.add_trace(ago.Scatter(x=cdata.index, y=rs, name="RSI"))
            fig_rsi.update_layout(title=f"{symbol} Relative  Index (RSI)",
                                  yaxis_title="RSI",
                                  xaxis_rangeslider_visible=True)
            st.plotly_chart(fig_rsi)
        if st.checkbox("Market Mood Index (MMI)"):
            st.write("Market Mood Index (MMI)")
            mmi_period = st.slider("Select the period for MMI", min_value=5, max_value=50, value=14)
            mmi_period = 10
            cdata['Close_shifted'] = cdata['Close'].shift(1)
            cdata['Change'] = cdata['Close'] - cdata['Close_shifted']
            cdata['Direction'] = cdata['Change'].apply(lambda x: 1 if x >= 0 else -1)
            cdata['Abs_Change'] = cdata['Change'].apply(abs)
            cdata['MMI'] = cdata['Abs_Change'].rolling(mmi_period).sum() / cdata['Abs_Change'].rolling(mmi_period).sum().shift(1)
            cdata.drop(['Close_shifted', 'Change', 'Direction', 'Abs_Change'], axis=1, inplace=True)

            # Display MMI chart
            st.line_chart(cdata['MMI'])
        stock_data = yf.Ticker(symbol).history(period="max")
        total_trades = stock_data.shape[0]
        buy_trades = stock_data[stock_data["Close"] > stock_data["Open"]].shape[0]
        sell_trades = stock_data[stock_data["Close"] < stock_data["Open"]].shape[0]
        buy_percentage = buy_trades / total_trades * 100
        sell_percentage = sell_trades / total_trades * 100
        # colors = ["green", "red"]
        fig_pc = ago.Figure(data=[ago.Pie(labels=['Buying', 'Selling'],
                                     values=[buy_percentage, sell_percentage])])
        # fig_pc.data[0].marker.colors[0] = "green"

        # # Set color for the selling percentage slice of the chart
        # fig_pc.data[0].marker.colors[1] = "red"
        fig_pc.update_layout(title=f"Percentage of buying and selling for {symbol}")
        st.plotly_chart(fig_pc)

    def NASDAQ():

        with st.sidebar:
            st.write("NASDAQ Inputs")
            symbol = st.selectbox("Select Symbol",stock_info.tickers_nasdaq())
            a = st.date_input("From date", datetime.date.today() - datetime.timedelta(30)) 
            b = st.date_input("To Date", datetime.date.today())

            # from_date = st.date_input(
            #     "From date", datetime.date.today() - datetime.timedelta(30)
            # )

            # to_date = st.date_input("To Date", datetime.date.today())

        cdata = yf.download(tickers=symbol, start=a, end=b)
        tickerData = yf.Ticker(symbol)
        # string_logo = '<img src=%s>' % tickerData.info['logo_url']
        # st.markdown(string_logo, unsafe_allow_html=True)
        string_name = tickerData.info['longName']
        st.header('**%s**' % string_name)
        # if tickerData == "AAPL","MSFT","TSLA","AMZN":
        try:
            pe_ratio = tickerData.info["trailingPE"]
        except KeyError:
            print("")
        else :
            pe_ratio = tickerData.info["trailingPE"]
            st.write(f"{symbol} P/E Ratio: {pe_ratio}")
        fig = ago.Figure()
        fig.add_trace(ago.Candlestick(x=cdata.index,open=cdata['Open'],high=cdata['High'],low=cdata['Low'],close=cdata['Close'], name = 'market data'))
        fig.update_layout(title='live share price evolution',yaxis_title='Stock Price (USD per Shares)')
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=15, label="15m", step="minute", stepmode="backward"),
                    dict(count=45, label="45m", step="minute", stepmode="backward"),
                    dict(count=1, label="HTD", step="hour", stepmode="todate"),
                    dict(count=3, label="3h", step="hour", stepmode="backward"),
                    dict(step="all")])))
        st.write(fig)
        string_summary = tickerData.info['longBusinessSummary']
        st.info(string_summary)
        
        string_summary1 = tickerData.news
        news_links = links_r(string_summary1)
        news_links = news_links[:1]
        a=news_links[0]
        a=a[:-2]
        st.info(a)
        st.markdown(f'''<a href={a}><button style="background-color:111111;">Today on {string_name}</button></a>''',unsafe_allow_html=True)
        # Additional analytics options
        st.subheader("Analytics")
        st.write("Select the analytics option you would like to see.")

        if st.checkbox("Moving Average"):
            st.write("Moving Average")
            ma_period = st.slider("Select the period for Moving Average", min_value=5, max_value=50, value=20)
            cdata['MA'] = cdata['Close'].rolling(ma_period).mean()
            fig_ma = ago.Figure()
            fig_ma.add_trace(ago.Candlestick(x=cdata.index,
                                            open=cdata['Open'],
                                            high=cdata['High'],
                                            low=cdata['Low'],
                                            close=cdata['Close'],
                                            name="Market Data"))
            fig_ma.add_trace(ago.Scatter(x=cdata.index, y=cdata['MA'], name=f"{ma_period}-day Moving Average"))
            fig_ma.update_layout(title=f"{symbol} Live Share Price Evolution with Moving Average",
                                 yaxis_title="Stock Price",
                                 xaxis_rangeslider_visible=True)
            st.plotly_chart(fig_ma)

        if st.checkbox("Relative Strength Index (RSI)"):
            st.write("Relative Strength Index (RSI)")
            rsi_period = st.slider("Select the period for RSI", min_value=5, max_value=50, value=14)
            delta = cdata['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(rsi_period).mean()
            avg_loss = loss.rolling(rsi_period).mean()
            rs = avg_gain / avg_loss
            
            # Plot RSI
            fig_rsi = ago.Figure()
            fig_rsi.add_trace(ago.Candlestick(x=cdata.index,
                                            open=cdata['Open'],
                                            high=cdata['High'],
                                            low=cdata['Low'],
                                            close=cdata['Close'],
                                            name="Market Data"))
            fig_rsi.add_trace(ago.Scatter(x=cdata.index, y=rs, name="RSI"))
            fig_rsi.update_layout(title=f"{symbol} Relative  Index (RSI)",
                                  yaxis_title="RSI",
                                  xaxis_rangeslider_visible=True)
            st.plotly_chart(fig_rsi)
        if st.checkbox("Market Mood Index (MMI)"):
            st.write("Market Mood Index (MMI)")
            mmi_period = st.slider("Select the period for MMI", min_value=5, max_value=50, value=14)
            mmi_period = 10
            cdata['Close_shifted'] = cdata['Close'].shift(1)
            cdata['Change'] = cdata['Close'] - cdata['Close_shifted']
            cdata['Direction'] = cdata['Change'].apply(lambda x: 1 if x >= 0 else -1)
            cdata['Abs_Change'] = cdata['Change'].apply(abs)
            cdata['MMI'] = cdata['Abs_Change'].rolling(mmi_period).sum() / cdata['Abs_Change'].rolling(mmi_period).sum().shift(1)
            cdata.drop(['Close_shifted', 'Change', 'Direction', 'Abs_Change'], axis=1, inplace=True)

            # Display MMI chart
            st.line_chart(cdata['MMI'])
        stock_data = yf.Ticker(symbol).history(period="max")
        total_trades = stock_data.shape[0]
        buy_trades = stock_data[stock_data["Close"] > stock_data["Open"]].shape[0]
        sell_trades = stock_data[stock_data["Close"] < stock_data["Open"]].shape[0]
        buy_percentage = buy_trades / total_trades * 100
        sell_percentage = sell_trades / total_trades * 100
        # colors = ["green", "red"]
        fig_pc = ago.Figure(data=[ago.Pie(labels=['Buying', 'Selling'],
                                     values=[buy_percentage, sell_percentage])])
        # fig_pc.data[0].marker.colors[0] = "green"

        # # Set color for the selling percentage slice of the chart
        # fig_pc.data[0].marker.colors[1] = "red"
        fig_pc.update_layout(title=f"Percentage of buying and selling for {symbol}")
        st.plotly_chart(fig_pc)


    def DOW():

        with st.sidebar:
            st.write("DOW Inputs")
            symbol = st.selectbox("Select Symbol",stock_info.tickers_dow())
            a = st.date_input("From date", datetime.date.today() - datetime.timedelta(30)) 
            b = st.date_input("To Date", datetime.date.today())

            

        cdata = yf.download(tickers=symbol, start=a, end=b)
        tickerData = yf.Ticker(symbol)
        # string_logo = '<img src=%s>' % tickerData.info['logo_url']
        # st.markdown(string_logo, unsafe_allow_html=True)
        string_name = tickerData.info['longName']
        st.header('**%s**' % string_name)
        try:
            pe_ratio = tickerData.info["trailingPE"]
        except KeyError:
            print("")
        else :
            pe_ratio = tickerData.info["trailingPE"]
            st.write(f"{symbol} P/E Ratio: {pe_ratio}")
        # pe_ratio = tickerData.info["trailingPE"]
        # st.write(f"{symbol} P/E Ratio: {pe_ratio}")
        
        fig = ago.Figure()


        fig.add_trace(ago.Candlestick(x=cdata.index,open=cdata['Open'],high=cdata['High'],low=cdata['Low'],close=cdata['Close'], name = 'market data'))

        fig.update_layout(title=' live share price evolution',yaxis_title='Stock Price (USD per Shares)')

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=15, label="15m", step="minute", stepmode="backward"),
                    dict(count=45, label="45m", step="minute", stepmode="backward"),
                    dict(count=1, label="HTD", step="hour", stepmode="todate"),
                    dict(count=3, label="3h", step="hour", stepmode="backward"),
                    dict(step="all")])))
        st.write(fig)
        string_summary = tickerData.info['longBusinessSummary']
        st.info(string_summary)
       
        string_summary1 = tickerData.news
        news_links = links_r(string_summary1)
        news_links = news_links[:1]
        a=news_links[0]
        a=a[:-2]
        st.info(a)
        st.markdown(f'''<a href={a}><button style="background-color:Green;">Today on {string_name}</button></a>''',unsafe_allow_html=True)
        st.subheader("Analytics")
        st.write("Select the analytics option you would like to see.")

        if st.checkbox("Moving Average"):
            st.write("Moving Average")
            ma_period = st.slider("Select the period for Moving Average", min_value=5, max_value=50, value=20)
            cdata['MA'] = cdata['Close'].rolling(ma_period).mean()
            fig_ma = ago.Figure()
            fig_ma.add_trace(ago.Candlestick(x=cdata.index,
                                            open=cdata['Open'],
                                            high=cdata['High'],
                                            low=cdata['Low'],
                                            close=cdata['Close'],
                                            name="Market Data"))
            fig_ma.add_trace(ago.Scatter(x=cdata.index, y=cdata['MA'], name=f"{ma_period}-day Moving Average"))
            fig_ma.update_layout(title=f"{symbol} Live Share Price Evolution with Moving Average",
                                 yaxis_title="Stock Price",
                                 xaxis_rangeslider_visible=True)
            st.plotly_chart(fig_ma)

        if st.checkbox("Relative Strength Index (RSI)"):
            st.write("Relative Strength Index (RSI)")
            rsi_period = st.slider("Select the period for RSI", min_value=5, max_value=50, value=14)
            delta = cdata['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(rsi_period).mean()
            avg_loss = loss.rolling(rsi_period).mean()
            rs = avg_gain / avg_loss
            
            # Plot RSI
            fig_rsi = ago.Figure()
            fig_rsi.add_trace(ago.Candlestick(x=cdata.index,
                                            open=cdata['Open'],
                                            high=cdata['High'],
                                            low=cdata['Low'],
                                            close=cdata['Close'],
                                            name="Market Data"))
            fig_rsi.add_trace(ago.Scatter(x=cdata.index, y=rs, name="RSI"))
            fig_rsi.update_layout(title=f"{symbol} Relative  Index (RSI)",
                                  yaxis_title="RSI",
                                  xaxis_rangeslider_visible=True)
            st.plotly_chart(fig_rsi)
        if st.checkbox("Market Mood Index (MMI)"):
            st.write("Market Mood Index (MMI)")
            mmi_period = st.slider("Select the period for MMI", min_value=5, max_value=50, value=14)
            mmi_period = 10
            cdata['Close_shifted'] = cdata['Close'].shift(1)
            cdata['Change'] = cdata['Close'] - cdata['Close_shifted']
            cdata['Direction'] = cdata['Change'].apply(lambda x: 1 if x >= 0 else -1)
            cdata['Abs_Change'] = cdata['Change'].apply(abs)
            cdata['MMI'] = cdata['Abs_Change'].rolling(mmi_period).sum() / cdata['Abs_Change'].rolling(mmi_period).sum().shift(1)
            cdata.drop(['Close_shifted', 'Change', 'Direction', 'Abs_Change'], axis=1, inplace=True)

            # Display MMI chart
            st.line_chart(cdata['MMI'])
        stock_data = yf.Ticker(symbol).history(period="max")
        total_trades = stock_data.shape[0]
        buy_trades = stock_data[stock_data["Close"] > stock_data["Open"]].shape[0]
        sell_trades = stock_data[stock_data["Close"] < stock_data["Open"]].shape[0]
        buy_percentage = buy_trades / total_trades * 100
        sell_percentage = sell_trades / total_trades * 100
        # colors = ["green", "red"]
        fig_pc = ago.Figure(data=[ago.Pie(labels=['Buying', 'Selling'],
                                     values=[buy_percentage, sell_percentage])])
        # fig_pc.data[0].marker.colors[0] = "green"

        # # Set color for the selling percentage slice of the chart
        # fig_pc.data[0].marker.colors[1] = "red"
        fig_pc.update_layout(title=f"Percentage of buying and selling for {symbol}")
        st.plotly_chart(fig_pc)

        
    def SNP500():

        with st.sidebar:
            st.write("SNP500 Inputs")
            symbol = st.selectbox("Select Symbol",stock_info.tickers_sp500())
            a = st.date_input("From date", datetime.date.today() - datetime.timedelta(30)) 
            b = st.date_input("To Date", datetime.date.today())

            

        cdata = yf.download(tickers=symbol, start=a, end=b)
        tickerData = yf.Ticker(symbol)
        # string_logo = '<img src=%s>' % tickerData.info['logo_url']
        # st.markdown(string_logo, unsafe_allow_html=True)
        string_name = tickerData.info['longName']
        st.header('**%s**' % string_name)
        try:
            pe_ratio = tickerData.info["trailingPE"]
        except KeyError:
            print("")
        else :
            pe_ratio = tickerData.info["trailingPE"]
            st.write(f"{symbol} P/E Ratio: {pe_ratio}")
        # pe_ratio = tickerData.info["trailingPE"]
        # st.write(f"{symbol} P/E Ratio: {pe_ratio}")

        fig = ago.Figure()


        fig.add_trace(ago.Candlestick(x=cdata.index,open=cdata['Open'],high=cdata['High'],low=cdata['Low'],close=cdata['Close'], name = 'market data'))

        fig.update_layout(title='live share price evolution',yaxis_title='Stock Price (USD per Shares)')

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=15, label="15m", step="minute", stepmode="backward"),
                    dict(count=45, label="45m", step="minute", stepmode="backward"),
                    dict(count=1, label="HTD", step="hour", stepmode="todate"),
                    dict(count=3, label="3h", step="hour", stepmode="backward"),
                    dict(step="all")])))
        st.write(fig)
        string_summary = tickerData.info['longBusinessSummary']
        st.info(string_summary)
        
        string_summary1 = tickerData.news
        news_links = links_r(string_summary1)
        news_links = news_links[:1]
        a=news_links[0]
        a=a[:-2]
        st.info(a)
        st.markdown(f'''<a href={a}><button style="background-color:Green;">Today on {string_name}</button></a>''',unsafe_allow_html=True)
        st.subheader("Analytics")
        st.write("Select the analytics option you would like to see.")

        if st.checkbox("Moving Average"):
            st.write("Moving Average")
            ma_period = st.slider("Select the period for Moving Average", min_value=5, max_value=50, value=20)
            cdata['MA'] = cdata['Close'].rolling(ma_period).mean()
            fig_ma = ago.Figure()
            fig_ma.add_trace(ago.Candlestick(x=cdata.index,
                                            open=cdata['Open'],
                                            high=cdata['High'],
                                            low=cdata['Low'],
                                            close=cdata['Close'],
                                            name="Market Data"))
            fig_ma.add_trace(ago.Scatter(x=cdata.index, y=cdata['MA'], name=f"{ma_period}-day Moving Average"))
            fig_ma.update_layout(title=f"{symbol} Live Share Price Evolution with Moving Average",
                                 yaxis_title="Stock Price",
                                 xaxis_rangeslider_visible=True)
            st.plotly_chart(fig_ma)

        if st.checkbox("Relative Strength Index (RSI)"):
            st.write("Relative Strength Index (RSI)")
            rsi_period = st.slider("Select the period for RSI", min_value=5, max_value=50, value=14)
            delta = cdata['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(rsi_period).mean()
            avg_loss = loss.rolling(rsi_period).mean()
            rs = avg_gain / avg_loss
            
            # Plot RSI
            fig_rsi = ago.Figure()
            fig_rsi.add_trace(ago.Candlestick(x=cdata.index,
                                            open=cdata['Open'],
                                            high=cdata['High'],
                                            low=cdata['Low'],
                                            close=cdata['Close'],
                                            name="Market Data"))
            fig_rsi.add_trace(ago.Scatter(x=cdata.index, y=rs, name="RSI"))
            fig_rsi.update_layout(title=f"{symbol} Relative  Index (RSI)",
                                  yaxis_title="RSI",
                                  xaxis_rangeslider_visible=True)
            st.plotly_chart(fig_rsi)
        if st.checkbox("Market Mood Index (MMI)"):
            st.write("Market Mood Index (MMI)")
            mmi_period = st.slider("Select the period for MMI", min_value=5, max_value=50, value=14)
            mmi_period = 10
            cdata['Close_shifted'] = cdata['Close'].shift(1)
            cdata['Change'] = cdata['Close'] - cdata['Close_shifted']
            cdata['Direction'] = cdata['Change'].apply(lambda x: 1 if x >= 0 else -1)
            cdata['Abs_Change'] = cdata['Change'].apply(abs)
            cdata['MMI'] = cdata['Abs_Change'].rolling(mmi_period).sum() / cdata['Abs_Change'].rolling(mmi_period).sum().shift(1)
            cdata.drop(['Close_shifted', 'Change', 'Direction', 'Abs_Change'], axis=1, inplace=True)

            # Display MMI chart
            st.line_chart(cdata['MMI'])
        stock_data = yf.Ticker(symbol).history(period="max")
        total_trades = stock_data.shape[0]
        buy_trades = stock_data[stock_data["Close"] > stock_data["Open"]].shape[0]
        sell_trades = stock_data[stock_data["Close"] < stock_data["Open"]].shape[0]
        buy_percentage = buy_trades / total_trades * 100
        sell_percentage = sell_trades / total_trades * 100
        # colors = ["green", "red"]
        fig_pc = ago.Figure(data=[ago.Pie(labels=['Buying', 'Selling'],
                                     values=[buy_percentage, sell_percentage])])
        # fig_pc.data[0].marker.colors[0] = "green"

        # # Set color for the selling percentage slice of the chart
        # fig_pc.data[0].marker.colors[1] = "red"
        fig_pc.update_layout(title=f"Percentage of buying and selling for {symbol}")
        st.plotly_chart(fig_pc)
        
    def DIV():

        with st.sidebar:
            st.write("DIV Inputs")
            symbol = "NASDAQ"
            segment = st.selectbox("Select Stock exchange", ["NASDAQ", "SNP500","DOW","NSE"])
            if segment == "NASDAQ":
                symbol = st.selectbox("Select Symbol",stock_info.tickers_nasdaq())
                dd=stock_info.get_dividends(symbol)
                
            elif segment == "SNP500":
                symbol = st.selectbox("Select Symbol",stock_info.tickers_sp500())
                dd=stock_info.get_dividends(symbol)
                
            elif segment == "DOW":
                symbol = st.selectbox("Select Symbol",stock_info.tickers_dow())
                dd=stock_info.get_dividends(symbol)
                
            else:
                tickers = pd.read_html('https://ournifty.com/stock-list-in-nse-fo-futures-and-options.html#:~:text=NSE%20F%26O%20Stock%20List%3A%20%20%20%20SL,%20%201000%20%2052%20more%20rows%20')[0]
                tickers = tickers.SYMBOL.to_list()
                for count in range(len(tickers)):
                    tickers[count] = tickers[count]
                symbol = st.selectbox("Select Symbol", tickers)
                symbol = symbol + '.ns'
                tickerDdd = yf.Ticker(symbol)
                dd=tickerDdd.dividends


        tickerData = yf.Ticker(symbol)
        # string_logo = '<img src=%s>' % tickerData.info['logo_url']
        # st.markdown(string_logo, unsafe_allow_html=True)
        string_name = tickerData.info['longName']
        st.header('**%s**' % string_name)
        

        st.write(dd)   
        string_summary = tickerData.info['longBusinessSummary']
        st.info(string_summary)
        string_summary1 = tickerData.news
        news_links = links_r(string_summary1)
        news_links = news_links[:1]
        a=news_links[0]
        a=a[:-2]
        st.info(a)
        st.markdown(f'''<a href={a}><button style="background-color:Green;">Today on {string_name}</button></a>''',unsafe_allow_html=True)
                        

    def crypto_display():

        Cry = ['ETH-USD','BTC-USD','XMR-USD','USDT-USD','BNB-USD','USDC-USD','XRP-USD','SOL-USD','ADA-USD','LUNA1-USD','HEX-USD','AVAX-USD','DOGE-USD','UST-USD','BUSD-USD','SHIB-USD','WBTC-USD','NEAR-USD','MATIC-USE','CRO-USD','DAI-USD','LTC-USD','ATOM-USD','LINK-USD','UNI1-USD']
        # Cry = ['BTC-USD','ETH-USD','XMR-USD']
        with st.sidebar:
            st.write("Crypto Inputs")
            # symbol = st.selectbox("Select Symbol",stock_info.get_top_crypto())
            symbol = st.selectbox("Select Symbol",Cry)
            a = st.date_input("From date", datetime.date.today() - datetime.timedelta(30)) 
            b = st.date_input("To Date", datetime.date.today())

            
        cdata = yf.download(tickers=symbol, start=a, end=b)
        tickerData = yf.Ticker(symbol)
        string_name = tickerData.info['shortName']
        st.header('**%s**' % string_name)
        try:
            pe_ratio = tickerData.info["trailingPE"]
        except KeyError:
            print("")
        else :
            pe_ratio = tickerData.info["trailingPE"]
            st.write(f"{symbol} P/E Ratio: {pe_ratio}")
        # pe_ratio = tickerData.info["trailingPE"]
        # st.write(f"{symbol} P/E Ratio: {pe_ratio}")

        fig = ago.Figure()
        fig.add_trace(ago.Candlestick(x=cdata.index,open=cdata['Open'],high=cdata['High'],low=cdata['Low'],close=cdata['Close'], name = 'market data'))
        fig.update_layout(title=f'{symbol} live share price evolution',yaxis_title='Stock Price (USD per Shares)')
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=15, label="15m", step="minute", stepmode="backward"),
                    dict(count=45, label="45m", step="minute", stepmode="backward"),
                    dict(count=1, label="HTD", step="hour", stepmode="todate"),
                    dict(count=3, label="3h", step="hour", stepmode="backward"),
                    dict(step="all")])))
        st.write(fig)
        string_summary = tickerData.info['description']
        st.info(string_summary)


        string_summary1 = tickerData.news
        news_links = links_r(string_summary1)
        news_links = news_links[:1]
        a=news_links[0]
        a=a[:-2]
        st.info(a)
        st.markdown(f'''<a href={a}><button style="background-color:Green;">Today on {string_name}</button></a>''',unsafe_allow_html=True)
        st.subheader("Analytics")
        st.write("Select the analytics option you would like to see.")

        if st.checkbox("Moving Average"):
            st.write("Moving Average")
            ma_period = st.slider("Select the period for Moving Average", min_value=5, max_value=50, value=20)
            cdata['MA'] = cdata['Close'].rolling(ma_period).mean()
            fig_ma = ago.Figure()
            fig_ma.add_trace(ago.Candlestick(x=cdata.index,
                                            open=cdata['Open'],
                                            high=cdata['High'],
                                            low=cdata['Low'],
                                            close=cdata['Close'],
                                            name="Market Data"))
            fig_ma.add_trace(ago.Scatter(x=cdata.index, y=cdata['MA'], name=f"{ma_period}-day Moving Average"))
            fig_ma.update_layout(title=f"{symbol} Live Share Price Evolution with Moving Average",
                                 yaxis_title="Stock Price",
                                 xaxis_rangeslider_visible=True)
            st.plotly_chart(fig_ma)

        if st.checkbox("Relative Strength Index (RSI)"):
            st.write("Relative Strength Index (RSI)")
            rsi_period = st.slider("Select the period for RSI", min_value=5, max_value=50, value=14)
            delta = cdata['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(rsi_period).mean()
            avg_loss = loss.rolling(rsi_period).mean()
            rs = avg_gain / avg_loss
            
            # Plot RSI
            fig_rsi = ago.Figure()
            fig_rsi.add_trace(ago.Candlestick(x=cdata.index,
                                            open=cdata['Open'],
                                            high=cdata['High'],
                                            low=cdata['Low'],
                                            close=cdata['Close'],
                                            name="Market Data"))
            fig_rsi.add_trace(ago.Scatter(x=cdata.index, y=rs, name="RSI"))
            fig_rsi.update_layout(title=f"{symbol} Relative  Index (RSI)",
                                  yaxis_title="RSI",
                                  xaxis_rangeslider_visible=True)
            st.plotly_chart(fig_rsi)
        if st.checkbox("Market Mood Index (MMI)"):
            st.write("Market Mood Index (MMI)")
            mmi_period = st.slider("Select the period for MMI", min_value=5, max_value=50, value=14)
            mmi_period = 10
            cdata['Close_shifted'] = cdata['Close'].shift(1)
            cdata['Change'] = cdata['Close'] - cdata['Close_shifted']
            cdata['Direction'] = cdata['Change'].apply(lambda x: 1 if x >= 0 else -1)
            cdata['Abs_Change'] = cdata['Change'].apply(abs)
            cdata['MMI'] = cdata['Abs_Change'].rolling(mmi_period).sum() / cdata['Abs_Change'].rolling(mmi_period).sum().shift(1)
            cdata.drop(['Close_shifted', 'Change', 'Direction', 'Abs_Change'], axis=1, inplace=True)

            # Display MMI chart
            st.line_chart(cdata['MMI'])
        stock_data = yf.Ticker(symbol).history(period="max")
        total_trades = stock_data.shape[0]
        buy_trades = stock_data[stock_data["Close"] > stock_data["Open"]].shape[0]
        sell_trades = stock_data[stock_data["Close"] < stock_data["Open"]].shape[0]
        buy_percentage = buy_trades / total_trades * 100
        sell_percentage = sell_trades / total_trades * 100
        # colors = ["green", "red"]
        fig_pc = ago.Figure(data=[ago.Pie(labels=['Buying', 'Selling'],
                                     values=[buy_percentage, sell_percentage])])
        # fig_pc.data[0].marker.colors[0] = "green"

        # # Set color for the selling percentage slice of the chart
        # fig_pc.data[0].marker.colors[1] = "red"
        fig_pc.update_layout(title=f"Percentage of buying and selling for {symbol}")
        st.plotly_chart(fig_pc)

    analysis_dict = {
        "SNP500": SNP500,
        "NASDAQ": NASDAQ,
        # __________________
        "Crypto": crypto_display, 
        "Nifty50": Nifty50,
        "NSE Stock Delivery": NSE,
        "DOW": DOW,
        "DIVIDENDS": DIV,
        # __________________
        
    }

    with st.sidebar:
        # image = Image.open('logo1.jpeg')
        image = Image.open('logo.png')
        st.image(image, caption='By FinTape financial solutions')
        st.markdown('<h1 style="float: left;">WITH LOVE :)</h1>',unsafe_allow_html=True,)
        selected_analysis = st.radio("Select Analysis", list(analysis_dict.keys()))
        st.write("---")

    st.header(selected_analysis)

    analysis_dict[selected_analysis]()
