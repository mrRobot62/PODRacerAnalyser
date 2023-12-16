from dash                   import Dash, html, dash_table, dcc, callback, Output, Input, ctx, State
from flask                  import Flask
from modules.datasets       import *
from dash.development.base_component import Component

import dash_bootstrap_components    as dbc
import pandas                       as pd
import plotly.express               as px
import plotly.graph_objects         as go
import copy

def _hasID(comp:Component) -> bool:
    return hasattr(comp,'id')

def _hasChildren(comp:Component) -> bool:
    return hasattr(comp,'children')

def _equalID(comp:Component, id:str, level:int=0) -> bool:
    if _hasID(comp):
        if comp.id == id:
            print (f"[{'+'*level}] component found")
            return True
    return False

#------------------------------------------------------------------------------------------------------
# Build the components
#
# This file contain all components which are used in the application
#------------------------------------------------------------------------------------------------------

# -------- Button on home page -----------
btn_static_data = dbc.Button(
    "Statical analysis", id="btn-static-data", n_clicks=0, outline=True, color="info", disabled=False, size="lg"
)
btn_dynamic_data = dbc.Button(
    "Dynamical analysis", id="btn-dynamic-data", n_clicks=0, outline=True, color="info", disabled=False, size="lg"
)
btn_grid_data = dbc.Button(
    "Show grid data", id="btn-grid-data", n_clicks=0, outline=True, color="danger", disabled=False, size="lg"
)

btn_live_config = dbc.Button(
    "Live configuration", id="btn-live-config", n_clicks=0, outline=True, color="primary", disabled=False, size="lg"
)

btn_live_run = dbc.Button(
    "RUN", id="btn-live-run", n_clicks=0, outline=False, color="success", disabled=False, size="lg"
)

btn_live_stop = dbc.Button(
    "STOP", id="btn-live-stop", n_clicks=0, outline=False, color="warn", disabled=False, size="lg"
)

load_serial_running = dcc.Loading(
    id="ld-serial-running", type="default", children=html.Div(id="running-1")
)

""" define upload component """
upload_component = dcc.Upload(

    id="upload-data",
    children=html.Div([
        html.A("Drag & Drop", style={'color':'red'}),
        " log file or ",
        html.A("Select a file", style={'color':'red'})
    ]),
    style={
        'width'         :'100%',
        'height'        : "35px",
        'lineHeigh'     : "35px",
        'borderWidth'   : "1px",
        'borderStyle'   : 'dashed',
        'borderRadius'  : '5px',
        'textAlign'     : 'center',
        'margin'        : '5px'
    },
    multiple=False
)


""" header row for static page """
static_header_row = dbc.Row(
    [
        dbc.Col(html.H2("Logfile analysis", style={'color':'darkcyan'}), width=6),
        dbc.Col(upload_component, width=4),
        dbc.Col(html.Div(children="", id="div-uploaded-file", style={'borderTopWidth':'10px' }), width=2)
    ]
)

""" header row for live-page """
livedata_header_row = dbc.Row(
    [
        dbc.Col(html.H2("Live data analysis", style={'color':'darkcyan'}), width=5),
        dbc.Col(btn_live_config, width=3),
        dbc.Col(btn_live_run,width=2),
        #dbc.Col(btn_live_stop,width=1),
        #dbc.Col(load_serial_running, width=2),
        dbc.Col([dcc.Loading(id="loading-run",type="default",children=html.Div(id="loading-run-out")),load_serial_running], width=2),
    ]   
)


#------------------------------------------------------------------------------------------------------
# Modal pop up windows 
#------------------------------------------------------------------------------------------------------
""" modal pop up window if live-button was clicked """

dd_serial_port = dcc.Dropdown(
            options=[],
            multi=False, placeholder="Select serial port",
            id="dd-serial-port", 
            
        )

sl_live_interval = dcc.Slider(
    min=100, max=500, step= 50, value=250, id="sl-live-interval"
)

btn_serial_test = dbc.Button(
    "Test", id="btn-serial-test", n_clicks=0, outline=True, color="info", disabled=False
)

live_config_layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dd_serial_port
                ),
                dbc.Col(
                    btn_serial_test
                )    
            ]
        ),
        html.Hr(),
        dbc.Row( 
            [
                dbc.Label("Update interval in ms"),
                sl_live_interval
            ]
        )
    ]
)


