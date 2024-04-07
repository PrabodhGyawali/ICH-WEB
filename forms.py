from flask_wtf import FlaskForm, RecaptchaField
from email_validator import validate_email
from wtforms import StringField, SubmitField, PasswordField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.validators import ValidationError



class SignIn(FlaskForm):
    class Meta:
        csrf = True  # Enable CSRF
    email = EmailField(render_kw={'placeholder': 'Email'}, name='Email', validators=[DataRequired(), Length(min=5)])
    password = PasswordField(name='Password', validators=[DataRequired()],
        render_kw={'placeholder': 'Password'})
    remember_me = BooleanField(name='Remember me', render_kw={'value': 0, 'id': 'remember_me'})
    submit = SubmitField(name='Submit')

class SignUp(FlaskForm):
    class Meta:
        csrf = True  # Enable CSRF


    username = StringField(name='Username', render_kw={'placeholder': 'Enter Username'},
                           validators=[DataRequired(), Length(min=5, max=25, message="5 to 25 characters only!")])
    email = EmailField(render_kw={'placeholder': 'Email'}, name='Email',
                       validators=[DataRequired(), Email(), Length(min=15)])
    password = PasswordField('New Password', [
        DataRequired(), Length(min=8),
        EqualTo('confirm', message='Passwords must match')
    ], render_kw={'placeholder': 'Enter Password'})
    confirm = PasswordField('Repeat Password',
        render_kw={'placeholder': 'Confirm Password'})

    # Required Boolean Fields
    Tos1 = BooleanField(validators=[DataRequired()],
                        render_kw={'value': 0, 'id': 'Tos1'})
    Tos2 = BooleanField(validators=[DataRequired()],
                        render_kw={'value': 0, 'id': 'Tos2'})

    # Optional Marketing Boolean Fields
    option1 = BooleanField(name=' System news (API usage alert, system update, temporary system shutdown, etc)',
                           render_kw={'id': 'option1', 'value': 0})
    option2 = BooleanField(name=' Product news (change to price, new product features, etc)',
                           render_kw={'id': 'option2', 'value': 0})
    option3 = BooleanField(name=' Corporate news (our life, the launch of a new service, etc)',
                           render_kw={'id': 'option3', 'value': 0})
    recaptcha = RecaptchaField()
    submit = SubmitField(name='Create Account')

class CreateKey(FlaskForm):
    key_name = StringField(name="key_name_input",
                           render_kw={'placeholder': 'API key name', "style": "margin-left: 0; width: 200px;"},
                           validators=[DataRequired(), Length(max=20)])
    submit = SubmitField(name="Generate", render_kw={'id': 'Generate'})
