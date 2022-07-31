"""
Uzduotys:
1.(3) Surasti, isvardinti ir pataisyti visas projekte rastas klaidas zemiau, uz bent 5 rastas ir pataisytas
pilnas balas:
    a) Sign_in puslapyje nenurodyti galimi metodai. Pridėta.
    b) Sign_up problema - trūko last_name lauko SignUpForm'e, class User paveldėjimo UserMixin (jį reikėjo
    susiimportuoti), funkcijoje sign_up reikėjo pridėti user'iui last_name=form.last_name.data
    c) Log_out problema - truko funkcijoje logout_user(), taip pat importo logout_user
    d) update_account_information pataisyta form_in_html=form vietoje form=form
    e) Sign_in problema. Vietoje "first_name=form.email_address.data" pataisyta į
    "email_address=form.email_address.data"
    f) Account information puslapyje pataisytas tekstas viršuje. Vietoje Sign Up įrašyta Update account
    information.
    g)  Update account information problema. Pataisytas metodas iš "POST" į "GET", pakoreguotas pirminis duomenų
    atvaizdavimas formos laukeliuose:
    if request.method == 'GET':
        form.email_address.data = current_user.email_address
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    h) class User first_name = db.Column(db.Integer, nullable=False) pakeista į String
    i) SignUp ir SignIn formose e-mail adreso laukas pakeistas i6 StringField į EmailField. Taip pat EmailField
    suimportuotas.
    ...
2.(7) Praplesti aplikacija i bibliotekos registra pagal apacioje surasytus reikalavimus:
    a)(1) Naudojant SQLAlchemy klases, aprasyti lenteles Book, Author su pasirinktinais atributais su tinkamu rysiu -
        vienas autorius, gali buti parases daug knygu, ir uzregistruoti juos admin'e
    b)(2) Sukurti (papildomus) reikiamus rysius tarp duombaziniu lenteliu, kad atitiktu zemiau pateiktus reikalavimus
    c) Sukurti puslapius Available Books ir My Books:
        i)(2) Available Books puslapis
            - isvesti bent knygos pavadinima ir autoriu
            - turi buti prieinamas tik vartotojui prisijungus,
            - rodyti visas knygas, kurios nera pasiskolintos
            - tureti mygtuka ar nuoroda "Borrow" prie kiekvienos knygos, kuri/ia paspaudus, knyga yra priskiriama
              varototojui ir puslapis perkraunamas
              (del paprastumo, sakome kad kiekvienos i sistema suvestos knygos turima lygiai 1)
        ii)(2) My Books puslapis
            - turi matytis ir buti prieinamas tik vartotojui prisijungus
            - rodyti visas knygas, kurios yra pasiskolintos prisijungusio vartotojo
            - salia kiekvienos knygos mygtuka/nuoroda "Return", kuri/ia paspaudus, knyga grazinama i biblioteka ir
              perkraunamas puslapis
    f)(2) Bonus: praplesti aplikacija taip, kad bibliotekoje kiekvienos knygos galetu buti
        daugiau negu vienas egzempliorius
Pastabos:
    - uzstrigus su pirmaja uzduotimi, galima paimti musu paskutini flask projekto template
        ir ten atlikti antra uzduoti
    - nereikalingus templates geriau panaikinti ar persidaryti, kaip reikia. Tas pats galioja su MyTable klase
    - antram vartotojui prisijungus, nebeturi matytis kyngos, kurios buvo pasiskolintos pirmojo vartotojo
        nei prie Available Books, nei prie My Books
    - visam administravimui, pvz. knygu suvedidimui galima naudoti admin
    - sprendziant bonus uzduoti, apsvarstyti papildomos lenteles isivedima
"""

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, AnonymousUserMixin, LoginManager, login_user, logout_user, current_user, \
    login_required
from flask_sqlalchemy import SQLAlchemy
import forms

app = Flask(__name__)


class MyAnonymousUserMixin(AnonymousUserMixin):
    is_admin = False


login_manager = LoginManager(app)

login_manager.login_view = 'sign_in'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'info'
login_manager.anonymous_user = MyAnonymousUserMixin

admin = Admin(app)

bcrypt = Bcrypt(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '(/("ZOHDAJK)()kafau029)ÖÄ:ÄÖ:"OI§)"Z$()&"()!§(=")/$'

db = SQLAlchemy(app)

helper_table = db.Table('helper', db.metadata,
                        db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
                        db.Column('author_id', db.Integer, db.ForeignKey('author.id')))

helper_table_2 = db.Table('helper_2', db.metadata,
                        db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id')))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', secondary=helper_table_2, back_populates='readers')
    is_admin = db.Column(db.Boolean, nullable=False, default=False)


class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    authors = db.relationship('Author', secondary=helper_table, back_populates='books')
    readers = db.relationship('User', secondary=helper_table_2, back_populates='books')
    stock = db.Column(db.Integer, nullable=False, default=1)


class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(300))
    books = db.relationship('Book', secondary=helper_table, back_populates='authors')


db.create_all()


class MyModelView(ModelView):

    def is_accessible(self):
        return current_user.is_admin


admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Book, db.session))
admin.add_view(MyModelView(Author, db.session))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/available_books')
@login_required
def available_books():
    page = request.args.get('page', 1, type=int)
    all_books = Book.query.paginate(page=page, per_page=10)
    return render_template('available_books.html', all_books=all_books)


@app.route('/my_books')
@login_required
def my_books():
    page = request.args.get('page', 1, type=int)
    my_books = Book.query.paginate(page=page, per_page=10)
    return render_template('my_books.html', my_books=my_books)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = forms.SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password1.data).decode()
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email_address=form.email_address.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Welcome, {current_user.first_name}', 'success')
        return redirect(url_for('home'))
    return render_template('sign_up.html', form=form)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = forms.SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'Welcome, {current_user.first_name}', 'success')
            return redirect(request.args.get('next') or url_for('home'))
        flash(f'User or password does not match', 'danger')
        return render_template('sign_in.html', form=form)
    return render_template('sign_in.html', form=form)


@app.route('/update_account_information', methods=['GET', 'POST'])
def update_account_information():
    form = forms.UpdateAccountInformationForm()
    if request.method == 'GET':
        form.email_address.data = current_user.email_address
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    if form.validate_on_submit():
        current_user.email_address = form.email_address.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        db.session.commit()
        flash('User information updated', 'success')
        return redirect(url_for('update_account_information'))
    return render_template('update_account_information.html', form_in_html=form)


@app.route("/borrow_book/<int:id>")
@login_required
def borrow_book(id):
    book_to_borrow = Book.query.get(id)
    if current_user in book_to_borrow.readers:
        flash(f'You already borrowed book "{book_to_borrow.title}"', 'danger')
        return redirect(url_for('available_books'))
    else:
        stock_updated = book_to_borrow.stock - 1
        book_to_borrow.stock = stock_updated
        book_to_borrow.readers.append(current_user)
        db.session.commit()
        flash(f'You borrowed book "{book_to_borrow.title}" successfully', 'success')
    return redirect(url_for('available_books'))


@app.route("/return_book/<int:id>")
@login_required
def return_book(id):
    book_to_return = Book.query.get(id)
    stock_updated = book_to_return.stock + 1
    book_to_return.stock = stock_updated
    book_to_return.readers.remove(current_user)
    db.session.commit()
    flash(f'You returned book "{book_to_return.title}" successfully', 'success')
    return redirect(url_for('my_books'))


@app.route('/sign_out')
def sign_out():
    logout_user()
    flash('Goodbye, see you next time', 'success')
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
