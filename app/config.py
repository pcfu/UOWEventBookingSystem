import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'csit214_database.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SECRET_KEY = 'secret'
	SESSION_TYPE = 'filesystem'
	'''
	JOBS = [ { 'id' : 'job1',
			   'func' : 'app.scheduled_tasks:deactivate_expired_slots',
			   'trigger' : 'interval',
			   'hours' : 1 },
			 { 'id' : 'job2',
			   'func' : 'app.scheduled_tasks:deactivate_expired_event_promotions',
			   'trigger' : 'interval',
			   'hours' : 1 }
			]
	SCHEDULER_API_ENABLED = True
	'''
	FLASK_ADMIN_SWATCH = 'sandstone'

	'''
	If required to store jobs record in db, add the following:

	-- 1 --
	from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

	-- 2 --
	SCHEDULER_JOBSTORES = {
		'default' : SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
	}

	-- 3 --
	Also add to JOBS dictionary, 'replace_existing' : True
	'''
