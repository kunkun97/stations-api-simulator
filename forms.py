from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, URL, NumberRange, Optional

class ControlForm(FlaskForm):
    api_endpoint = StringField('API Endpoint', validators=[DataRequired(), URL()], default="http://127.0.0.1:5001/data")
    interval = IntegerField('Interval (seconds)', validators=[DataRequired(), NumberRange(min=1)], default=15)
    start_index1 = IntegerField('Start Index Station 1', validators=[Optional(), NumberRange(min=0)], default=0)
    start_index2 = IntegerField('Start Index Station 2', validators=[Optional(), NumberRange(min=0)], default=0)
    start_index3 = IntegerField('Start Index Station 3', validators=[Optional(), NumberRange(min=0)], default=0)
    start_index4 = IntegerField('Start Index Station 4', validators=[Optional(), NumberRange(min=0)], default=0)
    start_index5 = IntegerField('Start Index Station 5', validators=[Optional(), NumberRange(min=0)], default=0)
    start_index6 = IntegerField('Start Index Station 6', validators=[Optional(), NumberRange(min=0)], default=0)