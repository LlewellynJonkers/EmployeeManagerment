from flask import flash, Blueprint, render_template, request
import datetime
from flask_login import login_required
from models import db, Province, District, School, Employee

employee_bp = Blueprint("employee",  __name__, url_prefix="/employees")

@employee_bp.route("/")
@login_required
def index():
    page = request.args.get("page")
    if page is None:
        page = 1
    page = int(page)
    pagination = db.paginate(Employee.query,page=page,per_page=25)
    return render_template("employees.html", pagination = pagination)