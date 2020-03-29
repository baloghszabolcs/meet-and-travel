import sys
import pymongo
import dateutil.parser
from bson import objectid, ObjectId
from PIL import Image
import base64

uri = "mongodb://127.0.0.1:27017/"
client = pymongo.MongoClient(uri)
db = client.test_db
collection = db.test_collection

with open("flaskapp/static/avatar_2x.png", "rb") as avat:
    avatar = base64.b64encode(avat.read())
    avatar = avatar.decode('utf-8')


def register(username, firstname, lastname, email, password, phone, passenger_or_driver):
    collection.insert_one({"username": username,
                           "firstName": firstname,
                           "lastName": lastname,
                           "email": email,
                           "password": password,
                           "phone": phone,
                           "passenger_or_driver": passenger_or_driver,
                           "address": '',
                           "profile_picture": avatar})


def update_account(email, username, firstname, lastname, new_email, phone, address,
                   passenger_or_driver):  # profile_picture
    collection.update_one({"email": email},
                          {"$set": {"username": username, "firstName": firstname, "lastName": lastname,
                                    "email": new_email, "phone": phone, "address": address,
                                    "passenger_or_driver": passenger_or_driver}})


def save_picture(picture, email):
    tmp_img = Image.open(picture)
    tmp_thumb = tmp_img.resize((200, 200), Image.ANTIALIAS)
    tmp_thumb.save("/tmp/thumb_file.png")
    with open("/tmp/thumb_file.png", "rb") as img:
        thumb_string = base64.b64encode(img.read())
    image_string = thumb_string.decode('utf-8')
    print(sys.getsizeof(image_string))
    collection.update_one({"email": email},
                          {"$set": {"profile_picture": image_string}})


def create_post_db(email, car_brand, car_model, car_color, date_of_manufacture, seats, place_of_departure, destination,
                   price, note, house_to_house, package_delivery, vehicle_type, travel_date, start_time, arrival_time):
    post_doc = {
        "posts": {'_id': objectid.ObjectId(), "car_brand": car_brand, "car_model": car_model, "car_color": car_color,
                  "date_of_manufacture": date_of_manufacture,
                  "seats": seats, "place_of_departure": place_of_departure, "destination": destination,
                  "price": price,
                  "note": note,
                  "house_to_house": house_to_house,
                  "package_delivery": package_delivery,
                  "vehicle_type": vehicle_type,
                  "travel_date": dateutil.parser.parse(travel_date),
                  "start_time": dateutil.parser.parse(start_time),
                  "arrival_time": dateutil.parser.parse(arrival_time)
                  }}
    collection.update_one({"email": email}, {"$push": post_doc})


def existing_email(email):
    if collection.find_one({"email": email}, {}):
        return True
    else:
        return False


def find_posts():
    return collection.find({}, {'posts': 1, 'email': 1, 'username': 1, 'phone': 1, 'profile_picture': 1, '_id': 0})


def find_posts_by_address(address):
    pipeline = [
        {"$match":
             {"posts.place_of_departure": address}},
        {'$unwind': "$posts"},
        {"$match": {
            '$and': [{"posts.place_of_departure": address}, {"posts.seats": {'$gt': 0}}]}},
        {"$group": {
            "_id": {
                'username': '$username',
                'email': '$email',
                'phone': '$phone'
            },
            "posts": {"$push": "$posts"}

        }},
        {"$project": {"_id": 1, 'posts': 1}}
    ]

    return collection.aggregate(pipeline)


def update_post_db(post_id, car_brand, car_model, car_color, date_of_manufacture, seats,
                place_of_departure, destination, price, note, house_to_house, package_delivery, vehicle_type,
                travel_date, start_time, arrival_time):
    collection.update_one(
        {"posts._id": ObjectId(post_id)},
        {"$set":
             {"posts.$.car_brand": car_brand,
              "posts.$.car_model": car_model,
              "posts.$.car_color": car_color,
              "posts.$.date_of_manufacture": date_of_manufacture,
              "posts.$.seats": seats,
              "posts.$.place_of_departure": place_of_departure,
              "posts.$.destination": destination,
              "posts.$.price": price,
              "posts.$.note": note,
              "posts.$.house_to_house": house_to_house,
              "posts.$.package_delivery": package_delivery,
              "posts.$.vehicle_type": vehicle_type,
              "posts.$.travel_date": travel_date,
              "posts.$.start_time": start_time,
              "posts.$.arrival_time": arrival_time
              }}
    )


def find_post_by_post_id(post_id):
    return collection.find({
        "posts._id": ObjectId(post_id)
    }, {'posts.$.price': 1, '_id': 0})


def find_by_email(email):
    return collection.find_one({"email": email},
                               {'_id': 0, 'email': 1, 'username': 1, 'firstName': 1, 'lastName': 1, 'phone': 1,
                                'address': 1, 'passenger_or_driver': 1, 'profile_picture': 1})


def find_by_email_everything(email):
    return collection.find_one({"email": email})


def find_posts_and_passengers(email):
    return collection.find_one({"email": email},
                               {'_id': 0, 'posts': 1})


def find_by_email_with_pass(email):
    return collection.find_one({"email": email},
                               {'_id': 0, 'email': 1, 'username': 1, 'firstName': 1, 'lastName': 1, 'phone': 1,
                                'address': 1, 'passenger_or_driver': 1, 'profile_picture': 1, 'password': 1})


