import os
from werkzeug.utils import secure_filename
from app import models, routes
from flask import redirect, url_for
from flask_login import current_user
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import ImageUploadField


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
		ext = os.path.splitext(file_data.filename)[1]
		idx = f'{obj.event_id:04}'
		root = 'img_eid' + idx
		obj.img_root = root
		return secure_filename(root + ext)

	form_extra_fields = {
		'path': ImageUploadField('Upload image',
					base_path=os.path.join(basedir, 'static/images'),
					thumbnail_size=(200, 200, True), namegen=prefix_name)
	}
