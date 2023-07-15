from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from dash import dash_table, State
import dash
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from loguru import logger
from icecream import ic

CLUSTER_COLUMN = 'cluster'
SCORE_COLUMN = 'search_score'



import pathlib

ic(__file__)
data_dir = pathlib.Path(__file__).parent / 'data'

data_list = ic(
    list(data_dir.iterdir())
)
 

def _load_df(d_name):
    logger.info(f'{d_name} data selected')
    return pd.read_csv(data_dir / d_name)
    
# df_original = pd.read_csv('./data/data_57.csv').dropna(subset=['text_input'])
# df_original.drop(['id', 'Unnamed: 0'], inplace=True, axis=1)
# df_original[SCORE_COLUMN] = 0

# logger.info(str(df_original.shape))
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])




table =  dash_table.DataTable(
    # df_original.to_dict('records'), 
    # [{"name": i, "id": i, 'hideable':True} for i in df_original.columns],
        editable=False,
        filter_action="native",
        # filter_action="custom",
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

        style_table={'height': '500px', 'overflowY': 'auto',

                     },
        style_data={
            'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },
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
                    dbc.Input(type='text'),
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

from . import utils
ALL_CLUSTERS_FILTER_LABEL = '--ALL--'
NOT_SPECIFIED_CLUSTER_F_LABEL = '--NOT SPECIFIED--'
filters_input = [
    dbc.Col(dbc.InputGroup(
        [
            dbc.Select(
                value=list(utils.fuzz_funcs.keys())[0],
                id='fuzzy-type',
                options=[
                    {"label": k.title(), "value": k }
                    for k, v in utils.fuzz_funcs.items()
                    # {"label": "Option 2", "value": 2},
                ]
            ),
            dbc.InputGroupText("min score:"),
            dbc.Input(id='fuzzy-score', type="number", min=0, max=100, step=1, value=60),
        ]
    ), md=3),
    dbc.Col(dbc.InputGroup(
        [
            # dbc.InputGroupText("Preprocess:"),
            # dbc.Checkbox( value=True, id='preproccessor-checkbox' ),
            dbc.Select(options=['plain', 'preprocces'], value='plain', id='fuzzy_preprocessor_select'),
        ]),
            md=1),
    dbc.Col(dbc.InputGroup(
        [
            dbc.Input(id='fuzzy-input', placeholder='Input for fuzzy search',    html_size=50),
            dbc.InputGroupText("for column:"),
            dbc.Select(
                value='text_input',
                # options=df_original.columns,
                id='fuzzy-column'
            )

        ]), md=5),
    
    dbc.Col(dbc.InputGroup([
        dbc.InputGroupText('Cluster'),
        dbc.Select(id='cluster-filter',
                #    options=[ALL_CLUSTERS_FILTER_LABEL, NOT_SPECIFIED_CLUSTER_F_LABEL] + list(df_original[CLUSTER_COLUMN].dropna().unique()),
                   value=ALL_CLUSTERS_FILTER_LABEL)
    ]), md=3)

]


@app.callback(
    [
        Output('fuzzy-column', 'options'),
        Output('cluster-filter', 'options'),
    ],
    Input('data_select', 'value')
)
def update_columns(d_name):
    if not d_name:
        return (None, None)
    df = _load_df(d_name)
    return (
        df.columns,
        [ALL_CLUSTERS_FILTER_LABEL, NOT_SPECIFIED_CLUSTER_F_LABEL] + list(df[CLUSTER_COLUMN].dropna().unique())
    )

from functools import partial


@app.callback(
    [
        Output('df-table', 'data'),
        Output('df-table', 'columns'),
    ],
    # Output('df-table', 'derived_virtual_data'),
    [
        Input('data_select', 'value'),
        Input('fuzzy-input', 'value'),
        Input('fuzzy-type', 'value'),
        Input('fuzzy-score', 'value'),
        Input('fuzzy-column', 'value'),
        Input('fuzzy_preprocessor_select', 'value'),
        Input('cluster-filter', 'value'),
    ]
)
def on_search_table(d_name, f_input, f_type, f_score, f_column, fuzzy_preprocessor_select, cluster_filter):
    
    if not d_name:
        d_name = data_list[0].name
    
    ic(f_input, f_type, f_score)
    rdf = _load_df(d_name)
    
    if cluster_filter == NOT_SPECIFIED_CLUSTER_F_LABEL:
        # rdf = rdfdropna(subset=[CLUSTER_COLUMN])
        rdf = rdf[rdf[CLUSTER_COLUMN].isnull()]
    elif cluster_filter != ALL_CLUSTERS_FILTER_LABEL:
        rdf = rdf[
            rdf[CLUSTER_COLUMN] == cluster_filter
        ]
    
    if f_input:
        processor = None if fuzzy_preprocessor_select == 'plain' else utils.preprocess
        score_func = partial(
            utils.fuzz_funcs[f_type],
            s2=f_input,
            score_cutoff=f_score,
            processor=processor
        )
        rdf.loc[:,SCORE_COLUMN] = rdf[f_column].apply(score_func).round(1)
        rdf = rdf[
            rdf[SCORE_COLUMN] > 0
        ]
        # rdf = df[
        #     df['text_input'].str.contains(f_input.lower(), regex=False)
        # ]
    else:
        rdf.loc[:,SCORE_COLUMN] = 0  # clean this column
    return (
        rdf.to_dict('records'),
        [{"name": i, "id": i, 'hideable':True} for i in rdf.columns]
    )




app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(
                html.H1(children='Cluster text records', style={'textAlign':'center'}),
                # width=9
            ),
            
            dbc.Col(
                
                dbc.InputGroup([
                    dbc.InputGroupText('Selected Data:'),
                    dbc.Select(
                        options=[f.name for f in data_list],
                        id='data_select'
                    ),
                ]),
                
                width=4
            )
        ]),
        # dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
        # dcc.Graph(id='graph-content')
        modal,

        
        dbc.Row( filters_input ),
        html.Hr(),

        dbc.Row(
            table,    
        ),
        
        html.Hr(),
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
            ], md=4),
            
            dbc.Col([
                dbc.Card([
                    html.Small(['Records: ', html.B(id='num-records')]),
                    html.Small(['Clusters: ', html.B(id='num-clusters')]),
                    html.Small(['Not clustered: ', html.B(id='num-not-clustered')]),
                ])
            ], md=3)
            
            
        ]),
    ])
    
])


@app.callback(
    [
        Output('num-records', 'children'),
        Output('num-clusters', 'children'),
        Output('num-not-clustered', 'children'),
        # Output('cluster-filter', 'options'),
    ],
    Input('df-table', 'data')
)
def update_stats(data):
    xdf = pd.DataFrame(data)
    return (
        (total:=xdf.shape[0]),
        len(xdf[CLUSTER_COLUMN].dropna().unique()) if total else 0,
        xdf[CLUSTER_COLUMN].isnull().sum() if total else 0,
        # [ALL_CLUSTERS_FILTER_LABEL, NOT_SPECIFIED_CLUSTER_F_LABEL] + (
        #     list(xdf[CLUSTER_COLUMN].dropna().unique()) if total else []
        # )
    )

@app.callback(
    Output("badge-selected", "children"),
    Input("df-table", "selected_rows")
)
def update_num_selected(selected_rows):

    
    return str(
        len(selected_rows),
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
