import os
from datetime import datetime
import pandas as pd
from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import  login_required
from werkzeug.utils import secure_filename
from models import db, School, Employee, District
from helpers import get_or_create

route_bp = Blueprint("upload", __name__, url_prefix="/upload")

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"xlsx", "xls"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@route_bp.route("/upload_schools", methods=["GET", "POST"])
@login_required
def upload_schools():
    if request.method == "POST":
        file = request.files["file"]

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(filepath)

            # Read Excel file
            df = pd.read_excel(filepath)

            # Expected columns: emis, name, payment_source, circuit, quintile, allocation, district_id
            for _, row in df.iterrows():
                try:
                    if not( row["District"] == "Pixley ka Seme" or row["District"] == "Pixley Ka Seme (Pxl): Phase 5"):
                        continue
                    emis = str(row["EMIS"]).strip()
                    name = str(row["School Name"]).strip()
                    payment_source = str(row["Payment Method"])
                    quintile = int(row["Quintile"])
                    circuit = int(row["Circuit"])
                    allocation = int(row["Grand Total"])
                    district_id = 0
                    if(row["District"] == "Pixley ka Seme"):
                        district_name = "Pixley Ka Seme (Pxl): Phase 5"
                        dst = District.query.filter_by(name=district_name).first()
                        district_id = dst.id
                    else:
                        dst = District.query.filter_by(name=row["District"]).first()
                        if dst:
                            district_id=dst.id

                    
                    get_or_create(db.session,School,defaults={
                        "name":name,
                        "payment_source":payment_source,
                        "circuit":circuit,
                        "quintile":quintile,
                        "allocation":allocation,
                        "district_id":district_id
                    },emis=emis)
                except Exception as e:
                    print(f"Error processing row: {row}. Error: {e}")
                    flash(f"Error processing row: {row}. Error: {e}", "danger")


            db.session.commit()
            flash("Schools uploaded successfully!", "success")
            return redirect(url_for("school.index"))

    return render_template("schools_bulk_insert.html")

@route_bp.route("/upload_SC03", methods=["GET", "POST"])
@login_required
def upload_employees():
    if request.method == "POST":
        file = request.files["file"]

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(filepath)

            # Read Excel file
            df = pd.read_excel(filepath,skiprows=5,dtype={"ID number":str})

            # Expected columns: emis, name, payment_source, circuit, quintile, allocation, district_id
            errors = []
            for _, row in df.iterrows():
                try:
                    schoolname = str(row["School"]).strip()
                    emis = schoolname[:schoolname.index(" ")].strip()
                    school = School.query.filter_by(emis=emis).first()
                    if school:
                        school_id = school.id
                        id_number = str(row["ID number"])
                        firstname = str(row["Firstname"])
                        surname = str(row["Surname"])
                        start_date = row["Contract start"].date()
                        end_date = row["Contract end date"].date() if not pd.isna(row["Contract end date"]) else None
                        #start_date = datetime.strptime(row["Contract start"],"%Y/%m/%d").date()
                        contract_status= str(row["Contract status"])
                        
                        get_or_create(db.session,Employee,defaults= {
                            "school_id":school_id,
                            "firstname": firstname,
                            "surname":surname,
                            "start_date":start_date,
                            "contract_status":contract_status,
                            "end_date":end_date
                        },id_number=id_number)
                        db.session.commit()
                except Exception as e:
                    errors.append(f"Error processing row: {row}. Error: {e}")
                    
            db.session.commit()
            flash("Schools uploaded successfully!", "success")
            if errors:
                for error in errors:
                    flash(error, "danger")
            return redirect(url_for("employee.index"))
    return render_template("employees_bulk_insert.html")

@route_bp.route("/upload_SC04", methods=["GET", "POST"])
@login_required
def update_employee_data():
    if request.method == "POST":
        file = request.files["file"]

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(filepath)

            # Read Excel file
            df = pd.read_excel(filepath,skiprows=5,dtype={"ID number":str})

            # Expected columns: emis, name, payment_source, circuit, quintile, allocation, district_id
            for _, row in df.iterrows():
                if str(row["District"]) == "Pixley Ka Seme (Pxl): Phase 5":
                    schoolname = str(row["School"]).strip()
                    emis = schoolname[:schoolname.index(" ")].strip()
                    school_id = School.query.filter_by(emis=emis).first().id
                    id_number = str(row["ID number"])
                    firstname = str(row["Firstname"])
                    surname = str(row["Surname"])
                    start_date = row["Contract start"].date()
                    end_date = row["Contract end date"].date() if not pd.isna(row["Contract end date"]) else None
                    #start_date = datetime.strptime(row["Contract start"],"%Y/%m/%d").date()
                    contract_status= str(row["Contract status"])
                    
                    get_or_create(db.session,Employee,defaults= {
                        "school_id":school_id,
                        "firstname": firstname,
                        "surname":surname,
                        "start_date":start_date,
                        "contract_status":contract_status,
                        "end_date":end_date
                    },id_number=id_number)
                    db.session.commit()
                    
            db.session.commit()
            flash("SC04 report successfully uploaded!", "success")
            return redirect(url_for("employee.index"))
    return render_template("employees_bulk_insert.html")