from flask import Flask
import datetime

app = Flask(__name__)

@app.route("/")
def hello_world():
    current_year = datetime.datetime.now().year
    return f"encore un vieux 3 0 de ces morts {current_year}"