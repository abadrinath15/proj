"""This module will organize the layout for the application; at present I'll presume to
only have one tab.
"""

import dash_core_components as dcc
import dash_html_components as html
from dash_table import DataTable
from typing import Final, List
import datetime as dt


PLACEHOLDER_WIDTH: Final = "2%"
COMPONENT_WIDTH: Final = "18%"


def generate_summary_layout(dates: List[dt.date]):
    layout = html.Div(
        [
            html.H1("Bond summary and optimization tool"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Date filter"),
                            dcc.Dropdown(
                                id="date_filter",
                                options=[{"label": x, "value": x} for x in dates],
                            ),
                        ],
                        style={"width": COMPONENT_WIDTH, "display": "inline-block"},
                    ),
                    # Spacing placeholder
                    html.Div(
                        style={"width": PLACEHOLDER_WIDTH, "display": "inline-block"}
                    ),
                    html.Div(
                        [
                            html.Label("Class option"),
                            dcc.Dropdown(
                                id="class_type",
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
                    html.Div(
                        style={"width": PLACEHOLDER_WIDTH, "display": "inline-block"}
                    ),
                    html.Div(
                        [
                            html.Div(id="class_label"),
                            dcc.Dropdown(id="class_filter"),
                        ],
                        style={"width": COMPONENT_WIDTH, "display": "inline-block"},
                    ),
                    # Spacing placeholder
                    html.Div(
                        style={"width": PLACEHOLDER_WIDTH, "display": "inline-block"}
                    ),
                    html.Div(
                        [html.Label("Rating filter"), dcc.Dropdown(id="rating_filter")],
                        style={"width": COMPONENT_WIDTH, "display": "inline-block"},
                    ),
                    # Spacing placeholder
                    html.Div(
                        style={"width": PLACEHOLDER_WIDTH, "display": "inline-block"}
                    ),
                    html.Div(
                        [
                            html.Label("Dur cell filter"),
                            dcc.Dropdown(id="dur_cell_filter"),
                        ],
                        style={"width": COMPONENT_WIDTH, "display": "inline-block"},
                    ),
                ],
            ),
            # Spacing placeholder
            html.Div(style={"height": "50px"}),
            html.Div(
                [
                    html.Button(
                        "Get summary statistics",
                        id="summary_button",
                        style={"height": "50px", "width": "100px"},
                    ),
                    html.Div(
                        DataTable(
                            id="market_value",
                            columns=[{"name": "Market value", "id": "market_value"}],
                        ),
                        style={"width": COMPONENT_WIDTH},
                    ),
                    DataTable(
                        id="summary_table",
                        columns=[
                            {"name": x, "id": x.lower()}
                            for x in [
                                "Measure",
                                "Minimum",
                                "Average",
                                "Median",
                                "Maximum",
                            ]
                        ],
                    ),
                ]
            ),
        ]
    )
    return layout
