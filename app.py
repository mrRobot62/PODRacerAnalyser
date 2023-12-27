
# Import packages
from dash                   import Dash, html, dash, page_container, page_registry, dash_table, dcc, callback, Output, Input, ctx, State, no_update
from flask                  import Flask
import plotly.express       as px
import plotly.graph_objects as go
import time 

import argparse
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
from modules.datasets import ImportHelpData, help_df
from modules.graph_utils import createTooltip

server = Flask(__name__)

# select the Bootstrap stylesheets and figure templates for the theme toggle here:
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.CYBORG

theme_toggle = ThemeSwitchAIO(
    aio_id="theme",
    themes=[url_theme2, url_theme1],
    icons={"left": "fa fa-sun", "right": "fa fa-moon"},
)


parser = argparse.ArgumentParser(__name__, description="Web analysis software for PODRacer telemetry data")

parser.add_argument("-p", "--port", type=int, default=8050, help="set a port, default is 8050")
parser.add_argument("-i", "--ipath", type=str, default="/data", help="set path to datafile")
parser.add_argument("-d", "--debug", action="store_true", help="if set, use debug mode for app")

args = parser.parse_args()
 

# This stylesheet defines the "dbc" class.  Use it to style dash-core-components
# and the dash DataTable with the bootstrap theme.
#dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
dbc_css = "css/dbc.min.css"


from modules.datasets import *
from modules.components import *

AppName    = "PODRacer LogVisualizer"
AppVersion = "1.0.1"



app = Dash(__name__, server=server, 
           use_pages=True,
            #external_stylesheets=[url_theme2, dbc_css, dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP]
            external_stylesheets=[url_theme1, dbc_css,  dbc.icons.BOOTSTRAP,dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME]
            )


navbar = dbc.NavbarSimple(
    dbc.Nav(
        [ 
            dbc.NavLink(page["name"], href=page["path"])
            # iterate registered pages
            # if file is available, check the dash.register_page(__name__, name="Static analysis", top_nav=True)
            # content. if it is a top_nav page, include it into the navigtion top-level
            for page in page_registry.values()
            #if page["module"] != "pages.not_found_404"
            if page.get("top_nav") 
        ]
    ),
    brand=f"{AppName} V{AppVersion}",
    color="primary",
    dark=True,
    className="mb-2",
)

#---------------------------------------------------------------
# Main skeleton for the application
# navbar - theme selector - page container
#   
# page_container is used by pages
#---------------------------------------------------------------
app.layout = dbc.Container(
    [ 
        navbar, 
        dbc.Row([theme_toggle]),
        dash.page_container
     ],
    fluid=True,
)

#---------------------------------------------------------------
# callbacks on app-level
#---------------------------------------------------------------

## APP-Callbacks
@app.callback(
    Output("offcanvas-graph-content", "is_open"),
    Input("btn-backdrop-1", "n_clicks"),
    State("offcanvas-graph-content", "is_open"),
)
def toggle_offcanvas(n1,is_open):
    if n1:
        return not is_open 
    return is_open

@app.callback(
    Output("offcanvas-graph2-content", "is_open"),
    Input("btn-backdrop-2", "n_clicks"),
    State("offcanvas-graph2-content", "is_open"),
)
def toggle_offcanvas2(n1,is_open):
    if n1:
        return not is_open 
    return is_open


@app.callback(
    Output("tt-data-point", "show"),
    Output("tt-data-point", "bbox"),
    Output("tt-data-point", "children"),
    Input("fig-static-main", "hoverData"),
    Input("fig-static-main", "figure"),
    Input(component_id='chk-hover-mode', component_property='value'),

)
def display_hover1(hoverData, fig, hmode):
    if hoverData is None or hmode:
        return False, no_update, no_update

    # demo only shows the first point, but other points may also be available
    tt, bbox = createTooltip(help_df, fig, hoverData)
    return True, bbox, tt

@app.callback(
    Output("tt-data-point-sub", "show"),
    Output("tt-data-point-sub", "bbox"),
    Output("tt-data-point-sub", "children"),
    Input("fig-static-sub1", "hoverData"),
    Input("fig-static-sub1", "figure")
)
def display_hover2(hoverData, fig):
    if hoverData is None:
        return False, no_update, no_update

    # demo only shows the first point, but other points may also be available
    tt, bbox = createTooltip(help_df, fig, hoverData)
    return True, bbox, tt

#******************************************************************************************
# Run server
#******************************************************************************************
if __name__ == "__main__":
    help_df = ImportHelpData()
    app.run_server(debug=args.debug, port=args.port )