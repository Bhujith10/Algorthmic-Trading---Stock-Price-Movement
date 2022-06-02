import numpy as np
import pandas as pd
import requests
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input,Output
import plotly.express as px
from plotly.subplots import make_subplots
import dash

app=dash.Dash(__name__)
server=app.server

from alphaVantageAPIkey import api_key
from secret import IEX_CLOUD_API_TOKEN

symbolsDF=pd.read_csv('listing_status.csv')
symbolsDF=symbolsDF[(symbolsDF['assetType']=='Stock')&(symbolsDF['exchange']=='NASDAQ')]
symbolsDF.reset_index(drop=True,inplace=True)

stockSymbols=[]
for i in range(len(symbolsDF)):
    label=symbolsDF.loc[i]['name']
    value=symbolsDF.loc[i]['symbol']
    stockSymbols.append(dict(label=label,value=value))

app.layout=html.Div(children=[
    html.H1(children='Stock Analysis',
           style={'textalign':'center'}),
    html.Br(),
    html.H4(children='This app uses the free services of AlphaVantage API. There is a limit on the api calls we can make per minute. So please leave atleast 1 minute gap between selecting stocks.'),
    html.Div(children=[dcc.Dropdown(id='dropdown',options=stockSymbols,placeholder='Select a Stock',value='AAPL')]),
    html.Br(),
    dcc.Graph(id='graph'),
    html.Br(),
    html.H2(children='Revenue - yearly'),
    dcc.Graph(id='graph1'),
    html.H2(children='Gross Profit - yearly'),
    dcc.Graph(id='graph2'),
    html.H2(children='Operating Income - yearly'),
    dcc.Graph(id='graph3'),
    html.H2(children='EBITDA - yearly'),
    dcc.Graph(id='graph4')
])

@app.callback(Output('graph','figure'),
              Output('graph1','figure'),
              Output('graph2','figure'),
              Output('graph3','figure'),
              Output('graph4','figure'),
             [Input('dropdown','value')])

