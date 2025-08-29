from flask import flash, Blueprint, render_template, request, redirect, url_for
import datetime
from flask_login import login_required
from models import db, Province, District, School, Employee



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