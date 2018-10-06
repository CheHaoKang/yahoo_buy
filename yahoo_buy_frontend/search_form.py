#  引入flask_wtf
from flask_wtf import FlaskForm
#  各別引入需求欄位類別
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.fields.html5 import EmailField
#  引入驗證
from wtforms.validators import DataRequired, Email

#  從繼承Form開始
class SearchForm(FlaskForm):
    input_question = StringField('Question', validators=[DataRequired(message='Not Null')])
    # input_category = StringField('Category', validators=[DataRequired(message='Not Null')])
    # input_sub_category = StringField('Sub-category', validators=[DataRequired(message='Not Null')])
    # input_answer = StringField('Answer', validators=[DataRequired(message='Not Null')])
    # email = EmailField('Email', validators=[DataRequired(message='Not Null')])
    # input_textarea = TextAreaField('', validators=[DataRequired(message='Not Null')], render_kw={'class': 'form-control', 'rows': 20, 'cols': 100})
    submit = SubmitField('Submit')