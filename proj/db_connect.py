import dash
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# Create the dash app
server = Flask(__name__)
app = dash.Dash(name=__name__, server=server, suppress_callback_exceptions=True)
app.server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Connection for a local postgres test table
app.server.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://aditya:postgres@localhost/bond_universe"


# Connection for a heroku table:

db = SQLAlchemy(app.server)


class Bond(db.Model):
    """SQLAlchemy db object representing the bond universe; only columns as needed are modelled

    Args:
        db ([type]): [description]
    """

    __tablename__ = "main_table"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    eff_date = db.Column(db.Date, nullable=False)
    class_1 = db.Column(db.String, nullable=False)
    class_2 = db.Column(db.String, nullable=False)
    class_3 = db.Column(db.String, nullable=False)
    class_4 = db.Column(db.String, nullable=False)
    rating = db.Column(db.String, nullable=False)
    dur_cell = db.Column(db.String, nullable=False)

    def __init__(
        self, id, eff_date, class_1, class_2, class_3, class_4, rating, dur_cell
    ) -> None:
        self.id = id
        self.eff_date = eff_date
        self.class_1 = class_1
        self.class_2 = class_2
        self.class_3 = class_3
        self.class_4 = class_4
        self.rating = rating
        self.dur_cell = dur_cell
