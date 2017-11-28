# -*- coding: utf-8 -*-

from flask import Flask, request, json, Response, render_template_string, abort, render_template, jsonify

app = Flask(__name__)

@app.route("/Vyshka_slovari_main")
def main_page():
	return render_template("Slovar_main.html")
	
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