import streamlit as st
import yfinance as yf


# List of top 100 crypto coins
coins = [
    "BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "MATIC", "SOL", "DOT", "LTC",
    "TRX", "AVAX", "SHIB", "UNI", "LINK", "ATOM", "XMR", "ETC", "XLM", "BCH",
    "APT", "LDO", "QNT", "NEAR", "ARB", "VET", "FIL", "ICP", "HBAR", "EOS",
    "MKR", "ALGO", "SAND", "AAVE", "EGLD", "THETA", "XTZ", "IMX", "AXS", "RUNE",
    "FLOW", "MANA", "GRT", "KCS", "ZEC", "FTM", "ENJ", "KAVA", "CRV", "SNX",
    "GALA", "1INCH", "COMP", "RPL", "CHZ", "FXS", "CAKE", "LRC", "HOT", "WAVES",
    "TWT", "NEXO", "BAL", "CELO", "YFI", "ZRX", "CVX", "ICX", "ONT", "SRM",
    "BNT", "SUSHI", "ANKR", "XVS", "DGB", "WAXP", "IOST", "RVN", "KEEP", "DODO",
    "MTL", "STMX", "REEF", "COTI", "ALPHA", "KMD", "CVC", "OXT", "BAND", "OGN",
    "LSK", "STORJ", "REN", "LPT", "CELR", "ARDR", "CTSI", "BTS", "ZEN", "REP"
]

class CoinResult:
    def __init__(self, ticker="n/a", fiat_wallet=0, coins=0.0, single_grid_width=0, lower_price=0, upper_price=0, current_price=0, bot_value=0):
        self.ticker = ticker
        self.fiat_wallet = fiat_wallet
        self.coins = coins
        self.single_grid_width = single_grid_width
        self.lower_price = lower_price
        self.upper_price = upper_price
        self.current_price = current_price
        self.bot_value = bot_value



def analyze_crypto(symbol, period="1mo", interval="5m", grids=66, fiat_wallet=10000):

    data = yf.download(f"{symbol}-USD", period=period, interval=interval)
    if data.empty:
        return CoinResult()



    lower_price = data['Low'].min()
    upper_price = data['High'].max()
    single_grid_width = (upper_price - lower_price) / grids 

    sell_orders = []
    coin_amount = 0  # initial amount of coins
    bot_value = 0.0
    single_trade_amount = fiat_wallet / (grids - 1)


    prev_grid = None
    sell_orders = []

    min = 0
    for close in data['Close']:
        min += 1
        current_grid = int((upper_price - close) / single_grid_width)

        # print(f"Price at {min}: {close}       Current grid: {current_grid}   Previous grid: {prev_grid}")


        if prev_grid is None or current_grid < prev_grid:
            # buy operation
            amount = single_trade_amount / close
            # print(f"==> Buy {symbol} at price {close} (= {amount}) - Grid {current_grid}  (Sell in Grid {current_grid+1} for {close + single_trade_amount})  ")
            fiat_wallet -= single_trade_amount
            coin_amount += amount
            sell_orders.append({'price': close + single_trade_amount, 'grid': current_grid + 1, 'amount': amount})

        sell_orders_in_current_grid = [order for order in sell_orders if order['grid'] == current_grid] 
        # print(f"Sell orders in current grid: {len(sell_orders_in_current_grid)}")

        current_sell_orders = [order for order in  sell_orders_in_current_grid if order['price'] >= close]
        # print(f"Current sell orders count: {current_sell_orders.count}")

        for order in current_sell_orders:
            fiat_wallet = fiat_wallet + order['amount'] * close
            coin_amount = coin_amount - order['amount']
            # print(f"<:::::::> Sell {symbol} at price {close} (= {order['amount']}) - Current {current_grid}  ")
            sell_orders.remove(order)

        prev_grid = current_grid
    
    last_price = data['Close'].iloc[-1]
    bot_value = fiat_wallet + coin_amount * last_price

    return CoinResult(symbol, fiat_wallet, coin_amount, single_grid_width, lower_price, upper_price, last_price, bot_value)


