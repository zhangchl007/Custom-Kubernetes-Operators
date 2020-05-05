# -*- coding: utf-8 -*-

from flask import Flask
app = Flask(__name__)
@app.route("/hi1")
def hello():
    app.config.from_pyfile('/config/config.cfg')
    return app.config['FOO']
@app.route("/hi2")
def hi():
    app.config.from_pyfile('/config/config.cfg')
    return app.config['MSG']
if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True)

