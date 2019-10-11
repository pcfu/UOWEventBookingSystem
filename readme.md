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
Dummy user accounts are already created in csit214_database.db so you don't have to run make_user_accounts.py again. You just have to run the main.py file and it should work.

```python
python -m main
http://localhost:4000/ # to access the website
```

## Contributing
For now we will have to create an Event class and create dummy events, and display them in a page, i think that's a good first step. You can either
```git
git branch -b <your_initials-branch>
```
and commit the branch or you can just do it in master.