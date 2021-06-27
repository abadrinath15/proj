"""In order to avoid concers that we're going to certainly have with the flask
application name and circular loops, we'll define all the callbacks here and 
register them
"""

from dash.dependencies import Input, Output, State
from typing import Dict, List, Optional, Tuple, Final
from sqlalchemy import distinct, select
import dash_html_components as html
from flask_sqlalchemy import Model, SQLAlchemy


def register_callbacks(app, db: SQLAlchemy, Bond: Model):
    CLASS_DICT: Final = {
        "class_1": [html.Label("Class 1 choice"), Bond.class_1],
        "class_2": [html.Label("Class 2 choice"), Bond.class_2],
        "class_3": [html.Label("Class 3 choice"), Bond.class_3],
        "class_4": [html.Label("Class 4 choice"), Bond.class_4],
    }

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

        class_label, class_obj = CLASS_DICT[class_choice]
        stmt = select(distinct(class_obj))
        result = db.session.execute(stmt)
        return class_label, [{"label": x[0], "value": x[0]} for x in result], False

    @app.callback(
        (Output("rating_filter", "options"), Output("rating_filter", "disabled")),
        Input("class_values", "disabled"),
        Input("class_values", "value"),
        State("class_choice", "value"),
    )
    def update_rating_filter(
        class_values_disabled: bool,
        class_value: Optional[str],
        class_choice: Optional[str],
    ) -> Tuple[List[Dict[str, str]], bool]:
        if class_value is None or class_value == "" or class_values_disabled:
            return [], True
        _, class_obj = CLASS_DICT[class_choice]
        stmt = select(distinct(Bond.rating)).where(class_obj == class_value)
        result = db.session.execute(stmt)
        return [{"label": x[0], "value": x[0]} for x in result], False
