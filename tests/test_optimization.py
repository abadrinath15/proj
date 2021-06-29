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


@pytest.fixture
def single_date_data() -> pd.DataFrame:
    df = pd.read_csv("data/universe.csv")
    df.columns = [x.lower() for x in df.columns]
    df["effdate"] = pd.to_datetime(df["effdate"], format="%m/%d/%Y")
    df = df[df["effdate"] == dt.datetime(2020, 2, 29)]
    return df