def updatedFigure(symbol):
    
    if(symbol):
        url_stock=f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&interval=5min&apikey={api_key}'
        url_ema12=f'https://www.alphavantage.co/query?function=EMA&symbol={symbol}&interval=daily&time_period=12&series_type=close&apikey={api_key}'
        url_ema26=f'https://www.alphavantage.co/query?function=EMA&symbol={symbol}&interval=daily&time_period=26&series_type=close&apikey={api_key}'
        url_rsi=f'https://www.alphavantage.co/query?function=RSI&symbol={symbol}&interval=daily&time_period=14&series_type=close&apikey={api_key}'
        url_income=f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={api_key}'
    else:
        url_stock=f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&outputsize=full&apikey={api_key}'
        url_ema12=f'https://www.alphavantage.co/query?function=EMA&symbol=AAPL&interval=daily&time_period=12&series_type=close&apikey={api_key}'
        url_ema26=f'https://www.alphavantage.co/query?function=EMA&symbol=AAPL&interval=daily&time_period=26&series_type=close&apikey={api_key}'
        url_rsi=f'https://www.alphavantage.co/query?function=RSI&symbol=AAPL&interval=daily&time_period=14&series_type=close&apikey={api_key}'
        url_income=f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol=AAPL&apikey={api_key}'
        
        
    income=requests.get(url_income).json()
    print(income)
    if income:
        stockRevenuesYearlyDF=pd.DataFrame(income['annualReports'])
        stockRevenuesYearlyDF.fillna(0,inplace=True)
        stockRevenuesYearlyDF['fiscalDateEnding']=pd.to_datetime(stockRevenuesYearlyDF['fiscalDateEnding'])
        stockRevenuesYearlyDF['year']=stockRevenuesYearlyDF['fiscalDateEnding'].dt.year
        stockRevenuesYearlyDF['grossProfit']=stockRevenuesYearlyDF['grossProfit'].astype('float')
        stockRevenuesYearlyDF['totalRevenue']=stockRevenuesYearlyDF['totalRevenue'].astype('float')
        stockRevenuesYearlyDF['operatingIncome']=stockRevenuesYearlyDF['operatingIncome'].astype('float')
        stockRevenuesYearlyDF['ebitda']=stockRevenuesYearlyDF['ebitda'].astype('float')
    
        fig1=px.bar(stockRevenuesYearlyDF,x='year',y='totalRevenue')
        fig2=px.bar(stockRevenuesYearlyDF,x='year',y='grossProfit')
        fig3=px.bar(stockRevenuesYearlyDF,x='year',y='operatingIncome')
        fig4=px.bar(stockRevenuesYearlyDF,x='year',y='ebitda')
    
    else:
        fig1=go.Figure(layout=go.Layout(xaxis=dict(visible=False),
                                       yaxis=dict(visible=False)))
        fig1.add_annotation(text='No data found',x=0.5,y=0.5,xref='paper',yref='paper',showarrow=False)
        
        fig2=go.Figure(layout=go.Layout(xaxis=dict(visible=False),
                                       yaxis=dict(visible=False)))
        fig2.add_annotation(text='No data found',x=0.5,y=0.5,xref='paper',yref='paper',showarrow=False)
        
        fig3=go.Figure(layout=go.Layout(xaxis=dict(visible=False),
                                       yaxis=dict(visible=False)))
        fig3.add_annotation(text='No data found',x=0.5,y=0.5,xref='paper',yref='paper',showarrow=False)
        
        fig4=go.Figure(layout=go.Layout(xaxis=dict(visible=False),
                                       yaxis=dict(visible=False)))
        fig4.add_annotation(text='No data found',x=0.5,y=0.5,xref='paper',yref='paper',showarrow=False)
    
    dema26=requests.get(url_ema26).json()
    dema12=requests.get(url_ema12).json()
    rsi=requests.get(url_rsi).json()
    data=requests.get(url_stock).json()
    
    ema12DF=pd.DataFrame(dema12['Technical Analysis: EMA']).transpose()
    ema12DF.reset_index(inplace=True)
    ema12DF.rename(columns={'index':'datetime','EMA':'EMA12'},inplace=True)
    
    ema26DF=pd.DataFrame(dema26['Technical Analysis: EMA']).transpose()
    ema26DF.reset_index(inplace=True)
    ema26DF.rename(columns={'index':'datetime','EMA':'EMA26'},inplace=True)
    
    ema12DF['datetime']=pd.to_datetime(ema12DF['datetime'])
    ema26DF['datetime']=pd.to_datetime(ema26DF['datetime'])
    ema12DF['EMA12']=ema12DF['EMA12'].astype('float32')
    ema26DF['EMA26']=ema26DF['EMA26'].astype('float32')
    
    emaDF=pd.merge(ema12DF,ema26DF,on='datetime')
    
    rsiDF=pd.DataFrame(rsi['Technical Analysis: RSI']).transpose()
    rsiDF.reset_index(inplace=True)
    rsiDF.rename(columns={'index':'datetime'},inplace=True)
    
    rsiDF['datetime']=pd.to_datetime(rsiDF['datetime'])
    rsiDF['RSI']=rsiDF['RSI'].astype('float32')
    
    stockDF=pd.DataFrame(data['Time Series (Daily)']).transpose()
    stockDF.reset_index(inplace=True)
    stockDF.columns=['datetime','open','high','low','close','volume']
    
    stockDF['datetime']=pd.to_datetime(stockDF['datetime'])
    stockDF['year']=stockDF['datetime'].dt.year
    stockDF['open']=stockDF['open'].astype('float32')
    stockDF['high']=stockDF['high'].astype('float32')
    stockDF['low']=stockDF['low'].astype('float32')
    stockDF['close']=stockDF['close'].astype('float32')
    stockDF['volume']=stockDF['volume'].astype('int64')
    
    stockDF=pd.merge(stockDF,emaDF,on='datetime')
    stockDF=pd.merge(stockDF,rsiDF,on='datetime')
    stockDF=stockDF[stockDF['year']>2020]
    
    stockDF['macd']=stockDF['EMA12']-stockDF['EMA26']
    stockDF['fast']=stockDF['macd'].ewm(span=9,adjust=False,min_periods=9).mean()
    stockDF['diff']=stockDF['macd']-stockDF['fast']
    
    fig=make_subplots(rows=3,cols=1,subplot_titles=['Price movement','MACD','RSI'])

    fig.add_trace(go.Candlestick(x=stockDF['datetime'],open=stockDF['open'],
                             high=stockDF['high'],low=stockDF['low'],close=stockDF['close'],name=symbol),row=1,col=1)


    fig.add_trace(go.Scatter(x=stockDF['datetime'],y=stockDF['macd'],mode='lines',name='MACD line'),row=2,col=1)
    fig.add_trace(go.Scatter(x=stockDF['datetime'],y=stockDF['fast'],mode='lines',name='Signal line'),row=2,col=1)
    fig.add_trace(go.Bar(x=stockDF['datetime'],y=stockDF['diff']),row=2,col=1)
    
    fig.add_trace(go.Scatter(x=stockDF['datetime'],y=stockDF['RSI'],mode='lines'),row=3,col=1)

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=False)),
                      autosize=False,
                      width=1000,
                      height=1000,
                      showlegend=False)

    return fig,fig1,fig2,fig3,fig4
    
if __name__ == '__main__':
    app.run_server()





