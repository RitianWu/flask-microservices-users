# project/api/models.py


from project import db


class User(db.Model):
	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	username = db.Column(db.String(128), nullable=False)
	email = db.Column(db.String(128), nullable=False)
	active = db.Column(db.Boolean(), default=False, nullable=False)
	create_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
	update_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(),
							onupdate=db.func.current_timestamp(), index=True)

	def __init__(self, username, email):
		self.username = username
		self.email = email
