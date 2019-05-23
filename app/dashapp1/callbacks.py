###########################################
# Libraries
###########################################

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_dangerously_set_inner_html
from textwrap import dedent
import json

from pandas_datareader import data as web
from datetime import datetime, date, timedelta
import humanize

import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import tweepy
import jsonpickle
import requests

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

from flask.helpers import get_root_path


###########################################
# Load data
###########################################

all_tweets = pd.read_csv(get_root_path(__name__) + "/Collect/tweets.csv")
all_tweets['created'] = all_tweets['created'].apply(lambda date: str(date)[0:10])

data = pd.read_csv(get_root_path(__name__) + "/running_avgs.csv")

def everyweek(stop):
    stop = stop.split("-")
    stop = date(int(stop[0]),int(stop[1]),int(stop[2]))
    d = date(2018, 12, 31)                    # January 1st
    d += timedelta(days = 7 - d.weekday())  # First Sunday
    flag = True 
    while d < stop:
        if flag:
            yield str(d)
            d += timedelta(days = 7)
            flag = True # Right now it's doing every week. Switch to False for every two weeks.
        else:
            flag = True
            d += timedelta(days = 7)
            
def humanize_string(str_date):
    str_date = str_date.split("-")
    str_date = date(int(str_date[0]),int(str_date[1]),int(str_date[2]))
    str_date = humanize.naturaldate(str_date)
    return str_date
        
slider_days = ['2018-12-28'] +[d for d in everyweek(data.date.unique()[-1])] + [data.date.unique()[-1]]

colors = {
   'background': '#f7fcfe',
   'title': '#0f0e6e',
   'text': '#061022'
}

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'hidden',
        'overflowY': 'auto',
        'wordBreak': 'break-word',
    }
}


###########################################
# Call backs
###########################################

