# CSIT214 - Event Booking System

Completed prototype for CSIT214's Event Booking System.
<br>Flask micro web service framework
<br>HTML, CSS, Bootstrap 4, JS, JQuery for frontend
## Installation

Follow the below instructions in cmd for a rough guide on how to get this working - The below code assumes you already have Git installed on your computer. The instruction creates an isolated venv and activates it, which then installs the required packages via requirements.txt so they are not installed globally.
```bash
::cd into your desired directory
git clone <this_repository_url>
python -m venv %cd%
cd Scripts
activate
cd ..
pip install -r requirements.txt
```

## Usage
```python
python -m event_system
```
to start an instance of the program
http://localhost:4000/ to access the website


## Tasks
- Test out the system and ensure that following functions can be done
    1. Staff User login, Create/Update/Delete 3 DIFFERENT Event Types & Date/Time
    2. Student Login
        - Search by event type, date range, price range
        - Book > 1 ticket, for >= 2 different events
        - Cancel existing booking
    3. Change Request
        - <s>User Management</s> / <b>System Admin </b>

## Contribution - Team Members
Fu Peichong<br>
Ong Yu Xiang<br>
Jonathan Kerk<br>
