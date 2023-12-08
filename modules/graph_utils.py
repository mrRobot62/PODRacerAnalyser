import pandas as pd
import plotly.graph_objects as go
from dash                   import html

static_df = None

template_theme1 = 'flatly'
template_theme2 = 'darkly'


def configGraph(df, fig, dataPoint, group, sv):
    ydata = f"df.{dataPoint}"
    vMax = max(eval(ydata))
    legend = f"{str(group)}|{dataPoint}"
    fig.add_scatter(name=legend, x=df.TIME, y=eval(ydata), line_shape='spline', line={'smoothing':sv})        
    return vMax


def updateGraph(df,
        smoothing_value, hover_mode, xaxis_type, yaxis_type, tasks, 
        channels, floats, ldata,
        toggle, title=""):
    fig = None
    ## graphs
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
            ymax.append(configGraph(df_t[ig], fig, c, g, smoothing_value))

    for ic, c in enumerate(floats):
        for ig, g in enumerate(df_filt_tasks.index.get_level_values('GROUPING').unique()):
            ymax.append(configGraph(df_t[ig], fig, c.lower(), g, smoothing_value))
            
    for ic, c in enumerate(ldata):
        for ig, g in enumerate(df_filt_tasks.index.get_level_values('GROUPING').unique()):
            ymax.append(configGraph(df_t[ig], fig, c.lower(), g, smoothing_value))
            

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

def createTooltip(df, fig, data):
    pt = data["points"][0]
    curves = fig["data"]
    bbox = pt["bbox"]
    curvID = pt["curveNumber"]
    ts = f"{pt['x']}ms"
    dp = f"{pt['y']}"

    grouping = curves[curvID]['name'].split('|')
    df_row = df.query(f"GROUPING=='{grouping[0]}' and DATA=='{grouping[1]}'")
    data = f"at '{ts}' with value '{dp}'"
    name = df_row['NAME'].iloc[0]
    range = df_row['RANGE'].iloc[0]
    desc = df_row['DESC'].iloc[0]
    if len(desc) > 300:
        desc = desc[:100] + '...'

    children = [
        html.Div([
            html.H5(f"{name}", style={"color": "darkblue", "overflow-wrap": "break-word"}),
            html.Hr(),
            html.P([
                "at ",
                html.B(ts, style={"color": "darkblue"}),
                " with value ",
                html.B(dp, style={"color": "darkblue"})
            ]),
            html.Hr(),
            html.P([
                "typical range ",
                html.B(range, style={"color": "darkblue"})
            ]),
            html.Hr(),
            html.P(f"{desc}"),
        ], style={'width': '450px', 'white-space': 'normal'})
    ]
    return (children, bbox)
