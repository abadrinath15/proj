"""This module will hold the optimization computation."""
from itertools import chain
from typing import List, Tuple

import pandas as pd
import pulp
from pulp.pulp import lpSum


def do_optimization(
    industrial_df: pd.DataFrame,
    financial_df: pd.DataFrame,
    utility_df: pd.DataFrame,
    security_bound: float,
    duration_bound: float,
    sector_bound: float,
    metric_col: str,
) -> Tuple[float, List[Tuple[str, float]]]:
    my_problem = pulp.LpProblem(sense=pulp.LpMaximize)
    industrial_vars, financial_vars, utility_vars = [
        [pulp.LpVariable(x, lowBound=0, upBound=security_bound) for x in df["cusip"]]
        for df in [industrial_df, financial_df, utility_df]
    ]

    def full_weighted_vector(col: str) -> list:
        return [
            wt * metric
            for wt, metric in chain(
                zip(industrial_vars, industrial_df[col]),
                zip(financial_vars, financial_df[col]),
                zip(utility_vars, utility_df[col]),
            )
        ]

    # Objective
    my_problem += lpSum(full_weighted_vector(metric_col))
    # Sum to 1 bound
    my_problem += (
        lpSum(industrial_vars + financial_vars + utility_vars) <= 1,
        "Total weight bound",
    )
    # Duration bound
    my_problem += (
        lpSum(full_weighted_vector("effdur")) == duration_bound,
        "Portfolio duration bound",
    )
    # Sector bounds
    my_problem += (lpSum(industrial_vars) <= sector_bound, "Industrial sector bound")
    my_problem += (lpSum(financial_vars) <= sector_bound, "Financial sector bound")
    my_problem += (lpSum(utility_vars) <= sector_bound, "Utility sector bound")
    status = my_problem.solve()
    if status == 1:
        return my_problem.objective.value(), [
            (var.name, var.value()) for var in my_problem.variables()
        ]
