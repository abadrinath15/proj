"""In order to avoid concers that we're going to certainly have with the flask
application name and circular loops, we'll define all the callbacks here and register 
them
"""

from dash.dependencies import Input, Output, State
from typing import Dict, List, Optional, Tuple, Final
from sqlalchemy import distinct, select
import dash_html_components as html
from flask_sqlalchemy import Model, SQLAlchemy
import datetime as dt


def register_callbacks(app, db: SQLAlchemy, Bond: Model):
    # Quick dictionary to reduce conditional bond_object lookups
    CLASS_DICT: Final = {
        "class_1": [html.Label("Class 1 choice"), Bond.class_1],
        "class_2": [html.Label("Class 2 choice"), Bond.class_2],
        "class_3": [html.Label("Class 3 choice"), Bond.class_3],
        "class_4": [html.Label("Class 4 choice"), Bond.class_4],
    }
    # rating and dur_cell if sorted naturally (alphabetically) are really ugly; we'll
    # define a formal sort order for both and reference them. The ceaveat to that is
    # these would need to be maintained manually...
    RATING_ORDER: Final = {"AAA": 0, "AA": 1, "A": 2, "BBB": 3}
    DUR_CELL_ORDER: Final = {
        "0to3": 0,
        "3to5": 1,
        "5to8": 2,
        "8to10": 3,
        "10to15": 4,
        "15+": 5,
    }

    @app.callback(
        (
            Output("class_label", "children"),
            Output("class_values", "options"),
            Output("class_values", "disabled"),
        ),
        Input("date_filter", "value"),
        Input("class_choice", "value"),
    )
    def update_class_for_choices(
        date_value: Optional[dt.date],
        class_choice: Optional[str],
    ) -> Tuple[html.Div, List[Dict[str, str]], bool]:
        if date_value is None or class_choice is None:
            return html.Label("Class value"), [], True

        class_label, class_obj = CLASS_DICT[class_choice]
        stmt = select(distinct(class_obj)).where(Bond.eff_date == date_value)
        result = db.session.execute(stmt)
        return class_label, [{"label": x[0], "value": x[0]} for x in result], False

    @app.callback(
        (Output("rating_filter", "options"), Output("rating_filter", "disabled")),
        Input("class_values", "disabled"),
        Input("class_values", "value"),
        State("date_filter", "value"),
        State("class_choice", "value"),
    )
    def update_rating_filter(
        class_values_disabled: bool,
        class_value: Optional[str],
        date_value: Optional[dt.datetime],
        class_choice: Optional[str],
    ) -> Tuple[List[Dict[str, str]], bool]:
        if class_value is None or class_values_disabled:
            return [], True
        _, class_obj = CLASS_DICT[class_choice]
        stmt = select(distinct(Bond.rating)).where(
            class_obj == class_value, Bond.eff_date == date_value
        )
        result = db.session.execute(stmt)
        ordered_results = [x[0] for x in result]
        ordered_results.sort(key=lambda val: RATING_ORDER[val])
        return [{"label": x, "value": x} for x in ordered_results], False

    @app.callback(
        (Output("dur_cell_filter", "options"), Output("dur_cell_filter", "disabled")),
        Input("rating_filter", "value"),
        Input("rating_filter", "disabled"),
        State("date_filter", "value"),
        State("class_choice", "value"),
        State("class_values", "value"),
    )
    def update_dur_cell_filter(
        rating_value: Optional[str],
        rating_disabled: Optional[str],
        date_value: Optional[dt.datetime],
        class_choice: Optional[str],
        class_value: Optional[str],
    ) -> Tuple[List[Dict[str, str]], bool]:
        if rating_value is None or rating_disabled:
            return [], True
        _, class_obj = CLASS_DICT[class_choice]
        stmt = select(distinct(Bond.dur_cell)).where(
            class_obj == class_value,
            Bond.eff_date == date_value,
            Bond.rating == rating_value,
        )
        result = db.session.execute(stmt)
        ordered_results = [x[0] for x in result]
        ordered_results.sort(key=lambda val: DUR_CELL_ORDER[val])
        return [{"label": x, "value": x} for x in ordered_results], False