modal_live_config = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("LIVE DATA configuration")),
        dbc.ModalBody(
            live_config_layout
        ),
    ],
    id="modal-live-config",
    size="lg",
    is_open=False,
    backdrop=False
)

modal_log_data = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle('Log data terminal')),
        dbc.ModalBody(
            html.P(children=[], id='modal-content-data'),
        ),
        dbc.ModalBody(
            dbc.Button(
                "Close",
                id="btn-log-data-close",
                className="ms-auto",
                n_clicks=0,
            )            
        )
    ],
    id='modal-log-data',
    size='lg', scrollable=True,
    is_open=False,
    backdrop=False
)

#------------------------------------------------------------------------------------------------------
# ?
#------------------------------------------------------------------------------------------------------


message_content = html.P(
    [
        html.P(html.P([html.I(className="bi bi-x-octagon-fill me-2"), html.P(id="message-err", style={'color': 'red'})])),
        html.P(html.P([html.I(className="bi bi-exclamation-triangle-fill me-2"), html.P(id="message-warn", style={'color': 'orange'})])),
        html.P(html.P([html.I(className="bi bi-info-circle-fill me-2"), html.P(id="message-info", style={'color': 'white'})])),
        html.P(html.P([html.I(className="bi bi-check-circle-fill me-2"), html.P(id="message-success", style={'color': 'green'})])),
    ],
    id="message-content"
)
#------------------------------------------------------------------------------------------------------
# Alerts
#------------------------------------------------------------------------------------------------------

alert_success = dbc.Alert(
    [
        html.P("",id="msg-alert-success"),
    ],
    id="alert-success",
    color="success",
    is_open=False,
    dismissable=True
)

alert_info = dbc.Alert(
    [
        html.P(id="msg-alert-info"),
    ],
    id="alert-info",
    color="primary",
    duration=1000,
    is_open=False
)

alert_warn = dbc.Alert(
    [
        html.P("",id="msg-alert-warn"),
    ],
    id="alert-warn",
    color="warning",
    is_open=False,
    dismissable=True
)

alert_error = dbc.Alert(
    [
        html.P(id="msg-alert-error"),
    ],
    id="alert-error",
    color="danger",
    is_open=False,
    dismissable=True
) 

#------------------------------------------------------------------------------------------------------
# RadioItems components
#------------------------------------------------------------------------------------------------------
""" xaxis data publishing as linear or logirthm """
rb_xaxis_type = dcc.RadioItems(
    ["Linear", "Log"],
    "Linear",
    id="rb-xaxis-type",
    labelStyle={'display': 'inline-block', 'marginTop': '3px'}
)
rb_xaxis2_type = copy.deepcopy(rb_xaxis_type)
rb_xaxis2_type.id="rb-xaxis2-type"

""" yaxis data publishing as linear or logirthm """
rb_yaxis_type = dcc.RadioItems(
    ["Linear", "Log"],
    "Linear",
    id="rb-yaxis-type",
    labelStyle={'display': 'inline-block', 'marginTop': '3px'}
)
rb_yaxis2_type = copy.deepcopy(rb_yaxis_type)
rb_yaxis2_type.id="rb-yaxis2-type"

#------------------------------------------ ------------------------------------------------------------
# Labels components
#------------------------------------------------------------------------------------------------------
rb_xaxis_type_comp = dbc.Row(
    [
        dbc.Label("XAxis-Type"), rb_xaxis_type
    ]
)
rb_xaxis2_type_comp = dbc.Row(
    [
        dbc.Label("XAxis-Type"), rb_xaxis2_type
    ]
)

rb_yaxis_type_comp = dbc.Row(
    [
        dbc.Label("YAxis-Type"), rb_yaxis_type
    ]
)
rb_yaxis2_type_comp = dbc.Row(
    [
        dbc.Label("YAxis-Type"), rb_yaxis2_type
    ]
)

#------------------------------------------------------------------------------------------------------
# Dropdown components 
#------------------------------------------------------------------------------------------------------
dd_tasks = dcc.Dropdown(
            ["MIXER", "HOVER_UPD", "RECV_RD","RECV_WR", "SDIST_UPD", "OFLOW_UPD", "STEERING_UPD"],
            [],     # insert defaults if you like
            multi=True, placeholder="Select tasks",
            id="dd-task-filter", 
            
        )
