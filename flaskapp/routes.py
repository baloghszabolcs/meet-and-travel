from flask import render_template, url_for, flash, redirect, request, session
from flaskapp.forms import RegistrationForm, LoginForm, SearchForm, AccountForm, CreatePostForm
from flaskapp import app, bcrypt
from flaskapp.database import register, find_by_email, find_by_email_with_pass, update_account, create_post_db, \
    search_calc, insert_passengers_for_driver, find_posts_and_passengers, insert_reserved_posts_for_passenger, \
    save_picture
from flaskapp.database import find_reserved_post, find_posts, find_posts_by_address, reserve_seats, reserved_roads
from datetime import datetime
from bson import ObjectId



@app.route('/', methods=['GET', 'POST'])
def index():
    login_form = LoginForm()
    search_form = SearchForm()
    modal_attr = ""
    today_date = datetime.now().strftime('%Y-%m-%d')

    if login_form.submit2.data:
        if login_form.validate_on_submit():
            user = find_by_email_with_pass(login_form.email.data)
            if user and bcrypt.check_password_hash(user["password"], login_form.password.data):
                session["user"] = login_form.email.data
                return redirect(url_for('home'))
            else:
                modal_attr = "myModal"
        else:
            modal_attr = "myModal"

    if search_form.submit_search.data:
        place_of_departure = search_form.honnan.data
        destination = search_form.hova.data
        estimated_travel_date = search_form.estimated_travel_date.data
        if estimated_travel_date:
            estimated_travel_date = estimated_travel_date.strftime('%Y-%m-%d')
        drivers = search_calc(place_of_departure, destination, estimated_travel_date)
        drivers = [post for post in drivers]
        for index, i in enumerate(drivers):
            j = i.pop('_id', None)
            drivers[index] = {**j, **i}
        return render_template('home2.html', drivers=drivers,
                               search_form=search_form, today_date=today_date, login_form=login_form)

    return render_template("index.html", login_form=login_form, modal_attr=modal_attr, search_form=search_form)


@app.route('/home', methods=['GET', 'POST'])
def home():
    if "user" in session:
        today_date = datetime.now().strftime('%Y-%m-%d')
        search_form = SearchForm()
        user = find_by_email(session["user"])
        passengers = []
        if user["address"]:
            drivers = find_posts_by_address(user['address'])
            drivers = [driver for driver in drivers if 'posts' in driver]
            for index, i in enumerate(drivers):
                j = i.pop('_id', None)
                drivers[index] = {**j, **i}
        else:
            drivers = find_posts()
            drivers = [driver for driver in drivers if 'posts' in driver]
            post_temp = []

            for driver in drivers:
                for post in driver['posts']:
                    if post['seats'] > 0:
                        post_temp.append(post)
                driver['posts'] = post_temp[:]
                post_temp.clear()

        if search_form.submit_search.data:
            place_of_departure = search_form.honnan.data
            destination = search_form.hova.data
            estimated_travel_date = search_form.estimated_travel_date.data
            if estimated_travel_date:
                estimated_travel_date = estimated_travel_date.strftime('%Y-%m-%d')

            drivers = search_calc(place_of_departure, destination, estimated_travel_date)

            drivers = [post for post in drivers]

            for index, i in enumerate(drivers):
                j = i.pop('_id', None)
                drivers[index] = {**j, **i}

            return render_template('home.html', drivers=drivers, user=user,
                                   search_form=search_form, today_date=today_date)

        return render_template('home.html', drivers=drivers, user=user,
                               search_form=search_form, today_date=today_date, passengers=passengers)

    return redirect(url_for('index'))


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    login_form = LoginForm()
    reg_form = RegistrationForm()
    modal_attr = ""

    if login_form.submit2.data:
        if login_form.validate_on_submit():
            user = find_by_email_with_pass(login_form.email.data)
            if user and bcrypt.check_password_hash(user["password"], login_form.password.data):
                session["user"] = login_form.email.data
                return redirect(url_for('home'))
            else:
                modal_attr = "myModal"
        else:
            modal_attr = "myModal"

    if reg_form.submit1.data:
        if reg_form.validate_on_submit() and request.form.get('select') != 'not selected':
            hashed_password = bcrypt.generate_password_hash(reg_form.password.data).decode('utf-8')
            register(reg_form.username.data, reg_form.firstName.data, reg_form.lastName.data, reg_form.email.data,
                     hashed_password, reg_form.phone_number.data, request.form.get('select'))
            session["user"] = reg_form.email.data
            flash(f'Fiók létrehozva !', 'success')
            return redirect(url_for('home'))
        elif request.method == 'POST' and request.form.get('select') == 'not selected':
            flash(f'Válassz a listából !', 'danger')
            print(reg_form.submit1.data, 'reg')

    return render_template('reg.html', reg_form=reg_form, login_form=login_form, modal_attr=modal_attr)


current_user = {}


