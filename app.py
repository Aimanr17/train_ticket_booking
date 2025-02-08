from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///train_booking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    train_number = db.Column(db.String(20), unique=True, nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)

class Seat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    coach_number = db.Column(db.Integer, nullable=False)
    seat_number = db.Column(db.String(3), nullable=False)
    is_locked = db.Column(db.Boolean, default=False)
    lock_timestamp = db.Column(db.DateTime)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled

with app.app_context():
    db.create_all()
    # Add sample train data if not exists
    if not Train.query.first():
        sample_train = Train(
            train_number="TR001",
            origin="Kuala Lumpur",
            destination="Penang",
            departure_time=datetime.now() + timedelta(days=1),
            arrival_time=datetime.now() + timedelta(days=1, hours=4),
            price=50.0
        )
        db.session.add(sample_train)
        db.session.commit()

        # Create seats for the train (20 seats per coach, 6 coaches)
        for coach in range(1, 7):  # 6 coaches
            for row in range(1, 5):  # 4 rows (A-D)
                for seat in range(1, 6):  # 5 seats per row (1-5)
                    new_seat = Seat(
                        train_id=sample_train.id,
                        coach_number=coach,
                        seat_number=f"{chr(64 + row)}{seat}"  # A1-A5, B1-B5, C1-C5, D1-D5
                    )
                    db.session.add(new_seat)
        db.session.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/trains')
def trains():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    date = request.args.get('date')
    trains = Train.query.filter_by(origin=origin, destination=destination).all()
    return render_template('trains.html', trains=trains)

@app.route('/seats/<int:train_id>')
def seats(train_id):
    train = Train.query.get_or_404(train_id)
    # Get all seats for this train
    seats = Seat.query.filter_by(train_id=train_id).all()
    
    # If no seats exist for this train, create them
    if not seats:
        # Create seats for each coach (A1-A5, B1-B5, C1-C5, D1-D5)
        for coach in range(1, 7):  # 6 coaches
            for row in ['A', 'B', 'C', 'D']:
                for num in range(1, 6):  # 5 seats per row
                    seat_number = f"{row}{num}"
                    new_seat = Seat(
                        train_id=train_id,
                        coach_number=coach,
                        seat_number=seat_number,
                        is_locked=False
                    )
                    db.session.add(new_seat)
        db.session.commit()
        # Get the newly created seats
        seats = Seat.query.filter_by(train_id=train_id).all()
    
    return render_template('seat_selection.html', train=train, seats=seats)

@app.route('/booking_summary/<int:train_id>')
def booking_summary(train_id):
    train = Train.query.get_or_404(train_id)
    
    # Get selected seats from cookies
    selected_seats = request.cookies.get('selected_seats', '[]')
    try:
        selected_seats = json.loads(selected_seats)
    except json.JSONDecodeError:
        selected_seats = []
    
    # Calculate total amount
    total_amount = train.price * len(selected_seats)
    
    return render_template('booking_summary.html', 
                         train=train, 
                         seats=selected_seats, 
                         total=total_amount)

@socketio.on('lock_seat')
def handle_seat_lock(data):
    seat_id = data['seat_id']
    seat = Seat.query.get(seat_id)
    if seat and not seat.is_locked:
        seat.is_locked = True
        seat.lock_timestamp = datetime.utcnow()
        db.session.commit()
        emit('seat_locked', {'seat_id': seat_id}, broadcast=True)

@socketio.on('unlock_seat')
def handle_seat_unlock(data):
    seat_id = data['seat_id']
    seat = Seat.query.get(seat_id)
    if seat and seat.is_locked:
        seat.is_locked = False
        seat.lock_timestamp = None
        db.session.commit()
        emit('seat_unlocked', {'seat_id': seat_id}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
