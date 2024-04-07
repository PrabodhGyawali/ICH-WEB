# Importing necessary libraries
import secrets
import flask
import datetime


from flask import Flask, render_template,  request, send_file, redirect, url_for, flash
from flask_login import login_user, logout_user, LoginManager, UserMixin, login_required, current_user

# Database imports
from typing import List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, DateTime, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError

# Forms import
import time, os
from werkzeug.security import generate_password_hash, check_password_hash

# Importing custom modules
import webapp
from sendmail import send_email
import forms
import threading
# Creating a Flask app
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['RECAPTCHA_PUBLIC_KEY'] = os.environ.get("RECAPTCHA_PUBLIC_KEY")
app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get("RECAPTCHA_PRIVATE_KEY")
# Connect to Database (Locally being a development file)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI")

db = SQLAlchemy()
db.init_app(app)

# Configure Flask-Login's Login Manager
login_manager = LoginManager()
login_manager.init_app(app)

# Define a custom unauthorized handler
@login_manager.unauthorized_handler
def unauthorized():
    # Redirect to the sign-up page
    return redirect(url_for('sign_in'))  # Assume 'sign-in' is the endpoint for your sign-up page


# User TABLE Configuration
class User(db.Model, UserMixin):
    __tablename__ = "user_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    # Relationships
    child_setting: Mapped["UserSettings"] = relationship(back_populates="parent")
    children_keys: Mapped[List["ApiKey"]] = relationship(back_populates="parent")

class UserSettings(db.Model):
    __tablename__ = "user_settings_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_table.id"))
    # Api-related attributes
    api_calls: Mapped[int] = mapped_column(Integer, nullable=False)
    subscription: Mapped[int] = mapped_column(Integer, nullable=False)
    date_joined: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    # Notification attributes
    notify_sys: Mapped[bool] = mapped_column(Boolean, nullable=False)
    notify_product: Mapped[bool] = mapped_column(Boolean,nullable=False)
    notify_corp: Mapped[bool] = mapped_column(Boolean, nullable=False)
    # Relationships
    parent: Mapped["User"] = relationship(back_populates="child_setting", single_parent=True)


