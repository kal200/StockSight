import yfinance as yf
import pandas as pd
import numpy as np
import logging
import re
import matplotlib.pyplot as plt 
import streamlit as st
import _datetime # type: ignore
import plotly.express as px
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import seaborn as sns
import nltk
from nltk.data import find
from nltk.downloader import Downloader
from nltk.sentiment.vader import SentimentIntensityAnalyzer



st.set_page_config(
    page_title="StockSight Dashboard",
    page_icon="📈"

)
st.set_option('client.showErrorDetails', False)

main_bg= f"""
<style>
[data-testid="stAppViewContainer"] {{

background-image: url(https://static.vecteezy.com/system/resources/previews/002/816/559/non_2x/abstract-blue-technology-diagonal-geometric-design-background-with-light-effect-free-vector.jpg);
background-size: cover;
background-attachment: scroll; 
}}
[data-testid="stHeader"] {{
background-color: rgba(0, 0, 0, 0);
}}
[data-testid="stSidebar"] {{
background-image: url(https://static.vecteezy.com/system/resources/previews/002/816/559/non_2x/abstract-blue-technology-diagonal-geometric-design-background-with-light-effect-free-vector.jpg);
background-position: center;
}}
</style>
"""

st.markdown(main_bg, unsafe_allow_html=True)



st.sidebar.success("Select Page")

st.title("StockSight Dashboard")

def ensure_vader_lexicon():
    try:
        find('sentiment/vader_lexicon.zip')
    except LookupError:
        nltk.download('vader_lexicon')
    
ensure_vader_lexicon()


main_ind = {"^GSPC": [],
            "^DJI": [], 
            "NDAQ": [], 
            "^RUT": []
           }
for ind in main_ind:
    open_a = yf.Ticker(ind).info.get('regularMarketOpen')
    prev_close = yf.Ticker(ind).info.get('regularMarketPreviousClose')
    year_h=yf.Ticker(ind).info.get('fiftyTwoWeekHigh')
    year_l=yf.Ticker(ind).info.get('fiftyTwoWeekLow')
    main_ind[ind] += [open_a, prev_close, year_h, year_l]
    
df_main_ind = pd.DataFrame.from_dict(main_ind)
df_main_ind.rename(columns= {"^GSPC": "S&P500", "^DJI": "DJI", "NDAQ": "Nasdaq", "^RUT": "Russell 2000"}, index = {0: 'Open', 1: "Prev. Close", 2: "52-Wk high", 3: "52-Wk Low"}, inplace=True)

styled_df = df_main_ind.T.style.set_properties(**{
    'font-size': '12pt'
})


st.subheader(":blue-background[U.S. Markets]")

st.write(styled_df.to_html(), unsafe_allow_html=True)



st.header("Stock Overview (select ticker)")
dash_start=st.date_input("Start Date", _datetime.date.today() - _datetime.timedelta(days = 366), min_value= _datetime.datetime(1980, 1, 1))
dash_start_pd= pd.to_datetime(dash_start)
dash_end=st.date_input("End Date", max_value=_datetime.datetime.today())
dash_end_pd= pd.to_datetime(dash_end)


#indices




allowed_dates = pd.date_range(
    start = '1980-01-01',
    end = _datetime.date.today()
)


#Select and display data for specific stock
dash_ticker=st.text_input("Enter ticker: ", "AAPL")
dash_data=yf.download(dash_ticker, start=dash_start, end=dash_end)


if not isinstance(dash_data.index, pd.DatetimeIndex):
    dash_data.index=pd.to_datetime(dash_data.index)


#Market cap and sector
mktcap = str(yf.Ticker(dash_ticker).info.get('marketCap'))
commapattern = r'(?<=\d)(?=(\d{3})+(\D|$))'
mcap = re.sub(commapattern, ',', mktcap)

sector = yf.Ticker(dash_ticker).info.get('sector')
industry = yf.Ticker(dash_ticker).info.get('industry')
desc = yf.Ticker(dash_ticker).info.get('longBusinessSummary')



fig=px.line(dash_data, x=dash_data.index, y='Adj Close', title=dash_ticker)   #the index of the DataFrame is the Date
fig.update_layout(title_x=0.5)
st.plotly_chart(fig)

col1, col2= st.columns(2)


col1.subheader(f"Market Cap: :blue[{mcap}]")
col2.subheader(f"Sector/Industry: :blue[{sector}/{industry}]")

codesc = st.checkbox("Show Company Description", False)

if codesc:
    st.subheader(f"Company Description: :blue[{desc}]")


#key data section
st.subheader("Key Data")

price_data, fundamental_data, news = st.tabs(["Price Data", "Fundamentals", "Recent News"])


def color_designate(val):
    color = "green" if val >= 0 else "red"
    return f"color: {color}"

from alpha_vantage.fundamentaldata import FundamentalData
alpha_key="45ORX0CSCRI25RC0"

