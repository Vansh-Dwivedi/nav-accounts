from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

with app.app_context():
    db.create_all()

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'name': user.name,
        'address': user.address,
        'phone_number': user.phone_number,
        'profile_pic': user.profile_pic,
        'description_file': user.description_file,
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for user in users])

@app.route('/user', methods=['POST'])
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
    
    return jsonify({'id': new_user.id})

@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted'})
    return jsonify({'message': 'User not found'}), 404

@app.route('/user/<int:id>', methods=['PUT'])
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
        return jsonify({'message': 'User updated'})
    return jsonify({'message': 'User not found'}), 404

if __name__ == '__main__':
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'photos'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'docs'), exist_ok=True)
    app.run(debug=True)