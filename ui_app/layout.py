from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from dash import dash_table, State
import dash
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from loguru import logger
from icecream import ic
from . import utils
from . import data_utils


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
                #    value=ALL_CLUSTERS_FILTER_LABEL
        )
    ]), md=3)

]


modal_set_cluster = html.Div(
    [
        html.Datalist(
            # children=[html.Option(x) for x in ['bittcoin', 'qark']],
            id='cluster_autocomplete'
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Set cluster")),
                dbc.ModalBody([
                    html.Div(
                        "Are you going to set cluster for the records?",
                        id='update_info'
                    ),
                    dbc.Input(type='text', 
                              autocomplete=True,
                              list='cluster_autocomplete',
                              id='set_cluster_input'),
                ]),
                dbc.ModalFooter(
                    [
                        dbc.Button("Update records", id="update", className="ms-auto", color='danger', n_clicks=0),
                        dbc.Button("Close", id="close", className="ms-auto", n_clicks=0)
                    ]
                ),
            ],
            id="modal_set_cluster",
            is_open=False,
        ),
    ]
)



df_initial = data_utils.load_df(data_utils.data_list[0])


table =  dash_table.DataTable(
    # [{}], [],
    df_initial.to_dict('records'), 
    [{"name": i, "id": i, 'hideable':True} for i in df_initial.columns],
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





layout = html.Div([
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
                        options=(vals:=[f.name for f in data_utils.data_list]),
                        value=vals[0] if vals else None,
                        id='data_select'
                    ),
                ]),
                
                width=4
            )
        ]),
        # dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
        # dcc.Graph(id='graph-content')
        modal_set_cluster,

        
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

