"""This is the application module.
"""
import dash
import dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct, select
from apps.summaries import generate_summary_layout
from callbacks import register_callbacks
from db_structure import build_bond
import os
import re
from dotenv import load_dotenv

load_dotenv()

# Create the dash app
server = Flask(__name__)
app = dash.Dash(name=__name__, server=server, suppress_callback_exceptions=True)
app.server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Connection for a local postgres test table
uri = os.environ.get("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.server.config["SQLALCHEMY_DATABASE_URI"] = uri
db = SQLAlchemy(app.server)
Bond = build_bond(db)
# Dates are independent of user input, so we'll go ahead and get that done now
stmt = select(distinct(Bond.eff_date))
result = db.session.execute(stmt)
app.layout = generate_summary_layout(sorted([x[0] for x in result]))
register_callbacks(app, db, Bond)

if __name__ == "__main__":
    app.run_server(debug=True)
