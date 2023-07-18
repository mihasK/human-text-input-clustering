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
CLUSTER_SCORE_COLUMN = 'cluster_score'
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
    Output("modal_set_cluster", "is_open"),
    [
        Input("button-set", "n_clicks"), 
        Input("close", "n_clicks")
    ],
    [
        State("modal_set_cluster", "is_open"),
        
    ],
)
def toggle_modal_set_cluster(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("update_info", "children"),
    Input("modal_set_cluster", "is_open"),
    [
        State('df-table', 'selected_rows'),
        State('data_select', 'value'),
    ]
)
def on_modal_set_cluster_open(is_open, selected_rows, data_select):
    if not is_open:
        return ''
    
    ic(selected_rows)
    return f"Are you going to set cluster for the {len(selected_rows)} rows of the data {data_select}?"

@app.callback(
    [
        Output("update_info", "children", allow_duplicate=True,),
        Output('data_select', 'value'),
        Output('df-table', 'selected_rows', allow_duplicate=True),
    ],
    [Input("update", "n_clicks")],
    [
        State('df-table', 'selected_rows'),
        State('set_cluster_input', 'value'),
        State('df-table', 'data'),
        State('data_select', 'value'),
    ],
        prevent_initial_call=True

)
def on_button_update_cluster_click(n, selected_rows, set_cluster_input, all_rows_data, data_select):
    
    if not selected_rows:
        return (
            'No rows selected',
            data_select,
            []
        )
    df_table = pd.DataFrame([
        all_rows_data[i] for i in selected_rows
    ]).drop([SCORE_COLUMN, CLUSTER_COLUMN], axis=1, errors='ignore')
    ic(df_table.shape, df_table.columns)
    
    df_source = data_utils.load_df(data_select).drop([SCORE_COLUMN], axis=1, errors='ignore')
    ic(df_source.shape, df_source.columns)
    
    ic(df_table.index)
    # ic(df_source_index.index)
    
    
    df_source.loc[
        ic(df_table['_RID']), CLUSTER_COLUMN
    ] = set_cluster_input
    
    data_utils.write_df(df_source, d_name=data_select)
    
    
    
    
    
    return (
        f"Successfully set cluster `{set_cluster_input}` for the {len(selected_rows)} rows.",
        data_select,
        []
    )

# stats = dbc.Card(
#     [
#         html.Div(
#             [



@app.callback(
    [
        Output('fuzzy-column', 'options'),
        Output('cluster-filter', 'options'),
        Output('cluster_autocomplete', 'children'),
    ],
    Input('data_select', 'value')
)
def reload_datasource(d_name):
    logger.debug('D source reload')
    if not d_name:
        return (None, None)
    df = data_utils.load_df(d_name)
    
    cc = list(df[CLUSTER_COLUMN].dropna().unique())
              
    return (
        df.columns,
        [ALL_CLUSTERS_FILTER_LABEL, NOT_SPECIFIED_CLUSTER_F_LABEL] + sorted(cc, key=str.lower),
        [html.Option(c) for c in cc]
    )


from snoop import snoop

        
  
@app.callback(
    Output('df-table', 'style_data_conditional'),
    Input('fuzzy-column', 'value'),  
)
def highlight_column(f_column):
    return [
            {
                'if': {
                    'column_id': f_column,
                },
                'backgroundColor': 'silver',
                # 'color': 'white'
                'minWidth': '300px'
            }
    ] 


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
        Input('calc_cluster_score_switch', 'value'),
    ]
)
# @snoop()
def on_search_table(d_name, f_input, f_type, f_score, f_column, fuzzy_preprocessor_select, cluster_filter,
                    calc_cluster_score_switch: bool):
    
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

    processor = None if fuzzy_preprocessor_select == 'plain' else utils.preprocess
    score_func = partial(
        utils.fuzz_funcs[f_type],
        
        score_cutoff=f_score,
        processor=processor
    )
    
    if f_input:
        rdf.loc[:,SCORE_COLUMN] = rdf[f_column].apply(partial(score_func, s2=f_input)).round(1)
        rdf = rdf[
            rdf[SCORE_COLUMN] > 0
        ]
        # rdf = df[
        #     df['text_input'].str.contains(f_input.lower(), regex=False)
        # ]
    else:
        rdf.loc[:,SCORE_COLUMN] = 0  # clean this column
    
    rdf[CLUSTER_SCORE_COLUMN] = 0
    if calc_cluster_score_switch:
        rdf.loc[~rdf[CLUSTER_COLUMN].isnull(), CLUSTER_SCORE_COLUMN] =\
            rdf.apply(
                lambda row: score_func(s1=row[f_column], s2=row[CLUSTER_COLUMN]),
                axis=1
            )
        rdf[CLUSTER_SCORE_COLUMN] = rdf[CLUSTER_SCORE_COLUMN].round(1)

    
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
