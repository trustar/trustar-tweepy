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



data = pd.read_csv(get_root_path(__name__) + "/running_avgs.csv")
options = [{"label": entity, "value": entity} for entity in data.groupby(['flagged']).sum().reset_index()[data.groupby(['flagged']).sum().reset_index()['frequency']>=50].flagged.values]

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
# Tabs
###########################################

# Tab One --- Malware Top 10

tab_one = html.Div(className = 'row', children = [

	# Graph
	html.Div([
		dcc.Graph(id="malware-graph1")
		],
		style={
			'marginRight': 20,
			'marginLeft': 20,
			'marginBottom': 10,
			'width': '79%',
			'display': 'inline-block',
			}
	),

	# Slider
	html.Div([
		dcc.RangeSlider(id="selected-range",
    		min=0,
    		max=len(slider_days)-1,
			value=[3,7],
			pushable=1,
    		marks={ i: {'label': f'{slider_days[i]}'} for i in range(0,len(slider_days))},
    		)
    		],
            style={
            	'marginBottom': 50,
            	"width": "90%", 
            	'display': 'inline-block',
            	'marginLeft': 20,
				'marginRight': 20,
            	}
    ),

], style={
			'backgroundColor':'white',
			'textAlign': 'center'})

# Tab Two --- Malware Line Plot
        
tab_two = html.Div(className = 'row', children = [
				
	# Graph
	html.Div([
		dcc.Graph(id="malware-graph2")
		],
		style={
			'marginLeft': 10,
			'marginTop': 30,
			'marginBottom': 20,
			'width': '70%',
			'display': 'inline-block',
			'vertical-align': 'middle',
			'float': 'left'
			}
	),


	# Dropdown
	html.Div([
   		dcc.Dropdown(id="selected-value",
            options=options,
            multi=True,
            value= ["Ryuk"],
            placeholder="Select an entity",
            clearable=False)
            ],
            style={
            	'marginLeft': 10,
            	'marginTop': 30,
            	'marginBottom': 20,
            	"width": "25%", 
            	'display': 'inline-block',
            	}
    ),
    
    # Text box
	html.Div([
            dcc.Markdown(dedent("""Click on data points in the graph.""")),
            html.Pre(id='click-data',style=styles['pre']),
            html.Div(id='click-data2')
        ])
   
	],
	style={
            	'marginLeft': 20,
            	'marginTop': 10,
            	'marginBottom': 20,
            	}
    )
    

###########################################
# Dashboard Layout
###########################################

layout = html.Div([
           	
	# Tabs
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Top Malware Detections per Day', value='tab-1', children=[tab_one]),
        dcc.Tab(label='Malware Timeline', value='tab-2', children=[tab_two])
    ]),
    html.Div(id='tabs-content')
])
