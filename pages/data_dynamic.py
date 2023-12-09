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
from modules.serial_reader import *
from modules.graph_utils import *

template_theme1 = "flatly"
template_theme2 = "darkly"

dash.register_page(__name__, name="Live analysis", top_nav=True)

live_df = None


#------------------------------------------------------------------------------------------------------
# Design the app
layout = html.Div(
    [
        dcc.Store(id="memory"),
        # HEADERf
        livedata_header_row,
        # ----------------------------------------------------------------------
        # Alerts
        # ----------------------------------------------------------------------
        #alert_success, alert_info, alert_warn, alert_error,

        # ----------------------------------------------------------------------
        # side canvas open for configure the graph
        # ----------------------------------------------------------------------
       offcanvas, offcanvas2,

        # ----------------------------------------------------------------------
        # the interval mechanism to read contiously serial data
        # ----------------------------------------------------------------------
        dcc.Interval(
            id='live-interval-component',
            interval=1*250, # in milliseconds
            n_intervals=0,
            disabled=False
        ),
        dcc.Interval(
            id='live-interval-component2',
            interval=1000, # in milliseconds
            n_intervals=0,
            disabled=False
        ),
        # ----------------------------------------------------------------------
        # User input to configure the graphs
        # ----------------------------------------------------------------------
        modal_live_config,

        # ----------------------------------------------------------------------
        # upper graph   
        # ----------------------------------------------------------------------
        dbc.Row([
            dbc.Col(
                [
                    dbc.Button(children=[html.I(className="fa fa-area-chart")],
                                id="btn-backdrop-1", 
                                outline=False, size="sm", n_clicks=0),
                    dbc.Tooltip("configure below graph", 
                                target="btn-backdrop-1"),

                ],
            )
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="fig-live-main", clear_on_unhover=True))
            ], align="center"),

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
            dbc.Col(dcc.Graph(id="fig-live-sub1", clear_on_unhover=True))
            ], align="center"),
    
    ]

) 

    
#------------------------------------------------------------------------------------------------------
# call back graphs (general)
#------------------------------------------------------------------------------------------------------
@callback(
    Output(component_id='fig-live-main', component_property='figure'),      # update main graph
    Output(component_id='fig-live-sub1', component_property='figure'),      # update sub graph
    # main graph
    Input(component_id='sl-spline', component_property='value'),            # get curve smoothness slider
    Input(component_id='chk-hover-mode', component_property='value'),       # get checkbox
    Input(component_id='rb-xaxis-type', component_property='value'),        # get x-axis type
    Input(component_id='rb-yaxis-type', component_property='value'),        # get y-axis type
    Input(component_id='dd-task-filter', component_property='value'),       # get dropdwon task
    Input(component_id='dd-channels-filter', component_property='value'),   # get dropdown channels
    Input(component_id='dd-float-filter', component_property='value'),      # get dropdown 
    Input(component_id='dd-ldata-filter', component_property='value'),      # get dropdown 

    # subgraph
    Input(component_id='rb-xaxis2-type', component_property='value'),       
    Input(component_id='rb-yaxis2-type', component_property='value'),
    Input(component_id='dd-task2-filter', component_property='value'),
    Input(component_id='dd-channels2-filter', component_property='value'),
    Input(component_id='dd-float2-filter', component_property='value'),
    Input(component_id='dd-ldata2-filter', component_property='value'),

    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),                     # dark/light mode
    State('memory', 'data')                                                 # get store
)
def update_live_main(
    smoothing_value, hover_mode, xaxis_type, yaxis_type, 
    tasks, channels, floats, ldata, 
    xaxis2_type, yaxis2_type,tasks2, channels2, floats2, ldata2,
    toggle, memory):
    template = template_theme2 if toggle else template_theme1
    fig = go.FigureWidget()
    fig2 = go.FigureWidget()
    fig.update_layout(template = template)
    fig2.update_layout(template = template)

    if live_df is not None:
        fig = updateGraph(live_df,
            smoothing_value, hover_mode, xaxis_type, yaxis_type, tasks, 
            channels, floats, ldata, 
            toggle, "Live data - main")
        fig2 = updateGraph(live_df,
            smoothing_value, hover_mode, xaxis2_type, yaxis2_type, 
            tasks2, channels2, floats2, ldata2, 
            toggle, "Live data additional")  

    else:
        #print (f"(2) No dataframe available - no file selected")
        pass
    return fig, fig2

# ----------------------------------------------------------------------
#   Callback for graphs (in live scenario)
# ----------------------------------------------------------------------
# @callback(
#     Output(component_id="fig-live-main", component_property="figure", allow_duplicate=True),        # update upper graph
#     Output(component_id="fig-live-sub1", component_property="figure", allow_duplicate=True),        # update lower graph
#     #Output(component_id="sl-live-interval", component_property="value", allow_duplicate=True),   # set the slider value

#     Output(component_id="alert-warn", component_property="is_open", allow_duplicate=True),          # use alerts
#     Output(component_id="msg-alert-warn", component_property="children", allow_duplicate=True),
#     Output(component_id="alert-error", component_property="is_open", allow_duplicate=True),
#     Output(component_id="msg-alert-error", component_property="children", allow_duplicate=True),