class ApiKey(db.Model):
    __tablename__ = "apikey_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    api_key: Mapped[str] = mapped_column(String, nullable=False)  # input hashed key
    status: Mapped[Boolean] = mapped_column(Boolean, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    # Relationships
    parent: Mapped["User"] = relationship(back_populates="children_keys")
    children_call_history: Mapped[List["CallHistory"]] = relationship(back_populates="parent")

# api call history database
class CallHistory(db.Model):
    __table__name = "cass_history_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    api_id: Mapped[int] = mapped_column(ForeignKey("apikey_table.id"))
    date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    # Relationships
    parent: Mapped["ApiKey"] = relationship(back_populates="children_call_history")
    

# Domains
with app.app_context():
    db.create_all()

# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalars().all()
    if len(user) == 0:
        return None
    else:
        return db.get_or_404(User, user_id)

@app.route('/debug')
def debug():
    date_joined = datetime.datetime.now().strftime('%d-%b-%Y-%I:%M%p')
    return date_joined

# Home page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Sending email
        if name != '' and email != '' and message != '':
            send_email(email, message, [os.environ.get("ICH_EMAIL")])  

    return render_template('index.html')


# Login page
@app.route('/login', methods=['GET', 'POST'])
def log():

    if request.method == 'POST':
        if 'email' in request.form:
            game = request.form['name']
            line = request.form['email']

            users = {
                'admin': 'admin'
            }

            if game in users and users[game] == line:

                joe = []
                folder = 'static/folders'
                names = os.listdir(folder)
                for i in names:
                    joe.append(i)
                return render_template('blank.html', list=joe)
            
            else:
                return render_template('login.html')

        if 'message' in request.form:
            colour = request.form['message']

            filename = f'static/folders/{colour}'

            try:
                return send_file(filename, as_attachment=True)
            
            except:
                pass


    return render_template('login.html')


@app.route('/generic.html')
def elements():
    return render_template('generic.html')


@app.route('/glimpse')
def glimpse():
    return render_template('example.html')


@app.route('/code', methods=['GET', 'POST'])
def code():
    if request.method == 'POST':
        game = request.form['name']
        line = request.form['email']
        colour = request.form['message']
        func = request.form['func']

        try:
            plot_thread = threading.Thread(target=webapp.run(game, colour, line, func))
            plot_thread.start()

            newu = game.split('.txt')

            time.sleep(1.5)

            filename = f'static/images/{newu[0]}.png'

            return send_file(filename, as_attachment=True)
        
        except Exception as s:
            print(s)
            return render_template('elements.html')
    else:
        return render_template('elements.html')


# API
@app.route('/api/documentation', methods=['GET', 'POST'])
def api_documentation():
    return render_template("api-documentation.html")


# Sign_in and Register
@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    # Log in process
    main_form = forms.SignIn()
    if main_form.validate_on_submit():
        email = request.form['Email']
        try:
            user = db.session.execute(db.select(User)
                                      .where(User.email == email))\
                                        .scalars().all()[0]
        except IndexError:
            return render_template('sign-in.html', main_form=main_form, error="Email isn't signed up.")
        else:
            # Check stored password hash against entered password hashed.
            if check_password_hash(user.password, main_form.password.data):
                # Log in and authenticate user after adding details to database.
                login_user(user)
                flask.flash('Logged in successfully')

                # Redirect to user account page
                return redirect(url_for('account'))
            else:
                return render_template('sign-in.html', main_form=main_form, error="Login Failed.")
    else:
        return render_template('sign-in.html', main_form=main_form, error="")


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check code below: error was creating when new user created their account.
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    def db_attribute_checker(data, attribute):
        if attribute == "username":
            attribute_list = db.session.execute(db.select(User).where(User.username == data)).scalars().all()
        else:
            attribute_list = db.session.execute(db.select(User).where(User.email == data)).scalars().all()
        return len(attribute_list) != 0

    form = forms.SignUp()
    if form.validate_on_submit():
        # Use Flask Flashes instead of putting in kwargs
        if db_attribute_checker(form.username.data, "username"):
            return render_template('register.html', form=form, error=["Username already exists", ""])
        elif db_attribute_checker(form.email.data, "email"):
            return render_template('register.html', form=form, error=["", "Email already exists"])
        else:
            # Add user details to db
            hash_salt_pass = generate_password_hash(password=form.password.data, method='pbkdf2:sha256', salt_length=8)
            new_user = User(
                email=form.email.data,
                username=form.username.data,
                password=hash_salt_pass,
            )
            db.session.add(new_user)
            db.session.commit()

            # Create Settings Tuple
            new_setting = UserSettings(
                user_id = new_user.id,
                api_calls = 25,
                subscription = 0,
                date_joined = datetime.datetime.now(),
                notify_sys = form.option1.data,
                notify_product = form.option2.data,
                notify_corp = form.option3.data,
            )
            db.session.add(new_setting)
            db.session.commit()

            # Log in and authenticate user after adding details to database.
            login_user(load_user(new_user.id))
            # load_user(new_user.id)

            flask.flash('Logged in successfully')

            # Redirect to user account page
            return redirect(url_for('account'))

    return render_template('register.html', form=form, error=["", ""])


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = forms.CreateKey()
    keys = db.session.execute(db.select(ApiKey).where(ApiKey.owner_id == current_user.id)).scalars().all()
    if request.method == "POST":
        if len(keys) > 0:
            # Key Actions
            key_raw = request.args.get('key')
            action = request.args.get('action')
            if key_raw is not None:
                try: 
                    key_id = int(key_raw)
                    if key_id in [key.id for key in keys]:
                        key_to_update = ApiKey.query.filter_by(id=key_id, owner_id=current_user.id).first()
                        # Code above also considers if key_id belongs to current_user.id (prevents anyone from changing status)
                        # Extra security layer in addtion to the @login_required handler
                        
                        if action == "activate":
                            key_to_update.status = not key_to_update.status
                            db.session.commit() 
                            flash('API key status updated successfully.')
                        elif action == "delete":
                            db.session.delete(key_to_update)
                            db.session.commit()
                            flash('API key deleted successfully.')
                        else:
                            flash('Invalid action.')
                            
                    else:
                        flash('API key not found.')
                    
                except SQLAlchemyError as exception:
                    db.session.rollback() # Rollback in case of error
                    flash('An error occured. Please try again')
                    print("Logging error: " + exception) # exception logging

                except ValueError:
                    # Handle the case where 'key' query parameter is not an integer
                    flash('Invalid key ID.')
                finally:
                    pass

    if form.validate_on_submit():
        if len(keys) >= 5:
            flask.flash("Api key limit reached.")
            render_template("account.html", form=form, keys=keys)
        else:
            # Create key
            api_key = secrets.token_hex(16)
            # Ensure key is unique (done without sql exception catching)
            secret_token_repeated = True
            while secret_token_repeated:
                if len(db.session.execute(db.select(ApiKey).where(ApiKey.api_key == api_key)).scalars().all()) > 0:
                    api_key = secrets.token_hex(16)
                else:
                    secret_token_repeated = False

            new_key = ApiKey(
                owner_id=current_user.id,
                api_key=api_key,
                status=True,
                name=form.key_name.data, # old key name is repeating here, need to fix error
            )
            db.session.add(new_key)
            db.session.commit()
            form = forms.CreateKey()
            keys = db.session.execute(db.select(ApiKey).where(ApiKey.owner_id == current_user.id)).scalars().all()
            render_template("account.html", form=form, keys=keys)

    return render_template("account.html", form=form, keys=keys)


@app.route("/sign-out")
@login_required
def sign_out():
    logout_user()
    return redirect(url_for('home'))


# Policies
@app.route('/privacy-policy')
def privacy_policy():
    return "Privacy Policy page"


if __name__ == '__main__':
    app.run(debug=False)
