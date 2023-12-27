import dash
from dash                   import Dash, html, dash_table, dcc, callback, Output, Input, ctx, State, no_update
from flask                  import Flask
import dash_daq as daq
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from flask                  import Flask
import dash_bootstrap_components as dbc

df = pd.read_csv("podrdata1.csv")
df["GROUPING"] = df.TASK + "_" + df.GROUP
df.set_index(["GROUPING"], inplace=True)
df[[df["CH_R"] < 0]] = 0
df[[df["CH_P"] < 0]] = 0
df[[df["CH_Y"] < 0]] = 0
df[[df["CH_H"] < 0]] = 0
df[[df["CH_T"] < 0]] = 0
cols = df.columns.to_list()

server = Flask(__name__)
app = Dash( __name__, 
            server=server, 
            use_pages=False,
            external_stylesheets=[dbc.themes.BOOTSTRAP,
            dbc.icons.BOOTSTRAP]
            )

fig = go.Figure()
app.layout = html.Div([
    #dcc.Store(id="figstore", data=fig),
    #dcc.Store(id="dataframe", data=None),
    html.H1("User Hover/Click Event"),
    html.Hr(),
    dbc.Row([
        dbc.Col([
                daq.BooleanSwitch(
                    id='btn-hover-mode', 
                    on=False, 
                    label="Hover Mode", labelPosition='top'),            
                daq.BooleanSwitch(
                    id='btn-spike-mode', 
                    on=False, 
                    label="Show Spikes", labelPosition='top'),             

                ],
            width=1
        ),
        dbc.Col(
            dcc.Graph(id='graph1', figure=fig),
        ),
    ]),  #ROW


]) #DIV

def createTraceData(df, fig, xAxisCol, yAxisCol, grouping, tail=0):
    if fig is None:
        fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df[xAxisCol],
            y=df[yAxisCol],
            name=yAxisCol,
            connectgaps=True,
            line_shape='spline' 
        )
    )    
    return fig

@callback(
    Output('graph1','figure'),
    #Output('data-table', '' )
    #Output('figstore', 'data'),
    #Output('dataframe', 'data'),
    Input('btn-hover-mode', 'on'),
    Input('btn-spike-mode', 'on'),
    State('graph1','figure'),

)
def updateGraph(hMode, spikes, f):
    start = end = 0
    df_t = df.loc[df.index.get_level_values('GROUPING') == "SDIST_UPD"]
    if 'xaxis' in f['layout']:
        start = f['layout']['xaxis']['range'][0]
        end = f['layout']['xaxis']['range'][1]
        df_t = df_t.loc[df_t['TIME'].between(left=start, right=end)]
    
    fig = createTraceData(df_t, None, "TIME", "CH_H", "SDIST_UPD")
    fig = createTraceData(df_t, fig, "TIME", "float0", "SDIST_UPD")
    fig = createTraceData(df_t, fig, "TIME", "ldata0", "SDIST_UPD")

    if hMode:
        fig.update_traces(hoverinfo='text+name', mode='lines+markers')

    if spikes:
        fig.update_xaxes(showspikes=True)
        fig.update_yaxes(showspikes=True)
    else:
        fig.update_xaxes(showspikes=False)
        fig.update_yaxes(showspikes=False)


    fig.update_layout(legend=dict(y=0.5, traceorder='reversed', font_size=16))

    return fig

# @callback(
#     Output('graph1','figure'),
#     Input('graph1', 'clickData'),
#     Input('graph1', 'hoverData'),
#     #State('figstore', 'data'),
#     #State('dataframe', 'data'),

# )
# def marker_line(cData, hData):
#     pass

if __name__ == "__main__":
    app.run_server(debug=False)


