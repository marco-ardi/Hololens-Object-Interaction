from flask import Flask
import os



app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
def get_images():
    result = [f for f in os.listdir("./static") if os.path.isfile(os.path.join("./static/", f))]
    #html=''
    html = '<meta http-equiv="refresh" content="11">'
    html+="\n"
    for x in result:
        html += '<img src="./static/{}"/>'.format(x)
    return html
