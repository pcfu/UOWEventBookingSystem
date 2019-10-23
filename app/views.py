from app import models, routes
from flask import redirect, url_for
from flask_login import current_user
from flask_admin import AdminIndexView, expose


class RestrictedAdminIndexView(AdminIndexView):
	@expose('/')
	def index(self):
		staff = None
		if current_user.is_authenticated:
			target = current_user.username
			staff = models.Staff.query.filter_by(username=target).first()

		if staff is not None:
			return self.render('/admin/index.html')
		else:
			return redirect(url_for('staff_login'))
