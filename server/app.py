#!/usr/bin/env python3

#1. create user model
#2. we will be encrypting the passwords so that they aren't in plaintext
#3. routes
#- signup
#- sign in
#- login
#- logout
#- checksession (keep the user logged)
#4. examine how this is used on the frontend
from flask import request, session, make_response, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

@app.before_request
def print_before_session():
    print('before', session)

@app.after_request
def print_session(response):
    print('after', session['user_id'])
    return response
#create new User instance, commit to database 
#create cookie/session to keep track of who is logged in on front-end and back-end
class Signup(Resource):
    def post(self):
        data = request.get_json()
        new_user = User(bio=data.get('bio'), image_url=data.get('image_url'), 
        #password_hash=data.get('password') will execute @password_hash.setter therefore running the encryption that we wrote in models.py
        username=data.get('username') )
        new_user.password_hash=data.get('password')
        #import ipdb; ipdb.set_trace()
        try:
            db.session.add(new_user)
            db.session.commit()
            #set session to user_id 
            session['user_id'] = new_user.id
            return make_response(new_user.to_dict(), 201)
        except Exception as e:
            return make_response({'message': str(e)}, 422)


# double check who is currently logged in and return that info to the client
# Flask session will automatically store info on the client side 
class CheckSession(Resource):
    def get(self):
        user_id = session['user_id']
        if user_id:
            cur_user = User.query.filter_by(id=user_id).first()
            return make_response(cur_user.to_dict(), 200)
        return make_response({'message': 'no one is logged in'}, 200)

class Login(Resource):
    def get(self):
        pass
    # post because i need to pass in login information
    def post(self):
        data = request.get_json()

        user = User.query.filter(User.username==data.get('username')).first()
        if not user:
            return make_response({'message':'no user with username'}, 401)
        #check if the password is correct (see models.py User.authenticate())
        if user.authenticate(data.get('password')):
            session['user_id'] = user.id 
            return make_response(user.to_dict(), 200)
        else:
            # 401 - unauthorized
            return make_response({'message': 'wrong password'}, 401)

class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return make_response({'message': 'user logged out'}, 200)

class RecipeIndex(Resource):
    def get(self):
        user = User.query.filter_by(id=session['user_id']).first()
        recipe_list = [recipe.to_dict() for recipe in user.recipes]
        return make_response(recipe_list, 200)

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)