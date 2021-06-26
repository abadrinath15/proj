"""This is the application module. 
"""

from layout import layout
from db_connect import app


app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=True)
