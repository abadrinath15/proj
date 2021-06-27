"""This is the application module.
"""
import dash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from layout import layout
from callbacks import register_callbacks
from db_connect import build_bond

# Create the dash app
server = Flask(__name__)
app = dash.Dash(name=__name__, server=server, suppress_callback_exceptions=True)
app.server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Connection for a local postgres test table
app.server.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://aditya:postgres@localhost/bond_universe"

db = SQLAlchemy(app.server)
app.layout = layout
Bond = build_bond(db)
register_callbacks(app, db, Bond)

if __name__ == "__main__":
    app.run_server(debug=True)
