from sqlalchemy import Table, Column, Integer, Float, String, MetaData, DateTime
from sqlalchemy	import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def get_id_from_email(session, relation, email):
	return session.query(relation).filter_by(email=email).first().id