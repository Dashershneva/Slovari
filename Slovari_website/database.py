import sqlite3
from flask import Flask
from flask import g

app = Flask(__name__)

DATABASE = 'slovari.db'

@app.before_request
def before_request():
    g.db = sqlite3.connect(DATABASE)
		
@app.route('/')
def string():
    string = g.db.execute("SELECT orth, ant FROM test WHERE id = 13").fetchall()
    return str(string)

if __name__ == '__main__':
    app.run(debug=True)