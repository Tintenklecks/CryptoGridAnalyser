from encodings import utf_8
import streamlit as st
import yfinance as yf


# List of top 100 crypto coins
coins = [
    "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD", "DOGE-USD", "MATIC-USD", "SOL-USD", "DOT-USD", "LTC-USD",
    "TRX-USD", "AVAX-USD", "SHIB-USD", "UNI-USD", "LINK-USD", "ATOM-USD", "XMR-USD", "ETC-USD", "XLM-USD", "BCH-USD",
    "APT-USD", "LDO-USD", "QNT-USD", "NEAR-USD", "ARB-USD", "VET-USD", "FIL-USD", "ICP-USD", "HBAR-USD", "EOS-USD",
    "MKR-USD", "ALGO-USD", "SAND-USD", "AAVE-USD", "EGLD-USD", "THETA-USD", "XTZ-USD", "IMX-USD", "AXS-USD", "RUNE-USD",
    "FLOW-USD", "MANA-USD", "GRT-USD", "KCS-USD", "ZEC-USD", "FTM-USD", "ENJ-USD", "KAVA-USD", "CRV-USD", "SNX-USD",
    "GALA-USD", "1INCH-USD", "COMP-USD", "RPL-USD", "CHZ-USD", "FXS-USD", "CAKE-USD", "LRC-USD", "HOT-USD", "WAVES-USD",
    "TWT-USD", "NEXO-USD", "BAL-USD", "CELO-USD", "YFI-USD", "ZRX-USD", "CVX-USD", "ICX-USD", "ONT-USD", "SRM-USD",
    "BNT-USD", "SUSHI-USD", "ANKR-USD", "XVS-USD", "DGB-USD", "WAXP-USD", "IOST-USD", "RVN-USD", "KEEP-USD", "DODO-USD",
    "MTL-USD", "STMX-USD", "REEF-USD", "COTI-USD", "ALPHA-USD", "KMD-USD", "CVC-USD", "OXT-USD", "BAND-USD", "OGN-USD",
    "LSK-USD", "STORJ-USD", "REN-USD", "LPT-USD", "CELR-USD", "ARDR-USD", "CTSI-USD", "BTS-USD", "ZEN-USD", "REP-USD"
]


def analyze_crypto(ticker, period="1mo", interval="5m", grids=66):
    """  Analyze the crypto data and counts the amount of changes up and down in the grid """
    # Fetch historical data
    data = yf.download(ticker, period=period, interval=interval)
    
    # Check if data is returned
    if data.empty:
        return 0,0,0, 0, 0, 0

    # Get the high and low prices
    upper_price = data['High'].max()
    lower_price = data['Low'].min()

    # Calculate the grid step
    single_grid_width = (upper_price - lower_price) / grids

    # Initialize UP and DOWN counters
    up_counter = 0
    down_counter = 0

    last_close = 0

    # Iterate through the data
    for i in range(1, len(data)):
        previous_close = data['Close'].iloc[i - 1]
        current_close = data['Close'].iloc[i]

        # Calculate previous and current grid levels
        previous_grid_level = int((previous_close - lower_price) // single_grid_width)
        current_grid_level = int((current_close - lower_price) // single_grid_width)

        # Check if it crossed the grid upwards or downwards
        if current_grid_level > previous_grid_level:
            up_counter += 1
        elif current_grid_level < previous_grid_level:
            down_counter += 1

        last_close = current_close

    # Return the results
    return up_counter, down_counter, single_grid_width, lower_price, upper_price, last_close

def xround(value):
    decimals = 10
    if value >= 1:
        decimals = 2
    elif value >= 0.1:
        decimals = 3
    elif value >= 0.01:
        decimals = 4
    elif value >= 0.001:
        decimals = 5
    elif value >= 0.0001:
        decimals = 6
    else:
        decimals = 9
    return f"{{:,.{decimals}f}}".format(value)

st.title("Crypto Grid Analysis")

NUMBER_OF_GRIDS = 50
PERIOD = "5d"     # period: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
INTERVAL = "1m"   # 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
TOP_N = 30
AMOUNT_OF_RESULTS = 30


NUMBER_OF_GRIDS = st.sidebar.select_slider("Number of Grids", options=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100], value=NUMBER_OF_GRIDS)
PERIOD = st.sidebar.select_slider("Data Period", options=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'], value=PERIOD)
INTERVAL = st.sidebar.select_slider("Data Interval", options=['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'], value=INTERVAL)
TOP_N = st.sidebar.select_slider("Check Top x Coins", options=range(1, 101), value=TOP_N)
AMOUNT_OF_RESULTS = st.sidebar.select_slider("Show Top x Results", options=range(1, 101), value=AMOUNT_OF_RESULTS)





results = []

if st.button("Analyze"):

    cols = st.columns(2)

    st.write(f"Number of Grids: {NUMBER_OF_GRIDS}, Period: {PERIOD}, Interval: {INTERVAL}")    
    st.write(f"Amount of coins checked: {TOP_N}")    
    st.write(f"Displayed results: {AMOUNT_OF_RESULTS}")    
    st.write(f"Number of Grids: {NUMBER_OF_GRIDS}, Period: {PERIOD}, Interval: {INTERVAL}")    
    st.write(f"Amount of coins checked: {TOP_N}")    
    st.write(f"Displayed results: {AMOUNT_OF_RESULTS}")    
    st.write(f"Number of Grids: {NUMBER_OF_GRIDS}, Period: {PERIOD}, Interval: {INTERVAL}")    
    st.write(f"Amount of coins checked: {TOP_N}")    
    st.write(f"Displayed results: {AMOUNT_OF_RESULTS}")    
    spinner_placeholder = st.empty()

    for index, coin in enumerate(coins[:TOP_N]):
        spinner_placeholder.markdown(f"Analyzing {index} of {TOP_N}: **{coin}**")
        (up, down, grid_step, min_price, max_price, last_close) = analyze_crypto(coin, period=PERIOD, interval=INTERVAL,grids=NUMBER_OF_GRIDS)
        results.append((coin, up, down, grid_step, min_price, max_price, last_close ))

    spinner_placeholder.empty()  # Remove the spinner
    spinner_placeholder.success(f'All {TOP_N} coins analysed!')
    # Sort results by "UP" in descending order
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)


    cols = st.columns(7)
    cols[0].markdown("**Coin**")
    cols[1].markdown("**UP**")
    cols[2].markdown("**DOWN**")
    cols[3].markdown("**Step**")
    cols[4].markdown("**Min**")
    cols[5].markdown("**Max**")
    cols[6].markdown("**Last**")


    for result in sorted_results[:AMOUNT_OF_RESULTS]:
        # loop through col and result 
        cols[0].write(f"{result[0]}")
        cols[1].write(f"{result[1]}")
        cols[2].write(f"{result[2]}")
        cols[3].write(f"{xround(result[3])}")
        cols[4].write(f"{xround(result[4])}")
        cols[5].write(f"{xround(result[5])}")
        cols[6].write(f"{xround(result[6])}")