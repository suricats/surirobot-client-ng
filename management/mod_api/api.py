import werkzeug
import datetime
from flask import Blueprint
from flask_restful import reqparse, Api, Resource, fields, marshal_with, inputs

from management import db
from .models import User, Picture, LogRecognize
from .utils import save_file, delete_file

from recognition_engine.utils import add_picture, remove_picture

mod_api = Blueprint('api', __name__)
api = Api(mod_api)

user_parser = reqparse.RequestParser()
user_parser.add_argument('firstname', type=str)
user_parser.add_argument('lastname', type=str)
user_parser.add_argument('email', type=str)

picture_parser = reqparse.RequestParser()
picture_parser.add_argument(
    'picture', type=werkzeug.datastructures.FileStorage, location='files'
)

log_recognize_parser = reqparse.RequestParser()
log_recognize_parser.add_argument('value', type=inputs.boolean)

user_fields = {
    'id': fields.Integer,
    'firstname': fields.String,
    'lastname': fields.String,
    'email': fields.String,
}

picture_fields = {
    'id': fields.Integer,
    'path': fields.String,
    'user_id': fields.Integer,
}

log_recognize_fields = {
    'id': fields.Integer,
    'value': fields.Boolean,
    'date': fields.DateTime,
}


# User
# shows a single user item and lets you delete a user item
class UserApi(Resource):
    @marshal_with(user_fields)
    def get(self, user_id):
        user = User.query.get(user_id)
        return user

    def delete(self, user_id):
        user = User.query.get(user_id)

        for picture in user.pictures:
            delete_file(picture.path)
            db.session.delete(picture)

        db.session.delete(user)
        db.session.commit()

        return '', 204

    @marshal_with(user_fields)
    def put(self, user_id):
        args = user_parser.parse_args()
        user = User.query.get(user_id)
        user.firstname = args['firstname']
        user.lastname = args['lastname']
        user.email = args['email']
        db.session.add(user)
        db.session.commit()

        return user, 201


# UserList
# shows a list of all users, and lets you POST to add new users
class UserListApi(Resource):
    @marshal_with(user_fields)
    def get(self):
        users = User.query.all()
        return users

    @marshal_with(user_fields)
    def post(self):
        args = user_parser.parse_args()
        user = User(
            firstname=args['firstname'],
            lastname=args['lastname'],
            email=args['email']
        )
        db.session.add(user)
        db.session.commit()

        return user, 201


# Picture
# shows a single picture item and lets you delete a picture item
class PictureApi(Resource):
    @marshal_with(picture_fields)
    def get(self, user_id, picture_id):
        picture = Picture.query.get(picture_id)
        return picture

    def delete(self, user_id, picture_id):
        picture = Picture.query.get(picture_id)

        remove_picture(picture)

        delete_file(picture.path)
        db.session.delete(picture)
        db.session.commit()

        return '', 204

    @marshal_with(picture_fields)
    def put(self, user_id, picture_id):
        picture = Picture.query.get(picture_id)
        args = picture_parser.parse_args()

        picture_path = save_file(args['picture'])
        delete_file(picture.path)
        picture.path = picture_path

        db.session.add(picture)
        db.session.commit()

        return picture, 201


# PictureList
# shows a list of picture, by user
class PictureListApi(Resource):
    @marshal_with(picture_fields)
    def get(self, user_id):
        user = User.query.get(user_id)
        pictures = user.pictures

        return pictures

    @marshal_with(picture_fields)
    def post(self, user_id):
        user = User.query.get(user_id)
        args = picture_parser.parse_args()

        picture_path = save_file(args['picture'])
        picture = Picture(user=user, path=picture_path)

        db.session.add(picture)
        db.session.commit()

        add_picture(picture)

        return picture, 201


# LogRecognize
# shows a single log item and lets you delete a log item
class LogRecognizeApi(Resource):
    @marshal_with(log_recognize_fields)
    def get(self, log_recognize_id):
        log = LogRecognize.query.get(log_recognize_id)
        return log

    def delete(self, log_recognize_id):
        log = LogRecognize.query.get(log_recognize_id)

        db.session.delete(log)
        db.session.commit()

        return '', 204

    @marshal_with(log_recognize_fields)
    def put(self, log_recognize_id):
        args = log_recognize_parser.parse_args()
        log = LogRecognize.query.get(log_recognize_id)
        log.value = args['value']
        log.date = datetime.datetime.now()
        db.session.add(log)
        db.session.commit()

        return log, 201


# LogRecognizeList
# shows a list of all logs, and lets you POST to add new logs
class LogRecognizeListApi(Resource):
    @marshal_with(log_recognize_fields)
    def get(self):
        logs = LogRecognize.query.all()
        return logs

    @marshal_with(log_recognize_fields)
    def post(self):
        args = log_recognize_parser.parse_args()
        log = LogRecognize(
            value=args['value']
        )
        db.session.add(log)
        db.session.commit()

        return log, 201


# Register routing
api.add_resource(UserListApi, '/users')
api.add_resource(UserApi, '/users/<int:user_id>')
api.add_resource(PictureListApi, '/users/<int:user_id>/pictures')
api.add_resource(PictureApi, '/users/<int:user_id>/pictures/<int:picture_id>')
api.add_resource(LogRecognizeListApi, '/logs/recognize')
api.add_resource(LogRecognizeApi, '/logs/recognize/<int:log_recognize_id>')