with price_data:
    st.subheader(f"Daily Pricing Data ({dash_ticker})")
    dash_data2=dash_data
    dash_data2["Daily % Change"] = (dash_data["Adj Close"]/dash_data["Adj Close"].shift(1) - 1) * 100
    dash_data2.dropna(inplace=True)
    styled_dash_data2 = dash_data2.style.map(color_designate,subset=["Daily % Change"])
    st.write(styled_dash_data2)
    

     
with fundamental_data:
    
    st.header(f"Fundamentals of {dash_ticker}")
    st.subheader(":blue-background[Key Fundamental Data]")
    fd=FundamentalData(alpha_key, output_format= "pandas")

    #st.subheader(f"{dash_ticker} Company Overview")

    

    #annual balance sheet
    def balance_annual():
        balance_sheet_a=fd.get_balance_sheet_annual(dash_ticker)[0]
        b_sheet_a=balance_sheet_a.T[2:]
        b_sheet_a.columns=list(balance_sheet_a.T.iloc[0])
        st.write(b_sheet_a)

    #quarterly balance sheet
    def balance_quarterly():
        balance_sheet_q=fd.get_balance_sheet_quarterly(dash_ticker)[0]
        b_sheet_q=balance_sheet_q.T[2:]
        b_sheet_q.columns=list(balance_sheet_q.T.iloc[0])
        st.write(b_sheet_q)

    #annual income statement
    def income_annual():
        income_statement_a=fd.get_income_statement_annual(dash_ticker)[0]
        inc_state_a=income_statement_a.T[2:]
        inc_state_a.columns=list(income_statement_a.T.iloc[0])
        st.write(inc_state_a)

    #quarterly income statement
    def income_quarterly():
        income_statement_q=fd.get_income_statement_quarterly(dash_ticker)[0]
        inc_state_q=income_statement_q.T[2:]
        inc_state_q.columns=list(income_statement_q.T.iloc[0])
        st.write(inc_state_q)

     #annual cash flows
    def cf_annual():
        cash_flows_a=fd.get_cash_flow_annual(dash_ticker)[0]
        c_flows_a=cash_flows_a.T[2:]
        c_flows_a.columns=list(cash_flows_a.T.iloc[0])
        st.write(c_flows_a)

     #Quarterly cash flows
    def cf_quarterly():
        cash_flows_q=fd.get_cash_flow_annual(dash_ticker)[0]
        c_flows_q=cash_flows_q.T[2:]
        c_flows_q.columns=list(cash_flows_q.T.iloc[0])
        st.write(c_flows_q)

    #Create dropdowns
    #metrics
    fund_options = ["Debt-to-Equity", "Quick Ratio", "Current Ratio"]

    fund_selected = st.selectbox("Select Fundamental Data/Ratio(s)", options=fund_options)

    stmnt_options=["Balance Sheet (Annual)", "Balance Sheet (Quarterly)", 
                 "Income Statement (Annual)", "Income statement (Quarterly)", 
                 "Cash Flow Statement(Annual)", "Cash Flow Statement (Quarterly)",
                 ]
    
    try:
        def displayFundMet():
            #if fund_selected == "Free Cash Flow":
                #fcf = yf.Ticker(dash_ticker).info.get('freeCashflow')
                #st.subheader(f"Free Cash Flow: {}")
            #if fund_selected == "EBITDA":
                #ebitda = yf.Ticker(dash_ticker).info.get('ebitda')
            #if fund_selected == "Total Debt":
                #totdebt = yf.Ticker(dash_ticker).info.get('totalDebt')
            if fund_selected == "Debt-to-Equity":
                de = yf.Ticker(dash_ticker).info.get('debtToEquity') /100
                st.subheader(f"Debt-to-Equity ratio: :blue[{round(de, 2)}]")
            if fund_selected == "Quick Ratio":
                qratio = yf.Ticker(dash_ticker).info.get('quickRatio')
                st.subheader(f"Quick ratio: :blue[{qratio}]")
            if fund_selected == "Current Ratio":
                cratio = yf.Ticker(dash_ticker).info.get('currentRatio')
                st.subheader(f"Current ratio: :blue[{cratio}]")
        displayFundMet()
    except Exception as e:
        st.write("Sorry, could not obtain requested metric(s)")
        logging.error(f"error occurred: {str(e)}")

            

    #statements
    st.subheader(":blue-background[Financial Statements]")
    stmnt_selected=st.selectbox("Select statement to review", options=stmnt_options, index=None)

    try:
        def display_statement():
            if stmnt_selected == "Balance Sheet (Annual)":
                st.subheader(f"Annual Balance Sheet ({dash_ticker})")
                balance_annual()
            elif stmnt_selected == "Balance Sheet (Quarterly)":
                st.subheader(f"Quarterly Balance Sheets ({dash_ticker})")
                balance_quarterly()
            elif stmnt_selected == "Income Statement (Annual)":
                st.subheader(f"Annual Income Statements ({dash_ticker})")
                income_annual()
            elif stmnt_selected == "Income Statement (Quarterly)":
                st.subheader(f"Quarterly Income Statements ({dash_ticker})")
                income_quarterly()
            elif stmnt_selected == "Cash Flow Statement(Annual)":
                st.subheader(f"Annual Cash Flow Statements for {dash_ticker}")
                cf_annual()
            elif stmnt_selected == "Cash Flow Statement(Quarterly)":
                st.subheader(f"Quarterly Cash Flow Statements for {dash_ticker}")
                cf_quarterly()

        display_statement()
    except Exception as e:
        st.write("Sorry, daily API request limit (25) exceeded.")
        logging.error(f"Error occurred: {str(e)}")
     

