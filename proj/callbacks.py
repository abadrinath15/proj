"""In order to avoid concers that we're going to certainly have with the flask
application name and circular loops, we'll define all the callbacks here and register
them
"""

import datetime as dt
from typing import Dict, Final, List, Optional, Tuple, Union

import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_table import FormatTemplate
from dash_table.Format import Format, Scheme
from flask_sqlalchemy import Model, SQLAlchemy
from sqlalchemy import distinct, select, true
from sqlalchemy.sql import func


def register_callbacks(app, db: SQLAlchemy, Bond: Model):
    # Quick dictionary to reduce conditional bond_object lookups
    CLASS_DICT: Final = {
        "class_1": [html.Label("Class 1 choice"), Bond.class_1],
        "class_2": [html.Label("Class 2 choice"), Bond.class_2],
        "class_3": [html.Label("Class 3 choice"), Bond.class_3],
        "class_4": [html.Label("Class 4 choice"), Bond.class_4],
        None: [None, None],
    }

    @app.callback(
        (
            Output("class_label", "children"),
            Output("class_filter", "options"),
            Output("class_filter", "disabled"),
            Output("class_filter", "value"),
        ),
        Input("date_filter", "value"),
        Input("class_type", "value"),
    )
    def update_class_for_choices(
        date_value: dt.date,
        class_type: Optional[str],
    ) -> Tuple[html.Div, List[Dict[str, str]], bool, None]:
        if class_type is None:
            return html.Label("Class value"), [], True, None

        class_label, class_obj = CLASS_DICT[class_type]
        stmt = select(distinct(class_obj)).where(Bond.eff_date == date_value)
        result = db.session.execute(stmt)
        return (
            class_label,
            [{"label": x[0], "value": x[0]} for x in result],
            False,
            None,
        )

    @app.callback(
        (
            Output("summary_table", "data"),
            Output("summary_table", "columns"),
            Output("market_value", "data"),
            Output("market_value", "columns"),
        ),
        Input("summary_button", "n_clicks"),
        State("date_filter", "value"),
        State("class_type", "value"),
        State("class_filter", "value"),
        State("rating_filter", "value"),
        State("dur_cell_filter", "value"),
    )
    def update_summary_table(
        num_clicks: Optional[int],
        date_value: dt.datetime,
        class_type: Optional[str],
        class_choices: Optional[List[str]],
        rating_values: Optional[List[str]],
        dur_cell_values: Optional[List[str]],
    ) -> Tuple[
        List[dict[str, Union[str, int]]],
        List[dict],
        List[dict[str, Union[str, int]]],
        List[dict],
    ]:
        col_names = [
            "Measure",
            "Minimum",
            "Average",
            "Median",
            "Maximum",
        ]
        if num_clicks is None or num_clicks == 0:
            return (
                [
                    {
                        "measure": "OAS",
                        "minimum": "--",
                        "average": "--",
                        "median": "--",
                        "maximum": "--",
                    },
                    {
                        "measure": "YTM",
                        "minimum": "--",
                        "average": "--",
                        "median": "--",
                        "maximum": "--",
                    },
                ],
                [{"name": x, "id": x.lower()} for x in col_names],
                [{"market_value": "--"}],
                [{"name": "Market value", "id": "market_value"}],
            )
        _, class_obj = CLASS_DICT[class_type]
        where_clauses = [
            Bond.eff_date == date_value,
            true()
            if any([class_obj is None, not class_choices])
            else class_obj.in_(class_choices),
            true() if not rating_values else Bond.rating.in_(rating_values),
            true() if not dur_cell_values else Bond.dur_cell.in_(dur_cell_values),
        ]
        stmt = select(
            func.min(Bond.oas),
            func.avg(Bond.oas),
            func.percentile_cont(0.5).within_group(Bond.oas.asc()),
            func.max(Bond.oas),
            func.min(Bond.ytm),
            func.avg(Bond.ytm),
            func.percentile_cont(0.5).within_group(Bond.ytm.asc()),
            func.max(Bond.ytm),
            func.sum(Bond.mv),
        ).where(*where_clauses)
        result = list(db.session.execute(stmt))[0]
        return (
            [
                {
                    "measure": "OAS",
                    "minimum": result[0],
                    "average": result[1],
                    "median": result[2],
                    "maximum": result[3],
                },
                {
                    "measure": "YTM",
                    "minimum": result[4],
                    "average": result[5],
                    "median": result[6],
                    "maximum": result[7],
                },
            ],
            [{"name": "Measure", "id": "measure"}]
            + [
                {
                    "name": x,
                    "id": x.lower(),
                    "type": "numeric",
                    "format": Format(precision=4, scheme=Scheme.fixed),
                }
                for x in col_names[1:]
            ],
            [{"market_value": result[8]}],
            [
                {
                    "name": "Market value",
                    "id": "market_value",
                    "type": "numeric",
                    "format": FormatTemplate.money(2),
                }
            ],
        )
