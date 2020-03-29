from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, BooleanField, DecimalField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskapp.database import existing_email, existing_username, find_by_email
from flaskapp.routes import session


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired('kötelező'),
                                                   Length(min=3, max=30, message='Minimum 3 és maximum 30 karakter')])
    firstName = StringField('Firstname', validators=[DataRequired('kötelező'),
                                                     Length(min=3, max=30, message='Minimum 3 és maximum 30 karakter')])
    lastName = StringField('Lastname', validators=[DataRequired('kötelező'),
                                                   Length(min=3, max=30, message='Minimum 3 és maximum 30 karakter')])
    email = StringField('Email', validators=[DataRequired('kötelező'), Email('helytelen formátum'),
                                             Length(min=3, max=30, message='Minimum 3 és maximum 30 karakter')])
    password = PasswordField('Password', validators=[DataRequired('kötelező'),
                                                     Length(min=8, max=60, message='Legalább 8 karakter')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired('kötelező'), EqualTo('password',
                                                                                                       message='Nem egyező jelszavak')])
    phone_number = StringField('Phone Number')

    submit1 = SubmitField('Regisztrálok')

    def validate_email(self, email):
        if existing_email(email.data):
            raise ValidationError('Ez az email már létezik')

    def validate_username(self, username):
        if existing_username(username.data):
            raise ValidationError('Ez a felhaználónév már létezik')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired('kötelező'), Email()])
    password = PasswordField('Password', validators=[DataRequired('kötelező'), Length(min=8, max=60)])
    # TODO: implement remember...
    submit2 = SubmitField('Belépés')


class SearchForm(FlaskForm):
    honnan = StringField(validators=[DataRequired(), Length(min=3, max=40, message='Minimum 3 és maximum 40 karakter')])
    hova = StringField()
    estimated_travel_date = DateField(format='%Y-%m-%d')
    submit_search = SubmitField('Keresés')


class AccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired('kötelező'),
                                                   Length(min=3, max=30, message='Minimum 3 és maximum 30 karakter')])
    firstName = StringField('Firstname', validators=[DataRequired('kötelező'),
                                                     Length(min=3, max=30, message='Minimum 3 és maximum 30 karakter')])
    lastName = StringField('Lastname', validators=[DataRequired('kötelező'),
                                                   Length(min=3, max=30, message='Minimum 3 és maximum 30 karakter')])
    email = StringField('Email', validators=[DataRequired('kötelező'), Email('helytelen formátum'),
                                             Length(min=3, max=30, message='Minimum 3 és maximum 30 karakter')])
    phone_number = StringField('Phone Number')
    address = StringField('Address', validators=[Length(min=0, max=30, message='Maximum 30 karakter')])
    picture = FileField('profilkép feltöltése', validators=[FileAllowed(['png', 'jpg'])])
    submit_account = SubmitField('Mentés')

    def validate_email(self, email):
        if email.data != session["user"]:
            if existing_email(email.data):
                raise ValidationError('Ez az email már létezik')

    def validate_username(self, username):
        if username.data != find_by_email(session["user"])["username"]:
            if existing_username(username.data):
                raise ValidationError('Ez a felhaználónév már létezik')


class CreatePostForm(FlaskForm):
    car_brand = StringField('car_brand', validators=[DataRequired('kötelező'),
                                                     Length(min=3, max=30, message='Minimum 3 és maximum 30 karakter')])
    car_model = StringField('car_model', validators=[DataRequired('kötelező'),
                                                     Length(min=2, max=30, message='Minimum 3 és maximum 30 karakter')])
    car_color = StringField('car_color', validators=[DataRequired('kötelező'),
                                                     Length(min=3, max=30, message='Minimum 3 és maximum 30 karakter')])
    date_of_manufacture = IntegerField('date_of_manufacture', validators=[DataRequired('kötelező')])

    def validate_date_of_manufacture(self, date_of_manufacture):
        if date_of_manufacture.data < 1900:
            raise ValidationError("évjárat > 1900 ")
        if date_of_manufacture.data > 2050:
            raise ValidationError("évjárat < 2050 ")

    seats = IntegerField(validators=[DataRequired('Kötelező')])
    place_of_departure = StringField('place_of_departure', validators=[DataRequired('kötelező'),
                                                                       Length(min=3, max=30,
                                                                              message='Minimum 3 és maximum 30 karakter')])
    destination = StringField('destination', validators=[DataRequired('kötelező'),
                                                         Length(min=3, max=30,
                                                                message='Minimum 3 és maximum 30 karakter')])
    start_time = TimeField(validators=[DataRequired('Kötelező')])
    arrival_time = TimeField(validators=[DataRequired('Kötelező')])
    price = IntegerField(validators=[DataRequired('kötelező')])

    def validate_start_time(self, start_time):
        if start_time.data >= self.arrival_time.data:
            raise ValidationError('indulási idő > érkezési idő')

    def validate_price(self, price):
        if price.data > 1000000:
            raise ValidationError("túl nagy szám")
    travel_date = DateField(format='%Y-%m-%d', validators=[DataRequired('válassz Dátumot')])
    note = TextAreaField(validators=[Length(max=300, message='Maximum 300 karakter')])
    package_delivery = BooleanField()
    house_to_house = BooleanField()
    submit_post = SubmitField('Feladás')

    def post_fill(self, car_brand, car_model, car_color, date_of_manufacture, seats, place_of_departure,
                  destination, price, note, house_to_house, package_delivery, travel_date, start_time, arrival_time):
        self.car_brand.data = car_brand
        self.car_model.data = car_model
        self.car_color.data = car_color
        self.date_of_manufacture.data = date_of_manufacture
        self.seats.data = seats
        self.place_of_departure.data = place_of_departure
        self.destination.data = destination
        self.price.data = price
        self.note.data = note
        self.house_to_house.data = house_to_house
        self.package_delivery.data = package_delivery
        self.travel_date.data = travel_date
        self.start_time.data = start_time
        self.arrival_time.data = arrival_time
