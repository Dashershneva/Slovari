#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, json, Response, render_template_string, abort, render_template, jsonify
from flask import g, url_for, redirect, send_from_directory
from flask_wtf import Form
from wtforms import StringField, PasswordField, SelectField, SelectMultipleField, BooleanField, RadioField
from wtforms.validators import InputRequired
import sqlite3
import re
import traceback
from lxml import etree
import os
import csv
from flask_login import LoginManager, current_user, login_required, login_user, logout_user, LoginManager, UserMixin
from werkzeug import secure_filename
import shutil
import os.path
import string, random

UPLOAD_FOLDER = 'csv_result'
UGC_UPLOAD_FOLDER = 'users'
ALLOWED_EXTENSIONS = set(['csv'])
BASE_DIR = os.path.dirname(__file__)
db_path = os.path.join(BASE_DIR, 'slovari.db')
csv_path = os.path.join(BASE_DIR, 'csv_result/results.csv')
scheme_path = os.path.join(BASE_DIR, 'scheme.xsd')
users_path = os.path.join(BASE_DIR, 'users.csv')
# users_dir_path = 'users'
folder_path = os.path.join(BASE_DIR, 'csv_result/')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Do not tell anyone'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#DATABASE = 'slovari.db'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    from models import User
    f = open(users_path, 'r', encoding='utf8').read().split('\n')
    for line in f:
        line = line.split(';')
        uid = int(line[0])
    return uid


def handle_exception(val):
    val_new = [("Нет информации", "—")]
    if val == []:
        return val_new
    if val[0][0] is None:
        return val_new
    if val[0][0] is not None:
        return val

def handle_gram(val):
    val_new = (' — ',)
    if val == []:
        return val_new
    if val[0][0] is None:
        return val_new
    if val[0][0] is not None:
        return val[0]

def secure_query(word):
    re_clr = re.compile(u"[^a-zа-яё‘]", re.I + re.U)
    word = re_clr.sub(u' ', word)
    if len(word.split()) > 1:
        word = word.split()[0]
    return word

#extended search fields names
pos_labels = [(' сущ. ','Существительное'),(' глаг. ','Глагол'),
              (' прил. ','Прилагательное'),(' нареч. ', 'Наречие'), (' числ. ', 'Числительное'), (' част. ','Частица'),
              (' предлог ','Предлог'), (' межд. ','Междометие')]
gender_labels = [(' ж. ','Женский'), (' м. ','Мужской'), (' ср. ','Средний')]
aspect_labels = [(' св. ','Совершенный'), (' нсв. ','Несовершенный')]
borrowings_labels = [('азерб.','Азербайджанский'),('англ.','Английский'),('голл.','Голландский'),
                     ('греч.','Греческий'),('исп.','Испанский'),('итал.', 'Итальянский'),('лат.','Латинский'),
                     ('нем.','Немецкий'),('норв.','Норвежский'),('перс.','Персидский'),('польск.', 'Польский'),
                     ('португ.','Португальский'),('румын.','Румынский'),('санкр.','Санскрит'),('сканд.','Скандинавское'),
                     ('ст.-слав.', 'Старославянский'),('тур.','Турецкий'),('тюрк.','Тюркское'),('узбек.','Узбекский'),
                     ('укр.','Украинский'), ('фин.', 'Финский'),('фр.','Французский'),('швед.','Шведский'),
                     ('япон.','Японский')]
