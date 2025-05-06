from flask import Blueprint, make_response, json, jsonify, render_template
from wtforms import Form, StringField, PasswordField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, EqualTo

data_bp = Blueprint('data', __name__)



class ProfileForm(FlaskForm):
    age = StringField('Age', [DataRequired(), Length(min=1, max=3)])
    email = StringField('Email', [DataRequired(), Length(min=6, max=35)])
    weight = StringField('Weight', [DataRequired(), Length(min=1, max=3)])
    height = StringField('Height', [DataRequired(), Length(min=1, max=3)])
    submit =SubmitField('Submit')

@data_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    form= ProfileForm()
    return render_template('profile.html', form=form)


@data_bp.route('/datas')
def send_data():
    data = {
        'username': 'JohnDoe'
    }
    
    return jsonify(data)
    