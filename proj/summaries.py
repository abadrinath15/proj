"""This module will organize the layout for the application; at present I'll presume to
only have one tab.
"""

import datetime as dt
from typing import Final, List

import dash_core_components as dcc
import dash_html_components as html
from dash_table import DataTable
import dash_bootstrap_components as dbc


SUMMARY_PLACEHOLDER_WIDTH: Final = "2%"
SUMMARY_COMPONENT_WIDTH: Final = "18%"
OPT_COL_WIDTH: Final = 3


def generate_summary_layout(
    dates: List[dt.date], ratings: List[str], dur_cells: List[str]
):
    layout = html.Div(
        [
            html.H1("Bond summary and optimization tool"),
            # Vertical spacing placeholder
            html.Div(style={"height": "50px"}),
            html.H3("Bond selections for summary and optimization"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Date filter"),
                            dcc.Dropdown(
                                id="date_filter",
                                options=[{"label": x, "value": x} for x in dates],
                                value=dates[0],
                                clearable=False,
                            ),
                        ],
                        style={
                            "width": SUMMARY_COMPONENT_WIDTH,
                            "display": "inline-block",
                        },
                    ),
                    # Spacing placeholder
                    html.Div(
                        style={
                            "width": SUMMARY_PLACEHOLDER_WIDTH,
                            "display": "inline-block",
                        }
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
                        style={
                            "width": SUMMARY_COMPONENT_WIDTH,
                            "display": "inline-block",
                        },
                    ),
                    # Spacing placeholder
                    html.Div(
                        style={
                            "width": SUMMARY_PLACEHOLDER_WIDTH,
                            "display": "inline-block",
                        }
                    ),
                    html.Div(
                        [
                            html.Div(id="class_label"),
                            dcc.Dropdown(id="class_filter", multi=True),
                        ],
                        style={
                            "width": SUMMARY_COMPONENT_WIDTH,
                            "display": "inline-block",
                        },
                    ),
                    # Spacing placeholder
                    html.Div(
                        style={
                            "width": SUMMARY_PLACEHOLDER_WIDTH,
                            "display": "inline-block",
                        }
                    ),
                    html.Div(
                        [
                            html.Label("Rating filter"),
                            dcc.Dropdown(
                                id="rating_filter",
                                options=[
                                    {"label": rating, "value": rating}
                                    for rating in ratings
                                ],
                                multi=True,
                            ),
                        ],
                        style={
                            "width": SUMMARY_COMPONENT_WIDTH,
                            "display": "inline-block",
                        },
                    ),
                    # Spacing placeholder
                    html.Div(
                        style={
                            "width": SUMMARY_PLACEHOLDER_WIDTH,
                            "display": "inline-block",
                        }
                    ),
                    html.Div(
                        [
                            html.Label("Dur cell filter"),
                            dcc.Dropdown(
                                id="dur_cell_filter",
                                options=[
                                    {"label": dur_cell, "value": dur_cell}
                                    for dur_cell in dur_cells
                                ],
                                multi=True,
                            ),
                        ],
                        style={
                            "width": SUMMARY_COMPONENT_WIDTH,
                            "display": "inline-block",
                        },
                    ),
                ],
            ),
            # Spacing placeholder
            html.Div(style={"height": "50px"}),
            html.Div(
                [
                    html.Div(
                        DataTable(
                            id="mv_num_bonds",
                            columns=[
                                {"name": "Number of bonds", "id": "num_bonds"},
                                {"name": "Market value", "id": "market_value"},
                            ],
                        ),
                        style={"width": SUMMARY_COMPONENT_WIDTH},
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
            # Spacing placeholder
            html.Div(style={"height": "50px"}),
            html.H3("Optimization controls"),
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Label("Target parameter"), width=OPT_COL_WIDTH
                            ),
                            dbc.Col(
                                html.Label("Security weight bound"), width=OPT_COL_WIDTH
                            ),
                            dbc.Col(
                                html.Label("Portfolio duration target ([3, 7])"),
                                width=OPT_COL_WIDTH,
                            ),
                            dbc.Col(
                                html.Label("Total sector limit ([20%, 50%])"),
                                width=OPT_COL_WIDTH,
                            ),
                        ],
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.RadioItems(
                                    id="opt_metric",
                                    options=[
                                        {"label": "OAS", "value": "oas"},
                                        {"label": "YTM", "value": "ytm"},
                                    ],
                                    value="oas",
                                    style={"width": "100px", "height": "50px"},
                                ),
                                width=OPT_COL_WIDTH,
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="sec_bound",
                                    options=[
                                        {"label": "1.00%", "value": 0.01},
                                        {"label": "2.00%", "value": 0.02},
                                        {"label": "3.00%", "value": 0.03},
                                    ],
                                    value=0.01,
                                ),
                                width=OPT_COL_WIDTH,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="duration_target",
                                    type="number",
                                    min=3,
                                    max=7,
                                    value=5,
                                    step=0.1,
                                    required=True,
                                ),
                                width=OPT_COL_WIDTH,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="sector_limit",
                                    type="number",
                                    min=20,
                                    max=50,
                                    value=35,
                                    step=1,
                                    required=True,
                                ),
                                width=OPT_COL_WIDTH,
                            ),
                        ],
                    ),
                ]
            ),
            # Vertical spacing placeholder
            html.Div(style={"height": "30px"}),
            html.Div(
                [
                    html.Button(
                        "Perform optimization",
                        id="opt_button",
                        style={"height": "50px", "width": "200px"},
                    ),
                    html.Div(style={"height": "20px"}),
                    html.Div(
                        DataTable(
                            id="opt_summary",
                            columns=[
                                {"name": "Result", "id": "opt_res"},
                                {"name": "Cash weight", "id": "cash_wt"},
                            ],
                        ),
                        style={"width": SUMMARY_COMPONENT_WIDTH},
                    ),
                ],
            ),
            # Vertical spacing placeholder
            html.Div(style={"height": "30px"}),
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(html.Label("Industrials Results")),
                            dbc.Col(html.Label("Financials Results")),
                            dbc.Col(html.Label("Utilities Results")),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                DataTable(
                                    id="industrial_results",
                                    columns=[
                                        {"name": "Cusip", "id": "ind_cusip"},
                                        {"name": "Weight", "id": "ind_wt"},
                                    ],
                                )
                            ),
                            dbc.Col(
                                DataTable(
                                    id="financials_results",
                                    columns=[
                                        {"name": "Cusip", "id": "fin_cusip"},
                                        {"name": "Weight", "id": "fin_wt"},
                                    ],
                                )
                            ),
                            dbc.Col(
                                DataTable(
                                    id="utility_results",
                                    columns=[
                                        {"name": "Cusip", "id": "utl_cusip"},
                                        {"name": "Weight", "id": "utl_wt"},
                                    ],
                                )
                            ),
                        ]
                    ),
                ]
            ),
        ],
        style={"marginLeft": 5, "width": "95%"},
    )
    return layout