marker_labels = [('авиа.','Авиационное'), ('анат.','Анатомическое'), ('антроп.','Антропологическое'),
                 ('археол.','Археологическое'), ('биол.','Биологическое'), ('бухг.','Бухгалтерское'),
                 ('воен.','Военное'),('вульг.','Вульгарное'), ('геогр.','Географическое'),('геод.','Геодезическое'),
                 ('геол.', 'Геологическое'),('горн.','Горное дело'),('дипл.','Дипломатическое'),
                 ('ж.-д.','Железнодорожное'),('жарг.','Жаргонное'), ('зоол.','Зоологическое'), ('ирон.','Ироничное'),
                 ('ист.','Историческое'), ('кино.','Кинематографическое'), ('книжн.','Книжное'),
                 ('ласк.','Ласкательное'), ('лингв.','Лингвистическое'),('лит.', 'Литературное'),('лог.','Логическое'),
                 ('матем.','Математическое'), ('мед.','Медицинское'),('метео.','Метеорологическое'), ('мор.','Морское'),
                 ('муз.','Музыкальное'), ('нар.-поэт.','Народно-поэтическое'),('нар.-разг.','Народно-разговорное'),
                 ('неодобр.','Неодобрительное'), ('офиц.','Официальное'),('полигр.','Полиграфическое'),
                 ('почтит.','Почтительное'), ('поэт.','Поэтическое'), ('презрит.','Презрительное'),
                 ('пренебр.','Пренебрежительное'), ('пчел.','Пчеловодческое'), ('разг.','Разговорное'),
                 ('разг.-сниж.','Разговорно-сниженное'),('рыб.','Рыболовное'),('с.-х.','Сельскохозяйственное'),
                 ('сад.','Садоводческое'),('смягчит.','Смягчительное'),('спорт.','Спортивное'),('театр.','Театральное'),
                 ('типогр.','Типографическое'),('трад.-нар.','Традиционно-народное'),
                 ('трад.-поэт.','Традиционно-поэтическое'), ('уменьш.','Уменьшительное'),
                 ('уменьш.-ласк.','Уменьшительно-ласкательное'), ('уничиж.','Уничижительное'), ('фам.','Фамильярное'),
                 ('физ.','Физическое'), ('физиол.','Физиологическое'),('филос.','Философское'),
                 ('фото.','Фотографическое'), ('хим.','Химическое'), ('церк.','Церковное'),
                 ('шутл.','Шутливое'), ('экон.','Экономическое'), ('электр.','Электрическое'), ('ювел.','Ювелирное')]

dict_labels = [(' Словарь эпитетов ',' Словарь эпитетов '),
               ('Большой Энциклопедический Словарь','Большой Энциклопедический Словарь'),
               ('Словарь антонимов','Словарь антонимов'),
               ('Словарь русских синонимов и сходных по смыслу выражений',
                'Словарь русских синонимов и сходных по смыслу выражений'),
               ('Толковый словарь Кузнецова','Толковый словарь Кузнецова')]

#defining form fields for extended search
class MyForm(Form):
    noun_field = RadioField('POS', choices=pos_labels)
    gender_field = RadioField('GENDER', choices=gender_labels)
    aspect_field = RadioField('ASPECT', choices=aspect_labels)
    borrowings_field = SelectMultipleField('BORROWINGS', choices=borrowings_labels)
    marker_field = SelectMultipleField('MARKERS', choices=marker_labels)
    dict_field = SelectMultipleField('DICTIONARY', choices=dict_labels)


class User(UserMixin):
    def __init__(self, email, uid, firstname, lastname, active=True):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.id = uid
        self.active = active

    def is_authenticated():
        return True

    def is_active():
        return True

    def is_anonymous():
        return False

    def get_id(self):
        return self.id

    def get_files(self):
        all_files = os.listdir(os.path.join(BASE_DIR, UGC_UPLOAD_FOLDER))
        user_files = [f for f in all_files if 'uid%s_'%self.id in f]
        return user_files

    def count_files(self):
        all_files = os.listdir(os.path.join(BASE_DIR, UGC_UPLOAD_FOLDER))
        user_files = [f for f in all_files if 'uid%s_'%self.id in f]
        return len(user_files)




@login_manager.user_loader
def load_user(user_id):

    user_id = str(user_id)
    uid, firstname, lastname, email = '', '', '', ''

    f = open(users_path, 'r', encoding='utf8').read().split('\n')
    for line in f:
        line = line.split(';')
        if line[0] == user_id:
            uid = line[0]
            firstname = line[1]
            lastname = line[2]
            email = line[3]
            active = True
            break

    if uid == '':
        print('no such user')
        return None
    else:
        return User(email, uid, firstname, lastname, active)


