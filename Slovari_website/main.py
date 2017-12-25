# -*- coding: utf-8 -*-

from flask import Flask, request, json, Response, render_template_string, abort, render_template, jsonify, g, url_for, redirect
from flask_wtf import Form
from wtforms import StringField, PasswordField, SelectField, SelectMultipleField, BooleanField, RadioField
from wtforms.validators import InputRequired
import sqlite3
import re
import os
from flask_login import LoginManager, current_user, login_required, login_user, logout_user, LoginManager, UserMixin
from werkzeug import secure_filename
import shutil

UPLOAD_FOLDER = 'csv_result'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Do not tell anyone'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATABASE = 'C:/Users/dsher/Downloads/slovari.db'


@login_manager.user_loader
def load_user(userid):
    from models import User
    f = open('users.csv', 'r', encoding='utf8').read().split('\n')
    for line in f:
        line = line.split(';')
        uid = int(line[0])
        print(uid)
    return uid


def handle_exception(val):
    val_new = [("пока не знаю)", "—")]
    if val == []:
        return val_new
    if val[0][0] == None:
        return val_new
    if val[0][0] != None:
        return val

def handle_gram(val):
    val_new = (' — ',)
    if val[0][0] == None:
        return val_new
    if val[0][0] != None:
        return val[0]

#extended search fields names
pos_labels = [(' сущ. ','Существительное'),(' глаг. ','Глагол'), (' мест. нареч. ','Местоименное наречие'),(' прил. ','Прилагательное'),
             (' нареч. ', 'Наречие'), (' числ. ', 'Числительное'), (' част. ','Частица'),(' предлог ','Предлог'), (' межд. ','Междометие')]
gender_labels = [(' ж. ','Женский'), (' м. ','Мужской'), (' ср. ','Средний')]
aspect_labels = [(' св. ','Совершенный'), (' нсв. ','Несовершенный')]
borrowings_labels = [('азерб.','Азербайджанский'),('англ.','Английский'),('голл.','Голландский'),('греч.','Греческий'),('исп.','Испанский'),
                     ('итал.', 'Итальянский'),('лат.','Латинский'),('нем.','Немецкий'),('норв.','Норвежский'),('перс.','Персидский'),
                     ('польск.', 'Польский'),('португ.','Португальский'),('румын.','Румынский'),('санкр.','Санскрит'),('сканд.','Скандинавское'),
                     ('ст.-слав.', 'Старославянский'),('тур.','Турецкий'),('тюрк.','Тюркское'),('узбек.','Узбекский'), ('укр.','Украинский'),
                     ('фин.', 'Финский'),('фр.','Французский'),('узбек.','Узбекский'),('швед.','Шведский'),('япон.','Японский')]
marker_labels = [('авиа.','Авиационное'), ('анат.','Анатомическое'), ('антроп.','Антропологическое'), ('археол.','Археологическое'),
                 ('биол.','Биологическое'), ('бухг.','Бухгалтерское'), ('воен.','Военное'),('вульг.','Вульгарное'), ('геогр.','Географическое'),
                 ('геод.','Геодезическое'), ('геол.', 'Геологическое'),('горн.','Горное дело'),('дипл.','Дипломатическое'),
                 ('ж.-д.','Железнодорожное'),('жарг.','Жаргонное'), ('зоол.','Зоологическое'), ('ирон.','Ироничное'),
                 ('ист.','Историческое'), ('кино.','Кинематографическое'), ('книжн.','Книжное'), ('ласк.','Ласкательное'), ('лингв.','Лингвистическое'),
                 ('лит.', 'Литературное'),('лог.','Логическое'), ('матем.','Математическое'), ('мед.','Медицинское'),
                 ('метео.','Метеорологическое'), ('мор.','Морское'), ('муз.','Музыкальное'), ('нар.-поэт.','Народно-поэтическое'),
                 ('нар.-разг.','Народно-разговорное'), ('неодобр.','Неодобрительное'), ('офиц.','Официальное'),
                 ('полигр.','Полиграфическое'), ('почтит.','Почтительное'), ('поэт.','Поэтическое'), ('презрит.','Презрительное'),
                 ('пренебр.','Пренебрежительное'), ('пчел.','Пчеловодческое'), ('разг.','Разговорное'), ('разг.-сниж.','Разговорно-сниженное'),
                 ('рыб.','Рыболовное'),('с.-х.','Сельскохозяйственное'), ('сад.','Садоводческое'),('смягчит.','Смягчительное'),
                 ('спорт.','Спортивное'),('театр.','Театральное'),('типогр.','Типографическое'),('трад.-нар.','Традиционно-народное'),
                 ('трад.-поэт.','Традиционно-поэтическое'), ('уменьш.','Уменьшительное'), ('уменьш.-ласк.','Уменьшительно-ласкательное'),
                 ('уничиж.','Уничижительное'), ('фам.','Фамильярное'), ('физ.','Физическое'), ('физиол.','Физиологическое'),
                 ('филос.','Философское'), ('фото.','Фотографическое'), ('хим.','Химическое'), ('церк.','Церковное'),
                 ('шутл.','Шутливое'), ('экон.','Экономическое'), ('электр.','Электрическое'), ('ювел.','Ювелирное')]