with news:
    st.subheader("Recent Headlines")

    #scraping finviz
    finviz_url= f'https://finviz.com/quote.ashx?t={dash_ticker}'


    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}
    req = Request(url = finviz_url, headers = hdr)
    response = urlopen(req)

    soup = BeautifulSoup(response, 'html.parser')

    news_table = soup.find(id="news-table")

    parsed_data=[]

    for row in news_table.find_all('tr'):
        if row.a:
            title = row.a.text

            source_div = row.find("div", class_ = "news-link-right flex gap-1 items-center")
            source= source_div.text.strip()

            source_link = row.find("a", class_="tab-link-news").attrs["href"]

            time_td = row.find('td', {'align': 'right'})
            time_data = time_td.text.strip().split(' ') if time_td else None
            if len(time_data) == 1:
                time = time_data[0]
            elif time_data[0] != "Today": 
                date = time_data[0] 
                time = time_data[1]
            else:
                date = _datetime.date.today()
                time_data[0] = date 
                time = time_data[1]
        parsed_data.append([date, time, title, source, source_link])


    #Organizing Data and Sentiment Scores
    sent_df= pd.DataFrame(parsed_data, columns = ['Date', 'Time', 'Title', 'Source', 'Source Link'])

    vader = SentimentIntensityAnalyzer()

    f = lambda title: vader.polarity_scores(title)['compound'] 
    comp_sent = sent_df['Title'].apply(f)
    sent_df["Compound Sentiment Score"] = comp_sent

    sent_df['Date'] = pd.to_datetime(sent_df.Date).dt.date

    #for display
    def color_designate(val):
        if val > 0:
            color = "green"
        elif val == 0:
            color = "orange"
        else:
            color = "red"
        return f"color: {color}"

    sent_df_a = sent_df.copy()
    sent_df_a.reset_index()
    sent_df_a.index = sent_df_a.index + 1
    sent_df_a.rename(columns = {"Source Link": "Visit Article"}, inplace=True)
    sent_df_a = sent_df_a[["Date", "Time", "Title", "Compound Sentiment Score", "Source", "Visit Article"]]
    #print(sent_df_a.columns)


    st.write(":blue[Note:] Adjust table slider or enter fullscreen (hover over table and access tools) to view all attributes.")

    st.dataframe(sent_df_a.style.map(color_designate, subset = ['Compound Sentiment Score']), column_config={
        "Visit Article": st.column_config.LinkColumn(
            
        )
        
    })
    #explanation
    st.write("Compound sentiment scores refer to the level of positivity/negativity in a headline as determined"
            " by the Vader sentiment analysis model. Vader provides a sentiment polarity score (-1 to 1), with 1 being the most positive."
            "Refer to the help page for more information about Vader and sentiment scores.")

    #Average Daily Compound Sentiment Scores

    
    
    mean_sent_df = sent_df.groupby(['Date'])['Compound Sentiment Score'].mean().reset_index()  

    news_check = st.checkbox("Further Sentiment Analysis", False)


    bar_colors = []
    def changeColor():
        for i in mean_sent_df["Compound Sentiment Score"]:
            bar_color = "green" if i > 0 else "red"
            bar_colors.append(bar_color)
            
     
        

    if news_check:
        changeColor()
        plt.figure(figsize=(12,8))
        plt.bar(x=mean_sent_df['Date'], height=mean_sent_df['Compound Sentiment Score'], width=0.35, color = bar_colors)

        for i, score in enumerate(mean_sent_df["Compound Sentiment Score"]):   #i for index, score for value
            offset = 0.002 if score > 0 else -abs(0.008)
            plt.text(x = mean_sent_df["Date"][i], y = score + offset, s = f"{score:2f}", color = "slateblue")

    
        plt.plot(mean_sent_df["Date"], mean_sent_df["Compound Sentiment Score"], marker='o', color='orange')
        plt.xlabel("Date", fontsize = 15)
        plt.ylabel("Average Compound Sentiment Score", fontsize = 15)
        plt.title("Daily Average Compound Sentiment Score", fontsize = 15)
        plt.style.use("seaborn-v0_8-dark")
        plt.grid(visible=True)
        st.pyplot(plt.gcf())

    

    


    