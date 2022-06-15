from flask import Flask, render_template, request, redirect
from form import LoginForm
from config import Config
import MySQLdb
from mysql.connector import connect

with connect(host="localhost", user="root", password="root-", ) as connection:
    app = """CREATE DATABASE IF NOT EXISTS app;"""
    with connection.cursor() as cursor:
        cursor.execute(app)
db = MySQLdb.connect(host="localhost", user="root", passwd="root-", db="app")
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS фио (
    id_фио INT AUTO_INCREMENT PRIMARY KEY,
    Имя VARCHAR(100),
    Фамилия VARCHAR(100));""")
cursor.execute("""CREATE TABLE IF NOT EXISTS организация (
    id_организация INT AUTO_INCREMENT PRIMARY KEY,
    Название_организации VARCHAR(100),
    ИНН_организации BIGINT);""")
cursor.execute("""CREATE TABLE IF NOT EXISTS переменные(
    id_переменные INT AUTO_INCREMENT PRIMARY KEY,
    Наименование_переменной VARCHAR(100),
    Условное_обозначение_переменной VARCHAR(100),
    Описание_переменной VARCHAR(100),
    Значение_переменной INT);""")
db.commit()
cursor.close()

app = Flask(__name__)

app.config.from_object(Config)

@app.route('/', methods=['GET', 'POST'])
def form():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('html/loginform.html', title='Входные данные', form=form)
    if request.method == 'POST':
        if request.form['Кнопка'] == 'Назад':
            return render_template('html/loginform.html', title='Входные данные', form=form)

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        if request.form['Кнопка'] == "Далее":
            db = MySQLdb.connect(host="localhost", user="root", passwd="root-", db="app")
            cursor = db.cursor()
            cursor.execute(''' INSERT INTO фио (Имя, Фамилия) VALUES(%s,%s)''',
                           (request.form['Имя'], request.form['Фамилия']))
            cursor.execute(''' INSERT INTO организация (Название_организации, ИНН_организации) VALUES(%s,%s)''',
                           (request.form['Название организации'], request.form['ИНН организации']))
            db.commit()
            cursor.close()
            return render_template('html/tablepermanent.html')
        if request.form['Кнопка'] == "Назад":
            return render_template('html/tablepermanent.html')

@app.route('/calculating', methods=['POST'])
def calculating():
    if request.method == 'POST':
        db = MySQLdb.connect(host="localhost", user="root", passwd="root-", db="app")
        cursor = db.cursor()
        cursor.executemany('''INSERT INTO переменные (Наименование_переменной, Условное_обозначение_переменной, Описание_переменной, Значение_переменной)
            VALUES
            (%s, %s, %s, %s)''',
                    (("Количество УПС", "U", "Количество УПС на участке", request.form['Количество УПС']),
                    ("Наличие Wi - Fi", "W", "Наличие Wi - Fi точки в составе УПС", request.form['Наличие Wi-Fi']),
                    ("Опция МАВР", "A", "Нужен ли комплект МАВР", request.form['Опция МАВР']),
                    ("Количество станций", "S", 'Количество станций на участке', request.form['Количество станций'])))
        db.commit()
        cursor.close()
        return redirect('/result')

@app.route('/result', methods=['GET', 'POST'])
def result():
    db = MySQLdb.connect(host="localhost", user="root", passwd="root-", db="app")
    cursor = db.cursor()
    cursor.execute("SELECT Значение_переменной FROM переменные ORDER BY id_переменные DESC LIMIT 4")
    value = []
    for i in cursor.fetchall():
        value.append(i[0])
    db.commit()
    cursor.close()
    if request.method == 'GET':
        return render_template('html/inputUPS.html', S=value[0], U=value[3], W=value[2], A=value[1], P=value[0]-1)
    if request.method == 'POST':
        return render_template('html/inputUPS.html', S=value[0], U=value[3], W=value[2], A=value[1], P=value[0] - 1)


@app.route('/resulting', methods=['POST'])
def resulting():
    db = MySQLdb.connect(host="localhost", user="root", passwd="root-", db="app")
    cursor = db.cursor()
    cursor.execute("SELECT Значение_переменной FROM переменные ORDER BY id_переменные DESC LIMIT 4")
    value = []
    for i in cursor.fetchall():
        value.append(i[0])
    C = []
    PU = []
    SU = []
    if request.method == "POST":
        for i in request.form.getlist('Количество УПС на перегоне'):
            PU.append(int(i))
        if sum(PU) > value[3]:
            message = "Сумма УПС на перегоне больше, чем количество УПС на участке! Проверьте еще раз данные."
            return render_template('html/inputUPS.html', S=value[0], U=value[3], W=value[2], A=value[1], message=message, P=value[0]-1)
        elif sum(PU) < value[3]:
            message = "Сумма УПС на перегоне меньше, чем количество УПС на участке! Проверьте еще раз данные."
            return render_template('html/inputUPS.html', S=value[0], U=value[3], W=value[2], A=value[1], message=message, P=value[0]-1)
        else:
            i = 1
            SU.append(PU[0])
            while i < len(PU):
                SU.append(PU[i] + PU[i - 1])
                i += 1
            SU.append(PU[-1])
        for i in SU:
            if int(i) / 26 <= 1:
                C.append(0)
            elif int(i) / 26 <= 2:
                C.append(2)
            elif int(i) / 26 <= 3:
                C.append(4)
            elif int(i) / 26 <= 4:
                C.append(6)
            elif int(i) / 26 <= 5:
                C.append(8)
        I = value[3] * (14 + value[2]) + 2 * value[0] + ((value[0] - 1) * 2) + sum(C) + value[1] * 16 + 16
        cursor.close()
        Ci = [i[0] for i in enumerate(C)]
        return render_template('html/result.html', IP=I, U=value[3], W=value[2], S=value[0], A=value[1], C=C, Ci=Ci, M=(value[0]-1)*2, )


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)