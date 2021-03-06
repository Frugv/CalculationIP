from flask import Flask, render_template, request, redirect
from LoginForm import LoginForm
from Conf import Config
import MySQLdb
from mysql.connector import connect

# Create database and table
with connect(host="localhost", user="root", password="q1w2a3s4", ) as connection:
    db = """CREATE DATABASE IF NOT EXISTS calculateip;"""
    with connection.cursor() as cursor:
        cursor.execute(db)
db = MySQLdb.connect(host="localhost", user="root", passwd="q1w2a3s4", db="calculateip")
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
cursor.execute("""CREATE TABLE IF NOT EXISTS упс(
    id_ups INT AUTO_INCREMENT PRIMARY KEY,
    Количество_УПС INT,
    Номер_станции INT);""")
db.commit()
cursor.close()

app = Flask(__name__)

app.config.from_object(Config)

@app.route('/', methods=['GET'])
def form():
    # Input form
    form = LoginForm()
    if request.method == 'GET':
        return render_template('html/LoginForm.html', title='Входные данные', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        # Connect with the database
        db = MySQLdb.connect(host="localhost", user="root", passwd="q1w2a3s4", db="calculateip")
        cursor = db.cursor()
        # Fetching data from the database
        cursor.execute("SELECT Значение_переменной FROM переменные ORDER BY id_переменные DESC LIMIT 4")
        value = []
        for i in cursor.fetchall():
            value.append(i[0])
        db.commit()
        cursor.close()
        return render_template('html/TableReturn.html', S=value[0], U=value[3], W=value[2], A=value[1])
    if request.method == 'POST':
        if request.form['Кнопка'] == "Далее":
            # Check the length of the TIN
            if len(request.form['ИНН организации']) >= 10 and len(request.form['ИНН организации']) <= 12:
                db = MySQLdb.connect(host="localhost", user="root", passwd="q1w2a3s4", db="calculateip")
                cursor = db.cursor()
                # Insert data in the database
                cursor.execute(''' INSERT INTO фио (Имя, Фамилия) VALUES(%s,%s)''',
                               (request.form['Имя'], request.form['Фамилия']))
                cursor.execute(''' INSERT INTO организация (Название_организации, ИНН_организации) VALUES(%s,%s)''',
                               (request.form['Название организации'], request.form['ИНН организации']))
                db.commit()
                cursor.close()
                return render_template('html/TableInput.html')
            else:
                form = LoginForm()
                message = "Вы ввели неверный ИНН, проверьте и введите снова."
                return render_template('html/LoginForm.html', title='Входные данные', form=form, message=message)
    if request.form['Кнопка'] == 'Назад':
        return render_template('html/TableInput.html')

@app.route('/calculating', methods=['POST'])
def calculating():
    if request.method == 'POST':
        # Connect with the database
        db = MySQLdb.connect(host="localhost", user="root", passwd="q1w2a3s4", db="calculateip")
        cursor = db.cursor()
        # Insert data in the database
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
    # Connect with the database
    db = MySQLdb.connect(host="localhost", user="root", passwd="q1w2a3s4", db="calculateip")
    cursor = db.cursor()
    # Fetching data from the database
    cursor.execute("SELECT Значение_переменной FROM переменные ORDER BY id_переменные DESC LIMIT 4")
    value = []
    for i in cursor.fetchall():
        value.append(i[0])
    cursor.close()
    if request.method == 'GET':
        return render_template('html/InputUPS.html', S=value[0], U=value[3], W=value[2], A=value[1], P=value[0]-1)
    if request.method == 'POST':
        return render_template('html/InputUPS.html', S=value[0], U=value[3], W=value[2], A=value[1], P=value[0] - 1)


@app.route('/resulting', methods=['POST'])
def resulting():
    # Connect with the database
    db = MySQLdb.connect(host="localhost", user="root", passwd="q1w2a3s4", db="calculateip")
    cursor = db.cursor()
    # Fetching data from the database
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
        #Data validation
        if sum(PU) != value[3]:
            message = "Количество УПС на всех перегонах должно быть равно количеству УПС на участке! Проверьте введенные данные."
            return render_template('html/InputUPS.html', S=value[0], U=value[3], W=value[2], A=value[1], message=message, P=value[0]-1)
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
        # Connect with the database
        db = MySQLdb.connect(host="localhost", user="root", passwd="q1w2a3s4", db="calculateip")
        cursor = db.cursor()
        i = 1
        for j in SU:
            cursor.execute(''' INSERT INTO упс (Количество_УПС, Номер_станции) VALUES(%s,%s)''',(j, i))
            i += 1
        db.commit()
        cursor.close()
        return render_template('html/Result.html', IP=I, U=value[3], W=value[2], S=value[0], A=value[1], C=C, Ci=Ci, M=(value[0]-1)*2, P=value[0]-1 )


if __name__ == "__main__":
    app.run(host='0.0.0.0')
