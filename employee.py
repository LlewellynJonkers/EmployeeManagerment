from flask import flash, Blueprint, render_template, request, redirect, url_for
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from flask_login import login_required
from helpers import get_or_create, entry_statuses
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

@employee_bp.route("/summary/<int:employee_id>")
@login_required
def summary(employee_id):
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    print(f"Start date: {start_date}, End date: {end_date}")

    today = date.today()

    # Previous month's 21st
    prev_month_21 = (today.replace(day=1) - relativedelta(days=1)).replace(day=21)

    # Current month's 20th
    current_month_20 = today.replace(day=20)

    employee = Employee.query.get(employee_id)

    if not employee:
        flash("Employee not found","danger")
        return redirect(url_for("employee.index"))
    
    start_date = datetime.strptime(start_date,"%Y-%m-%d").date() if start_date else prev_month_21
    end_date = datetime.strptime(end_date,"%Y-%m-%d").date() if end_date else current_month_20 

    entries = [entry for entry in employee.entries if start_date <= entry.date <= end_date]
    summary = {}

    for status in entry_statuses:
        count = len([entry for entry in entries if entry.status == status])
        summary[status] = count


    return render_template("employee_summary.html", employee=employee,summary=summary,start_date=start_date,end_date=end_date)