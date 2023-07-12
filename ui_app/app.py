from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from dash import dash_table, State
import dash
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from loguru import logger

df = pd.read_csv('./data/data_57.csv')

logger.info(str(df.shape))
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])



table =  dash_table.DataTable(
    df.to_dict('records'), 
    [{"name": i, "id": i, 'hideable':True} for i in df.columns],
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        selected_columns=[],
        selected_rows=[],
        # page_action="native",
        # page_current= 0,
        page_size= 100,
        # page_action='none',
        fixed_rows={'headers': True},

        style_table={'height': '500px', 'overflowY': 'auto'},
        
        # style_data_conditional=         [
        #     {
        #         'if': {
        #             'filter_query': '{cluster} is nil',
        #         },
        #         'backgroundColor': 'white',
        #         # 'color': 'white'
        #     },
        # ],
        id='df-table',
        css =[
            # {'selector':'.dash-spreadsheet-menu','rule':'position:absolute;bottom:-30px'}, #move below table
            # {'selector':'.show-hide','rule':'font-family:Impact'}, #change font
        ]
)



modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Set cluster")),
                dbc.ModalBody([
                    dbc.Input(type='text')
                ]),
                dbc.ModalFooter(
                    [
                        dbc.Button("Update records", id="update", className="ms-auto", n_clicks=0),
                        dbc.Button("Close", id="close", className="ms-auto", n_clicks=0)
                    ]
                ),
            ],
            id="modal",
            is_open=False,
        ),
    ]
)


@app.callback(
    Output("modal", "is_open"),
    [
        Input("button-set", "n_clicks"), 
        Input("close", "n_clicks")
    ],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# stats = dbc.Card(
#     [
#         html.Div(
#             [

app.layout = html.Div([
    html.H1(children='Cluster text records', style={'textAlign':'center'}),
    # dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    # dcc.Graph(id='graph-content')
    modal,
    dbc.Container([

        dbc.Row(
            table,    
        ),
        
        
        dbc.Row([
            
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button('Select all', outline=True, color="primary", id='select-all-button'), 
                    dbc.Button('Select all on current page', outline=True, color="primary", id='select-all-on-page-button'), 
                    dbc.Button('Deselect all', outline=True, color="secondary", className="me-1", id='deselect-all-button'), 
                ]),
                
            ], md=4),
            
            dbc.Col([
                dbc.Button(
                    [
                        "Specify cluster",
                        dbc.Badge(
                            "0",
                            color="danger",
                            pill=True,
                            text_color="white",
                            className="position-absolute top-0 start-100 translate-middle",
                            id="badge-selected"
                        ),
                    ],
                    color="primary",
                    className="position-relative",
                    id='button-set'
                )
            ], md=4)
            
            
        ]),
    ])
    

])


@app.callback(
    Output("badge-selected", "children"),
    Input("df-table", "selected_rows")
)
def update_num_selected(selected_rows):
    
    return str(
        len(selected_rows)
    )


@app.callback(
    [Output('df-table', 'selected_rows')],
    [
        Input('select-all-button', 'n_clicks'),
        Input('select-all-on-page-button', 'n_clicks'),
        Input('deselect-all-button', 'n_clicks')
    ],
    [
        State('df-table', 'data'),
        State('df-table', 'derived_virtual_data'),
        State('df-table', 'derived_viewport_data'),
        State('df-table', 'derived_virtual_selected_rows')
    ]
)
def select_all(select_n_clicks, select_on_page_n_clicks, deselect_n_clicks, original_rows, filtered_rows, filtered_rows_on_page, selected_rows):
    ctx = dash.callback_context.triggered[0]
    ctx_caller = ctx['prop_id']
    if filtered_rows is not None:
        if ctx_caller == 'select-all-button.n_clicks':
            logger.info("Selecting all rows..")
            selected_ids = [row for row in filtered_rows]
            return [[i for i, row in enumerate(original_rows) if row in selected_ids]]
        if ctx_caller == 'select-all-on-page-button.n_clicks':
            logger.info("Selecting all rows on the current page..")
            selected_ids = [row for row in filtered_rows_on_page]
            return [[i for i, row in enumerate(original_rows) if row in selected_ids]]
        if ctx_caller == 'deselect-all-button.n_clicks':
            logger.info("Deselecting all rows..")
            return [[]]
        raise PreventUpdate
    else:
        raise PreventUpdate
    
    
# @callback(
#     Output('graph-content', 'figure'),
#     Input('dropdown-selection', 'value')
# )
# def update_graph(value):
#     dff = df[df.country==value]
#     return px.line(dff, x='year', y='pop')

if __name__ == '__main__':
    app.run(debug=True)
