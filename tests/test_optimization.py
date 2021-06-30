import pytest
import pandas as pd
from proj.optimization import do_optimization
import datetime as dt


def test_infeasible(single_date_data: pd.DataFrame):
    # We'll provide a very small number of bonds (10); even with the highest sector
    # weights it's impossible for duration to hit targets. As such we should expect
    # an infeasible result
    small_sample = single_date_data.head(10)
    industrial_df = small_sample[small_sample["class_2"] == "INDUSTRIAL"]
    financial_df = small_sample[small_sample["class_2"] == "FINANCIAL"]
    utility_df = small_sample[small_sample["class_2"] == "UTILITY"]
    assert (
        do_optimization(industrial_df, financial_df, utility_df, 0.03, 3.5, 0.3, "oas")
        is None
    )


def test_results_within_bounds(single_date_data: pd.DataFrame):
    industrial_df = single_date_data[single_date_data["class_2"] == "INDUSTRIAL"]
    financial_df = single_date_data[single_date_data["class_2"] == "FINANCIAL"]
    utility_df = single_date_data[single_date_data["class_2"] == "UTILITY"]
    security_bound = 0.03
    dur_target = 3.5
    sector_bound = 0.3
    metric = "oas"
    res, wts = do_optimization(
        industrial_df,
        financial_df,
        utility_df,
        security_bound,
        dur_target,
        sector_bound,
        metric,
    )
    wts = pd.DataFrame(wts, columns=["cusip", "wt"])
    wts = wts.set_index("cusip").join(single_date_data.set_index(["cusip"]))
    assert sum(wts["wt"] * wts["effdur"]) == pytest.approx(dur_target, abs=1e-6)
    assert all(security_bound >= wt for wt in wts["wt"])
    assert all(
        sector_bound > c_s or sector_bound == pytest.approx(c_s, 1e-6)
        for c_s in [
            sum(wts[wts["class_2"] == class_i]["wt"])
            for class_i in ["INDUSTRIAL", "FINANCIAL", "UTILITY"]
        ]
    )


@pytest.fixture
def single_date_data() -> pd.DataFrame:
    df = pd.read_csv("data/universe.csv")
    df.columns = [x.lower() for x in df.columns]
    df["effdate"] = pd.to_datetime(df["effdate"], format="%m/%d/%Y")
    df = df[df["effdate"] == dt.datetime(2020, 2, 29)]
    return df
