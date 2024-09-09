
#!/usr/bin/env python3


#1. import bcrypt
#2. write models
# - include @hybrid_property, password_hash.setter, authenticate
#3.write routes 
# - login, signup, authenticate 
#4.review React
from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

@app.before_request
def check_if_logged_in():
    open_access_list = [
        'signup',
        'login',
        'check_session'
    ]
    #cookie session and server session, stores user id
    #Flask session is persisted as a cookie in the user's browser by default. 
    print(session)

    if (request.endpoint) not in open_access_list and (not session.get('user_id')):
        return {'error': '401 Unauthorized'}, 401



class Signup(Resource):
    
    def post(self):

        request_json = request.get_json()

        username = request_json.get('username')
        # see later
        password = request_json.get('password')
        image_url = request_json.get('image_url')
        bio = request_json.get('bio')

        user = User(
            username=username,
            image_url=image_url,
            bio=bio
        )

        # the setter contains the encryption code 
        user.password_hash = password

        try:

            db.session.add(user)
            db.session.commit()
            #hash and save user_id on client-side and on server
            #Flask session is persisted as a cookie in the user's browser by default. 
            session['user_id'] = user.id


            return user.to_dict(), 201

        except IntegrityError:

            return {'error': '422 Unprocessable Entity'}, 422

class CheckSession(Resource):

    def get(self):
        # server sets cookie son client-side
        # and saves the user_id on server side but hashed
        user_id = session['user_id']
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200
        
        return {}, 401


class Login(Resource):
    #using post only because we need to pass along data
    def post(self):

        request_json = request.get_json()

        username = request_json.get('username')
        password = request_json.get('password')

        user = User.query.filter(User.username == username).first()

        if user:
            # see models, method authenticate contains code to check_password_hash
            if user.authenticate(password):

                # sets flask server with user_id
                session['user_id'] = user.id
                return user.to_dict(), 200

        return {'error': '401 Unauthorized'}, 401

class Logout(Resource):

    def delete(self):

        session['user_id'] = None
        
        return {}, 204
        

class RecipeIndex(Resource):

    def get(self):

        user = User.query.filter(User.id == session['user_id']).first()
        return [recipe.to_dict() for recipe in user.recipes], 200
        
        
    def post(self):

        request_json = request.get_json()

        title = request_json['title']
        instructions = request_json['instructions']
        minutes_to_complete = request_json['minutes_to_complete']

        try:

            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=session['user_id'],
            )

            db.session.add(recipe)
            db.session.commit()

            return recipe.to_dict(), 201

        except IntegrityError:

            return {'error': '422 Unprocessable Entity'}, 422


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)