from flask import flash, Blueprint, render_template, request, redirect, url_for
import datetime
from flask_login import login_required
from models import db, Province, District, School, Employee,RegisterEntry, Register
from helpers import get_or_create, entry_statuses



school_bp = Blueprint("school",  __name__, url_prefix="/schools")

@school_bp.route("/")
@login_required
def index():
    records = School.query.all()
    return render_template("schools.html", schools=records)

@school_bp.route('/edit')
@login_required
def edit():
    id = request.args.get("id")
    if id:
        pass
    return redirect(url_for("school.index"))


@school_bp.route('/<string:emis>/details/')
@login_required
def details(emis):
    school = School.query.filter_by(emis=emis).first()
    if school:
        attendance_summury = {}
        for status in entry_statuses:
            count = db.session.execute(
                db.select(db.func.count()).select_from(School)
                .join(Employee)
                .join(Employee.entries)
                .where(School.id == school.id)
                .where(RegisterEntry.status == status)
            ).scalar_one()
            attendance_summury[status] = count
        return render_template("school_details.html", school=school, attendance_summary=attendance_summury)
    else:
        redirect(url_for("school.index"))

#@school_bp.route('/<string:emis>/summary/')
