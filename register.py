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
        records = Register.query.filter_by(school_id=school_id)
        
    else:
        return redirect(url_for('school.index'))