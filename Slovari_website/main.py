# -*- coding: utf-8 -*-

from flask import Flask, request, json, Response, render_template_string, abort, render_template, jsonify, g
import sqlite3

app = Flask(__name__)

DATABASE = 'C:\\Users\\dsher\\PycharmProjects\\Tests\\slovari.db'

@app.before_request
def before_request():
    g.db = sqlite3.connect(DATABASE)

@app.route("/Vyshka_slovari_main", methods=['POST', 'GET'])
def main_page():
    return render_template("Slovar_main.html")

@app.route('/Vyshka_slovari_main/<word>')
def show_entries(word):
    mng1 = g.db.execute("SELECT sense, dic_name FROM test WHERE orth='%s' AND dic_name='Большой Энциклопедический Словарь'" % word).fetchall()
    mng2 = g.db.execute("SELECT sense, dic_name FROM test WHERE orth='%s' AND dic_name=' \"Толковый словарь Кузнецова\" '" % word).fetchall()
    syn = g.db.execute("SELECT ant, dic_name FROM test WHERE orth='%s' AND dic_name='Словарь антонимов'" % word).fetchall()
    ant = g.db.execute("SELECT syn, dic_name FROM test WHERE orth='%s' AND dic_name='Словарь русских синонимов и сходных по смыслу выражений'" % word).fetchall()
    return render_template('Show_entries.html',
                           synonyms=syn[0],
                           antonyms=ant[0],
                           meaning1=mng1,
                           meaning2=mng2)

@app.route("/Vyshka_slovari_about")
def about_page():
    return render_template('Slovar_about.html')

@app.route("/Vyshka_slovari_extended_search")
def extended_search_page():
    return render_template('Slovar_extended_search.html')
	
@app.route("/Vyshka_slovari_enter")
def enter_page():
    return render_template('Slovar_enter.html')
	
@app.route("/Vyshka_slovari_register")
def register_page():
    return render_template('Slovar_register.html')
	
if __name__ == "__main__":
    app.run(debug=True)