#     Input(component_id="live-interval-component", component_property="n_intervals"),                # get interval vom dcc.Interval
#     State('memory', 'data'),                                                                        # read store
#     prevent_initial_call='initial_duplicate'
# )
# def live_stream_data(interval, memory):

#     warnOpen = errOpen = False
#     warnMsg = errMsg = None 
#     fig = go.FigureWidget()
#     fig2 = go.FigureWidget()
#     if memory is None:
#         return fig, fig2, warnOpen, warnMsg, errOpen, errMsg
# #        return warnOpen, warnMsg, errOpen, errMsg
#     if memory['runnable']:
# #        return warnOpen, warnMsg, errOpen, errMsg
#         return fig, fig2,warnOpen, warnMsg, errOpen, errMsg
#     else:
#         warnOpen=True
#         warnMsg = f"live streaming not possible. runnable is set to '{memory['runnable']}'. Check serial port"
# #    return warnOpen, warnMsg, errOpen, errMsg
#     return fig, fig2, warnOpen, warnMsg, errOpen, errMsg
   
#------------------------------------------------------------------------------------------------------
# call back for content of modal window
#------------------------------------------------------------------------------------------------------
@callback(
    Output("modal-live-config", "is_open"),
    Output("dd-serial-port", "options"),            # to write options (available serial prots)
    Output("btn-live-run", "disabled"),             # enable/disable run-botton
    Output("live-interval-component", "disabled"),  # enable/disable interval component 
    Output("memory", "data"),                       # set store
    Input("btn-live-config", "n_clicks"),           # get click from "open model windows" button
    Input("dd-serial-port", "value"),               # get value from dropdown serial ports
    Input("sl-live-interval", "value"),             # get value from intervall slider
    [State("modal-live-config", "is_open")],        # read store
)
def toggle_modal(n1, ddValue, slValue, is_open):
    data = {'interval':slValue, 'runnable': False, 'port':ddValue, 'run':None}
    ports = scanSerialPorts()
    options = [{'label': i, 'value': i} for i in ports]
    disabled = True if ddValue is None else False       
    data['run'] = not disabled
    if n1:
        return not is_open, options, disabled, disabled, data
    
    return is_open, options, disabled, disabled, data
    
#------------------------------------------------------------------------------------------------------
# callback loading-widget
#------------------------------------------------------------------------------------------------------
@callback(
    Output(component_id="loading-run-out", component_property="children"),
    Input(component_id="live-interval-component2", component_property="n_intervals"),
    State('memory', 'data'),                                                                        # read store
)
def system_running(click, memory):
    time.sleep(1.0)
    return ""

#------------------------------------------------------------------------------------------------------
# callback activate/deactivate live-interval-components
#------------------------------------------------------------------------------------------------------
@callback(
    Output(component_id="live-interval-component", component_property="disabled", allow_duplicate=True),
    Output(component_id="live-interval-component2", component_property="disabled", allow_duplicate=True),
    Input(component_id="btn-live-run", component_property="value"),
    State('memory', 'data'),
    prevent_initial_call='initial_duplicate'                                                                        # read store
)
def system_running(value, data):
    disable = True
    if data is not None:
        if data['port'] is not None:
            # Note: if button was clicked, the states are changed to STOP and run=False
            #       that means - system can run 
            disable = False if value == 'STOP' else True
    return disable, disable

#------------------------------------------------------------------------------------------------------
# callback run button
#------------------------------------------------------------------------------------------------------
@callback(
#     Output(component_id="live-interval-component", component_property="disabled", allow_duplicate=True),
    Output(component_id="live-interval-component2", component_property="disabled", allow_duplicate=True),
    Output(component_id="btn-live-run", component_property="children"),
    Output(component_id="btn-live-run", component_property="value"),
    Output(component_id="btn-live-run", component_property="style"),
    Output("memory", "data", allow_duplicate=True),                                                   # set store
    Input(component_id="btn-live-run", component_property="n_clicks"),
    State('memory', 'data'),    
    prevent_initial_call='initial_duplicate'
)
def run_clicked(clicks, data):
    color = 'green'
    if data is None:
        # only during intial load
        data = {}
        data['run'] = True
        data['port'] = None
        data['interval'] = None
        data['runnable'] = False
        color = 'GREEN'
        txt = 'RUN'
    elif data['run']:
        # change state of button
        color = 'RED'
        txt = 'STOP'
        data['run'] = not data['run']
    else:
        color = 'GREEN'
        txt = 'RUN'
        data['run'] = not data['run']

    style = {'background-color': color}
    return (not data['run']), txt, txt, style, data

    # if data is None:
    #     data = {}
    #     data['runnable'] = False
    #     data['interval'] = 0
    #     data['port'] = None
    #     txt = "RUN"
    # else:
    #     txt = 'RUN' if data['runnable'] else 'STOP'
    #     data['runnable'] = not data['runnable']
    #     if not data['runnable']:
    #         color = 'red'
    # style = {'background-color':color}
    # return txt, txt, style, data