dd_tasks2 = copy.deepcopy(dd_tasks)
dd_tasks2.id = "dd-task2-filter"

dd_channels = dcc.Dropdown(
    {
        'CH_R':'ROLL',
        'CH_P':'PITCH',
        'CH_Y':'YAW',
        'CH_H':'HOVER',
        'CH_T':'THRUST',
        'AUX2':'AUX2',
        'AUX3':'AUX3',
     
    },
    ["CH_H"],
    multi=True, placeholder="Select channels",
    id="dd-channels-filter"
)
dd_channels2 = copy.deepcopy(dd_channels)
dd_channels2.id = "dd-channels2-filter"

dd_pids = dcc.Dropdown(
    {"PID_R":"ROLL", "PID_P":"PITCH", "PID_Y":"YAW","PID_H":"HOVER"},
    [], # insert defaults if you like
    multi=True, placeholder="Select PID channels",
    id="dd-pid-filter"
)
dd_pids2 = copy.deepcopy(dd_pids)
dd_pids2.id = "dd-pid2-filter"


dd_floats = dcc.Dropdown(
            ["FLOAT0", "FLOAT1", "FLOAT2","FLOAT3","FLOAT4","FLOAT5","FLOAT6","FLOAT7"],
            [], # insert defaults if you like
            multi=True, placeholder="Float values",
            id="dd-float-filter"
        )
dd_floats2 = copy.deepcopy(dd_floats)
dd_floats2.id = "dd-float2-filter"

dd_longs = dcc.Dropdown(
            ["LONG0", "LONG1", "LONG2","LONG3","LONG4","LONG5","LONG6","LONG7"],
            [], # insert defaults if you like
            multi=True, placeholder="Long values",
            id="dd-ldata-filter"
        )
dd_longs2 = copy.deepcopy(dd_longs)
dd_longs2.id = "dd-ldata2-filter"

# dd_graph_select = dcc.Dropdown(
#     options=[
#         {'label':'Main-Graph', 'value':'fig-main'},
#         {'label':'Sub-Graph', 'value':'fig-graph2'},
#     ],
#     value = "fig-main",
#     id="dd-graph-select"
# )

#------------------------------------------------------------------------------------------------------
# Checkboxes components
#------------------------------------------------------------------------------------------------------

chk_hover_mode = dcc.Checklist(
    options=[
        {'label':'Enable HoverMode', 'value':'hovermode'}
    ],
    id="chk-hover-mode",
    value=[]
)
chk_hover_mode2 = copy.deepcopy(chk_hover_mode)
chk_hover_mode2.id = "chk-hover2-mode"

# chk_enable_live = dcc.Checklist(
#     options=[
#         {'label':'Live-Mode', 'value':True}
#     ],
#     id="chk-live-mode",
#     value=[]
# )

#------------------------------------------------------------------------------------------------------
# Slider componentes
#------------------------------------------------------------------------------------------------------

rs_time = dcc.RangeSlider(
            idx_time_min, idx_time_max, 500, id="rs-time", marks=None
        )

sl_spline = dcc.Slider(
    min=0.0, max=0.75, step=(0.75/10),value=0.375, id="sl-spline"
)

#------------------------------------------------------------------------------------------------------
# offcanvas components
#------------------------------------------------------------------------------------------------------
# open on the left side - this canva is used twice - for upper graph and lower graph  
offcanvas = dbc.Offcanvas(
    [
        dbc.Row(
            html.H5("Configure MainGraph")
        ),
        html.Hr(),        dbc.Row([
            dbc.Col([chk_hover_mode]),
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col([rb_xaxis_type_comp]), 
            dbc.Col([rb_yaxis_type_comp])]
        ),
        html.Hr(),
        dbc.Row(dbc.Col(["Smooting",sl_spline])),
        html.Hr(),
        dbc.Row([dbc.Label("Choose tasks"), dbc.Col(dd_tasks)]),
        dbc.Row([dbc.Label("Choose channels"), dbc.Col(dd_channels)]),
        dbc.Row([dbc.Label("Choose PIDs"), dbc.Col(dd_pids)]),
        dbc.Row([dbc.Label("Choose floats"), dbc.Col(dd_floats)]),
        dbc.Row([dbc.Label("Choose longs"), dbc.Col(dd_longs)])
    ],
    id="offcanvas-graph-content",
    scrollable=True,
    is_open=False
)

