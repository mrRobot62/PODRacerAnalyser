import pandas as pd
import plotly.graph_objects as go

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
            # building a access to the yaxis value for later evaluation
            # Note: the time basis (xaxis is allways the same)
            #ydata = f"df_t[{ig}].{c}"
            #ymax.append(eval(ydata).max())
            #legend = f"{c}_{str(g)}"
            #fig.add_scatter(name=legend, x=df_t[ig].TIME, y=eval(ydata), line_shape='spline', line={'smoothing':smoothing_value})        
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

