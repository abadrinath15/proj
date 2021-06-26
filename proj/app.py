"""This is the application module. 
"""
import dash
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from layout import layout

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


class BondUniverse(db.Model):
    """SQLAlchemy db object representing the bond universe; only columns as needed are modelled

    Args:
        db ([type]): [description]
    """

    __tablename__ = "bond_table"
    # __mapper_args__ = {
    #     "include_properties": [
    #         "id",
    #         "eff_date",
    #         "class_1",
    #         "class_2",
    #         "class_3",
    #         "class_4",
    #         "rating",
    #         "dur_cell",
    #     ]
    # }
    ID = db.Column(db.Integer, nullable=False, primary_key=True)
    EffDate = db.Column(db.Date, nullable=False)
    Class1 = db.Column(db.String, nullable=False)
    Class2 = db.Column(db.String, nullable=False)
    Class3 = db.Column(db.String, nullable=False)
    Class4 = db.Column(db.String, nullable=False)
    Rating = db.Column(db.String, nullable=False)
    DurCell = db.Column(db.String, nullable=False)

    def __init__(
        self, id, eff_date, class_1, class_2, class_3, class_4, rating, dur_cell
    ) -> None:
        self.ID = id
        self.EffDate = eff_date
        self.Class1 = class_1
        self.Class2 = class_2
        self.Class3 = class_3
        self.Class4 = class_4
        self.Rating = rating
        self.DurCell = dur_cell


app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=True)