def existing_username(username):
    if collection.find_one({"username": username}, {}):
        return True
    else:
        return False


def search_calc(place_of_departure, destination, estimated_travel_date):
    if destination == '' and not estimated_travel_date:
        pipeline = [
            {"$match":
                 {"posts.place_of_departure": place_of_departure}},
            {'$unwind': "$posts"},
            {"$match": {
                '$and': [{"posts.place_of_departure": place_of_departure}, {"posts.seats": {'$gt': 0}}]}},
            {"$group": {
                "_id": {
                    'username': '$username',
                    'email': '$email',
                    'phone': '$phone',
                    'profile_picture': '$profile_picture'
                },
                "posts": {"$push": "$posts"}

            }},
            {"$project": {"_id": 1, 'posts': 1}}
        ]

        return collection.aggregate(pipeline)

    elif destination != '' and not estimated_travel_date:

        pipeline = [
            {"$match": {
                '$and': [{"posts.place_of_departure": place_of_departure}, {'posts.destination': destination}]}},
            {'$unwind': "$posts"},
            {"$match": {
                '$and': [{"posts.place_of_departure": place_of_departure}, {'posts.destination': destination},
                         {"posts.seats": {'$gt': 0}}]}},
            {"$group": {
                "_id": {
                    'username': '$username',
                    'email': '$email',
                    'phone': '$phone'
                },
                "posts": {"$push": "$posts"}

            }},
            {"$project": {"_id": 1, 'posts': 1}}
        ]

        return collection.aggregate(pipeline)

    elif destination == '' and estimated_travel_date:

        pipeline = [
            {"$match": {
                '$and': [{"posts.place_of_departure": place_of_departure},
                         {"posts.travel_date": dateutil.parser.parse(estimated_travel_date)}]}},
            {'$unwind': "$posts"},
            {"$match": {
                '$and': [{"posts.place_of_departure": place_of_departure},
                         {"posts.travel_date": dateutil.parser.parse(estimated_travel_date)},
                         {"posts.seats": {'$gt': 0}}]}},
            {"$group": {
                "_id": {
                    'username': '$username',
                    'email': '$email',
                    'phone': '$phone'
                },
                "posts": {"$push": "$posts"}

            }},
            {"$project": {"_id": 1, 'posts': 1}}
        ]

        return collection.aggregate(pipeline)

    elif destination and estimated_travel_date:

        pipeline = [
            {"$match": {
                '$and': [{"posts.place_of_departure": place_of_departure}, {"posts.destination": destination},
                         {"posts.travel_date": dateutil.parser.parse(estimated_travel_date)}]}},
            {'$unwind': "$posts"},
            {"$match": {
                '$and': [{"posts.place_of_departure": place_of_departure}, {"posts.destination": destination},
                         {"posts.travel_date": dateutil.parser.parse(estimated_travel_date)},
                         {"posts.seats": {'$gt': 0}}]}},
            {"$group": {
                "_id": {
                    'username': '$username',
                    'email': '$email',
                    'phone': '$phone'
                },
                "posts": {"$push": "$posts"}

            }},
            {"$project": {"_id": 1, 'posts': 1}}
        ]

        return collection.aggregate(pipeline)

    else:
        return {}


def reserve_seats(post_id, seats):
    collection.update_one({"posts._id": ObjectId(post_id)},
                          {"$inc": {"posts.$.seats": -seats}})


def insert_passengers_for_driver(post_id, passenger_email, passenger_username,
                                 passenger_firstName, passenger_lastName, passenger_phone, seats):
    if passenger_exists(passenger_email, post_id):
        pass
    else:
        collection.update_one({"posts._id": ObjectId(post_id)},
                              {"$push":
                                   {"posts.$.passengers":
                                        {"passenger_email": passenger_email, "passenger_username": passenger_username,
                                         "passenger_firstName": passenger_firstName,
                                         "passenger_lastName": passenger_lastName,
                                         "passenger_phone": passenger_phone,
                                         "seat": seats}}})


def passenger_exists(passenger_email, post_id):
    post = collection.find_one({'posts._id': ObjectId(post_id)},
                               {
                                   'posts.$': 1, '_id': 0
                               })

    post = post['posts'].pop(0)
    if 'passengers' in post:
        for p in post['passengers']:
            if passenger_email == p['passenger_email']:
                return True
            else:
                return False


def insert_reserved_posts_for_passenger(post_id, user_email, seats):
    if (road_exists(user_email, post_id)):
        collection.update_one({'email': user_email, 'reserved_roads.post_id': post_id},
                              {'$inc': {'reserved_roads.$.reserved_seats': seats}})
    else:
        collection.update_one({"email": user_email},
                              {'$push':
                                   {'reserved_roads': {'post_id': post_id,
                                                       'reserved_seats': seats}}})


def road_exists(email, post_id):
    return collection.find_one(
        {'email': email},
        {
            'reserved_roads': {'$elemMatch': {'post_id': post_id}},
            '_id': 0
        }
    )


def reserved_roads(email):
    return collection.find_one({"email": email},
                               {'reserved_roads': 1, '_id': 0})


def find_reserved_post(post_id):
    return collection.find({
        'posts._id': ObjectId(post_id)
    }, {'posts.$': 1, '_id': 0, 'username': 1, 'email': 1, 'phone': 1, 'profile_picture': 1})
