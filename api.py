from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

# Model User
class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"User(name={self.name}, email={self.email})"

# Argument parsers
user_args = reqparse.RequestParser()
user_args.add_argument('name', type=str, required=True, help="Name cannot be blank")
user_args.add_argument('email', type=str, required=True, help="Email cannot be blank")

user_query_args = reqparse.RequestParser()
user_query_args.add_argument('name', type=str, help="Filter by name")
user_query_args.add_argument('email', type=str, help="Filter by email")

# Fields for marshalling
userFields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
}

# Resource for multiple users
class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        args = user_query_args.parse_args()
        query = UserModel.query
        if args['name']:
            query = query.filter(UserModel.name.like(f"%{args['name']}%"))
        if args['email']:
            query = query.filter(UserModel.email.like(f"%{args['email']}%"))
        users = query.all()
        return users

    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        # Check for duplicate name or email
        if UserModel.query.filter_by(email=args['email']).first() or UserModel.query.filter_by(name=args['name']).first():
            abort(409, message="User with that name or email already exists")
        user = UserModel(name=args["name"], email=args["email"])
        db.session.add(user)
        db.session.commit()
        return user, 201

# Resource for individual user
class User(Resource):
    @marshal_with(userFields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        return user

    @marshal_with(userFields)
    def patch(self, id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        user.name = args["name"]
        user.email = args["email"]
        db.session.commit()
        return user

    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}, 200

# Register resources
api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:id>')

@app.route('/')
def home():
    return '<h1>Kelompok 4</h1>'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
