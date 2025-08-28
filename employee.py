from flask import flash, Blueprint, render_template, request
import datetime
from flask_login import login_required
from models import db, Province, District, School, Employee

employee_bp = Blueprint("employee",  __name__, url_prefix="/employees")

@employee_bp.route("/")
@login_required
def index():
    records = Employee.query.all()
    return render_template("employees.html", employees=records)