#defining form fields for extended search
class MyForm(Form):
    noun_field = RadioField('POS', choices=pos_labels)
    gender_field = RadioField('GENDER', choices=gender_labels)
    aspect_field = RadioField('ASPECT', choices=aspect_labels)
    borrowings_field = SelectMultipleField('BORROWINGS', choices=borrowings_labels)
    marker_field = SelectMultipleField('MARKERS', choices=marker_labels)


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



@login_manager.user_loader
def load_user(user_id):

    user_id = str(user_id)
    uid, firstname, lastname, email = '', '', '', ''

    f = open('users.csv', 'r', encoding='utf8').read().split('\n')
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
        print('%s %s'%(firstname, lastname))
        return User(email, uid, firstname, lastname, active)


@app.before_first_request
def before_first_request():
    ld = os.listdir(os.getcwd())
    if 'users.csv' not in ld:
        f = open('users.csv', 'w', encoding='utf8')
        f.write('id;name;lname;email;password')
        f.close()
    else:
        print('users.csv located')
    if 'users' not in ld:
        os.mkdir('users')
    else:
        print('users folder located')


@app.before_request
def before_request():
    g.db = sqlite3.connect(DATABASE)
    g.user = current_user


@app.route("/Vyshka_slovari_main", methods=['POST', 'GET'])
def main_page():
    return render_template("Slovar_main.html")

@app.route('/Vyshka_slovari_main/<word>', methods=['POST', 'GET'])
def show_entries(word):
    word = word.lower()
    mng1 = g.db.execute(
        "SELECT sense, dic_name FROM test WHERE orth='%s' AND dic_name='Большой Энциклопедический Словарь'" % word).fetchall()
    mng2 = g.db.execute(
        "SELECT sense, dic_name FROM test WHERE orth='%s' AND dic_name='Толковый словарь Кузнецова'" % word).fetchall()
    ant = g.db.execute(
        "SELECT ant, dic_name FROM test WHERE orth='%s' AND dic_name='Словарь антонимов'" % word).fetchall()
    syn = g.db.execute(
        "SELECT syn, dic_name FROM test WHERE orth='%s' AND dic_name='Словарь русских синонимов и сходных по смыслу выражений'" % word).fetchall()
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

    ant = handle_exception(ant)
    syn = handle_exception(syn)
    epith = handle_exception(epith)
    phon = handle_exception(phon)
    etym = handle_exception(etym)
    usg = handle_exception(usg)
    pos = handle_gram(pos)
    gen = handle_gram(gen)
    asp = handle_gram(asp)
    gov = handle_gram(gov)

    return render_template('Show_entries.html',
                           word=word,
                           synonyms=syn,
                           antonyms=ant,
                           epithets=epith,
                           stress=phon,
                           etymology=etym,
                           usage=usg,
                           part_of_speech=pos,
                           gender=gen,
                           aspect=asp,
                           govern=gov,
                           meaning1=mng1,
                           meaning2=mng2)

