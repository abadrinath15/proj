"""This module will organize the layout for the application; at present I'll presume to 
only have one tab.
"""
import dash_html_components as html
import dash_core_components as dcc
from db_connect import app, Bond, db
from dash.dependencies import Input, Output
from sqlalchemy import select, distinct
from typing import Tuple, Dict, List, Optional, Final

PLACEHOLDER_WIDTH: Final[str] = "2%"
COMPONENT_WIDTH: Final[str] = "23%"

layout = html.Div(
    [
        html.H1("Bond summary and optimization tool"),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Class option"),
                        dcc.Dropdown(
                            id="class_choice",
                            options=[
                                {
                                    "label": "Class 1",
                                    "value": "class_1",
                                },
                                {
                                    "label": "Class 2",
                                    "value": "class_2",
                                },
                                {
                                    "label": "Class 3",
                                    "value": "class_3",
                                },
                                {"label": "Class 4", "value": "class_4"},
                            ],
                        ),
                    ],
                    style={"width": COMPONENT_WIDTH, "display": "inline-block"},
                ),
                # Spacing placeholder
                html.Div(style={"width": PLACEHOLDER_WIDTH, "display": "inline-block"}),
                html.Div(
                    [
                        html.Div(id="class_label"),
                        dcc.Dropdown(id="class_values"),
                    ],
                    style={"width": COMPONENT_WIDTH, "display": "inline-block"},
                ),
                # Spacing placeholder
                html.Div(style={"width": PLACEHOLDER_WIDTH, "display": "inline-block"}),
                html.Div(
                    [html.Label("Rating filter"), dcc.Dropdown(id="rating_filter")],
                    style={"width": COMPONENT_WIDTH, "display": "inline-block"},
                ),
                # Spacing placeholder
                html.Div(style={"width": PLACEHOLDER_WIDTH, "display": "inline-block"}),
                html.Div(
                    [html.Label("Dur cell filter"), dcc.Dropdown(id="dur_cell_filter")],
                    style={"width": COMPONENT_WIDTH, "display": "inline-block"},
                ),
            ],
        ),
    ]
)


@app.callback(
    (
        Output("class_label", "children"),
        Output("class_values", "options"),
        Output("class_values", "disabled"),
    ),
    Input("class_choice", "value"),
)
def update_class_for_choices(
    class_choice: Optional[str],
) -> Tuple[html.Div, List[Dict[str, str]], bool]:
    if class_choice is None or class_choice == "":
        return html.Label("Class value"), [], True
    class_dict = {
        "class_1": [html.Label("Class 1 choice"), Bond.class_1],
        "class_2": [html.Label("Class 2 choice"), Bond.class_2],
        "class_3": [html.Label("Class 3 choice"), Bond.class_3],
        "class_4": [html.Label("Class 4 choice"), Bond.class_4],
    }
    class_label, class_obj = class_dict[class_choice]
    stmt = select(distinct(class_obj))
    result = db.session.execute(stmt)
    return class_label, [{"label": x[0], "value": x[0]} for x in result], False
