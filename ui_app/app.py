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
from functools import partial


from . import data_utils

from .layout import layout


CLUSTER_COLUMN = 'cluster'
SCORE_COLUMN = 'search_score'

ALL_CLUSTERS_FILTER_LABEL = '--ALL--'
NOT_SPECIFIED_CLUSTER_F_LABEL = '--NOT SPECIFIED--'



    
# df_original = pd.read_csv('./data/data_57.csv').dropna(subset=['text_input'])
# df_original.drop(['id', 'Unnamed: 0'], inplace=True, axis=1)
# df_original[SCORE_COLUMN] = 0

# logger.info(str(df_original.shape))
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = layout


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
    df = data_utils.load_df(d_name)
    return (
        df.columns,
        [ALL_CLUSTERS_FILTER_LABEL, NOT_SPECIFIED_CLUSTER_F_LABEL] + list(df[CLUSTER_COLUMN].dropna().unique())
    )


from snoop import snoop


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
# @snoop()
def on_search_table(d_name, f_input, f_type, f_score, f_column, fuzzy_preprocessor_select, cluster_filter):
    
    ic(d_name)
    if not d_name:
        d_name =data_utils.data_list[0].name
    
    ic(f_input, f_type, f_score)
    rdf = data_utils.load_df(d_name)
    
    if cluster_filter == NOT_SPECIFIED_CLUSTER_F_LABEL:
        # rdf = rdfdropna(subset=[CLUSTER_COLUMN])
        rdf = rdf[rdf[CLUSTER_COLUMN].isnull()]
    elif cluster_filter and cluster_filter != ALL_CLUSTERS_FILTER_LABEL:
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
        
    ic([{"name": i, "id": i, 'hideable':True} for i in rdf.columns])
    return (
        rdf.to_dict('records'),
        [{"name": i, "id": i, 'hideable':True} for i in rdf.columns]
    )


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
