from app import db, config
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
import datetime
from hashlib import md5

# task_table = db.Table('task_table',
# 					  db.Column(
# 						  'organization_id', db.Integer, db.ForeignKey('organization.id')
# 					  ),
# 					  db.Column(
# 						  'task_id', db.Integer, db.ForeignKey('task.id')
# 					  )
# 					  )


role_table = db.Table('user_role',
					  db.Column(
						  'user_id', db.Integer, db.ForeignKey('user.id')
					  ),
					  db.Column(
						  'role_id', db.Integer, db.ForeignKey('role.id')
					  )
)

admin_user_table = db.Table('admin_user_table',
							db.Column(
								'user_id', db.Integer, db.ForeignKey('user.id')
							),
							db.Column(
								'organization_id', db.Integer, db.ForeignKey('organization.id')
							)
)



class Role(db.Model):
	__tablename__ = 'role'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), unique=True)
	users = relationship(
		"User",
		secondary=role_table,
		back_populates="roles"
	)

	def __init__(self, name):
		self.name = name.lower()

	def __repr__(self):
		return '<Role {}>'.format(self.name)

	def __str__(self):
		return self.name


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(120))
	last_name = db.Column(db.String(120))
	username = db.Column(db.String(120), unique=True)
	email = db.Column(db.String(120), unique=True)
	password = db.Column(db.String(120))
	sync_password = db.Column(db.String(120))
	sync_username = db.Column(db.String(120))
	__tablename__ = 'user'
	tasks = relationship("Task", back_populates="user")

	roles = relationship(
		"Role",
		secondary=role_table,
		back_populates="users"
	)

	admin_orgs = relationship(
		"Organization",
		secondary=admin_user_table,
		back_populates="admin_users"
	)
	type = db.Column(db.String(50))

	def __init__(self, email, password, roles=None):
		self.username = username.lower()
		self.set_password(password)

	#Needed flask properties
	@property
	def is_authenticated(self):
		return True

	@property
	def is_active(self):
		return True

	@property
	def is_anonymous(self):
		return False

	#password functions
	def set_password(self, password):
		self.password = generate_password_hash(password)

	def set_sync_password(self, password):
		self.sync_password = password
		for o in self.admin_orgs:
			o.add_task(self)

	def check_password(self, password):
		return check_password_hash(self.password, password)

	def get_id(self):
		return self.username

	def add_roles(self, *roles):
		self.roles.extend([role for role in roles if role not in self.roles])

	def check_role(self, role):
		if type(role) is str:
			rolelist = []
			for r in self.roles:
				rolelist.append(r.name)
			if role in rolelist:
				return True
		if role in self.roles:
			return True
	def gen_sync_username(self):
		self.sync_username = config.syncloginprefix + '-' + self.first_name + '.' + self.last_name

	def add_task(self, org):
		self.tasks.append(Task(org, self))

	def __repr__(self):
		return '<User %r>' % self.username




class Task(db.Model):
	__tablename__ = 'task'
	id = db.Column(db.Integer, primary_key=True)
	is_complete = db.Column(db.Integer)
	is_sent = db.Column(db.Integer)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
	organization = relationship("Organization", uselist=False)
	user = relationship("User", uselist=False, back_populates="tasks")

	def __init__(self, org, user):
		self.organization = org
		self.user = user

	def __repr__(self):
		return '<Task ID {}>'.format(self.id)

class Organization(db.Model):
	__tablename__ = 'organization'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120))
	admin_ou = db.Column(db.String(120))
	tasks = relationship("Task")
	admin_users = relationship(
		"User",
		secondary=admin_user_table,
		back_populates="admin_orgs"
	)

	def __init__(self, name):
		self.name = name.lower()

	def __repr__(self):
		return '<Organization {}>'.format(self.name)

	def __str__(self):
		return self.name

	def add_task(self, user):
		self.tasks.append(Task(self, user))


