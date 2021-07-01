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
from dash_table import FormatTemplate
from sqlalchemy import distinct, select, true
from sqlalchemy.sql import func
from itertools import chain
from optimization import do_optimization


def register_callbacks(app, db: SQLAlchemy, Bond: Model) -> None:
    """Avoid circular importsby passing in the application, database, and bond model
    and create the callbacks from them (essentially a decorator pattern)

    Args:
        app: dash dash application
        db (SQLAlchemy): sqlalchmey db object
        Bond (Model): bond model

    """
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
        """Update class filter dropdown to reflect choice of class type and date

        Args:
            date_value (dt.date): date selected
            class_type (Optional[str]): class type selected, ex class_1

        Returns:
            Tuple[html.Div, List[Dict[str, str]], bool, None]: Tuple of: label above
            the class filter box, class filter options, class filter box enabledness,
            class filter value placeholder
        """
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
        """Refresh summary table contents upon changing options

        Args:
            date_value (dt.datetime): date selected
            class_values (Optional[List[str]]): class selected, may be none
            rating_values (Optional[List[str]]): ratings values selected, may be none
            dur_cell_values (Optional[List[str]]): duration cell values selected, may
            be none
            class_type (Optional[str]): class type, does not refresh upon change as
            the class value really determines a selection

        Returns:
            Tuple[ List[dict[str, Union[str, int]]], List[dict],
            List[dict[str, Union[str, int]]], List[dict], ]: [description]
        """
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
        State("duration_target", "min"),
        State("duration_target", "max"),
        State("sector_limit", "min"),
        State("sector_limit", "max"),
    )
    def enable_opt_button(
        duration_target: Optional[float],
        sector_limit: Optional[float],
        dur_min: float,
        dur_max: float,
        sector_min: float,
        sector_max: float,
    ) -> bool:
        """Blocks the optimization button if invalid duration/sector values are
        selected

        Args:
            duration_target (Optional[float]): duration value
            sector_limit (Optional[float]): sector value
            dur_min (float): duration min boundary
            dur_max (float): duration max boundary
            sector_min (float): sector min boundary
            sector_max (float): sector max boundary

        Returns:
            bool: True to disable button, false to enable it
        """
        if (duration_target is None or sector_limit is None) or any(
            [
                duration_target < dur_min,
                duration_target > dur_max,
                sector_limit < sector_min,
                sector_limit > sector_max,
            ]
        ):
            return True
        return False

    @app.callback(
        (
            Output("opt_summary", "data"),
            Output("industrial_results", "data"),
            Output("financials_results", "data"),
            Output("utility_results", "data"),
            Output("industrial_results", "columns"),
            Output("financials_results", "columns"),
            Output("utility_results", "columns"),
            Output("opt_summary", "columns"),
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
        List[dict],
        List[dict],
        List[dict],
        List[dict],
    ]:
        """Reads inputs/filters to optimization routine and outputs to tables

        Args:
            n_clicks (Optional[int]): placeholder for checking if button is clicked
            date_value (dt.date): date selected
            class_type (str): class selected
            class_values (Optional[List[str]]): class values
            rating_values (Optional[List[str]]): ratings values
            dur_cell_values (Optional[List[str]]): duration cell values
            opt_metric (str): optimization metricj
            sec_bound (float): single security weight constraint
            duration_bound (float): duration target
            sector_limit (float): sector limit constraint

        Returns:
            Tuple[ List[Dict[str, Union[str, float]]], List[Dict[str, Union[str, float]]], List[Dict[str, Union[str, float]]], List[Dict[str, Union[str, float]]], List[dict], List[dict], List[dict], List[dict], ]: [description]
        """
        wt_cols_names = ["cusip", "ticker", "mat_dt", "wt"]
        blanks = [{x: "--" for x in wt_cols_names}]
        percentage = FormatTemplate.percentage(2)
        wt_col_dicts = [
            {"name": x, "id": y}
            for x, y in zip(
                ["Cusip", "Ticker", "Maturity date", "Weight"], wt_cols_names
            )
        ]
        if n_clicks is None or n_clicks == 0:
            return (
                [{x: "--" for x in ["opt_res", "cash_wt"]}],
                blanks,
                blanks,
                blanks,
                wt_col_dicts,
                wt_col_dicts,
                wt_col_dicts,
                [
                    {"name": "Result", "id": "opt_res"},
                    {"name": "Cash weight", "id": "cash_wt"},
                ],
            )
        # Rescale sector limit to be a percentage
        sector_limit = sector_limit / 100
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
            Bond.mat_dt,
            Bond.ticker,
        ).where(*where_clauses)
        try:
            result = list(db.session.execute(stmt))
        except IndexError:
            return (
                [{"opt_res": "0", "cash_wt": 1}],
                blanks,
                blanks,
                blanks,
                wt_col_dicts,
                wt_col_dicts,
                wt_col_dicts,
                [
                    {"name": "Result", "id": "opt_res"},
                    {"name": "Cash weight", "id": "cash_wt", "format": percentage},
                ],
            )
        df = pd.DataFrame(
            result,
            columns=["cusip", "oas", "ytm", "class_2", "effdur", "mat_dt", "ticker"],
        )
        df["mat_dt"] = pd.to_datetime(df["mat_dt"], format="%m/%d/%Y").dt.date
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
                blanks,
                blanks,
                blanks,
                wt_col_dicts,
                wt_col_dicts,
                wt_col_dicts,
                [
                    {"name": "Result", "id": "opt_res"},
                    {"name": "Cash weight", "id": "cash_wt"},
                ],
            )
        res_max, cusip_wts = opt_results
        cusip_wts = pd.DataFrame(cusip_wts, columns=["cusip", "wts"]).set_index("cusip")

        def get_sector_wts(
            sector_df: pd.DataFrame,
        ) -> pd.DataFrame:
            res_df: pd.DataFrame = (
                sector_df.set_index("cusip")
                .join(cusip_wts)[["ticker", "mat_dt", "wts"]]
                .query("""wts > 0""")
                .sort_values(
                    ["wts", "ticker", "mat_dt"], ascending=[False, True, False]
                )
                .reset_index()
            )
            return res_df.append(
                pd.Series(
                    ["--", "--", "Total", res_df["wts"].sum()], index=res_df.columns
                ),
                ignore_index=True,
            )

        industrial_res, financial_res, utility_res = [
            get_sector_wts(sector_df)
            for sector_df in [industrial_df, financial_df, utility_df]
        ]

        cash_wt = 1 - (
            industrial_res.iloc[-1]["wts"]
            + financial_res.iloc[-1]["wts"]
            + utility_res.iloc[-1]["wts"]
        )
        non_blank_cols = [
            {"name": "Cusip", "id": "cusip"},
            {"name": "Ticker", "id": "ticker"},
            {"name": "Maturity date", "id": "mat_dt"},
            {"name": "Weight", "id": "wts", "type": "numeric", "format": percentage},
        ]

        def _nice_data_values(df: pd.DataFrame) -> pd.DataFrame:
            """[summary]

            Args:
                df (pd.DataFrame): [description]

            Returns:
                pd.DataFrame: [description]
            """
            return blanks if df.empty else df.to_dict("records")

        def _nice_col_types(df) -> Union[List[Dict[str, str]], dict]:
            """Quick helper function to not keep writing the same conditionals over
            and over; returns numeric types if the dataframe is non-empty, allows for
            blanks when it is

            Args:
                df (pd.DataFrame): [description]

            Returns:
                Union[List[Dict[str, str]], dict]: nice numeric column types if the
                input dataframe is not empty blanks if it is
            """

            return wt_col_dicts if df.empty else non_blank_cols

        return (
            [{"opt_res": res_max, "cash_wt": cash_wt}],
            *[
                _nice_data_values(x)
                for x in [industrial_res, financial_res, utility_res]
            ],
            *[_nice_col_types(x) for x in [industrial_res, financial_res, utility_res]],
            [
                {
                    "name": "Result",
                    "id": "opt_res",
                    "type": "numeric",
                    "format": Format(precision=2, scheme=Scheme.fixed),
                },
                {
                    "name": "Cash weight",
                    "id": "cash_wt",
                    "type": "numeric",
                    "format": percentage,
                },
            ],
        )
