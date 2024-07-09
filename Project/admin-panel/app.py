from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_bcrypt import Bcrypt
import os
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['SECRET_KEY'] = 'your_secret_key_here'
CORS(app)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    profile_pic = db.Column(db.String(120), nullable=True)
    description_file = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password,
        address=data['address'],
        phone_number=data['phone_number']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.form
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        login_user(user)
        return jsonify({'message': 'Login successful'})
    return jsonify({'message': 'Invalid email or password'}), 401

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/users', methods=['GET'])
@login_required
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'address': user.address,
        'phone_number': user.phone_number,
        'profile_pic': user.profile_pic,
        'description_file': user.description_file,
        'created_at': user.created_at
    } for user in users])

@app.route('/user', methods=['POST'])
@login_required
def add_user():
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
    
    app.logger.info(f'Added new user: {new_user.name}')
    
    return jsonify({'id': new_user.id})

@app.route('/user/<int:id>', methods=['DELETE'])
@login_required
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        app.logger.info(f'Deleted user: {user.name}')
        return jsonify({'message': 'User deleted'})
    app.logger.warning(f'Tried to delete non-existing user with id: {id}')
    return jsonify({'message': 'User not found'}), 404

@app.route('/user/<int:id>', methods=['PUT'])
@login_required
def update_user(id):
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
        app.logger.info(f'Updated user: {user.name}')
        return jsonify({'message': 'User updated'})
    app.logger.warning(f'Tried to update non-existing user with id: {id}')
    return jsonify({'message': 'User not found'}), 404

if __name__ == '__main__':
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'photos'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'docs'), exist_ok=True)
    app.run(debug=True)