from flask import abort
from flask_login import current_user
from .models import Permission
from functools import wraps

def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def in_deco(*args,**kwargs):
			if not current_user.can(permission):
				abort(403)
			return f(*args,**kwargs)
		return in_deco
	return decorator

def administrator_required(f):
	return permission_required(Permission.ADMINISTER)(f)