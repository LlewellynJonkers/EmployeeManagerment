import os
from datetime import datetime
import pandas as pd
from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required
from werkzeug.utils import secure_filename
from models import db, School, Employee, District,WorkWeek,Register,RegisterEntry
from helpers import get_or_create

register_bp = Blueprint("register",__name__,url_prefix="/registers")

@register_bp.route("/school")
@login_required
def school_registers():
    school_id = request.args.get("school_id")
    if school_id:
        school = School.query.filter_by(id=school_id).first()
        return render_template("single_schools_registers.html",school = school,workweeks=WorkWeek.query.all())
    else:
        return redirect(url_for('school.index'))

@register_bp.route("/add",methods=["GET","POST"])
@login_required
def add_school_register():
    if request.method=="POST":
        school_id = request.form.get("school_id")
        week_id = request.form.get("week_id")
        if school_id and week_id:
            school = School.query.filter_by(id=school_id).first()
            week = WorkWeek.query.filter_by(id=week_id).first()
            if school and week:
                register = get_or_create(db.session,Register,defaults={"school_id":school.id,"week_id":week.id},
                                         school_id=school.id,week_id=week.id)
                db.session.commit()

                school.employees.sort(key=lambda emp: emp.surname)
                for emp in school.employees:
                    for day_offset in range(5):
                        day_date = week.start_date + pd.Timedelta(days=day_offset)
                        day_name = day_date.strftime("%A")
                        status = request.form.get(f"status_{emp.id}_{day_name}")
                        if status:
                            get_or_create(db.session,RegisterEntry,defaults={"employee_id":emp.id,"register_id":register.id, "day_of_week":day_name,"date":day_date,"status":status},
                                  employee_id=emp.id,register_id=register.id,day_of_week=day_name)
                db.session.commit()
                flash("Register saved successfully!","success")

                return redirect(url_for("register.school_registers",school_id=school.id))