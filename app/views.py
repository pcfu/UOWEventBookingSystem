from werkzeug.utils import secure_filename

from app import models, routes
from flask import redirect, url_for
from flask_login import current_user
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import ImageUploadField
import os

basedir = os.path.abspath(os.path.dirname(__file__))

def is_staff_user():
	staff = None
	if current_user.is_authenticated:
		target = current_user.username
		staff = models.Staff.query.filter_by(username=target).first()
	return staff is not None


class NoBypassAdminView(AdminIndexView):
	@expose('/')
	def index(self):
		if is_staff_user():
			return self.render('/admin/index.html')
		else:
			return redirect(url_for('staff_login'))


class NoBypassModelView(ModelView):
	def is_accessible(self):
		return is_staff_user()

	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('staff_login'))


class EventCreateView(NoBypassModelView):
	def prefix_name(obj, file_data):
		parts = os.path.splitext(file_data.filename)
		return secure_filename('file-%s%s' % parts)
	form_excluded_columns = ['image']
	form_extra_fields = {
		'path': ImageUploadField('Image',
									  base_path=os.path.join(basedir, 'static\\images'),
									  thumbnail_size=(100, 100, True), namegen=prefix_name)
	}




