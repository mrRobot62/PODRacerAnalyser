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
            dbc.Col(dcc.Graph(id="fig-static-main"))
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
            dbc.Col(dcc.Graph(id="fig-static-sub1"))
            ], 
            align="center"
        ),
        
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
    df = static_df
    df_filt_tasks = None
    df_t = []

    template = template_theme2 if toggle else template_theme1
    fig = go.FigureWidget()
    fig.update_layout(
        template = template
    )
    
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
    Output(component_id='fig-static-main', component_property='figure'),
    Output(component_id='fig-static-sub1', component_property='figure'),
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
        print (f"(2) No dataframe available - no file selected")
    return fig, fig2


# ----------------------------------------------------------------------
# This callback is used from upload component. 
# if a file was uploaded, the callback function configure the current figure
# based on configuration from offcanvas
# ----------------------------------------------------------------------
@callback(
    Output(component_id='fig-static-main', component_property='figure', allow_duplicate=True),
    Output(component_id='fig-static-sub1', component_property='figure', allow_duplicate=True),
    Output(component_id='div-uploaded-file', component_property='children'),

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

    template = template_theme2 if toggle else template_theme1

    fig = go.FigureWidget()
    fig2 = go.FigureWidget()
    fig.update_layout(template = template)
    fig2.update_layout(template = template)

    if fname is None:
        return fig, fig2
    
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in fname:
        #
        # please note, we work on a server, no physical file/folder is usable
        # so all data is stored in the component and we decode this binary data
        # and put them into a dataframe
        data = io.StringIO(decoded.decode('utf-8'))
        static_df = loadDataset(data)

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
        print (f"(1) No dataframe available - no file selected")

    #return fig
    return fig, fig2, fname

