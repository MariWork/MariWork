
from sqlalchemy import Table, Column, Integer, Float, String, MetaData, DateTime
from sqlalchemy	import create_engine
from sqlalchemy.types import ARRAY
from sqlalchemy.ext.declarative import declarative_base
import os

from werkzeug.security import generate_password_hash, check_password_hash

import bcrypt

engine = create_engine(os.environ["DATABASE_URL"], echo=True)

meta = MetaData()
Base = declarative_base()

class Job(Base):
	__tablename__ = "jobs"

	id = Column(Integer, primary_key=True)
	job_name = Column(String)
	company_name = Column(String)
	salary = Column(Float)
	description = Column(String)
	website_link = Column(String)
	creator_id = Column(Integer)
	categories = Column(ARRAY(String))
	tags = Column(ARRAY(String))

	def __repr__(self):
		return "<Job(job_name='%s', company_name='%s', salary='%s', description='%s', website_link='%s')>" \
		% (self.job_name, self.company_name, self.salary, self.description, self.website_link)

class User(Base):

	__tablename__ = "user"

	id = Column(Integer, primary_key=True)
	first_name = Column(String(128))
	last_name = Column(String(128))
	email = Column(String(256))
	password_hash = Column(String(128))
	description = Column(String)
	link = Column(String)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(password, self.password_hash)


class Student(Base):
	__tablename__ = "students"
	id = Column(Integer, primary_key=True)
	first_name = Column(String(128))
	last_name = Column(String(128))
	email = Column(String(256))
	password_hash = Column(String(2048))
	description = Column(String)
	link = Column(String)
	school_name	= Column(String)

	def set_password(self, password):
		self.password_hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode()

	def __repr__(self):
		return "<Student(first_name='%s', last_name='%s', email='%s', \
		school_name='%s', description='%s', link='%s'>" \
		% (self.first_name, self.last_name, self.email, self.school_name ,self.description, self.link)

class Employer(Base):
	__tablename__ = "employers"
	id = Column(Integer, primary_key=True)
	first_name = Column(String(128))
	last_name = Column(String(128))
	email = Column(String(256))
	password_hash = Column(String(2048))
	description = Column(String)
	link = Column(String)
	company_name = Column(String)

	def set_password(self, password):
		temp_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
		print(temp_hash)
		print(type(temp_hash))
		self.password_hash = temp_hash

	def __repr__(self):
		return "<Student(first_name='%s', last_name='%s', email='%s', \
		company_name='%s', description='%s', link='%s'>" \
		% (self.first_name, self.last_name, self.email, self.company_name ,self.description, self.link)


if __name__ == "__main__":
	Base.metadata.create_all(engine)