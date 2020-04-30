import os
import json

from priv.create_tables import Job, Employer
from src.database_functions import check_if_https_in_url, get_id_from_email, return_value_if_none

import bcrypt

from flask import Flask, render_template, request
import flask
import flask_login 

from werkzeug.security import generate_password_hash, check_password_hash

from cryptography.fernet import Fernet

from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker


with open("static/components/html_strings.json", 'r') as jsonfile:
	html_components_dict = json.load(jsonfile)

engine = create_engine(os.environ["DATABASE_URL"], echo = True)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

users = dict()
for employer in session.query(Employer):
	users[employer.email] = {"password_hash": employer.password_hash}


class User(flask_login.UserMixin):
	
	def __init__(self):
		self.is_authenticated_local = False

	def set_is_authenticated(self, value):
		self.is_authenticated_local = value

@login_manager.user_loader
def user_loader(email):
	if email not in users:
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):

	email = request.form.get("email")
	if email not in users:
		return

	user = User()
	user.id = email

	password = request.form["password"]

	if bcrypt.checkpw(password.encode(), \
			session.query(Employer).filter(func.lower(Employer.email)==func.lower(email)).first().password_hash.encode()):
		user.set_is_authenticated(True)

	else:
		user.set_is_authenticated(False)

	return user

@app.route('/')
def home():
	login_dict_key = "login"

	if flask_login.current_user.is_authenticated:
		login_dict_key = "logout"

	return render_template("home.html", login_placeholder=html_components_dict[login_dict_key])


@app.route('/view_jobs')
def view_jobs():
	login_dict_key = "login"

	if flask_login.current_user.is_authenticated:
		login_dict_key = "logout"
	all_jobs = []
	all_volunteering = []

	for job in session.query(Job).order_by(Job.tags.asc()):
		print(job)
		job_button = "<a target=\"_blank\" href=\""+job.website_link+"\" class=\"btn btn-success\">View</a>"
		job_name = job.job_name	
		if job.tags is not None:
			for tag in job.tags:
				job_name += f' <span class="badge badge-warning">{tag}</span>'
		temp_list = [job_name, job.company_name, job.description, job_button]
		if job.categories is not None:
			if "paid-employment" in job.categories: 
				all_jobs.append(temp_list)
		if job.categories is None or "volunteering" in job.categories:
			all_volunteering.append(temp_list)
			print("volunteer!")

	return render_template("jobs_list.html", list_of_all_jobs=str(all_jobs), list_of_all_volunteering=str(all_volunteering), login_placeholder=html_components_dict[login_dict_key])

@app.route("/protected")
@flask_login.login_required
def protected():
	return "Logged in as " + flask_login.current_user.id

@app.route('/employer_login', methods=["GET", "POST"])
def employer_login():
	login_dict_key = "login"

	if flask_login.current_user.is_authenticated:
		login_dict_key = "logout"

	if request.method == "POST":

		email = request.form["email"]
		password = request.form["password"]

		print(email)
		print(password)

		list_of_results = []

		if bcrypt.checkpw(password.encode(), \
			session.query(Employer).filter(func.lower(Employer.email)==func.lower(email)).first().password_hash.encode()):

			user = User()
			user.id = email
			flask_login.login_user(user)

			return flask.redirect(flask.url_for("view_created_jobs"))

		return render_template("login_employer.html", login_placeholder=html_components_dict[login_dict_key])

	return render_template("login_employer.html", login_placeholder=html_components_dict[login_dict_key])

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return flask.redirect(flask.url_for("home"))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return flask.redirect(flask.url_for("employer_login"))

@app.route('/view_created_jobs')
@flask_login.login_required
def view_created_jobs():
	creator_id = get_id_from_email(session, Employer, flask_login.current_user.id)
	creator_jobs = list()
	for job in session.query(Job).filter_by(creator_id=creator_id).all():
		job_name = job.job_name
		company_name = job.company_name
		modify_link = "/edit_job?job_id="+str(job.id)
		delete_link = "/delete_job?job_id="+str(job.id)
		creator_jobs.append([job_name, company_name, modify_link, delete_link])

	return render_template("view_created_jobs.html", list_of_all_jobs=creator_jobs)

@app.route("/edit_job", methods=["GET", "POST", "DELETE"])
@flask_login.login_required
def edit_job():
	if request.method == "POST":
		job_id = int(request.form["job_id"],0)

		job = session.query(Job).filter_by(id=job_id).first()
		job.job_name = request.form["job_name"]
		job.company_name = request.form["company_name"]
		print("salary: "+str(request.form["salary"]))
		salary = float(request.form["salary"])
		job.description = request.form["description"]
		job.website_link = request.form["website_link"]

		session.commit()

		return flask.redirect(flask.url_for("view_created_jobs"))

	job_id = request.args.get("job_id")
	job = session.query(Job).filter_by(id=job_id).first()

	job_name = job.job_name
	company_name = job.company_name
	salary = job.salary
	description = job.description
	website_link = job.website_link

	print("job+id "+str(job_id))

	return render_template("edit_job.html", 
		job_id=job_id,
		job_name=job_name,
		company_name=company_name,
		salary=salary,
		description=description,
		website_link=website_link)

@app.route("/delete_job", methods=["GET", "POST"])
@flask_login.login_required
def delete_job():
	job_id = int(request.args.get("job_id"))
	job = session.query(Job).filter_by(id=job_id).first()
	session.delete(job)
	session.commit()
	return flask.redirect(flask.url_for("view_created_jobs"))

@app.route('/create_employer', methods=["GET", "POST"])
def create_employer():

	if request.method == "POST":

		first_name = request.form["first_name"]
		last_name = request.form["last_name"]
		email = request.form["email"]
		password = request.form["password"]
		description = request.form["description"]
		link = check_if_https_in_url(request.form["link"])
		company_name = request.form["company_name"]

		print(password)

		new_employer = Employer(first_name=first_name, 
			last_name=last_name, 
			email=email, 
			description=description, 
			link=link, 
			company_name=company_name)
		new_employer.set_password(password)
		session.add(new_employer)
		session.commit()

		return flask.redirect(flask.url_for("view_created_jobs"))

	return render_template("sign_up_employer.html")

@app.route('/create_job', methods=["GET", "POST"])
@flask_login.login_required
def create_job():

	if request.method=="POST":

		job_name = request.form["job_name"]
		company_name = request.form["company_name"]
		salary = float(request.form["salary"])
		description = request.form["description"]
		website_link = check_if_https_in_url(request.form["website_link"])
		creator_id = get_id_from_email(session, Employer, flask_login.current_user.id)

		new_job = Job(job_name=job_name, 
			company_name=company_name, 
			salary=salary, 
			description=description, 
			website_link=website_link, 
			creator_id=creator_id)

		session.add(new_job)
		session.commit()

		return flask.redirect(flask.url_for("view_created_jobs"))

	return render_template("create_job.html")

@app.route("/contact")
def contact():
	login_dict_key = "login"

	if flask_login.current_user.is_authenticated:
		login_dict_key = "logout"

	return render_template("contact.html", login_placeholder=html_components_dict[login_dict_key])

if __name__ == '__main__':
	print("Employers")
	for employer in session.query(Employer):
			print(employer.first_name, employer.email, employer.password_hash)
	employer = session.query(Employer).filter_by(email="laurencel2001@gmail.com").first()
	employer.set_password("password")
	session.add(employer)
	session.commit()
	app.run(debug=True)
