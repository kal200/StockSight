import streamlit as st

st.set_page_config(
    page_title="Help",
    page_icon="❓"

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

st.markdown(main_bg, unsafe_allow_html=True)

doc_url_plotly = "https://plotly.com/graphing-libraries/"
url_av = "https://www.alphavantage.co/"
urls_vader = {
    "vader_intro": "https://pypi.org/project/vaderSentiment/",
    "vader_docs": "https://vadersentiment.readthedocs.io/en/latest/"
}



st.title("Help")

st.header("Chart Tools")
st.write(":red[Note:] The Plotly Graphing Library is used to display charts in this app."
         f"  \n  Its documentation can be found here: {doc_url_plotly}")
st.image('assets\helpimage1.png')
st.write("When using an interactive graph, hover over each tool (located in the red box shown in this example image) to see its function.")

st.subheader("Analyzing Charts")
col1, col2 = st.columns(2)
col1.image('assets\helpimage2.png')
col2.image('assets\helpimage2b.png')
st.write("You can focus on a specified window in a chart by either zooming in (left), or by dragging the cursor to the side in the graph body (right)."
         "  \n  :red[Note:] While both methods allow focusing on a specific window, zooming by dragging the cursor also allows you to zoom in on a specific part of the chart/line. ")
st.write("  \n  To revert to the original graph format, select either the autoscale or home icons")

st.header("Accesing Data")
st.write(f":orange[Fundamental Data Access:] Currently, the :grey-background[:blue[AlphaVantage API]] ({url_av}) used to obtain fundamental data caps daily API request limits at 25 for non-premium plans."
         "  \n  This results in the error message: 'Sorry, daily API request limit (25) exceeded.' The number of available requests refreshes daily.")
st.header("More Information (General)")
st.subheader("Useful Links")
st.markdown("-General Reference: https://www.investopedia.com/")
st.markdown("-Beta: https://www.investopedia.com/terms/b/beta.asp")
st.write("-Alpha: https://www.investopedia.com/terms/a/alpha.asp")
st.write("-Sharpe Ratio: https://www.investopedia.com/terms/s/sharperatio.asp")
st.write("-Volatility: https://www.investopedia.com/terms/v/volatility.asp")
st.write("-Drawdown: https://www.investopedia.com/terms/d/drawdown.asp")
st.write("-Logarithmic Returns: https://saturncloud.io/blog/what-are-logarithmic-returns-and-how-to-calculate-them-in-pandas-dataframe/")
st.write("-Compound Returns: https://www.investopedia.com/terms/c/compoundreturn.asp")

st.write("More information about the Vader sentiment analysis model:"
         f"  \n  {urls_vader['vader_intro']}  \n  {urls_vader['vader_docs']}")

