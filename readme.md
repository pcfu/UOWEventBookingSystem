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
1. Logged in account stays logged in - will have to initiate some sort of onunload to disconnect connected user after leaving the website/closing browser
2. Setting rules for account names with regex, and special exceptions such as null or none or nil etc.
3. Once the above (prioritized and chosen) tasks are done, a major cleanup will be required - HTML requires segregation with inline css styling as much as possible, JS to live separately in /js/. Flask end will have to deal with code block segmentation and categorizing for organization.


## Contributing
```git
git branch -b <your_initials-branch>
```
