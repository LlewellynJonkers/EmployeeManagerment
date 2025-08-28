import os
import pandas as pd
from flask import Blueprint, request, redirect, url_for, flash, render_template
from werkzeug.utils import secure_filename
from models import db, School, Employee, District

route_bp = Blueprint("upload", __name__, url_prefix="/upload")

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"xlsx", "xls"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@route_bp.route("/upload_schools", methods=["GET", "POST"])
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

                school = School(
                    emis=emis,
                    name=name,
                    payment_source=payment_source,
                    circuit=circuit,
                    quintile=quintile,
                    allocation=allocation,
                    district_id=district_id
                )
                db.session.add(school)

            db.session.commit()
            flash("Schools uploaded successfully!", "success")
            return redirect(url_for("school.index"))

    return render_template("schools_bulk_insert.html")
