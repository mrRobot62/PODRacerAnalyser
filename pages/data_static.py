# Import packages
import dash
from dash                   import Dash, html, dash_table, dcc, callback, Output, Input, ctx, State, no_update
from flask                  import Flask
import plotly.express       as px
import plotly.graph_objects as go
import io
import base64

import argparse
import dash_bootstrap_components as dbc
from modules.datasets import *
from modules.components import *
from pages.default_fig import default_fig
from dash_bootstrap_templates import ThemeSwitchAIO
from modules.dynamic_serial_reader import *
from modules.graph_utils import *

template_theme1 = 'flatly'
template_theme2 = 'darkly'

dash.register_page(__name__, name="File analysis", top_nav=True)

static_df = None

#------------------------------------------------------------------------------------------------------
# Design the app
layout = html.Div(
    [
        # HEADERf
        static_header_row,
        # ----------------------------------------------------------------------
        # Alerts
        # ----------------------------------------------------------------------
        alert_success, alert_info, alert_warn, alert_error,
        # ----------------------------------------------------------------------
        # side canvas open for configure the graph
        # ----------------------------------------------------------------------
        offcanvas,offcanvas2,
        # User input for main figure
        # ----------------------------------------------------------------------
        # upper graph   
        # ----------------------------------------------------------------------

        dbc.Row([
            dbc.Col([dbc.Button(children=[html.I(className="fa fa-area-chart")],
                                id="btn-backdrop-1", 
                                outline=False, size="sm", n_clicks=0),
                    dbc.Tooltip("configure below graph", target="btn-backdrop-1")
                    ],width=1),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="fig-static-main", clear_on_unhover=True))
            ], 
            align="center"
        ),
        
        # ----------------------------------------------------------------------
        html.Hr(),
        # ----------------------------------------------------------------------

        # ----------------------------------------------------------------------
        # lower graph   
        # ----------------------------------------------------------------------
        dbc.Row([
            dbc.Col([dbc.Button(children=[html.I(className="fa fa-area-chart")],
                                id="btn-backdrop-2", 
                                outline=False, size="sm", n_clicks=0),
                    dbc.Tooltip("configure below graph", target="btn-backdrop-2")
                    ],width=1),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="fig-static-sub1", clear_on_unhover=True))
            ], 
            align="center"
        ),
        # ----------------------------------------------------------------------
        # Tooltips for both graphs 
        # ----------------------------------------------------------------------
        tt_data_point, tt_data_point_sub,
    ]

)

@callback(
    Output(component_id='fig-static-main', component_property='figure'),
    Output(component_id='fig-static-sub1', component_property='figure'),
    Output(component_id="alert-warn", component_property="is_open"),
    Output(component_id="msg-alert-warn", component_property="children"),

    # main graph
    Input(component_id='sl-spline', component_property='value'),
    Input(component_id='chk-hover-mode', component_property='value'),
    Input(component_id='rb-xaxis-type', component_property='value'),
    Input(component_id='rb-yaxis-type', component_property='value'),
    Input(component_id='dd-task-filter', component_property='value'),
    Input(component_id='dd-channels-filter', component_property='value'),
    Input(component_id='dd-float-filter', component_property='value'),
    Input(component_id='dd-ldata-filter', component_property='value'),
    # subgraf
    Input(component_id='rb-xaxis2-type', component_property='value'),
    Input(component_id='rb-yaxis2-type', component_property='value'),
    Input(component_id='dd-task2-filter', component_property='value'),
    Input(component_id='dd-channels2-filter', component_property='value'),
    Input(component_id='dd-float2-filter', component_property='value'),
    Input(component_id='dd-ldata2-filter', component_property='value'),


    Input(ThemeSwitchAIO.ids.switch("theme"), "value") 
)
def update_static_main(
    smoothing_value, hover_mode, xaxis_type, yaxis_type, 
    tasks, channels, floats, ldata, 
    xaxis2_type, yaxis2_type,tasks2, channels2, floats2, ldata2,
    toggle):
    template = template_theme2 if toggle else template_theme1
    fig = go.FigureWidget()
    fig2 = go.FigureWidget()
    fig.update_layout(template = template)
    fig.update_traces(hoverinfo="none", hovertemplate=None)

    fig2.update_layout(template = template)

    if static_df is not None:
        fig = updateGraph(static_df,
            smoothing_value, hover_mode, xaxis_type, yaxis_type, 
            tasks, channels, floats, ldata, 
            toggle)
        fig2 = updateGraph(static_df,
            smoothing_value, hover_mode, xaxis2_type, yaxis2_type, 
            tasks2, channels2, floats2, ldata2, 
            toggle)

    else:
        return fig, fig2, True, "{}".format("No dataframe avaiable - no file selected")

    return fig, fig2, False, None


