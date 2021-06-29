"""This is the application module.
"""
import os
from typing import Final

import dash
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct, select
import dash_bootstrap_components as dbc

from summaries import generate_summary_layout
from callbacks import register_callbacks
from db_structure import build_bond

load_dotenv()

# Create the dash app
server = Flask(__name__)
app = dash.Dash(
    name=__name__,
    server=server,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
app.server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Connection for a local postgres test table
uri = os.environ.get("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.server.config["SQLALCHEMY_DATABASE_URI"] = uri
db = SQLAlchemy(app.server)
Bond = build_bond(db)
# We'll go ahead and process the unique values for all dropdowns here
# Dates
stmt = select(distinct(Bond.eff_date))
dates = sorted([x[0] for x in db.session.execute(stmt)])

# Rating and dur_cell if sorted naturally (alphabetically) are really ugly; we'll
# define a formal sort order for both and reference them. The ceaveat to that is
# these would need to be maintained manually...

# Ratings
RATING_ORDER: Final = {"AAA": 0, "AA": 1, "A": 2, "BBB": 3}
stmt = select(distinct(Bond.rating))
ratings = sorted(
    [x[0] for x in db.session.execute(stmt)], key=lambda y: RATING_ORDER[y]
)

# Dur_cell
DUR_CELL_ORDER: Final = {
    "0to3": 0,
    "3to5": 1,
    "5to8": 2,
    "8to10": 3,
    "10to15": 4,
    "15+": 5,
}
stmt = select(distinct(Bond.dur_cell))
dur_cells = sorted(
    [x[0] for x in db.session.execute(stmt)], key=lambda y: DUR_CELL_ORDER[y]
)
app.layout = generate_summary_layout(dates, ratings, dur_cells)
register_callbacks(app, db, Bond)

if __name__ == "__main__":
    app.run_server(debug=True)
