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
    "Live configuration", id="btn-live-config", n_clicks=0, outline=True, color="danger", disabled=False, size="lg"
)

ld_serial_running = dcc.Loading(
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


""" the complete header row. """
static_header_row = dbc.Row(
    [
        dbc.Col(html.H2("Logfile analysis", style={'color':'darkcyan'}), width=6),
        dbc.Col(upload_component, width=4),
        dbc.Col(html.Div(children="", id="div-uploaded-file", style={'border-top-width':'10px' }), width=2)
    ]
)

""" the complete header row. """
livedata_header_row = dbc.Row(
    [
        dbc.Col(html.H2("Live data analysis", style={'color':'darkcyan'}), width=6),
        dbc.Col(btn_live_config, width=4),
        #dbc.Col(html.Div(children="", id="div-uploaded-file", style={'border-top-width':'10px' }), width=2)
        dbc.Col(ld_serial_running, width=2)
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
    min=100, max=500, step=50, value=250, id="sl-live-interval"
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
        dbc.ModalFooter(
            [
                dbc.Button(
                    "Close", id="close-live", className="ms-auto", n_clicks=0
                ),
                dbc.Button(
                    "Run", id="run-live", color="success", className="ms-auto", n_clicks=0
                )
            ]    
        ),
    ],
    id="modal-live-config",
    size="lg",
    is_open=False,
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
