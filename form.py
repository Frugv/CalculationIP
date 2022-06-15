from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    firstname = StringField('Имя:', validators=[DataRequired()])
    lastname = StringField('Фамилия:', validators=[DataRequired()])
    organisation = StringField('Название организации:', validators=[DataRequired()])
    inn = IntegerField('ИНН организации:', validators=[DataRequired()])
    submit = SubmitField('Далее')


