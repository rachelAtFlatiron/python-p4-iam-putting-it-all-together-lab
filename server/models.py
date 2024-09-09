from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'


    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    #private attribute, will be managed via properties 
    #we won't be saving the plaintext password in the database 
    _password_hash = db.Column(db.String)
    bio = db.Column(db.String)
    image_url = db.Column(db.String)

    recipes = db.relationship('Recipe', back_populates='user')
    
    serialize_rules = ('-recipes.user', )

    #create a property for password
    #hybrid_property - allow us to set password_hash directly inside the sqlite3 database
    #however we will make it such that we cannot view this property in Flask-SQLAlchemy 
    @hybrid_property #getter
    def password_hash(self):
        raise AttributeError('password_hash is private')
    
    @password_hash.setter
    def password_hash(self, password):
        #generate_password_hash is a built in method provided by bcrypt that encrypts plaintext
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        #returns True or False
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    __table_args__ = (
        db.CheckConstraint('length(instructions) >= 50'),
    )


    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='recipes')

    serialize_rules = ('-user.recipes', )

    def __repr__(self):
        return f'<Recipe {self.id}: {self.title}>'