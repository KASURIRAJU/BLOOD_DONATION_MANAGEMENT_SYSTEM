from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import os, random

app = Flask(__name__)
CORS(app)

# --- DB CONFIG ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'blood_donation.db').replace('\\', '/')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODEL ---
class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    blood_group = db.Column(db.String(10))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)

    donation_date = db.Column(db.String(20))
    donation_time = db.Column(db.String(20))

    ref_id = db.Column(db.String(20))
    status = db.Column(db.String(20), default="pending")

    order_id = db.Column(db.String(20))
    start_date = db.Column(db.String(20))
    expiry_date = db.Column(db.String(20))

with app.app_context():
    db.create_all()

# --- ROUTES ---
@app.route('/')
def home():
    return send_from_directory(basedir, 'index.html')

# REGISTER
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    # Unique REF ID
    while True:
        ref_id = "REF" + str(random.randint(10000, 99999))
        if not Donor.query.filter_by(ref_id=ref_id).first():
            break

    donor = Donor(
        name=data['name'],
        age=data['age'],
        blood_group=data['blood_group'],
        phone=data['phone'],
        email=data['email'],
        address=data['address'],
        donation_date=data['date'],
        donation_time=data['time'],
        ref_id=ref_id,
        status="pending"
    )

    db.session.add(donor)
    db.session.commit()

    return jsonify({"ref_id": ref_id})

# ADMIN LOGIN
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if data['username'] == "raju@77" and data['password'] == "admin123":
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

# GET DONORS
@app.route('/api/donors', methods=['GET'])
def donors():
    data = Donor.query.all()

    result = []
    for d in data:
       result.append({
    "id": d.id,
    "ref_id": d.ref_id,
    "name": d.name,
    "age": d.age,
    "blood_group": d.blood_group,
    "phone": d.phone,
    "email": d.email,
    "address": d.address,
    "date": d.donation_date,
    "time": d.donation_time,
    "status": d.status,
    "order_id": d.order_id,
    "start_date": d.start_date,
    "expiry_date": d.expiry_date
}) 

    return jsonify(result)

# PROCESS DONOR
@app.route('/api/process/<int:id>', methods=['POST'])
def process(id):
    donor = Donor.query.get(id)

    if donor:
        order_id = "BD" + str(10000 + donor.id)

        start = datetime.today()
        expiry = start + timedelta(days=270)  # 9 months approx

        donor.status = "processed"
        donor.order_id = order_id
        donor.start_date = start.strftime("%Y-%m-%d")
        donor.expiry_date = expiry.strftime("%Y-%m-%d")

        db.session.commit()

        return jsonify({"success": True})

    return jsonify({"error": "Not found"}), 404

# CHECK STATUS
@app.route('/api/status/<ref>', methods=['GET'])
def status(ref):
    donor = Donor.query.filter_by(ref_id=ref).first()

    if donor:
        if donor.status == "processed":
            return jsonify({
                "status": "processed",
                "order_id": donor.order_id,
                "start_date": donor.start_date,
                "expiry_date": donor.expiry_date,
                "name": donor.name,
                "age": donor.age,
                "blood_group": donor.blood_group,
                "phone": donor.phone,
                "email": donor.email,
                "address": donor.address,
                "date": donor.donation_date,
                "time": donor.donation_time
            })
        return jsonify({"status": "pending"})

    return jsonify({"error": "Invalid REF"}), 404
@app.route('/api/delete/<int:id>', methods=['DELETE'])
def delete_donor(id):
    donor = Donor.query.get(id)

    if donor:
        db.session.delete(donor)
        db.session.commit()
        return jsonify({"success": True})

    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)