"""This module connects the code for connecting to the PostgreSql server."""
from flask_sqlalchemy import Model, SQLAlchemy


def build_bond(db: SQLAlchemy) -> Model:
    class Bond(db.Model):
        """
        SQLAlchemy db object representing the bond universe; only columns as needed
        are modelled

        """

        __tablename__ = "main_table"
        u_id = db.Column("id", db.Integer, nullable=False, primary_key=True)
        eff_date = db.Column(db.Date, nullable=False)
        class_1 = db.Column(db.String, nullable=False)
        class_2 = db.Column(db.String, nullable=False)
        class_3 = db.Column(db.String, nullable=False)
        class_4 = db.Column(db.String, nullable=False)
        rating = db.Column(db.String, nullable=False)
        dur_cell = db.Column(db.String, nullable=False)
        oas = db.Column(db.Numeric, nullable=False)
        ytm = db.Column(db.Numeric, nullable=False)
        mv = db.Column(db.Numeric, nullable=False)
        effdur = db.Column(db.Numeric, nullable=False)
        cusip = db.Column(db.String, nullable=False)
        ticker = db.Column(db.String, nullable=False)
        mat_dt = db.Column(db.String, nullable=False)

        def __init__(
            self,
            u_id,
            eff_date,
            class_1,
            class_2,
            class_3,
            class_4,
            rating,
            dur_cell,
            mv,
            effdur,
            cusip,
            ticker,
            mat_dt,
        ) -> None:
            self.u_id = u_id
            self.eff_date = eff_date
            self.class_1 = class_1
            self.class_2 = class_2
            self.class_3 = class_3
            self.class_4 = class_4
            self.rating = rating
            self.dur_cell = dur_cell
            self.mv = mv
            self.effdur = effdur
            self.cusip = (cusip,)
            self.ticker = (ticker,)
            self.mat_dt = mat_dt

    return Bond