@app.route('/account', methods=['GET', 'POST'])
def account():
    if "user" in session:
        global current_user
        passenger = ''
        driver = ''
        user = find_by_email(session["user"])
        current_user = user
        account_form = AccountForm()

        if request.method == 'GET':
            account_form.email.data = user["email"]
            account_form.username.data = user["username"]
            account_form.firstName.data = user["firstName"]
            account_form.lastName.data = user["lastName"]
            account_form.address.data = user["address"]
            account_form.phone_number.data = user["phone"]
        if account_form.validate_on_submit() and request.form.get('select') != 'not selected':
            update_account(session["user"], account_form.username.data, account_form.firstName.data,
                           account_form.lastName.data, account_form.email.data, account_form.phone_number.data,
                           account_form.address.data, request.form.get('select'))
            session["user"] = account_form.email.data

            if account_form.picture.data:
                profile_image = account_form.picture.data
                save_picture(profile_image, session["user"])
            current_user = find_by_email(session["user"])
            flash('Sikeres frissítés !', 'success')
        return render_template('account.html', account_form=account_form, user=current_user)
    return redirect(url_for('index'))


@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if "user" in session:
        user = find_by_email(session["user"])
        modal_attr = ""
        today_date = datetime.now().strftime('%Y-%m-%d')
        post_form = CreatePostForm()
        if post_form.validate_on_submit() and request.form.get('select_vehicle') != 'not selected':
            if find_by_email(session["user"])["phone"] == '':
                modal_attr = "myModal2"
                return render_template('create_post.html', post_form=post_form, today_date=today_date,
                                       modal_attr=modal_attr, user=user)
            if find_by_email(session["user"])["passenger_or_driver"] == 'Utas':
                modal_attr = "myModal3"
                return render_template('create_post.html', post_form=post_form, today_date=today_date,
                                       modal_attr=modal_attr, user=user)

            create_post_db(session["user"], post_form.car_brand.data, post_form.car_model.data,
                           post_form.car_color.data, post_form.date_of_manufacture.data, post_form.seats.data,
                           post_form.place_of_departure.data, post_form.destination.data, post_form.price.data,
                           post_form.note.data,
                           post_form.house_to_house.data, post_form.package_delivery.data,
                           request.form.get('select_vehicle'),
                           post_form.travel_date.data.strftime('%Y-%m-%d'), post_form.start_time.data.strftime('%H:%M'),
                           post_form.arrival_time.data.strftime('%H:%M'))

            modal_attr = "myModal"
        elif request.method == 'POST' and request.form.get('select_vehicle') == 'not selected':
            flash(f'Válassz a listából !', 'danger')
        return render_template('create_post.html', post_form=post_form, today_date=today_date, modal_attr=modal_attr,
                               user=user)
    return redirect(url_for('index'))


reserved_post_azon = ''


@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':
        reserve_seats(request.form.get('post_azon'), int(request.form.get('free_seats')))
        user = find_by_email(session["user"])
        insert_passengers_for_driver(request.form.get('post_azon'), user["email"],
                                     user["username"], user["firstName"], user["lastName"], user["phone"],
                                     int(request.form.get('free_seats')))
        insert_reserved_posts_for_passenger(request.form.get('post_azon'), session['user'],
                                            int(request.form.get('free_seats')))
        global reserved_post_azon
        reserved_post_azon = request.form.get('post_azon')
        return redirect(url_for('passenger'))
    return redirect(url_for('home'))


def passenger_seats(passenger_email, actual_post_id):
    reserved_seats = None
    roads = reserved_roads(passenger_email)
    if roads:
        for road in roads['reserved_roads']:
            if ObjectId(road['post_id']) == actual_post_id:
                reserved_seats = road['reserved_seats']
    return reserved_seats


@app.route('/driver', methods=['GET', 'POST'])
def driver():
    if "user" in session:
        user = find_by_email(session["user"])
        posts_and_passengers = find_posts_and_passengers(session["user"])
        if posts_and_passengers:
            posts_and_passengers = posts_and_passengers['posts']
        else:
            posts_and_passengers = []
        return render_template('driver.html', posts_and_passengers=posts_and_passengers, user=user,
                               reserved_seats_by_passenger=passenger_seats)
    return redirect(url_for('index'))


@app.route('/passenger', methods=['GET', 'POST'])
def passenger():
    if "user" in session:
        user = find_by_email(session["user"])
        roads = reserved_roads(session['user'])
        global reserved_post_azon

        if reserved_post_azon:
            current_reserved_post = ObjectId(reserved_post_azon)
        else:
            current_reserved_post = ''
        reserved_post_azon = ''
        posts = []
        if roads:
            for _id in roads['reserved_roads']:
                post = find_reserved_post(_id['post_id'])
                for i in post:
                    posts.append((i, _id['reserved_seats']))

            return render_template('passenger.html', drivers=posts, user=user,
                                   current_reserved_post=current_reserved_post)
        else:
            return render_template('passenger.html', drivers=posts, user=user,
                                   current_reserved_post=current_reserved_post)


@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for('index'))


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response
