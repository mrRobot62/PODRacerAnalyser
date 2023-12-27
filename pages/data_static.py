# Import packages
import dash
from dash                   import Dash, html, dash_table, dcc, callback, Output, Input, ctx, State, no_update
from flask                  import Flask
import plotly.express       as px
import plotly.graph_objects as go
import io
import base64
import json

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
help_df = None

#------------------------------------------------------------------------------------------------------
# Design the app
layout = html.Div(
    [
        static_store,
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
            dbc.Col(dcc.Graph(id="fig-static-main", 
                              clear_on_unhover=True))
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
    Output(component_id="static-store", component_property="data"),

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


    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    #
    # using for measure ms/freq
    Input('fig-static-main', 'clickData'),
    Input('fig-static-main', 'hoverData'),
 
    State('static-store', 'data'),
    State('fig-static-main', "figure"),

)
def update_static_main(
    smoothing_value, hover_mode, xaxis_type, yaxis_type, 
    tasks, channels, floats, ldata, 
    xaxis2_type, yaxis2_type,tasks2, channels2, floats2, ldata2,
    toggle, 
    clickData, hoverData, 
    store, state_fig):
    clicked = ctx.triggered_id if not None else 'No clicks yet'
    msg = None
    help_df = None
    if store is None:
        store = {
            'marks' : {
                'horizontal' : [{}],
                'vertical' : [{},{}]
            } ,
            'data' : None,
            'xaxis' : {
                'range': []
            }
        }
    template = template_theme2 if toggle else template_theme1
    fig = go.FigureWidget()
    fig2 = go.FigureWidget()


    #-----------------------------------------------------
    # update graph due to user dropbox selections
    #-----------------------------------------------------

    if static_df is not None:
        fig = updateGraph(static_df, 
            smoothing_value, hover_mode, xaxis_type, yaxis_type, 
            tasks, channels, floats, ldata, 
            toggle, store)
        fig2 = updateGraph(static_df, 
            smoothing_value, hover_mode, xaxis2_type, yaxis2_type, 
            tasks2, channels2, floats2, ldata2, 
            toggle, store)
        
        fig.update_layout(xaxis_range = state_fig['layout']['xaxis']['range'])
        store['xaxis']['range'] = state_fig['layout']['xaxis']['range']
    else:
        return fig, fig2, True, "{}".format("No dataframe avaiable - no file selected"), store

    if hoverData is not None and hover_mode:
        # default hover template
        pass

    if clickData is not None and hover_mode:
        id = lastID = 0
        xpos = clickData['points'][0]['x']
        if not store['marks']['vertical'][0]:
            lastX = 0
            lastID = 0
            id = 0
        else:
            lastX = store['marks']['vertical'][0]['x0']
            id = 1
        cn = clickData['points'][0]['curveNumber']
        pn = clickData['points'][0]['pointNumber']

        ymax = int(max(state_fig['layout']['yaxis']['range'])) 
        ymin = 0
        if xpos != lastX:
            # vertical line
            marker = setMarkerLine(
                xpos,ymin,xpos,ymax,
                cn, pn, id, lastID,
                line='line', width=3, color="red", dash="solid")  
            store['marks']['vertical'][id] = marker
            for line in store['marks']['vertical']:
                if line:
                    createMarkerLine(fig, line)
        else:
            store['marks']['vertical'] = [{},{}]

    msg1 = json.dumps( clickData,indent=2 )
    msg2 = json.dumps( hoverData,indent=2 )
    print ("clickData----------------")
    print(msg1)
    print ("hoverData++++++++++++++++")
    print(msg2)
    print ("************************")
    return fig, fig2, False, None, store

    #-----------------------------------------------------
    # update graph due to markers
    #---------------------------------------------------
'''
    if hoverData is not None and len(store['marks']['vertical']) == 1:
        xmin = store['marks']['vertical'][0]['x0']
        xpos = hoverData['points'][0]['x']
        ypos = int(max(state_fig['layout']['yaxis']['range'])) 
        pn = clickData['points'][0]['pointNumber']
        cn = clickData['points'][0]['curveNumber']
        marker = setMarkerLine(
            xmin,ypos,xpos,ypos,
            cn, pn, 
            line='measure', width=3, color="green", dash="dot")
        if len(store['marks']['horizontal']) == 0:
            store['marks']['horizontal'].append(marker)
        else:
            store['marks']['horizontal'][0] = marker

#        createMarkerLine(fig, marker)  

    if clickData is not None:
        xpos = clickData['points'][0]['x']
        pn = clickData['points'][0]['pointNumber']
        cn = clickData['points'][0]['curveNumber']

        ymin = int(min(state_fig['layout']['yaxis'][ 'range']))
        ymax = int(max(state_fig['layout']['yaxis']['range']))

        if  len(store['marks']['vertical']) == 0:
            marker = setMarkerLine(
                xpos,ymin,xpos,ymax, 
                cn, pn, 
                line='line', color="red" )
            store['marks']['vertical'].append(marker)
#        elif len(store['marks']['vertical']) == 1:
#            for line in store['marks']['vertical']:
#                createMarkerLine(fig, line)

    if len(store['marks']['vertical']) > 0:
        createMarkerLine(fig, store['marks']['vertical'][0])
    if len(store['marks']['horizontal']) > 0:
        createMarkerLine(fig, store['marks']['horizontal'][0])
'''



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

    # main graph
    Input(component_id='sl-spline', component_property='value'),
    Input(component_id='chk-hover-mode', component_property='value'),
    Input(component_id='rb-xaxis-type', component_property='value'),
    Input(component_id='rb-yaxis-type', component_property='value'),
    Input(component_id='dd-task-filter', component_property='value'),
    Input(component_id='dd-channels-filter', component_property='value'),
    Input(component_id='dd-float-filter', component_property='value'),
    Input(component_id='dd-ldata-filter', component_property='value'),

    # sub graph
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

#----------------------------------------------------------------------
# dynamically scale of x-axis ticks
#----------------------------------------------------------------------
@callback(
    Output(component_id='fig-static-main', component_property='figure', allow_duplicate=True),
    Input(component_id='fig-static-main', component_property='relayoutData'),
    State('fig-static-main', 'figure'),
    prevent_initial_call=True

)
def relayout_data(data, fig):
    outputs = []
    if fig is not None and len(fig['data']) > 0:
        try:
            diff = max(fig['layout']['xaxis']['range']) - \
                    min(fig['layout']['xaxis']['range'])
            # divede the spectrum in 5% steps
            ticks = int( (diff / 100.0) * 5)
            n = (-1 if ticks < 100 else -2 if ticks < 1000 else -3)
            ticks = round(ticks, n)
            fig['layout']['xaxis']['dtick'] = ticks
            fig['layout']['xaxis']['autorange'] = False
        except (KeyError, TypeError) as err:
            fig['layout']['xaxis']['autorange'] = True

    return fig