# ----------------------------------------------------------------------
# This callback is used from upload component. 
# if a file was uploaded, the callback function configure the current figure
# based on configuration from offcanvas
# ----------------------------------------------------------------------
@callback(
    Output(component_id='fig-static-main', component_property='figure', allow_duplicate=True),
    Output(component_id='fig-static-sub1', component_property='figure', allow_duplicate=True),
    Output(component_id='div-uploaded-file', component_property='children'),
    Output(component_id="alert-warn", component_property="is_open", allow_duplicate=True),
    Output(component_id="msg-alert-warn", component_property="children", allow_duplicate=True),
    Output(component_id="alert-error", component_property="is_open", allow_duplicate=True),
    Output(component_id="msg-alert-error", component_property="children", allow_duplicate=True),

    # main grapf
    Input(component_id='sl-spline', component_property='value'),
    Input(component_id='chk-hover-mode', component_property='value'),
    Input(component_id='rb-xaxis-type', component_property='value'),
    Input(component_id='rb-yaxis-type', component_property='value'),
    Input(component_id='dd-task-filter', component_property='value'),
    Input(component_id='dd-channels-filter', component_property='value'),
    Input(component_id='dd-float-filter', component_property='value'),
    Input(component_id='dd-ldata-filter', component_property='value'),

    # subgraph
    Input(component_id='rb-xaxis2-type', component_property='value'),
    Input(component_id='rb-yaxis2-type', component_property='value'),
    Input(component_id='dd-task2-filter', component_property='value'),
    Input(component_id='dd-channels2-filter', component_property='value'),
    Input(component_id='dd-float2-filter', component_property='value'),
    Input(component_id='dd-ldata2-filter', component_property='value'),

    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),

    # this inputs are from dcc.Upload
    Input(component_id='upload-data', component_property='contents'),
    State(component_id='upload-data', component_property='filename'),
    #State(component_id='upload-data', component_property='last_modified') ,

    prevent_initial_call=True
)
def handle_upload(
    smoothing_value, hover_mode, xaxis_type, yaxis_type, 
    tasks, channels, floats, ldata,
    xaxis2_type, yaxis2_type, tasks2, channels2, floats2, ldata2,
    toggle, content, fname
    ):

    global static_df
    is_open = False
    template = template_theme2 if toggle else template_theme1

    fig = go.FigureWidget()
    fig2 = go.FigureWidget()
    fig.update_layout(template = template)
    fig2.update_layout(template = template)

    if fname is None:
        return fig, fig2, None, True, "No dataset loaded", False, None
    
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in fname:
        #
        # please note, we work on a server, no physical file/folder is usable
        # so all data is stored in the component and we decode this binary data
        # and put them into a dataframe
        data = io.StringIO(decoded.decode('utf-8'))
        static_df = loadDataset(data)
    else:
        return fig, fig2, None, False, None, True, "{}".format('only CSV files allowed')
         
    if static_df is not None:
        fname = f"File: {fname}"
        fig = updateGraph(static_df,
            smoothing_value, hover_mode, xaxis_type, yaxis_type, 
            tasks, channels, floats, ldata, 
            toggle,fname)
        fig2 = updateGraph(static_df,
            smoothing_value, hover_mode, xaxis2_type, yaxis2_type, 
            tasks2, channels2, floats2, ldata2, 
            toggle,fname)        
    else:
        return fig, fig2, True, "No dataset loaded", False, None


    return fig, fig2, fname, False, None, False, None

