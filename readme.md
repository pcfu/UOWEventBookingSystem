# CSIT214 - Event Booking System

This repository contains the prototype for CSIT214's Event Booking System for my group. It uses Flask and its extension modules for the implementation.

## Installation

Follow the below instructions in cmd/bash for a rough guide on how to get this working - The below code assumes you already have Git installed on your computer. The instruction creates an isolated venv and activates it, which then installs the required packages via requirements.txt so they are not installed globally.
```bash
::cd into your desired directory
git clone <this_repository_url>
python -m venv <virtual-env name>
cd <virtual-env name>
cd Scripts
activate
cd ..
pip install -r requirements.txt
```

## Usage
while in the virtual environment created
```python
python -m event_system
```
to start an instance of the program
http://localhost:4000/ to access the website


## Tasks
1. Implement the change request as per required
2. Models segregation into different files under /models
3. Access control / permissions for flask-admin views
4. Implement Booking function - forms and retrieval of event-specific booking page
5. Implement listener for image(_thumb) for when an event is deleted


## Contributing
If you are a collaborator, push into the appropriate branch that is branched from dev