@app.before_first_request
def before_first_request():
    ld = os.listdir(os.getcwd())
    # if 'users.csv' not in ld:
    #     f = open(users_path, 'w', encoding='utf8')
    #     f.write('id;name;lname;email;password')
    #     f.close()
    # else:
    #     pass
    #     # print('users.csv located')
    # if 'users' not in ld:
    #     os.mkdir(os.path.join(os.getcwd(), 'users'))
    # else:
    #     pass
    #     # print('users folder located')
    # f = open(users_path, 'r', encoding='utf8')
    # for line in f:
    #     uid = line.split(';')[0]
    #     if uid != 'id':
    #         try:
    #             os.mkdir(os.path.join(os.getcwd(), 'users/%s'%uid))
    #         except Exception as e:
    #             print('user %s folder exists'%uid)





@app.before_request
def before_request():
    g.db = sqlite3.connect(db_path)
    g.user = current_user

@app.route("/")
@app.route("/Vyshka_slovari_main", methods=['POST', 'GET'])
def main_page():
    rand_word = g.db.execute("SELECT * FROM test WHERE usg = 'книжн.' ORDER BY RANDOM() LIMIT 1").fetchall()
    rand_word = handle_exception(rand_word)
    print("rand: ", rand_word[0][1])
    return render_template("Show_random.html",
                           rand_word=rand_word
                           )

@app.route('/Vyshka_slovari_main/<word>', methods=['POST', 'GET'])
def show_entries(word):
    word = word.lower()
    word = secure_query(word)
    mng1 = g.db.execute(
        "SELECT sense, dic_name FROM test WHERE orth='%s' \
         AND dic_name='Большой Энциклопедический Словарь'" % word).fetchall()
    mng2 = g.db.execute(
        "SELECT sense, dic_name FROM test WHERE orth='%s' AND dic_name='Толковый словарь Кузнецова'" % word).fetchall()
    ant = g.db.execute(
        "SELECT ant, dic_name FROM test WHERE orth='%s' AND dic_name='Словарь антонимов'" % word).fetchall()
    syn = g.db.execute(
        "SELECT syn, dic_name FROM test WHERE orth='%s' \
         AND dic_name='Словарь русских синонимов и сходных по смыслу выражений'" % word).fetchall()
    epith = g.db.execute(
        "SELECT epith, dic_name FROM test WHERE orth='%s' AND dic_name=' Словарь эпитетов '" % word).fetchall()
    phon = g.db.execute(
        "SELECT phon, dic_name FROM test WHERE orth='%s' AND dic_name='Толковый словарь Кузнецова'" % word).fetchall()
    etym = g.db.execute(
        "SELECT etym, dic_name FROM test WHERE orth='%s' AND dic_name='Толковый словарь Кузнецова'" % word).fetchall()
    usg = g.db.execute(
        "SELECT usg, dic_name FROM test WHERE orth='%s' AND dic_name='Толковый словарь Кузнецова'" % word).fetchall()
    pos = g.db.execute(
        "SELECT pos FROM test WHERE orth='%s' AND dic_name='Толковый словарь Кузнецова'" % word).fetchall()
    gen = g.db.execute(
        "SELECT gender FROM test WHERE orth='%s' AND dic_name='Толковый словарь Кузнецова'" % word).fetchall()
    asp = g.db.execute(
        "SELECT asp FROM test WHERE orth='%s' AND dic_name='Толковый словарь Кузнецова'" % word).fetchall()
    gov = g.db.execute(
        "SELECT gov FROM test WHERE orth='%s' AND dic_name='Толковый словарь Кузнецова'" % word).fetchall()
    examp = g.db.execute(
        "SELECT examp, dic_name FROM test WHERE orth='%s' \
        AND dic_name='Толковый словарь Кузнецова'" % word).fetchall()

    print(word, syn, ant, epith)

    mng1 = handle_exception(mng1)
    mng2 = handle_exception(mng2)
    ant = handle_exception(ant)
    syn = handle_exception(syn)
    epith = handle_exception(epith)
    phon = handle_exception(phon)
    etym = handle_exception(etym)
    usg = handle_exception(usg)
    examp = handle_exception(examp)
    pos = handle_gram(pos)
    gen = handle_gram(gen)
    asp = handle_gram(asp)
    gov = handle_gram(gov)

    print(mng1, word, syn, ant, epith, asp)

    return render_template('Show_entries.html',
                           word=word,
                           synonyms=syn,
                           antonyms=ant,
                           epithets=epith,
                           stress=phon,
                           etymology=etym,
                           usage=usg,
                           example=examp,
                           part_of_speech=pos,
                           gender=gen,
                           aspect=asp,
                           govern=gov,
                           meaning1=mng1,
                           meaning2=mng2)

