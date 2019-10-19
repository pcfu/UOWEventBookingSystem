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
1. Currently the login system is kind of botched. The login authentication grabs User_user.id when authenticating even if you are logging in as admin.
Since Staff and User are 2 different tables, naturally they have clashing ids which in this case messes up the Flask_Login.
A temporary implementation is to redirect User level login to 'index' and Staff level login to 'admin/index' from the Flask_Admin library
    
    Requires more research on Flask_Login to understand if there is a way to implement user/admin system,
or using @roles_required decorators are better

2. Probably need some revision on the Database design, particularly on Event and User, maybe considering merging Staff into User with a is_admin attribute?

3. Research on the optimal way to use Flask_Admin - I think the current way of using ModelView is not the best

4. Integrate frontend html which is separately made into this program, and probably good to look up on Flask_Bootstrap



## Contributing
```git
git branch -b <your_initials-branch>
```