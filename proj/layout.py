"""This module will organize the layout for the application; at present I'll presume to 
only have one tab.
"""
import dash_html_components as html
import dash_core_components as dcc

layout = html.Div(
    [
        html.H1("Bond summary and optimization tool"),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Class filter"),
                        dcc.Dropdown(
                            id="class_filter",
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
                    style={"width": "32%", "display": "inline-block"},
                ),
                # Spacing placeholder
                html.Div(style={"width": "2%", "display": "inline-block"}), 
                html.Div(
                    [html.Label("Rating filter"), dcc.Dropdown(id="rating_filter")],
                    style={"width": "32%", "display": "inline-block"},
                ),
                # Spacing placeholder
                html.Div(style={"width": "2%", "display": "inline-block"}),
                html.Div(
                    [html.Label("Dur cell filter"), dcc.Dropdown(id="dur_cell_filter")],
                    style={"width": "32%", "display": "inline-block"},
                ),
            ],
        ),
    ]
)
