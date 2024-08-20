import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import _datetime # type: ignore
import plotly.express as px
import statsmodels
import plotly.graph_objects as go





st.set_page_config(
    page_title="Charts and Analytics",
    page_icon="📈"

)



main_bg= f"""
<style>
[data-testid="stAppViewContainer"] {{

background-image: url(https://static.vecteezy.com/system/resources/previews/002/816/559/non_2x/abstract-blue-technology-diagonal-geometric-design-background-with-light-effect-free-vector.jpg);
background-size: cover;
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

def color_designate(val):
    color = "green" if val >= 0 else "red"
    return f"color: {color}"

st.markdown(main_bg, unsafe_allow_html=True)



st.sidebar.success("Select Page")






st.title('Charts and Analytics')
st.subheader("Overview, Trends, and Key Metrics")
start = st.date_input("Start Date: ", _datetime.datetime.today() - _datetime.timedelta(days = 366))
end = st.date_input("End Date: ", _datetime.datetime.today())
date_diff = (end-start).days
user_ticker_choice=st.text_input("Enter Ticker: ", 'AAPL')

#specific stock data
df=yf.download(user_ticker_choice,start,end, progress=False)  


#s&p500 data
sp500_benchmark= yf.download('^GSPC', start, end)

#Useful Variables
shared_variables = {"logreturns": np.log(df['Adj Close']/df['Adj Close'].shift(1)),
                        'bench_log': np.log(sp500_benchmark['Adj Close']/sp500_benchmark['Adj Close'].shift(1))
                        }


#13wk Treasury Bill

def get_annual_rfr(ticker = '^IRX', start = start, end = end):
    annual_rfr = yf.download(ticker, start, end)['Adj Close']/100
    return annual_rfr



def daily_rfr(periods = 252, start = start, end = end):
    return (1 + get_annual_rfr()) ** (1/periods) - 1

daily_rfr(periods = 252, start = start, end = end)
    
def get_rfr():
    daily_r_free = daily_rfr()
    rates_data = pd.DataFrame({"Annual_rfr": get_annual_rfr(), "Daily_rfr": daily_r_free})
    return rates_data

rates_df = get_rfr()
rates_df['sec_ret'] = shared_variables['logreturns']
rates_df['ex_ret'] = rates_df['sec_ret']-rates_df['Daily_rfr']
std_excess = np.std(rates_df['sec_ret']-rates_df['Daily_rfr'])

avg_excess = rates_df['ex_ret'].mean()

risk_free_rate = rates_df['Daily_rfr'].mean()

#Dataframe housing log returns for market and specific stock
#get dataframe with log returns for specific stock
stock_data = df.copy()
stock_data['stock_ret'] = shared_variables['logreturns']
stock_data.drop(stock_data.columns[0:6], axis = 1, inplace = True)
stock_data.dropna(inplace = True)
#dataframe with benchmark (s&p 500) log returns
benchmark_data = sp500_benchmark.copy()
benchmark_data['bench_ret'] = shared_variables['bench_log']
benchmark_data.drop(benchmark_data.columns[0:6], axis = 1, inplace = True)
benchmark_data.dropna(inplace = True)
#New dataframe housing log returns
log_df = pd.concat([stock_data, benchmark_data], axis = 1)
log_df.reset_index()
#Covariance between stock and benchmark (s&p)
covariance = np.cov(log_df['stock_ret'], log_df['bench_ret'], ddof=1)[1,0]
#Variance of benchmark
variance_bench = np.var(log_df['bench_ret'])
#Beta calculation
beta = covariance/variance_bench
#Rolling beta dataframe
window = 7
cov_roll = log_df['stock_ret'].rolling(window).cov(log_df['bench_ret']).dropna()
var_bench_roll = log_df['bench_ret'].rolling(window).var().dropna()
df_roll_beta = pd.DataFrame({"Cov_roll": cov_roll, "Var_roll": var_bench_roll, "Beta_roll": cov_roll/var_bench_roll})
    

st.subheader(f'Displays data from {start.strftime("%B %d, %Y")} to {end.strftime("%B %d, %Y")}')
st.write("Descriptive Statistics:")
st.write(df.describe())


#DATA VISUALIZATIONS

#CUSTOM LENGTH SMA/EMA 
st.subheader("Closing Price Over Time (with custom-Length moving average)")

movavg_options = ["Simple Moving Average(SMA)", "Exponential Moving Average(EMA)"]

movavg_selected = st.selectbox("Select Type of Moving Average", options = movavg_options)

movavg_length = st.number_input("Enter Length (days) of Moving Average", 1)


def plot_sma():
    sma_custom=df.Close.rolling(movavg_length).mean()

    fig_sma_custom= go.Figure()

    fig_sma_custom.add_trace(go.Scatter(
        x= df.index,
        y= sma_custom,
        mode='lines',
        name=f"SMA{movavg_length}",
        line=dict(color="#17becf")
    ))

    fig_sma_custom.add_trace(go.Scatter(
        x= df.index,
        y= df.Close,
        mode= "lines",
        name= "Closing Price",
        line=dict(color='#d62728')
    ))

    fig_sma_custom.update_layout(
        xaxis_title="Time",
        yaxis_title="Closing Price",
        title=f"{user_ticker_choice} Closing Price with {movavg_length}-Day SMA",
        title_x = 0.34
    )

    st.plotly_chart(fig_sma_custom)

def plot_ema():
    ema_custom = df.Close.ewm(span = movavg_length, min_periods = movavg_length).mean()

    fig_ema = go.Figure()

    fig_ema.add_trace(go.Scatter(
        x= df.index,
        y= ema_custom,
        mode= "lines",
        name= f"EMA{movavg_length}",
        line=dict(color="#17becf")
    ))

    fig_ema.add_trace(go.Scatter(
        x= df.index,
        y= df.Close,
        mode= "lines",
        name="Closing Price",
        line=dict(color="#d62728")
    ))

    fig_ema.update_layout(
        xaxis_title = "Time",
        yaxis_title = "Closing Price",
        title = f"{user_ticker_choice} Closing Price with {movavg_length}-day EMA"
    )

    st.plotly_chart(fig_ema)

if movavg_selected == "Simple Moving Average(SMA)":
    plot_sma()
else:
    plot_ema()

#CALCULATE AND DISPLAY METRICS

st.header("Key Metrics/Models")


metric_options = ["Volatility (Standard Deviation)", "Drawdown", "Alpha", "Beta", "Capital Asset Pricing Model (CAPM)", 
                  "Logarithmic Returns", "Compound Returns", "Sharpe Ratio"]

#initialize session state
if 'metrics_selected' not in st.session_state:
    st.session_state['metrics_selected'] = []

def metricMultiSelect():
    selected_metrics = st.session_state['metrics_selected']   #this is bc m_selection will be the key (ensures m_selected is updated; selection is updated, synchronized)

    #log returns
    def displayLog():
        logreturns = shared_variables['logreturns']
        fig_log = px.line(df, x = df.index, y= logreturns, title = f"Logarithmic Returns for {user_ticker_choice}")
        fig_log.update_layout(
        xaxis_title= "Time",
        yaxis_title= "Log Return",
        title_x = 0.35)
        st.plotly_chart(fig_log)
        return True   #prevents excessive/unnecessary function calls
    
    #compound returns
    def displayCompReturns():             
        cumcompreturns = np.exp(shared_variables['logreturns'].cumsum()) * 100     #Just Buy and Hold strategy
        fig_comp = px.line(df, x = df.index, y = cumcompreturns, title = f"Compound Returns (%) Over Time for {user_ticker_choice}")
        fig_comp.update_layout(
            xaxis_title = "Time", 
            yaxis_title = "Compound Returns (%)",
            title_x = 0.3
        )
        fig_comp.update_traces(line_color = "blue")
        st.plotly_chart(fig_comp)
        return True

    #Volatility/standard deviation
    def displayVolatility():
        volatility = shared_variables['logreturns'].std()
        vol_df = pd.DataFrame({"Volatility": [volatility]})
        st.subheader(f"Volatility of {user_ticker_choice} for the period {start}-{end}: ") 
        st.subheader(f":gray-background[:blue[{volatility:3f}]]")
        return True
    
    #Drawdown
    def displayDrawDown():
        df['CumulativeReturns'] = np.exp(shared_variables['logreturns'].cumsum())   
        df['CumulativeMax'] = df.CumulativeReturns.cummax()
        df['Drawdown'] = df['CumulativeMax'] - df['CumulativeReturns'] 
        df['Drawdown(%)'] = (df['CumulativeMax'] - df['CumulativeReturns'])/df['CumulativeMax'] * 100
        maxDrawDown =  df['Drawdown(%)'].max()
        maxDrawDate = df['Drawdown(%)'].idxmax()
        st.subheader(f'The Maximum Drawdown was :blue[{maxDrawDown:2f}%] on {maxDrawDate.strftime("%B %d, %Y")}')
        fig_drawdown = go.Figure()
        fig_drawdown.add_trace(go.Scatter(
            x=df.index,
            y=df['CumulativeReturns'],
            mode="lines",
            name="Cumulative Returns",
            line=dict(color="#17becf")
        ))
        fig_drawdown.add_trace(go.Scatter(
            x=df.index,
            y=df['CumulativeMax'],
            mode="lines",
            name="Cumulative Max (Peak)",
            line=dict(color="#d62728")
        ))
        fig_drawdown.add_trace(go.Scatter(
            x=df.index,
            y=df['Drawdown'],
            mode="lines",
            name="Drawdown",
            line=dict(color="#e35f1e")
        ))
        fig_drawdown.update_layout(
            xaxis_title= "Time",
            yaxis_title= "Drawdown",
            title= f"Drawdowns with Cumulative Returns and Maxima for {user_ticker_choice}",
            title_x = 0.1
        )
        st.plotly_chart(fig_drawdown)

        return True

    #Sharpe Ratio
    def displaySharpe():
        sharpe_ratio = avg_excess/std_excess
        st.subheader(f"Sharpe Ratio for {user_ticker_choice} for the period {start} to {end}: :blue[{sharpe_ratio:2f}]")
        return True


    #Beta
    def displayBeta():
        beta_today = yf.Ticker(user_ticker_choice).info.get('beta') 
        #beta = (covariance of investment and benchmark returns)/variance of benchmark (market)
        if date_diff >= 1:
            st.subheader(f"Beta coefficient for the period {start}  to  {end}: :blue[{beta:2f}]")
        st.subheader(f"Beta coefficient, today,  {_datetime.datetime.today().strftime('%Y-%m-%d')}:")
        st.subheader(f":blue[{beta_today}]")
        return True
    

    #Alpha; alpha = avgstockret - (risk free rate + beta *(avgmarketret - risk free rate))
    def displayAlpha():
        avg_stock_ret = shared_variables['logreturns'].mean()
        avg_market_ret = shared_variables['bench_log'].mean()
        alpha = avg_stock_ret - (risk_free_rate + beta * (avg_market_ret - risk_free_rate))
        st.subheader(f"Alpha for {user_ticker_choice} for the period {start} to {end}: :blue[{alpha:2f}]")
        return True
    
    #CAPM; expected return = rfr + beta(market_ret - riskfreerate)
    # df_roll_beta = pd.DataFrame({"Cov_roll": cov_roll, "Var_roll": var_bench_roll, "Beta_roll": cov_roll/var_bench_roll})
    def displayCapm():
        equity_risk_premium =  shared_variables['bench_log'] - risk_free_rate
        exp_return = risk_free_rate + df_roll_beta["Beta_roll"] * equity_risk_premium 
        exp_return_period = risk_free_rate.mean() + beta * equity_risk_premium.mean()
        df_roll_beta["Ke"] = exp_return  #expected return (cost of equity)

        fig_capm = px.scatter(df_roll_beta, x="Beta_roll", y="Ke", title = "CAPM", template = "plotly_dark", trendline = "ols")
        fig_capm.update_layout(title_x=0.5, 
                               xaxis_title = "Rolling Beta",
                               yaxis_title = "Expected Returns (Cost of Equity(Ke))"
                 )
        st.plotly_chart(fig_capm)
        a = px.get_trendline_results(fig_capm).px_fit_results.iloc[0].rsquared
        
        st.subheader(f"Expected Returns (%) over entire period {start} to {end} using beta = {beta:2f}: ")
        st.subheader(f":gray-background[:violet[{str((exp_return_period * 100)):}]]")
        st.subheader("R-Squared: ")
        st.subheader(f":grey-background[:violet[{a}]]")

        return True
    

    if "Logarithmic Returns" in selected_metrics and displayLog() != True:
        displayLog()
    if "Compound Returns" in selected_metrics and displayCompReturns != True:
        displayCompReturns()
    if "Volatility (Standard Deviation)" in selected_metrics and displayVolatility != True:
        displayVolatility()
    if "Drawdown" in selected_metrics and displayDrawDown != True:
        displayDrawDown()
    if "Beta" in selected_metrics and displayBeta != True:
        displayBeta()
    if "Alpha" in selected_metrics and displayAlpha != True:
        displayAlpha()
    if "Sharpe Ratio" in selected_metrics and displaySharpe != True:
        displaySharpe()
    if "Capital Asset Pricing Model (CAPM)" in selected_metrics and displayCapm != True:
        displayCapm()


st.multiselect(label="Select Metric(s)", options=metric_options, key ='metrics_selected')  
metricMultiSelect()
st.write(":blue[Note:] Refer to 'Help' page for additional information about a metric/model.")







    
    
    


