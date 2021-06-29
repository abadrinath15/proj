"""In order to avoid concers that we're going to certainly have with the flask
application name and circular loops, we'll define all the callbacks here and register
them
"""

import datetime as dt
from typing import Dict, Final, List, Optional, Tuple, Union
import pandas as pd
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_table import FormatTemplate
from dash_table.Format import Format, Scheme
from flask_sqlalchemy import Model, SQLAlchemy
from sqlalchemy import distinct, select, true
from sqlalchemy.sql import func
from itertools import chain
from optimization import do_optimization


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
            Output("mv_num_bonds", "data"),
            Output("mv_num_bonds", "columns"),
        ),
        Input("date_filter", "value"),
        Input("class_filter", "value"),
        Input("rating_filter", "value"),
        Input("dur_cell_filter", "value"),
        State("class_type", "value"),
    )
    def update_summary_table(
        date_value: dt.datetime,
        class_values: Optional[List[str]],
        rating_values: Optional[List[str]],
        dur_cell_values: Optional[List[str]],
        class_type: Optional[str],
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
        _, class_obj = CLASS_DICT[class_type]
        where_clauses = [
            Bond.eff_date == date_value,
            true()
            if any([class_obj is None, not class_values])
            else class_obj.in_(class_values),
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
            func.count(Bond.mv),
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
            [{"num_bonds": result[9], "market_value": result[8]}],
            [
                {
                    "name": "Number of bonds",
                    "id": "num_bonds",
                    "type": "numeric",
                    "format": Format(group=","),
                },
                {
                    "name": "Market value",
                    "id": "market_value",
                    "type": "numeric",
                    "format": FormatTemplate.money(2),
                },
            ],
        )

    @app.callback(
        Output("opt_button", "disabled"),
        Input("duration_target", "value"),
        Input("sector_limit", "value"),
    )
    def enable_opt_button(
        duration_target: Optional[float], sector_limit: Optional[float]
    ) -> bool:
        if duration_target is None or sector_limit is None:
            return True
        return False

    @app.callback(
        (
            Output("opt_summary", "data"),
            Output("industrial_results", "data"),
            Output("financials_results", "data"),
            Output("utility_results", "data"),
        ),
        Input("opt_button", "n_clicks"),
        State("date_filter", "value"),
        State("class_type", "value"),
        State("class_filter", "value"),
        State("rating_filter", "value"),
        State("dur_cell_filter", "value"),
        State("opt_metric", "value"),
        State("sec_bound", "value"),
        State("duration_target", "value"),
        State("sector_limit", "value"),
    )
    def populate_optimization_results(
        n_clicks: Optional[int],
        date_value: dt.date,
        class_type: str,
        class_values: Optional[List[str]],
        rating_values: Optional[List[str]],
        dur_cell_values: Optional[List[str]],
        opt_metric: str,
        sec_bound: float,
        duration_bound: float,
        sector_limit: float,
    ) -> Tuple[
        List[Dict[str, Union[str, float]]],
        List[Dict[str, Union[str, float]]],
        List[Dict[str, Union[str, float]]],
        List[Dict[str, Union[str, float]]],
    ]:
        if n_clicks is None or n_clicks == 0:
            return (
                [{"opt_res": "--", "cash_wt": "--"}],
                [{"ind_cusip": "--", "ind_wt": "--"}],
                [{"fin_cusip": "--", "fin_wt": "--"}],
                [{"utl_cusip": "--", "utl_wt": "--"}],
            )
        _, class_obj = CLASS_DICT[class_type]
        where_clauses = [
            Bond.eff_date == date_value,
            true()
            if any([class_obj is None, not class_values])
            else class_obj.in_(class_values),
            true() if not rating_values else Bond.rating.in_(rating_values),
            true() if not dur_cell_values else Bond.dur_cell.in_(dur_cell_values),
        ]
        stmt = select(
            Bond.cusip,
            Bond.oas,
            Bond.ytm,
            Bond.class_2,
            Bond.effdur,
        ).where(*where_clauses)
        try:
            result = list(db.session.execute(stmt))
        except IndexError:
            return (
                [{"opt_res": "0", "cash_wt": 1}],
                [{"ind_cusip": "--", "ind_wt": "--"}],
                [{"fin_cusip": "--", "fin_wt": "--"}],
                [{"utl_cusip": "--", "utl_wt": "--"}],
            )
        df = pd.DataFrame(
            result,
            columns=["cusip", "oas", "ytm", "class_2", "effdur"],
        )
        df["oas"] = df["oas"].astype("float")
        df["ytm"] = df["ytm"].astype("float")
        df["effdur"] = df["effdur"].astype("float")
        industrial_df = df[df["class_2"] == "INDUSTRIAL"]
        financial_df = df[df["class_2"] == "FINANCIAL"]
        utility_df = df[df["class_2"] == "UTILITY"]

        opt_results = do_optimization(
            industrial_df,
            financial_df,
            utility_df,
            sec_bound,
            duration_bound,
            sector_limit,
            opt_metric,
        )
        if opt_results is None:
            return (
                [{"opt_res": "Infeasible", "cash_wt": "--"}],
                [{"ind_cusip": "--", "ind_wt": "--"}],
                [{"fin_cusip": "--", "fin_wt": "--"}],
                [{"utl_cusip": "--", "utl_wt": "--"}],
            )
        res_max, cusip_wts = opt_results
        cusip_wts = pd.DataFrame(cusip_wts, columns=["cusip", "wts"]).set_index("cusip")

        def get_sector_wts(
            sector_df: pd.DataFrame,
            cusip_col: str,
            wt_col: str,
        ) -> pd.DataFrame:
            res_df = (
                sector_df.set_index("cusip")
                .join(cusip_wts)[["wts"]]
                .query("""wts > 0""")
                .sort_values("wts", ascending=False)
                .reset_index()
                .rename(columns={"cusip": cusip_col, "wts": wt_col})
            )
            return res_df.append(
                pd.Series(["Total", res_df[wt_col].sum()], index=res_df.columns),
                ignore_index=True,
            )

        industrial_res, financial_res, utility_res = [
            get_sector_wts(sector_df, cusip_col, wt_col)
            for sector_df, cusip_col, wt_col in zip(
                [industrial_df, financial_df, utility_df],
                ["ind_cusip", "fin_cusip", "utl_cusip"],
                ["ind_wt", "fin_wt", "utl_wt"],
            )
        ]

        cash_wt = 1 - sum(
            [
                industrial_res.iloc[-1]["ind_wt"],
                financial_res.iloc[-1]["fin_wt"],
                utility_res.iloc[-1]["utl_wt"],
            ]
        )
        return (
            [{"opt_res": res_max, "cash_wt": cash_wt}],
            industrial_res.to_dict("records"),
            financial_res.to_dict("records"),
            utility_res.to_dict("records"),
        )
