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
        school = School.query.filter_by(id=school_id)
        return render_template("single_schools_registers.html",school = school,workweeks=WorkWeek.query.all())
    else:
        return redirect(url_for('school.index'))

@register_bp.route("/add")
@login_required
def add_school_register():
    pass