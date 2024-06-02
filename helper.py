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
    """ Structure for a single coin analysis result."""
    def __init__(self, ticker="n/a", marketcap_index=-1, fiat_wallet=0, coin_wallet=0.0, single_grid_width=0, lower_price=0, upper_price=0, current_price=0, bot_value=0, buys = 0, sells = 0):
        self.index = marketcap_index
        self.ticker = ticker
        self.fiat_wallet = fiat_wallet
        self.coins = coin_wallet
        self.single_grid_width = single_grid_width
        self.lower_price = lower_price
        self.upper_price = upper_price
        self.current_price = current_price
        self.bot_value = bot_value
        self.buys = buys
        self.sells= sells


################################################################
def analyze_crypto(symbol, marketcap_index, period="1mo", interval="5m", grids=33, fiat_wallet=1000):
    """ Method to analyse the gain/loss in a given period for a given crypto coin. """
    print(f"YF '{symbol}-USD' period={period}, interval={interval}")
    try:
        data = yf.download(f"{symbol}-USD", period=period, interval=interval)
        if data.empty:
            return None

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

        return CoinResult(symbol, marketcap_index, fiat_wallet, coin_amount, single_grid_width, lower_price, upper_price, last_price, bot_value, buys, sells)
    except ValueError as e:
        print(f"Error analyzing {symbol}: {e}")
        return None

################################################################
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



################################################################
def money_formatter(number):
    """ Default formatter with thousand seperator and 2 fragment digits."""
    return f"{xround(number, 2)}" 


