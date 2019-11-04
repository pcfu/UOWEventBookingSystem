# CSIT214 - Event Booking System

This repository contains the prototype for CSIT214's Event Booking System for my group. It uses Flask micro framework for web services and Flask-SQLAlchemy (for now)

## Installation

Follow the below instructions in cmd/bash for a rough guide on how to get this working - The below code assumes you already have Git installed on your computer. The instruction creates an isolated venv and activates it, which then installs the required packages via requirements.txt so they are not installed globally.
```bash
::cd into your desired directory
git clone <this_repository_url>
python -m venv %cd%
cd Scripts
activate
cd ..
pip install -r requirements.txt
deactivate
```

## Usage
```python
python -m event_system
```
to start an instance of the program
http://localhost:4000/ to access the website


## Tasks
1. Implement Payment model to track payment records for successful bookings
2. Page for user to view, amend or cancel bookings
3. Adding payments when increasing booking quantity from user's booking page - updating entry in db
4. Implement Refund model for refunds
5. Issuing refund when decreasing quantity from user's booking page - updating entry in db
6. Promotion codes for bookings (Promotion model)
7. Account page for users to change email, password, etc etc.
8. Fix CVV validation for month if current_year = year but entered month is < current_month


## Contributing
```git
git branch -b <your_initials-branch>
```