@app.route("/Vyshka_slovari_about")
def about_page():
    return render_template('Slovar_about.html')

@app.route("/Vyshka_slovari_dictionaries")
def about_dict():
    return render_template('Dictionaries.html')
	
@app.route("/Vyshka_slovari_how_search_works")
def how_search_works():
	return render_template('Slovar_how_search_works.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/Vyshka_slovari_extended_search", methods=['POST', 'GET'])
def extended_search_page():
    form = MyForm()
    if form.is_submitted():
        pos = form.noun_field.data
        gender = form.gender_field.data
        aspect = form.aspect_field.data
        borrowed = form.borrowings_field.data
        marker = form.marker_field.data
        dict = form.dict_field.data
        result = ["По вашему запросу ничего не найдено :("]
        if dict == []:
            dict = '%'
        else:
            dict = dict[0]
        print(pos, gender, aspect, borrowed, marker, dict)
        if pos != 'None':
            if aspect == 'None' and gender == 'None'\
                    and borrowed == [] and marker == []:
                result = g.db.execute(
                    "SELECT orth, phon, sense, pos, gender, \
                     asp, dic_name, usg, etym_lang FROM test WHERE pos='%s' AND \
                     dic_name LIKE '%s' AND orth != 'None'" % (pos,dict)).fetchall()
            elif borrowed != [] and aspect == 'None' and gender == 'None' and marker == []:
                result = g.db.execute(
                    "SELECT orth, phon, sense, pos, gender, \
                     asp, dic_name, usg, etym_lang FROM test WHERE pos='%s' \
                     AND etym_lang='%s' AND dic_name LIKE '%s'" % (pos,borrowed[0],dict)).fetchall()
            elif marker != [] and aspect == 'None' and gender == 'None':
                if borrowed == []:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, \
                         asp, dic_name, usg, etym_lang FROM test WHERE pos='%s' \
                         AND usg='%s' AND dic_name LIKE '%s'" % (pos, marker[0], dict)).fetchall()
                else:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, \
                         asp, dic_name, usg, etym_lang FROM test WHERE pos='%s' AND usg='%s' \
                        AND etym_lang='%s' AND dic_name LIKE '%s'" % (pos, marker[0], borrowed[0],dict)).fetchall()
            elif gender != 'None' and aspect == 'None':
                if borrowed == [] and marker == []:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, \
                         asp, dic_name, usg, etym_lang FROM test WHERE gender='%s' \
                         AND pos='%s' AND dic_name LIKE '%s'" % (gender, pos, dict)).fetchall()
                elif borrowed == [] and marker != []:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, \
                         asp, dic_name, usg, etym_lang FROM test WHERE gender='%s' \
                         AND usg='%s' AND dic_name LIKE '%s'" % (gender, marker[0], dict)).fetchall()
                elif borrowed != [] and marker == []:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, \
                         asp, dic_name, usg, etym_lang FROM test WHERE gender='%s' \
                         AND etym_lang='%s' AND dic_name LIKE '%s'" % (gender, borrowed[0], dict)).fetchall()
                else:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, \
                         asp, dic_name, usg, etym_lang FROM test WHERE gender='%s' \
                         AND pos='%s' AND etym_lang='%s' AND usg='%s' \
                          AND dic_name LIKE '%s'" % (gender,pos,borrowed[0],marker[0], dict)).fetchall()
            elif aspect != 'None' and gender == 'None':
                if borrowed == [] and marker == []:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, \
                         asp, dic_name, usg, etym_lang FROM test WHERE pos=' глаг. ' \
                         AND asp='%s' AND dic_name LIKE '%s'" % (aspect, dict)).fetchall()
                elif borrowed != [] and marker == []:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, \
                         asp, dic_name, usg, etym_lang FROM test WHERE pos=' глаг.' \
                         AND asp='%s' AND etym_lang='%s' AND dic_name LIKE '%s'" % (aspect,borrowed[0],dict)).fetchall()
                elif borrowed == [] and marker != []:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, \
                         asp, dic_name, usg, etym_lang FROM test WHERE pos=' глаг. \
                         ' AND asp='%s' AND usg='%s' AND dic_name LIKE '%s'" % (aspect,marker[0],dict)).fetchall()
                else:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, \
                         asp, dic_name, usg, etym_lang FROM test WHERE pos=' глаг. \
                         ' AND asp='%s' AND usg='%s' AND etym_lang='%s' \
                          AND dic_name LIKE '%s'" % (aspect,marker[0], borrowed[0],dict)).fetchall()
        elif borrowed != [] and pos=='None' and gender=='None' and aspect == 'None':
            if marker == []:
                result = g.db.execute(
                    "SELECT orth, phon, sense, pos, gender, \
                     asp, dic_name, usg, etym_lang FROM test WHERE etym_lang='%s' \
                    AND dic_name LIKE '%s'" % (borrowed[0],dict)).fetchall()
            else:
                result = g.db.execute(
                    "SELECT orth, phon, sense, pos, gender, \
                     asp, dic_name, usg, etym_lang FROM test WHERE etym_lang='%s' \
                     AND usg='%s' AND dic_name LIKE '%s'" % (borrowed[0],marker[0],dict)).fetchall()
        elif marker != [] and pos=='None' and gender=='None' and aspect == 'None' and borrowed==[]:
            result = g.db.execute(
                "SELECT orth, phon, sense, pos, gender, \
                 asp, dic_name, usg, etym_lang FROM test WHERE usg='%s' \
                AND dic_name LIKE '%s'" % (marker[0],dict)).fetchall()
        elif dict != '%' and pos=='None' and gender=='None' and aspect == 'None' and marker == [] and borrowed==[]:
            result = g.db.execute(
                "SELECT orth, phon, sense, pos, gender, \
                 asp, dic_name, usg, etym_lang FROM test WHERE dic_name='%s'" % dict).fetchall()
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['orth', 'phon', 'sense', 'pos', 'gender', 'asp', 'dic_name', 'usg', 'etym_lang']
            filewriter = csv.DictWriter(csvfile, delimiter=' ', fieldnames=fieldnames)
            filewriter.writeheader()
            for item in result:
                filewriter.writerow({'orth':str(item[0]), 'phon':str(item[1]),
                                     'sense':str(item[2]), 'pos':str(item[3]),
                                     'gender':str(item[4]), 'asp':str(item[5]),
                                     'dic_name':str(item[6]), 'usg':str(item[7]),
                                     'etym_lang':str(item[8])})
        csvfile.close()
        length = len(result)
        print(result)
        return render_template('Show_extended_entries.html', form=form, result=result, length=length)
    return render_template('Slovar_extended_search.html', form=form)


@app.route('/csv_result/results.csv')
def download():
    return send_from_directory(folder_path, "results.csv")

@app.route('/csv_result/Instruktsia_po_zapolneniyu_shablona_TEI.pdf')
def instruction():
    return send_from_directory(folder_path, "Instruktsia_po_zapolneniyu_shablona_TEI.pdf")

@app.route('/csv_result/TEI-shablon.xlsx')
def template():
    return send_from_directory(folder_path, "TEI-shablon.xlsx")

@app.route("/Vyshka_slovari_enter")
def enter_page():
    return render_template('Slovar_enter.html')


@app.route('/check_user_id', methods=['GET', 'POST'])
def checkUserId():
    registered = False
    email = request.form['e-mail']
    password = request.form['password']

    if not validateEmail(email):
        # return redirect(url_for('enter_page'))
        return render_template('Slovar_enter.html', mistake = 'Неверный формат email')

    db = open(users_path, 'r', encoding='utf8').read().split('\n')
    for line in db:
        if line == '':
            pass
        else:
            e = line.split(';')
            if e[3] == email:
                if e[4] == password:
                    registered = True
                    firstname, lastname = e[1], e[2]
                    break

    if registered:
        uid = int(e[0])
        u = User(email, uid, firstname, lastname)
        login_user(u)
        return redirect(url_for('main_page'))
    else:
        uid =  None
        # print('bad pair login\pw')
        # return redirect(url_for('enter_page'))
        return render_template('Slovar_enter.html', mistake = 'Проверьте правильность логина и пароля')


def validateEmail(email):
    m = re.search('[A-Za-z0-9\.]+@[A-Za-z0-9]+\.[A-Za-z]', email)
    if m:
        return True
    else:
        return False


def validateInput(line):
    m = re.findall('[^A-Z^a-z^А-Я^а-я^0-9^_^\.]', line)
    if m:
        return False
    else:
        return True


@app.route('/new_user', methods=['GET', 'POST'])
def new_user():

    f = open(users_path, 'r', encoding='utf8').read().split('\n')[1:]
    try:
        last_id = int(f[-1].split(';')[0])
    except:
        last_id = 0
    new_id = last_id + 1
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['e-mail']
    password = request.form['password']
    password_check = request.form['password_check']

    mistake = None
    if password != password_check:
        mistake = 'Пароли не совпадают'
    if not validateEmail(email) :
        mistake = 'Неверный формат email'
    for i in [firstname, lastname, password, password_check]:
        if not validateInput(i):
            mistake = 'Недопустимые символы'
            break

    if mistake:
        # return redirect(url_for('main_page'))
        return render_template('Slovar_register.html', mistake=mistake)

    else:
        nu = '%s;%s;%s;%s;%s'%(new_id, firstname, lastname, email, password)
        
        f_ = open(users_path, 'r', encoding='utf8').read()
        f = open(users_path, 'w', encoding='utf8')
        f.write(f_)
        f.write('\n'+nu)
        f.close()

        u = User(email, new_id, firstname, lastname)
        login_user(u)

        return redirect(url_for('main_page'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main_page'))


@app.route("/Vyshka_slovari_register", methods=['GET', 'POST'])
def register_page():
    return render_template('Slovar_register.html', mistake='')


@app.route("/cabinet", methods=['GET', 'POST'])
def cabinet():
    return render_template('cabinet.html', mistake = '')


def validate_slov(fname, SCHEME_FILE=scheme_path):

    with open(SCHEME_FILE) as xsd:
        xmlschema_doc = etree.parse(xsd)
    xmlschema = etree.XMLSchema(xmlschema_doc)

    is_valid = False
    error = []
    name = ''
    try:
        with open(fname, encoding='utf-8') as valid:
            doc = etree.parse(valid)
        xmlschema.assert_(doc)
        is_valid = xmlschema.validate(doc)
        if is_valid:
            name = doc.getroot()[1][0][0].text
    except Exception as e:
        error = traceback.format_exception_only(type(e), e)
        error = re.sub(r'File "(.*)/(.*?)"', 'File "\\2"', ''.join(error))
    return is_valid, error, name


def idGen():
    s = string.ascii_letters + string.digits
    return ''.join([random.choice(s) for _ in range(0,24)])


@app.route("/upload_slov", methods=['GET', 'POST'])
def uploadSlov():
    if request.method == 'POST':
        f = request.files['file']
        new_fname = 'uid%s_%s_%s'%( current_user.id, idGen(), f.filename)
        f.save(os.path.join(BASE_DIR, UGC_UPLOAD_FOLDER, new_fname))

        is_valid = validate_slov(os.path.join(BASE_DIR, UGC_UPLOAD_FOLDER, new_fname))

        if is_valid[0]:
            # shutil.move(os.path.join(BASE_DIR, UGC_UPLOAD_FOLDER))
            return redirect(url_for('cabinet'))
        else:
            os.remove(os.path.join(BASE_DIR, UGC_UPLOAD_FOLDER, new_fname))
            # print(os.listdir(BASE_DIR, UGC_UPLOAD_FOLDER))
            return render_template('cabinet.html', mistake='К сожалению, Ваш словарь не прошел валидацию :(')


if __name__ == "__main__":
    app.run(debug=True)