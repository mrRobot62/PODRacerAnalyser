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


df = pd.read_csv("/Users/bernhardklein/Library/Mobile Documents/com~apple~CloudDocs/FPV/POD_Racer/PODRacerAnalyser/dash_exampels/basics/2018_eng.csv")

cols = df.columns[2:5].values.tolist() # "GDP per Capita" & "Social Support"
# plotly figure
server = Flask(__name__)


app = Dash(__name__, server=server, 
           use_pages=False,
            external_stylesheets=[dbc.themes.BOOTSTRAP,
            dbc.icons.BOOTSTRAP]
            )


fig = go.Figure()
for col in cols:
    figpx = px.scatter(df.assign(Plot=col),
                       x=col,
                       y="Score",
                       size="Population",
                       color="Continent",
                       hover_name="Country/Region",
                       hover_data=["Plot"],
                       size_max=60,
                       color_discrete_sequence=px.colors.qualitative.G10).update_traces(visible=False)
    
    fig.add_traces(figpx.data)

fig.update_layout(
    updatemenus=[
        {
            "buttons": 
            [
                {
                    "label": k,
                    "method": "update",
                    "args": 
                    [
                        {"visible": [t.customdata[0][0]==k for t in fig.data]},
                    ],
                }
                for k in cols
            ]
        }
    ]
).update_traces(visible=True, selector=lambda t: t.customdata[0][0]==cols[0] )


app.layout = html.Div([
    html.H1("Change graph by button"),
    dcc.Graph(id='graph', figure=fig),
])


if __name__ == "__main__":
    app.run_server(debug=False, dev_tools_ui=True, threaded=True)