from sqlalchemy import Table, Column, Integer, Float, String, MetaData, DateTime
from sqlalchemy	import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def get_id_from_email(session, relation, email):
	return session.query(relation).filter_by(email=email).first().id

def check_if_https_in_url(original_url):
	if "https://" in original_url:
		return original_url
	else:
		return "https://"+original_url

def return_value_if_none(variable_value, return_value):
	print("return_value_if_none	!")
	print(variable_value)
	print(type(variable_value))
	if variable_value is None or variable_value	== '':
		return return_value	
	else:
		variable_value