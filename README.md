# Smart Parking Management System

## Overview

The Smart Parking Management System is an IoT-based project designed to efficiently monitor and manage parking lot occupancy. It utilizes ESP32 microcontrollers and IR sensors to detect slot availability, with a user-friendly web interface for interaction. The project includes distinct functionalities for owners and users, ensuring a seamless parking experience.

---

## Features

### Owner Portal:

* **Update Slot Status:** Owners can manually mark slots as occupied, free, or under construction.
* **View Vehicle Logs:** A detailed history of all parked vehicles.

### User Portal:

* **Available Slots Overview:** Displays the current availability of parking slots.
* **Parking History:** Shows the user's past parking activities.
* **Payment Summary:** Users can view unpaid entries and update them as paid via the "Pay Now" button.

### Dashboard Tabs:

1. **Home:** Displays the parking lot layout.
2. **History:** Shows parking logs with details like:

   * In Time
   * Out Time
   * Duration
   * Status (Paid/Unpaid)
   * Amount (calculated at ₹50/hour).
3. **Payment History:** Displays past paid entries.

---

## Technology Stack

* **Backend:** Flask
* **Frontend:** HTML, CSS, JavaScript
* **Database:** SQLite
* **IoT Components:**

  * ESP32 microcontrollers
  * IR sensors for slot occupancy detection
* **Communication Protocol:** MQTT

---

## System Architecture

1. **Hardware Layer:**

   * IR sensors detect slot occupancy.
   * ESP32 processes sensor data and communicates via MQTT.
2. **Backend:**

   * Flask handles user authentication, slot updates, and log management.
3. **Frontend:**

   * A responsive web interface for owners and users.
4. **Database:**

   * SQL stores user data, slot statuses, and transaction logs.

---

## Installation and Setup

### Prerequisites

* Python 3.8 or higher
* Flask
* SQLite
* MQTT broker (e.g., Mosquitto)
* ESP32 setup with IR sensors

### Steps

1. Clone the repository:

2. Navigate to the project directory:

3. Install dependencies:

4. Set up database.

5. Deploy the Flask app:
   
7. Configure ESP32 devices to connect to the MQTT broker.


## Usage

### Owner Login

1. Navigate to the Owner Portal.
2. Log in with credentials.
3. Update slot statuses and view logs as needed.

### User Login

1. Navigate to the User Portal.
2. Log in with credentials.
3. View available slots, parking history, and payment summary.
4. Use the "Pay Now" button to clear unpaid entries.

---

## Future Enhancements

* Integration of payment gateways for real-time transactions.
* Advanced analytics for parking trends and predictions.
* Mobile app version for users.

---

## Contributing

Contributions are welcome! Please fork the repository and create a pull request for any enhancements or bug fixes.

---

## Contact

For any queries or feedback, reach out to:

* **Email:** [vins.techn@gmail.com](mailto:vins.techn@gmail.com)
* **GitHub:** [Vinay's GitHub](https://github.com/Vinstheking)
