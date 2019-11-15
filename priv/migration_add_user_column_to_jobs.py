from sqlalchemy import Table, Column, Integer, Float, String, MetaData, DateTime
from sqlalchemy	import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os

from werkzeug.security import generate_password_hash, check_password_hash

import bcrypt

engine = create_engine(os.environ["DATABASE_URL"], echo=True)
engine.execute('alter table jobs add column creator_id Integer')
