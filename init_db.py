from app import app, db, Train, Seat
from datetime import datetime, timedelta

def init_db():
    with app.app_context():
        # Add sample trains
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

        # Create seats for the train
        for coach in range(1, 7):  # 6 coaches
            for row in range(1, 5):  # 4 rows (A-D)
                for seat in range(1, 6):  # 5 seats per row (1-5)
                    new_seat = Seat(
                        train_id=sample_train.id,
                        coach_number=coach,
                        seat_number=f"{chr(64 + row)}{seat}",  # A1-A5, B1-B5, C1-C5, D1-D5
                        is_locked=False
                    )
                    db.session.add(new_seat)
        db.session.commit()

if __name__ == '__main__':
    init_db()
    print("Database initialized with sample data!")
