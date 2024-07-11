from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
CORS(app)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    profile_pic = db.Column(db.String(120), nullable=True)
    description_file = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

with app.app_context():
    db.create_all()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Admin.query.filter_by(id=data['id']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    auth = request.form
    if not auth or not auth.get('username') or not auth.get('password'):
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user = Admin.query.filter_by(username=auth.get('username')).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.get('password')):
        token = jwt.encode({'id': user.id, 'exp' : datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token' : token})

    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

@app.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'name': user.name,
        'address': user.address,
        'phone_number': user.phone_number,
        'profile_pic': user.profile_pic,
        'description_file': user.description_file,
        'created_at': user.created_at
    } for user in users])

@app.route('/user', methods=['POST'])
@token_required
def add_user(current_user):
    data = request.form
    name = data['name']
    address = data['address']
    phone_number = data['phone_number']
    profile_pic = None
    description_file = None

    if 'profile_pic' in request.files:
        profile_pic = request.files['profile_pic']
        profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], 'photos', profile_pic.filename))
        profile_pic = profile_pic.filename

    if 'description_file' in request.files:
        description_file = request.files['description_file']
        description_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'docs', description_file.filename))
        description_file = description_file.filename

    new_user = User(name=name, address=address, phone_number=phone_number, profile_pic=profile_pic, description_file=description_file)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'id': new_user.id})

@app.route('/user/<int:id>', methods=['DELETE'])
@token_required
def delete_user(current_user, id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted'})
    return jsonify({'message': 'User not found'}), 404

@app.route('/user/<int:id>', methods=['PUT'])
@token_required
def update_user(current_user, id):
    user = User.query.get(id)
    if user:
        data = request.form
        user.name = data['name']
        user.address = data['address']
        user.phone_number = data['phone_number']
        
        if 'profile_pic' in request.files:
            profile_pic = request.files['profile_pic']
            profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], 'photos', profile_pic.filename))
            user.profile_pic = profile_pic.filename

        if 'description_file' in request.files:
            description_file = request.files['description_file']
            description_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'docs', description_file.filename))
            user.description_file = description_file.filename

        db.session.commit()
        return jsonify({'message': 'User updated'})
    return jsonify({'message': 'User not found'}), 404

if __name__ == '__main__':
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'photos'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'docs'), exist_ok=True)
    app.run(debug=True)
