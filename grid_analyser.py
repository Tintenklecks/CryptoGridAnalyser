""" App to determin the current """
import streamlit as st

from helper import coins, analyze_crypto, xround, money_formatter


if 'html' not in st.session_state:
    st.session_state['html'] = ''
    st.session_state['overview'] = ''


st.set_page_config(page_title="Crypto Grid Analyser", page_icon="💰", layout="centered", initial_sidebar_state="collapsed")
st.title("Crypto Grid Analysis")

col1, col2 = st.columns([4, 1])
col1.markdown("**Crypto Grid Analysis** is a tool to help you determine the best grid for your crypto grid trading bot. Choose from the list of top 100 cryptocurrencies and see how much money you can make - backtested until today.")
st.write("")

NUMBER_OF_GRIDS = 30
PERIOD = "1d"     # period: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
INTERVAL = "1m"   # 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
TOP_N = 100
AMOUNT_OF_RESULTS = 10
INVESTMENT = 1000

col1, col2, col3, col4, col5 = st.columns(5)

INVESTMENT_VALUES = list(range(20, 100, 20)) + list(range(100, 1000, 100)) + list(range(1000, 10001, 1000)) 



NUMBER_OF_GRIDS = col1.selectbox("Number of Grids", options=range(5, 101, 5), index=6)
PERIOD = col2.selectbox("Data Period", options=['1d', '5d', '1mo', '3mo', '6mo']) #  , '1y', '2y', '5y', '10y', 'ytd', 'max'], value=PERIOD)
TOP_N = col3.selectbox("Top x by market cap", options=range(1, 101), index=99)
AMOUNT_OF_RESULTS = col4.selectbox("Show Top x Results", options=range(1, 101), index=9)
INVESTMENT = col5.selectbox("Investment in USD", options=INVESTMENT_VALUES, format_func=money_formatter, index=13)
 
AMOUNT_OF_RESULTS = min(AMOUNT_OF_RESULTS, TOP_N)

if PERIOD in ['1d', '5d']:
    INTERVAL = "1m"
elif PERIOD == "1mo":
    INTERVAL = "2m"
elif PERIOD == "3mo": 
    INTERVAL = "60m"
elif PERIOD == "6mo":
    INTERVAL = "60m"

col2.write(f"Interval: {INTERVAL}")

st.write(" ")
analyse_button = st.button("📈 Analyse", help="Click here to start the analysis")

results = []

if analyse_button:
    spinner_placeholder = st.empty()
    skipped = ""


    for index, coin in enumerate(coins[:TOP_N]):
        spinner_placeholder.markdown(f"Analyzing {index} of {TOP_N}: **{coin}** {f'(skipped: {skipped})' if skipped else ''}")
        coin_result = analyze_crypto(coin, marketcap_index=index, period=PERIOD, interval=INTERVAL,grids=NUMBER_OF_GRIDS, fiat_wallet=INVESTMENT)
        if coin_result is not None:
            results.append(coin_result) 
        else:
            coin_result = analyze_crypto(coin, marketcap_index=index, period=PERIOD, interval=INTERVAL,grids=NUMBER_OF_GRIDS, fiat_wallet=INVESTMENT)
            if coin_result is not None:
                results.append(coin_result)
            else:
                skipped = coin + " " + skipped

    spinner_placeholder.empty()  # Remove the spinner

    if skipped != "":
        skipped = f"The following coins were skipped: {skipped. replace(' ', ', ')}"


    spinner_placeholder.success(f'All {TOP_N} coins analysed!. {skipped}')

    sorted_results = results #  sorted(results, key=lambda x: x[1], reverse=True)
    sorted_results = sorted(results, key=lambda x: x.bot_value, reverse=True)

    cols = st.columns(8)

    st.markdown("", unsafe_allow_html=True) 

    html = "<table><tr>"
    for index, headline in enumerate(("Coin", "Buys", "Sells", "Fiat", "Coins", "Grid Price", "min Price", "max Price", "Last Price", "Gain/Loss" )):
        html += f"<th>{headline}</th>"
    html += "</tr>"
 
    for result in sorted_results:   
        gain_loss= (result.bot_value - INVESTMENT) / INVESTMENT * 100
        sign = "+" if gain_loss > 0 else ""
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
                    <td>{sign}{xround(gain_loss, decimals=1)}%</td>
                    </tr>
        """
    html += "</table>"
    html = html.replace("  ", " ").replace("\n", "")
    if html != st.session_state.html:
        st.session_state.html = html
        st.write(st.session_state.html, unsafe_allow_html=True)
    