def xround(value):
    """ Rounds the value and determins the amount of decimals according to the value. """
    decimals = 10
    value = abs(value)
    if value >= 10000:
        decimals = 0
    elif value >= 1000:
        decimals = 1
    elif value >= 1:
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
INVESTMENT = 100

col1, col2, col3 = st.columns([1, 1, 1])

NUMBER_OF_GRIDS = col1.select_slider("Number of Grids", options=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100], value=NUMBER_OF_GRIDS)
PERIOD = col2.select_slider("Data Period", options=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'], value=PERIOD)
INTERVAL = col3.select_slider("Data Interval", options=['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'], value=INTERVAL)
TOP_N = col1.select_slider("Check Top x Coins", options=range(1, 101), value=TOP_N)
AMOUNT_OF_RESULTS = col2.select_slider("Show Top x Results", options=range(1, 101), value=AMOUNT_OF_RESULTS)
INVESTMENT = col3.select_slider("Investment in USD", options=range(100, 10001, 100), value=INVESTMENT)





results = []

if st.button("Analyze"):

    st.markdown(f"""
        <style>
            td {{ text-align: center; font-weight: heavy; color: #FF0000" }}
        </style>
        <table>
            <tr>
                <td><b>Number of Grids</b></td>
                <td><b>Data Period</b></td>
                <td><b>Data Interval</b></td>
                <td><b>Check Top x Coins</b></td>
                <td><b>Show Top x Results</b></td>
                <td><b>Investment/Grid</b></td>
            </tr>
            <tr>
                <td>{NUMBER_OF_GRIDS}</td>
                <td>{PERIOD}</td>
                <td>{INTERVAL}</td>
                <td>{TOP_N}</td>
                <td>{AMOUNT_OF_RESULTS}</td>
                <td>{xround(INVESTMENT/NUMBER_OF_GRIDS)}</td>
            </tr>
        </table>
    """, unsafe_allow_html=True)


    spinner_placeholder = st.empty()


    for index, coin in enumerate(coins[:TOP_N]):
        spinner_placeholder.markdown(f"Analyzing {index} of {TOP_N}: **{coin}**")
        coin_result = analyze_crypto(coin, period=PERIOD, interval=INTERVAL,grids=NUMBER_OF_GRIDS)
        results.append(coin_result)

    # sort the results array by coin_result.fiat_wallet
    spinner_placeholder.empty()  # Remove the spinner
    spinner_placeholder.success(f'All {TOP_N} coins analysed!')
    # Sort results by "UP" in descending order
    sorted_results = results #  sorted(results, key=lambda x: x[1], reverse=True)
    sorted_results = sorted(results, key=lambda x: x.bot_value, reverse=True)

    cols = st.columns(8)

    for index, headline in enumerate(("Coin", "Fiat", "Coins", "Grid Price", "min Price", "max Price", "Last Price", "Bot Value" )):
        cols[index].markdown(f"**{headline}**")

    for result in sorted_results:
        cols[0].markdown(f'<a href="https://www.tradingview.com/symbols/{result.ticker}USDT/" target="_blank">{result.ticker}</a>', unsafe_allow_html=True)
        # cols[0].markdown(f"**{result.ticker}**")
        cols[1].markdown(f"{xround(result.fiat_wallet)}")
        cols[2].markdown(f"{xround(result.coins)}")
        cols[3].markdown(f"${xround(result.single_grid_width)}") 
        cols[4].markdown(f"{xround(result.lower_price)}")
        cols[5].markdown(f"{xround(result.upper_price)}")
        cols[6].markdown(f"{xround(result.current_price)}")
        cols[7].markdown(f"${xround(result.bot_value)}")

    exit()

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
        cols[0].markdown(f'<a href="https://www.tradingview.com/symbols/{result[0]}USDT/">XXX https://www.tradingview.com/symbols/{result[0]}USDT/ {result[0]}</a>', unsafe_allow_html=True)
        cols[1].write(f"{result[1]}")
        cols[2].write(f"{result[2]}")
        cols[3].write(f"{xround(result[3])}")
        cols[4].write(f"{xround(result[4])}")
        cols[5].write(f"{xround(result[5])}")
        cols[6].write(f"{xround(result[6])}")