def register_callbacks(app):

    # Tab 1 -- Malware Bar Plot

    @app.callback(
        Output('malware-graph1', 'figure'),
        [Input('selected-range', 'value')]) 
    def update_figure(selected):

        min_date = slider_days[selected[0]]
        max_date = slider_days[selected[1]]

        new_data = data[data['date']>=min_date]
        new_data = new_data[new_data['date']<=max_date]

        new_data = new_data.groupby(by=['flagged']).agg({'frequency':'sum', 'running_avg':'mean'}).sort_values(by=['frequency'], ascending=False).reset_index().head(25)

        new_data_malware = new_data[new_data['running_avg']>=0.5]
        new_data_entity = new_data[new_data['running_avg']<0.5][0:5]

        figure={
               'data': [{	'x': new_data_malware.flagged.values,
                            'y': new_data_malware.frequency.values,
                            'type': 'bar',
                            'name': 'Malware  ',
                            'text': [f"{detection:.1%} likelihood<br>{number} tweets" for (detection,number) in zip(new_data_malware.running_avg.values,new_data_malware.frequency.values)],
                            'hoverinfo':'text',
                            'marker':{
                                'color': new_data_malware.running_avg.values,
                                'colorscale': 'Bluered',
                                'showscale': True,
                                'colorbar': {
                                'thickness': 10,
                                'tickvals': [0,0.5,1],
                                'ticktext': ['Not malware','Undecided','Malware'],
                                'tickfont': {'size': 12}
                            },
                            'cmin': 0, 'cmax':1
                        }},
                        {	'x': new_data_entity.flagged.values,
                            'y': new_data_entity.frequency.values,
                            'type': 'bar',
                            'name': 'Entity',
                            'text': [f"{detection:.1%} likelihood<br>{number} tweets" for (detection,number) in zip(new_data_entity.running_avg.values,new_data_entity.frequency.values)],
                            'hoverinfo':'text',
                            'marker':{
                                'color': new_data_entity.running_avg.values,
                                'colorscale': 'Bluered',
                                'showscale': True,
                                'colorbar': {
                                'thickness': 10,
                                'tickvals': [0,0.5,1],
                                'ticktext': ['Not malware','Undecided','Malware'],
                                'tickfont': {'size': 12}
                            },
                            'cmin': 0, 'cmax':1
                        }}],
                'layout': go.Layout(
                    title=f"Entity Detection on Twitter<br>From {humanize_string(min_date)} to {humanize_string(max_date)}<br> <br>",
                    xaxis={'title': '','tickangle':20},
                    yaxis={'title': f'Number of tweets<br>'},
                    margin={'l': 50, 'b': 50, 't': 50, 'r': 50},
                    legend={'x': 1.2, 'y': 1, 'bgcolor': '#f7fcfe', 'bordercolor': "#C7CBCD", 'borderwidth':1, 'uirevision':True},
                    hovermode='closest')
               }

        return figure


    # Tab 2 -- Malware Line Plot

    @app.callback(
        Output('malware-graph2', 'figure'),
        [Input('selected-value', 'value')]) 
    def update_figure(selected):

        trace = []
        ms = " - ".join(selected)

        for malware in selected:
            df_mw = data[data['flagged']==malware]
            x = df_mw.date.values
            y = df_mw.frequency.values
            c = df_mw.running_avg
            t = [f"{malware}<br>{detection:.1%} likelihood<br>{frequency} tweets<br>{date}" for date,detection,frequency in zip(df_mw.date.values,df_mw.running_avg,df_mw.frequency.values)]

            trace.append(
            go.Scatter(
                        x=x,
                        y=y,
                        text=t,
                        mode='lines+markers',
                        name=malware,
                        opacity=0.8,
                        marker={
                            'size': 10,
                            'color': c,
                            'colorscale': 'Bluered',
                            'showscale': True,
                            'colorbar': {
                            'thickness': 10,
                            'tickvals': [0,0.5,1],
                            'ticktext': ['Not malware','Undecided','Malware'],
                            'tickfont': {'size': 8}
                            },
                            'cmin': 0, 'cmax':1
                        },
                        hoverinfo='text',
                        line={
                            'color': '#E5E7E9'}
                    ) 
                )

        figure = {
                    'data': trace,
                    'layout': go.Layout(
                    clickmode= 'event+select',
                    title=f"{ms} Detection on Twitter",
                    xaxis={'title': 'Day'},
                    yaxis={'title': f'Number of tweets'},
                    margin={'l': 50, 'b': 50, 't': 50, 'r': 50},
                    legend={'x': -.1, 'y': -.2, 'orientation':'h'},
                    hovermode='closest',
                )
            }

        return figure

    @app.callback(
        Output('click-data', 'children'),
        [Input('malware-graph2', 'clickData')])
    def display_click_data(clickData):
        if len(json.dumps(clickData))<=5:
            return None
        js = str(json.dumps(clickData))
        js = json.loads(js)
        malware = js['points'][0]['text'].split("<br>")[0]
        return info(malware)

    @app.callback(
        Output('click-data2', 'children'),
        [Input('malware-graph2', 'clickData')])
    def display_click_data(clickData):
        if len(json.dumps(clickData))<=5:
            return None
        js = str(json.dumps(clickData))
        js = json.loads(js)
        malware = js['points'][0]['text'].split("<br>")[0]
        dat = js['points'][0]['x']
        return get_tweet(malware, dat)

    def info(malware):
        label = "not malware"
        lab = data[data['flagged']==malware].running_avg.values[-1]
        if lab >= 0.5: 
            label = "malware"
        return f"{malware}\n"+\
               f"First detected: {data[data['flagged']==malware].date.min()}\n"+\
               f"Total detections: {data[data['flagged']==malware].frequency.sum()} tweets\n"+\
               f"Current state: {label} ({lab:.1%}).\n"

    def get_tweet(malware, date):
        print(malware,date)
        df = all_tweets[all_tweets['created']==date]
        for tweet in df.text.dropna().values:
            if malware in tweet:
                return f"Example tweet from {date}: " + tweet

