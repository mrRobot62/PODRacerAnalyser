import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash                   import Dash, html, dash_table, dcc, callback, Output, Input, ctx, State
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash import jupyter_dash
from flask                  import Flask
import dash_bootstrap_components as dbc

from collections import deque
import io
import tailer

from modules.csv_columns import *

# code and plot setup
# settings
pd.options.plotting.backend = "plotly"
countdown = 20
#global df

# sample dataframe of a wide format
#np.random.seed(4); cols = list('abc')
#X = np.random.randn(50,len(cols))  
#df=pd.DataFrame(X, columns=cols)
#df.iloc[0]=0;

df=pd.DataFrame(columns=columns)

# plotly figure
server = Flask(__name__)


app = Dash(__name__, server=server, 
           use_pages=False,
            external_stylesheets=[dbc.themes.BOOTSTRAP,
            dbc.icons.BOOTSTRAP]
            )


app.layout = html.Div([
    html.H1("Streaming of random data"),
            dcc.Interval(
            id='interval-component',
            interval=1*200, # in milliseconds
            n_intervals=0
        ),
    dcc.Graph(id='graph'),
])

# Define callback to update graph
@app.callback(
    Output('graph', 'figure'),
    [Input('interval-component', "n_intervals")]
)
def streamFig(value):
    
    global df
    fname = "livedata.csv"
    #
    # read only last 1000 rows from CSV and load them into dataframe
    with open (fname, 'r') as f:
        q = deque(f, 150)
    
    df2 = pd.read_csv(io.StringIO(''.join(q)),header=None)
    df2.columns=columns
    df = pd.concat([df, df2])
    df3 = df[['float0','float1']].tail(150)

#    last_row = last_lines[1].split(',')
#    df2 = pd.read_csv(io.StringIO('\n'.join(last_lines)), usecols=columns, on_bad_lines='skip' )
#    df.loc[len(df)] = last_row
#    df3=df[['CH_H','float0']]

    # read complete CSV as larger as inperformante
    #df2 = pd.read_csv(fname)
    #df3=df2[['float0','long0']]
    #df3 = df3.tail(150)


    fig = df3.plot(template = 'plotly_dark')
    
    #fig.show()
    
    colors = px.colors.qualitative.Plotly
    for i, col in enumerate(df3.columns):
            fig.add_annotation(x=df3.index[-1], y=df3[col].iloc[-1],
                                   text = str(df3[col].iloc[-1])[:4],
                                   align="right",
                                   arrowcolor = 'rgba(0,0,0,0)',
                                   ax=25,
                                   ay=0,
                                   yanchor = 'middle',
                                   font = dict(color = colors[i]))
    
    return(fig)


if __name__ == "__main__":
    app.run_server(debug=False, dev_tools_ui=True, threaded=True)