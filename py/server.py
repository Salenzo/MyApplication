import requests
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<script>requestAnimationFrame(() => location.href='?frame='+location.query)"

app.run()