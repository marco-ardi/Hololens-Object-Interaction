from flask import Flask
import os



app = Flask(__name__)

@app.route('/')
def get_images():
    result = [f for f in os.listdir("./static") if os.path.isfile(os.path.join("./static/", f))]
    
    html = '<meta http-equiv="refresh" content="11">'
    for x in result:
        html += '<img src="./static/{}"/>'.format(x)
    return html
