from flask_admin.babel import lazy_gettext
from flask_admin.contrib.sqla.filters import BaseSQLAFilter, BooleanEqualFilter, FilterEmpty


class FilterNull(FilterEmpty):
	def operation(self):
		return lazy_gettext('is NULL')


class BooleanFilter(BooleanEqualFilter):
	def apply(self, query, value, alias=None):
		if value == '1':
			return query.filter(self.column == True)
		else:
			return query.filter(self.column == False)

	def operation(self):
		return 'is true'


class RegularUserFilter(BaseSQLAFilter):
	def apply(self, query, value, alias=None):
		if value == '1':
			return query.filter(self.column == 1)
		else:
			return query.filter(self.column != 1)

	def operation(self):
		return 'regular'


class StaffUserFilter(BaseSQLAFilter):
	def apply(self, query, value, alias=None):
		if value == '1':
			return query.filter(self.column == 2)
		else:
			return query.filter(self.column != 2)

	def operation(self):
		return 'staff'


class AdminUserFilter(BaseSQLAFilter):
	def apply(self, query, value, alias=None):
		if value == '1':
			return query.filter(self.column == 3)
		else:
			return query.filter(self.column != 3)

	def operation(self):
		return 'admin'