#
# used bei fig-graph2
offcanvas2 = dbc.Offcanvas(
    [
        dbc.Row(
            html.H5("Configure SubGraph")
        ),
        html.Hr(),
        dbc.Row([
            dbc.Col([chk_hover_mode2]),
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col([rb_xaxis2_type_comp]), 
            dbc.Col([rb_yaxis2_type_comp])]
        ),
        html.Hr(),
        dbc.Row(dbc.Col(["Smooting",sl_spline])),
        html.Hr(),
        dbc.Row([dbc.Label("Choose tasks"), dbc.Col(dd_tasks2)]),
        dbc.Row([dbc.Label("Choose channels"), dbc.Col(dd_channels2)]),
        dbc.Row([dbc.Label("Choose PIDs"), dbc.Col(dd_pids2)]),
        dbc.Row([dbc.Label("Choose floats"), dbc.Col(dd_floats2)]),
        dbc.Row([dbc.Label("Choose longs"), dbc.Col(dd_longs2)])
    ],
    id="offcanvas-graph2-content",
    scrollable=True,
    is_open=False
)

#------------------------------------------------------------------------------------------------------
# Graph-Tooltip
#------------------------------------------------------------------------------------------------------
tt_data_point = dcc.Tooltip(
    id="tt-data-point"
)

tt_data_point_sub = dcc.Tooltip(
    id="tt-data-point-sub"
)

#------------------------------------------------------------------------------------------------------
# Create marker lines
#------------------------------------------------------------------------------------------------------
def setMarkerLine(x0, y0, x1, y1, line, color="red", width=1, dash='solid'):
    #     marker = {'x0':x0, 'y0':y0, 'x1':x1, 'y1':y1, 'color':color, 'marker':marker, 'dir':0|1}
    marker = {}
    _dir = 1
    if x0 != x1:    # horizontal line
        y1 = y0 
        _dir = 0
    if y0 != y1:    # vertical line
        x1 = x0 
        _dir = 1

    marker = {'x0':x0, 'y0':y0, 'x1':x1, 'y1':y1, 
              'width': width, 'color':color, 'dash':dash, 
              'line':line, 'dir': _dir}
    return marker 

def createMarkerLine(fig, marker):
    fig.add_shape(type="line",
        x0=marker['x0'], y0=marker['y0'], x1=marker['x1'], y1=marker['y1'],
        line=dict(
            color=marker['color'],
            width=marker['width'],
            dash=marker['dash'],
        )
    )
    # create a flag
    if marker['line'] == 'start':
        # vertical
        if marker['dir'] :
            fig.add_shape(
                type="rect",
                x0=marker['x0'], 
                y0=marker['y1'], 
                x1=marker['x1']+30,
                y1=marker['y1']-10,
                fillcolor=marker['color'],
                line=dict(
                    color=marker['color'],
                    width=marker['width'],
                    dash=marker['dash'],
                )
            )
        # horizontal
        else:
            fig.add_shape(
                type="rect",
                x0=marker['x1'], 
                y0=marker['y0'], 
                x1=marker['x1']-30,
                y1=marker['y1']+10,
                fillcolor=marker['color'],
                line=dict(
                    color=marker['color'],
                    width=marker['width'],
                    dash=marker['dash'],
                )
            )    
    elif  marker['line'] == 'end':
        if  marker['dir'] :
            fig.add_shape(
                type="rect",
                x0=marker['x0'], 
                y0=marker['y1'], 
                x1=marker['x1']-30,
                y1=marker['y1']-10,
                fillcolor=marker['color'],
                line=dict(
                    color=marker['color'],
                    width=marker['width'],
                    dash=marker['dash'],
                )
            )    
        else:
            fig.add_shape(
                type="rect",
                x0=marker['x1'], 
                y0=marker['y0'], 
                x1=marker['x1']-30,
                y1=marker['y1']-10,
                fillcolor=marker['color'],
                line=dict(
                    color=marker['color'],
                    width=marker['width'],
                    dash=marker['dash'],
                )
            )      


#------------------------------------------------------------------------------------------------------
# Store data in memory
#------------------------------------------------------------------------------------------------------
static_store = dcc.Store(
    id='static-store'
)

global_store = dcc.Store(
    id='global-store'
)
