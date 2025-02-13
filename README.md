# Train Ticket Booking Application

A real-time train ticket booking web application featuring a seat locking functionality.

## Features

- **Real-time Seat Booking**: Users can see seat availability and lock seats in real-time.
- **Coaches and Seats**: The application supports 6 coaches, each with 20 seats.
- **Interactive Interface**: Users can select seats through an intuitive interface.
- **Booking Flow**: Seamless flow from origin/destination selection to payment confirmation.
- **Real-time Updates**: All users receive real-time updates on seat availability as bookings are made.

## Setup and Installation

1. **Create a Virtual Environment**:
   ```bash
   python -m venv .venv
   ```

2. **Activate the Virtual Environment**:
   ```bash
   # Windows
   .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```

5. **Access the Application**:
   Open your browser and navigate to `http://localhost:5000`.

## Project Structure

- `/train_ticket_booking` - Main application directory
  - `/static` - Contains static files (CSS, JavaScript)
  - `/templates` - Contains HTML templates
  - `app.py` - Main Flask application file
  - `models.py` - Database models definition
  - `config.py` - Configuration settings for the application

## Contribution

Feel free to fork the repository and submit pull requests for any improvements or features you wish to add!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.