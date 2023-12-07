# Import packages
import dash
from dash                   import Dash, html, dash_table, dcc, callback, Output, Input, ctx, State
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
        # HEADERf
        livedata_header_row,
        offcanvas, offcanvas2,

        dcc.Interval(
            id='live-interval-component',
            interval=1*250, # in milliseconds
            n_intervals=0
        ),
        modal_live_config,
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
            dbc.Col(dcc.Graph(id="fig-live-main"))
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
            dbc.Col(dcc.Graph(id="fig-live-sub1"))
            ], align="center"),
        
        # ----------------------------------------------------------------------
        # Bottom-Row  
        # ----------------------------------------------------------------------
    ]

)

""" 
def _configGraph(df, fig, dataPoint, group, sv):
    ydata = f"df.{dataPoint}"
    vMax = max(eval(ydata))
    legend = f"{dataPoint}_{str(group)}"
    fig.add_scatter(name=legend, x=df.TIME, y=eval(ydata), line_shape='spline', line={'smoothing':sv})        
    return vMax


def _updateGraph(
        smoothing_value, hover_mode, xaxis_type, yaxis_type, tasks, 
        channels, floats, ldata,
        toggle, title=""):
    fig = None
    ## graphs
    df = live_df
    df_filt_tasks = None
    df_t = []
    fig = go.FigureWidget()

    if len(tasks) == 0:
        return fig
    
    # for every task we need a separate grouped dataset
    for idx, t in enumerate(tasks):
        df_t.append(df.loc[df.index.get_level_values('GROUPING') == tasks[idx]])
        df_filt_tasks = pd.concat([df_filt_tasks, df_t[idx]],axis=0)

    #
    # build now für every task / every channel a separate scatter-plot
    ymax = []
    for ic, c in enumerate(channels):
        for ig, g in enumerate(df_filt_tasks.index.get_level_values('GROUPING').unique()):
            # building a access to the yaxis value for later evaluation
            # Note: the time basis (xaxis is allways the same)
            #ydata = f"df_t[{ig}].{c}"
            #ymax.append(eval(ydata).max())
            #legend = f"{c}_{str(g)}"
            #fig.add_scatter(name=legend, x=df_t[ig].TIME, y=eval(ydata), line_shape='spline', line={'smoothing':smoothing_value})        
            ymax.append(_configGraph(df_t[ig], fig, c, g, smoothing_value))

    for ic, c in enumerate(floats):
        for ig, g in enumerate(df_filt_tasks.index.get_level_values('GROUPING').unique()):
            ymax.append(_configGraph(df_t[ig], fig, c.lower(), g, smoothing_value))
            
    for ic, c in enumerate(ldata):
        for ig, g in enumerate(df_filt_tasks.index.get_level_values('GROUPING').unique()):
            ymax.append(_configGraph(df_t[ig], fig, c.lower(), g, smoothing_value))
            

    #
    #
    template = template_theme1 if toggle else template_theme2
    fig.update_xaxes(title="milliseconds", type='linear' if xaxis_type == 'Linear' else 'log')
    fig.update_yaxes(title="measurement", type='linear' if yaxis_type == 'Linear' else 'log')
    fig.update_layout(
        #title="Main graph",
        #xaxis_tickformat='ms',
        template=template,
        xaxis=dict(
            dtick=500,
            rangeslider=dict(
                visible=True
            )
        ),
        yaxis=dict(
            dtick = (sum(ymax) / len(ymax)) * 0.25             # 25% form max value
        ),
    )
    if title != "":
        fig.update_layout(
            title=title,
            title_x=0
        )
    if len(hover_mode) > 0:
        fig.update_traces(mode="markers+lines", hovertemplate=None)
        fig.update_layout(
            hovermode="x unified"
        )

    return fig

 """
 
@callback(
    Output(component_id='fig-live-main', component_property='figure'),
    Output(component_id='fig-live-sub1', component_property='figure'),
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
def update_live_main(
    smoothing_value, hover_mode, xaxis_type, yaxis_type, 
    tasks, channels, floats, ldata, 
    xaxis2_type, yaxis2_type,tasks2, channels2, floats2, ldata2,
    toggle):
    template = template_theme2 if toggle else template_theme1
    fig = go.FigureWidget()
    fig2 = go.FigureWidget()
    fig.update_layout(template = template)
    fig2.update_layout(template = template)

    if live_df is not None:
        fig = updateGraph(live_df,
            smoothing_value, hover_mode, xaxis_type, yaxis_type, tasks, 
            channels, floats, ldata, 
            toggle)
        fig2 = updateGraph(live_df,
            smoothing_value, hover_mode, xaxis2_type, yaxis2_type, 
            tasks2, channels2, floats2, ldata2, 
            toggle,fname)  

    else:
        print (f"(2) No dataframe available - no file selected")
    return fig

# ----------------------------------------------------------------------
#   Callback for modal window (serial configuration)
# ----------------------------------------------------------------------
@callback(
    Output("modal-live-config", "is_open"),
    Output("dd-serial-port", "options"),
    Input("btn-live-config", "n_clicks"),
    [State("modal-live-config", "is_open")],
)
def toggle_modal(n1, is_open):
    if n1:
        ports = scanSerialPorts()
        options = [{'label': i, 'value': i} for i in ports]
        return not is_open, options
    return is_open, []
