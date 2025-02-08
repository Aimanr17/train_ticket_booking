document.addEventListener('DOMContentLoaded', function() {
    const selectedSeats = new Set();
    const maxSeats = parseInt(localStorage.getItem('passengers')) || 1;

    // Connect to WebSocket if available
    if (typeof socket !== 'undefined') {
        socket.on('connect', () => {
            console.log('Connected to WebSocket');
        });

        socket.on('seat_locked', (data) => {
            const seat = document.querySelector(`[data-seat-id="${data.seat_id}"]`);
            if (seat) {
                seat.classList.add('locked');
                if (selectedSeats.has(data.seat_id)) {
                    selectedSeats.delete(data.seat_id);
                    updateSelectedSeats();
                }
            }
        });

        socket.on('seat_unlocked', (data) => {
            const seat = document.querySelector(`[data-seat-id="${data.seat_id}"]`);
            if (seat) {
                seat.classList.remove('locked');
            }
        });
    }

    // Initialize date input with tomorrow's date
    const dateInput = document.getElementById('date');
    if (dateInput) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        dateInput.min = tomorrow.toISOString().split('T')[0];
        dateInput.value = tomorrow.toISOString().split('T')[0];
    }

    // Seat selection functionality
    const seatingPlan = document.querySelector('.seating-plan');
    if (seatingPlan) {
        console.log('Seating plan found');
        seatingPlan.addEventListener('click', function(e) {
            const seat = e.target.closest('.seat');
            if (!seat || seat.classList.contains('locked')) {
                console.log('Invalid seat click or seat is locked');
                return;
            }

            console.log('Seat clicked:', seat.dataset.seatNumber);
            const seatId = seat.dataset.seatId;

            if (seat.classList.contains('selected')) {
                console.log('Deselecting seat');
                selectedSeats.delete(seatId);
                seat.classList.remove('selected');
            } else if (selectedSeats.size < maxSeats) {
                console.log('Selecting seat');
                selectedSeats.add(seatId);
                seat.classList.add('selected');
            }

            updateSelectedSeats();
        });
    }

    // Update selected seats display
    function updateSelectedSeats() {
        const list = document.getElementById('selected-seats-list');
        const confirmButton = document.getElementById('confirm-seats');
        const totalAmount = document.getElementById('total-amount');
        
        if (list) {
            list.innerHTML = '';
            selectedSeats.forEach(seatId => {
                const seat = document.querySelector(`[data-seat-id="${seatId}"]`);
                if (seat) {
                    const li = document.createElement('li');
                    li.textContent = `Coach ${seat.dataset.coach} - Seat ${seat.dataset.seatNumber}`;
                    list.appendChild(li);
                }
            });
        }

        if (totalAmount && typeof window.trainPrice !== 'undefined') {
            totalAmount.textContent = (selectedSeats.size * window.trainPrice).toFixed(2);
        }

        if (confirmButton) {
            confirmButton.disabled = selectedSeats.size === 0;
            if (selectedSeats.size > 0) {
                confirmButton.onclick = function() {
                    // Store selected seats in local storage
                    const selectedSeatsArray = Array.from(selectedSeats).map(seatId => {
                        const seat = document.querySelector(`[data-seat-id="${seatId}"]`);
                        return {
                            id: seatId,
                            coach_number: seat.dataset.coach,
                            seat_number: seat.dataset.seatNumber
                        };
                    });

                    localStorage.setItem('selected_seats', JSON.stringify(selectedSeatsArray));
                    document.cookie = `selected_seats=${JSON.stringify(selectedSeatsArray)}; path=/`;
                    window.location.href = `/booking_summary/${window.trainId}`;
                };
            }
        }
    }

    // Handle booking confirmation on summary page
    const confirmBookingBtn = document.getElementById('confirm-booking');
    if (confirmBookingBtn) {
        console.log('Confirm booking button found');
        confirmBookingBtn.addEventListener('click', function() {
            console.log('Confirm booking clicked');
            const selectedSeats = JSON.parse(localStorage.getItem('selected_seats') || '[]');
            
            if (typeof socket !== 'undefined') {
                selectedSeats.forEach(seat => {
                    socket.emit('lock_seat', { seat_id: seat.id });
                });
            }

            alert('Booking confirmed! Thank you for choosing our service.');
            localStorage.removeItem('selected_seats');
            window.location.href = '/';  // Redirect to main page
        });
    }
});
