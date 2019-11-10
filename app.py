import os

from priv.create_tables import Job, Employer

import bcrypt

from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash

from cryptography.fernet import Fernet

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


app = Flask(__name__)

engine = create_engine(os.environ["DATABASE_URL"], echo = True)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

# conn = engine.connect()

@app.route('/')
def home():

	all_jobs = []

	for job in session.query(Job):
		print(job)
		temp_list = [job.job_name, job.company_name, job.website_link]
		all_jobs.append(temp_list)

	return render_template("jobs_list.html", list_of_all_jobs=str(all_jobs))

@app.route('/employer_login', methods=["GET", "POST"])
def employer_login():

	if request.method == "POST":

		email = request.form["email"]
		password = request.form["password"]

		list_of_results = []

		password_hash = ''

		for employer in session.query(Employer).filter_by(email=email).all():
			
			password_hash = employer.password_hash
			print(employer.email)
			print(employer.first_name)
			print(password)
			print(password_hash)
			print(bcrypt.checkpw(password.encode(), password_hash.encode()))
		return "Done"

	return render_template("login_employer.html")

@app.route('/create_employer', methods=["GET", "POST"])
def create_employer():

	if request.method == "POST":

		first_name = request.form["first_name"]
		last_name = request.form["last_name"]
		email = request.form["email"]
		password = request.form["password"]
		description = request.form["description"]
		link = request.form["link"]
		company_name = request.form["company_name"]

		print(password)

		new_employer = Employer(first_name=first_name, last_name=last_name, email=email, description=description, link=link, company_name=company_name)
		new_employer.set_password(password)
		session.add(new_employer)
		session.commit()

		return "Succes! created employer"

	return render_template("sign_up_employer.html")


@app.route('/create_job', methods=["GET", "POST"])
def create_job():

	if request.method=="POST":

		job_name = request.form["job_name"]
		company_name = request.form["company_name"]
		salary = request.form["salary"]
		description = request.form["description"]
		website_link = request.form["website_link"]


		new_job = Job(job_name=job_name, company_name=company_name, salary=salary, description=description, website_link=website_link)
		session.add(new_job)
		session.commit()

		return "Succes! created job"

	return render_template("create_job.html")


@app.route('/view_jobs')
def view_jobs():

	for job in session.query(Job):
		print(job.job_name)

if __name__ == '__main__':
	print("Employers")
	for employer in session.query(Employer):
			print(employer.first_name, employer.email, employer.password_hash)
	app.run(debug=True)
