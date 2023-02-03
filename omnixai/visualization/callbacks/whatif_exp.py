import dash
import copy
import json
import omnixai.visualization.state as board
from dash import Input, Output, State, callback
from ..pages.whatif_exp import create_result_column


@callback(
    Output("whatif-explanation-state", "data"),
    [
        Input("select-instance-whatif", "value"),
        Input("first-instance-set-btn", "n_clicks"),
        Input("first-instance-reset-btn", "n_clicks"),
        Input("second-instance-set-btn", "n_clicks"),
        Input("second-instance-reset-btn", "n_clicks"),
    ],
    [
        State("first-instance-feature-name", "value"),
        State("first-instance-feature-value", "value"),
        State("second-instance-feature-name", "value"),
        State("second-instance-feature-value", "value"),
        State("whatif-explanation-state", "data")
    ]
)
def change_parameters(
        instance,
        first_set_click,
        first_reset_click,
        second_set_click,
        second_reset_click,
        first_feature_name,
        first_feature_value,
        second_feature_name,
        second_feature_value,
        state_data
):
    params = json.loads(state_data) if state_data is not None else {}
    ctx = dash.callback_context
    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "select-instance-whatif":
            params["display_instance"] = int(instance)
            board.whatif_state.set_display_instance(int(instance))

        elif prop_id == "first-instance-set-btn":
            if first_feature_name and first_feature_value:
                index = board.whatif_state.get_display_instance()
                example = board.whatif_state.get_instance("instances-a", index).to_pd()
                example[first_feature_name] = first_feature_value
                board.whatif_state.set_instance("instances-a", index, example.iloc[0])

        elif prop_id == "first-instance-reset-btn":
            index = board.whatif_state.get_display_instance()
            example = board.whatif_state.instances.iloc(index).to_pd()
            board.whatif_state.set_instance("instances-a", index, example.iloc[0])
            board.whatif_state.set_explanations("what-if-a")

        elif prop_id == "second-instance-set-btn":
            if second_feature_name and second_feature_value:
                index = board.whatif_state.get_display_instance()
                example = board.whatif_state.get_instance("instances-b", index).to_pd()
                example[second_feature_name] = second_feature_value
                board.whatif_state.set_instance("instances-b", index, example.iloc[0])

        elif prop_id == "second-instance-reset-btn":
            index = board.whatif_state.get_display_instance()
            example = board.whatif_state.instances.iloc(index).to_pd()
            board.whatif_state.set_instance("instances-b", index, example.iloc[0])
            board.whatif_state.set_explanations("what-if-b")

    return json.dumps(params)


@callback(
    Output("first-instance-feature-value", "options"),
    Input("first-instance-feature-value-parent", "n_clicks"),
    State("first-instance-feature-name", "value"),
)
def update_first_feature_value_dropdown(n_clicks, feature_name):
    options = []
    ctx = dash.callback_context
    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "first-instance-feature-value-parent":
            features = board.whatif_state.get_feature_values()
            options = [{"label": v, "value": v} for v in features.get(feature_name, [])]
    return options


@callback(
    Output("second-instance-feature-value", "options"),
    Input("second-instance-feature-value-parent", "n_clicks"),
    State("second-instance-feature-name", "value"),
)
def update_second_feature_value_dropdown(n_clicks, feature_name):
    options = []
    ctx = dash.callback_context
    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "second-instance-feature-value-parent":
            features = board.whatif_state.get_feature_values()
            options = [{"label": v, "value": v} for v in features.get(feature_name, [])]
    return options


@callback(
    Output("result-column", "children"),
    Input("whatif-explanation-state", "data")
)
def update_view(data):
    state = copy.deepcopy(board.whatif_state)
    if data:
        params = json.loads(data)
        for param, value in params.items():
            state.set_param(param, value)
    return create_result_column(state)