@app.route("/Vyshka_slovari_about")
def about_page():
    return render_template('Slovar_about.html')

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
        print(pos,gender,aspect,borrowed,marker)
        result = ["По Вашему запросу ничего не найдено :("]
        if pos != 'None':
            if aspect == 'None' and gender == 'None' and borrowed == [] and marker == []:
                result = g.db.execute(
                    "SELECT orth, phon, sense, pos, gender, asp, dic_name, usg, etym_lang FROM test WHERE pos='%s'" %pos).fetchall()
            elif borrowed != [] and aspect == 'None' and gender == 'None' and marker == []:
                result = g.db.execute(
                    "SELECT orth, phon, sense, pos, gender, asp, dic_name, usg, etym_lang FROM test WHERE pos='%s' AND etym_lang='%s'" %(pos,borrowed[0])).fetchall()
            elif marker != [] and aspect == 'None' and gender == 'None':
                if borrowed == []:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, asp, dic_name, usg, etym_lang FROM test WHERE pos='%s' AND usg='%s'" % (
                        pos, marker[0])).fetchall()
                else:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, asp, dic_name, usg, etym_lang FROM test WHERE pos='%s' AND usg='%s' \
                        AND etym_lang='%s'" % (
                            pos, marker[0], borrowed[0])).fetchall()
            elif gender != 'None' and aspect == 'None':
                if borrowed == [] and marker == []:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, asp, dic_name, usg, etym_lang FROM test WHERE gender='%s' AND pos='%s'" %(gender, pos)).fetchall()
                elif borrowed == [] and marker != []:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, asp, dic_name, usg, etym_lang FROM test WHERE gender='%s' AND usg='%s'" % (
                        gender, marker[0])).fetchall()
                elif borrowed != [] and marker == []:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, asp, dic_name, usg, etym_lang FROM test WHERE gender='%s' AND etym_lang='%s'" % (
                            gender, borrowed[0])).fetchall()
                else:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, asp, dic_name, usg, etym_lang FROM test WHERE gender='%s' AND pos='%s' AND etym_lang='%s'\
                        AND usg='%s'" % (gender,pos,borrowed[0],marker[0])).fetchall()
            elif aspect != 'None' and gender == 'None':
                if borrowed == [] and marker == []:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, asp, dic_name, usg, etym_lang FROM test WHERE pos=' глаг. ' AND asp='%s'" %aspect).fetchall()
                elif borrowed != [] and marker == []:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, asp, dic_name, usg, etym_lang FROM test WHERE pos=' глаг. ' AND asp='%s' AND etym_lang='%s'" % (
                        aspect,borrowed[0])).fetchall()
                elif borrowed == [] and marker != []:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, asp, dic_name, usg, etym_lang FROM test WHERE pos=' глаг. ' AND asp='%s' AND usg='%s'" % (
                        aspect,marker[0])).fetchall()
                else:
                    result = g.db.execute(
                        "SELECT orth, phon, sense, pos, gender, asp, dic_name, usg, etym_lang FROM test WHERE pos=' глаг. ' AND asp='%s' \
                         AND usg='%s' AND etym_lang='%s'" % (aspect,marker[0], borrowed[0])).fetchall()
        elif borrowed != [] and pos=='None' and gender=='None' and aspect == 'None':
            if marker == []:
                result = g.db.execute(
                    "SELECT orth, phon, sense, pos, gender, asp, dic_name, usg, etym_lang FROM test WHERE etym_lang='%s'" %borrowed[0]).fetchall()
            else:
                result = g.db.execute(
                    "SELECT orth, phon, sense, pos, gender, asp, dic_name, usg, etym_lang FROM test WHERE etym_lang='%s' AND usg='%s'" %(borrowed[0],marker[0])).fetchall()
        elif marker != [] and pos=='None' and gender=='None' and aspect == 'None':
            result = g.db.execute(
                "SELECT orth, phon, sense, pos, gender, asp, dic_name, usg, etym_lang FROM test WHERE usg='%s'" %
                marker[0]).fetchall()
        with open('csv_result/results.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['orth', 'phon', 'sense', 'pos', 'gender', 'asp', 'dic_name', 'usg', 'etym_lang']
            filewriter = csv.DictWriter(csvfile, delimiter=' ', fieldnames=fieldnames)
            filewriter.writeheader()
            for item in result:
                filewriter.writerow({'orth':str(item[0]), 'phon':str(item[1]), 'sense':str(item[2]), 'pos':str(item[3]),
                                     'gender':str(item[4]), 'asp':str(item[5]), 'dic_name':str(item[6]),
                                     'usg':str(item[7]), 'etym_lang':str(item[8])})
        csvfile.close()
        print(type(result))
        return render_template('Show_extended_entries.html', form=form, result=result)
    return render_template('Slovar_extended_search.html', form=form)


@app.route('/csv_result/results.csv')
def download():
    return send_from_directory('csv_result/', "results.csv")


@app.route("/Vyshka_slovari_enter")
def enter_page():
    return render_template('Slovar_enter.html')


@app.route("/check_user_id", methods=['GET', 'POST'])
def checkUserId():
    registered = False
    email = request.form['e-mail']    
    password = request.form['password']
    print(email, password)

    db = open('users.csv', 'r', encoding='utf8').read().split('\n')
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
        return redirect("/Vyshka_slovari_main")
    else:
        uid =  None
        return render_template('Slovar_enter.html', mistake=True)


def validateEmail(email):
    m = re.search('[A-Za-z0-9\.]+@[A-Za-z0-9]+\.[A-Za-z]', email)
    if m:
        return True
    else:
        return False


@app.route("/new_user", methods=['GET', 'POST'])
def new_user():

    f = open('users.csv', 'r', encoding='utf8').read().split('\n')[1:]
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

    mistake = ''
    if password != password_check:
        mistake += 'Пароли не совпадают!\n'
    if not validateEmail(email) :
        mistake += 'Введите корректный email!\n'

    if mistake != '':
        return render_template('/Slovar_register.html', mistake=mistake)

    else:
        nu = '%s;%s;%s;%s;%s'%(new_id, firstname, lastname, email, password)
        
        f_ = open('users.csv', 'r', encoding='utf8').read()
        f = open('users.csv', 'w', encoding='utf8')
        f.write(f_)
        f.write('\n'+nu)
        f.close()

        os.mkdir('users/%s'%new_id)
        u = User(email, new_id, firstname, lastname)
        login_user(u)

        return render_template('/Slovar_main.html', mistake='')


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/Vyshka_slovari_main")


@app.route("/Vyshka_slovari_register", methods=['GET', 'POST'])
def register_page():
    return render_template('/Slovar_register.html', mistake='')


@app.route("/cabinet", methods=['GET', 'POST'])
def cabinet():
    return render_template('/cabinet.html')


@app.route("/upload_slov", methods=['GET', 'POST'])
def uploadSlov():
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        shutil.move(f.filename, "users/%s/%s"%(current_user.id, f.filename))
        return redirect('/Vyshka_slovari_main')


if __name__ == "__main__":
    app.run(debug=True)