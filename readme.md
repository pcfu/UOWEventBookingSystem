# CSIT214 - Event Booking System

This repository contains the prototype for CSIT214's Event Booking System for my group. It uses Flask micro framework for web services and Flask-SQLAlchemy

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
1. Once the above (prioritized and chosen) tasks are done, a major cleanup will be required - HTML requires segregation with inline css styling as much as possible, JS to live separately in /js/. Flask end will have to deal with code block segmentation and categorizing for organization.

### Optional Tasks (mostly UI)
- Member/Staff login + registration interactable buttons: highlight on mouseover? make consistent with rest of website theme
- Payment page: Price set to 2 decimal places
- Error messages: Create a css class for error messages
- Consider making even title text smaller on event search page
- (not so important) Event details page. List of timings. Make thematically similar to my_bookings listing


## Contributing
```git
git branch -b <your_initials-branch>
```
