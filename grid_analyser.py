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
    def __init__(self, ticker="n/a", fiat_wallet=0, coins=0.0, single_grid_width=0, lower_price=0, upper_price=0, current_price=0, bot_value=0, buys = 0, sells = 0):
        self.ticker = ticker
        self.fiat_wallet = fiat_wallet
        self.coins = coins
        self.single_grid_width = single_grid_width
        self.lower_price = lower_price
        self.upper_price = upper_price
        self.current_price = current_price
        self.bot_value = bot_value
        self.buys = buys
        self.sells= sells



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

    buys = 0
    sells = 0

    for close in data['Close']:
        current_grid = int((upper_price - close) / single_grid_width)

        if prev_grid is None or current_grid < prev_grid:
            # buy operation
            buys = buys + 1
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
            sells = sells + 1
            fiat_wallet = fiat_wallet + order['amount'] * close
            coin_amount = coin_amount - order['amount']
            # print(f"<:::::::> Sell {symbol} at price {close} (= {order['amount']}) - Current {current_grid}  ")
            sell_orders.remove(order)


        prev_grid = current_grid
    
    last_price = data['Close'].iloc[-1]
    bot_value = fiat_wallet + coin_amount * last_price

    return CoinResult(symbol, fiat_wallet, coin_amount, single_grid_width, lower_price, upper_price, last_price, bot_value, buys, sells)


def xround(value, decimals = None, currency=""):
    """ Rounds the value and determins the amount of decimals according to the value. """
    if decimals != None:
        return f"{currency}{{:,.{decimals}f}}".format(value)
    absvalue = abs(value)
    if absvalue >= 10000:
        decimals = 0
    elif absvalue >= 1000:
        decimals = 1
    elif absvalue >= 1:
        decimals = 2
    elif absvalue >= 0.1:
        decimals = 3
    elif absvalue >= 0.01:
        decimals = 4
    elif absvalue >= 0.001:
        decimals = 5
    elif absvalue >= 0.0001:
        decimals = 6
    else:
        decimals = 9
    return f"{currency}{{:,.{decimals}f}}".format(value)

if 'html' not in st.session_state:
    st.session_state['html'] = ''
    st.session_state['overview'] = ''


st.set_page_config(page_title="Crypto Grid Analyser", page_icon="💰", layout="centered", initial_sidebar_state="collapsed")
st.title("Crypto Grid Analysis")
st.markdown("**Crypto Grid Analysis** is a tool to help you determine the best grid for your crypto grid trading bot. Choose from the list of top 100 cryptocurrencies and see how much money you can make - backtested until today.")    
st.markdown("---")


NUMBER_OF_GRIDS = 50
PERIOD = "1d"     # period: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
INTERVAL = "1m"   # 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
TOP_N = 100
AMOUNT_OF_RESULTS = 10
INVESTMENT = 1000

col1, col2, col3 = st.columns([1, 1, 1])

investment_values = list(range(10, 100, 10)) + list(range(100, 1000, 100)) + list(range(1000, 10000, 1000)) + list(range(10000, 100001, 10000))


def money_formatter(number):
    return f"{xround(number, 2)}" 


NUMBER_OF_GRIDS = col1.select_slider("Number of Grids", options=range(5, 101, 5), value=NUMBER_OF_GRIDS)
PERIOD = col2.select_slider("Data Period", options=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'], value=PERIOD)
INTERVAL = col3.select_slider("Data Interval", options=['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'], value=INTERVAL)
TOP_N = col1.select_slider("Check Top x Coins by market cap", options=range(1, 101), value=TOP_N)
AMOUNT_OF_RESULTS = col2.select_slider("Show Top x Results", options=range(1, 101), value=AMOUNT_OF_RESULTS)
INVESTMENT = col3.select_slider("Investment in USD", options=investment_values, format_func=money_formatter, value=INVESTMENT)
 
AMOUNT_OF_RESULTS = min(AMOUNT_OF_RESULTS, TOP_N)

st.markdown("---")



results = []

if st.button("Analyze"):

    st.session_state.overview = f"""
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
                <td><b>Investment</b></td>
                <td><b>Investment/Grid</b></td>
            </tr>
            <tr>
                <td>{NUMBER_OF_GRIDS}</td>
                <td>{PERIOD}</td>
                <td>{INTERVAL}</td>
                <td>{TOP_N}</td>
                <td>{AMOUNT_OF_RESULTS}</td>
                <td>{xround(INVESTMENT, 2, '$')}</td>
                <td>{xround(INVESTMENT/NUMBER_OF_GRIDS, 2, '$')}</td>
            </tr>
        </table>
    """

    st.markdown(st.session_state.overview, unsafe_allow_html=True)


    spinner_placeholder = st.empty()


    for index, coin in enumerate(coins[:TOP_N]):
        spinner_placeholder.markdown(f"Analyzing {index} of {TOP_N}: **{coin}**")
        coin_result = analyze_crypto(coin, period=PERIOD, interval=INTERVAL,grids=NUMBER_OF_GRIDS, fiat_wallet=INVESTMENT)
        results.append(coin_result)

    # sort the results array by coin_result.fiat_wallet
    spinner_placeholder.empty()  # Remove the spinner
    spinner_placeholder.success(f'All {TOP_N} coins analysed!')
    # Sort results by "UP" in descending order
    sorted_results = results #  sorted(results, key=lambda x: x[1], reverse=True)
    sorted_results = sorted(results, key=lambda x: x.bot_value, reverse=True)

    cols = st.columns(8)

    st.markdown("", unsafe_allow_html=True) 

    html = "<table><tr>"
    for index, headline in enumerate(("Coin", "Buys", "Sells", "Fiat", "Coins", "Grid Price", "min Price", "max Price", "Last Price", "Bot Value" )):
        html += f"<th>{headline}</th>"
    html += "</tr>"
 
    for result in sorted_results:   
        html += f""" 
                    <tr>
                    <td><a href='https://www.tradingview.com/symbols/{result.ticker}USDT/' target='_blank'>{result.ticker}</a></td>
                    <td>{xround(result.buys, decimals=0)}</td>
                    <td>{xround(result.sells, decimals=0)}</td>
                    <td>{xround(result.fiat_wallet, 2, "$")}</td>
                    <td>{xround(result.coins,currency=f"{result.ticker} ")}</td>
                    <td>{xround(result.single_grid_width)}</td> 
                    <td>{xround(result.lower_price)}</td>
                    <td>{xround(result.upper_price)}</td>
                    <td>{xround(result.current_price)}</td>
                    <td>{xround(result.bot_value, decimals=2, currency="$")}</td>
                    </tr>
        """
    html += "</table>"
    st.session_state.html = html.replace("  ", " ").replace("\n", "")


    st.markdown(st.session_state.html, unsafe_allow_html=True)
    