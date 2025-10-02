import os
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import pandas as pd
from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required
from werkzeug.utils import secure_filename
from models import db, School, Employee, District,WorkWeek,Register,RegisterEntry,File,RegisterFile
from helpers import get_or_create, entry_statuses

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
    school=None
    week = None
    school_id = request.args.get("school_id")
    week_id = request.args.get("week_id")
    if school_id and week_id:
        school = School.query.filter_by(id=school_id).first()
        week = WorkWeek.query.filter_by(id=week_id).first()
        if (not school) or (not week):
            flash("School/Week not found","danger")
            return redirect(url_for("register.school_registers"))
    
    if request.method=="POST":
        if school_id and week_id:
            if school and week:
                notes = request.form.get("notes")
                notes = notes if notes else None
                register, _ = get_or_create(db.session,Register,defaults={"school_id":school.id,"week_id":week.id,"notes":notes},
                                         school_id=school.id,week_id=week.id)
                print(f"the type for register is {type(register)}")
                db.session.commit()

                school.employees.sort(key=lambda emp: emp.surname)
                for emp in school.employees:
                    for day_offset in range(5):
                        day_date = week.start_date + pd.Timedelta(days=day_offset)
                        day_name = day_date.strftime("%A")
                        status = request.form.get(f"status_{emp.id}_{day_name}")
                        if status:
                            print(f"Saving entry for {emp.firstname} {emp.surname} on {day_name} ({day_date}): {status}")
                            get_or_create(db.session,RegisterEntry,defaults={"employee_id":emp.id,"register_id":register.id, "day_of_week":day_name,"date":day_date,"status":status},
                                  employee_id=emp.id,register_id=register.id,day_of_week=day_name)
                db.session.commit()
                flash("Register saved successfully!","success") 
                file = request.files["file"]
                if file and file.filename:
                    filename = secure_filename(f"{school.emis}-{school.name}_{week.label}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.',1)[1].lower()}")
                    upload_folder = 'uploads/registers'
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)

                    new_file = File(filename=filename, file_path=file_path, upload_date=datetime.now())
                    db.session.add(new_file)
                    db.session.commit()

                    register.file_id = new_file.id
                    db.session.commit()

                    register_file = RegisterFile(register_id=register.id, file_id=new_file.id)
                    db.session.add(register_file)
                    db.session.commit()

                return redirect(url_for("register.school_registers",school_id=school.id))
    return render_template("create_school_register.html",
                       schools=School.query.all(),
                       weeks=WorkWeek.query.all(),
                       school=school,
                       week=week, 
                       statuses=entry_statuses, default_status_index=0)


@register_bp.route("/edit",methods=["GET","POST"])
@login_required
def edit_school_register():
    register_id = request.args.get("register_id")
    register = None
    if register_id:
        register = Register.query.filter_by(id=register_id).first()
        if not register:
            flash("Register not found","danger")
            return redirect(url_for("register.school_registers"))
    else:
        flash("Register ID is required","danger")
        return redirect(url_for("register.school_registers"))

    if request.method=="POST":
        if register:
            notes = request.form.get("notes")
            register.notes = notes if notes else None
            db.session.commit()

            school = register.school
            week = register.work_week
            school.employees.sort(key=lambda emp: emp.surname)
            for emp in school.employees:
                for day_offset in range(5):
                    day_date = week.start_date + pd.Timedelta(days=day_offset)
                    day_name = day_date.strftime("%A")
                    status = request.form.get(f"status_{emp.id}_{day_name}")
                    if status:
                        print(f"Updating entry for {emp.firstname} {emp.surname} on {day_name} ({day_date}): {status}")
                        entry, created = get_or_create(db.session,RegisterEntry,defaults={"employee_id":emp.id,"register_id":register.id, "day_of_week":day_name,"date":day_date,"status":status},
                              employee_id=emp.id,register_id=register.id,day_of_week=day_name)
                        if not created:
                            entry.status = status
            db.session.commit()
            flash("Register updated successfully!","success") 

            file = request.files["file"]
            if file and file.filename:
                print(f"File found: {file.filename}")
                filename = secure_filename(f"{school.emis}_{week.label}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.',1)[1].lower()}")
                upload_folder = 'uploads\\registers'
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                print(f"File saved to {file_path}")

                File_record = File(
                    filename=filename,
                    file_path=file_path,
                    description=f"{school.name} register for {week.label}",
                    file_type="register_file")
                db.session.add(File_record)
                db.session.commit()

                
                print(f"New file record created with file_id: {File_record.id}")

                register.file_id = File_record.id
                db.session.commit()

                register_file = RegisterFile(register_id=register.id, file_id=File_record.id)
                db.session.add(register_file)
                db.session.commit()
            else:
                print("No file found or uploaded.")

            return redirect(url_for("register.school_registers",school_id=school.id))
    entries = RegisterEntry.query.filter_by(register_id=register.id).all() if register else []
    entries_dict = {(entry.employee_id, entry.day_of_week): entry for entry in entries}
    return render_template("edit_school_register.html",
                       schools=School.query.all(),
                       weeks=WorkWeek.query.all(),
                       week=register.work_week if register else None,
                       school=register.school if register else None,
                       register=register,
                       statuses=entry_statuses, 
                       entries_dict=entries_dict)


@register_bp.route("/view/<int:register_id>")
@login_required
def view_register(register_id):
    register = Register.query.filter_by(id=register_id).first()
    if not register:
        flash("Register not found","danger")
        return redirect(url_for("register.school_registers"))
    entries = RegisterEntry.query.filter_by(register_id=register.id).all()
    entries_by_employee = {}
    school = register.school
    for entry in entries:
        if entry.employee_id not in entries_by_employee:
            entries_by_employee[entry.employee_id] = []
        entries_by_employee[entry.employee_id].append(entry)
    
    for emp_entries in entries_by_employee.values():
        emp_entries.sort(key=lambda e: e.date)
    
    return render_template("view_register.html",register=register,entries_by_employee=entries_by_employee, statuses=entry_statuses,school=school)


@register_bp.route("/summary/<string:emis>")
@login_required
def school_register_summary(emis):
    school = School.query.filter_by(emis=emis).first()
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    print(f"Start date: {start_date}, End date: {end_date}")

    today = date.today()

    # Previous month's 21st
    prev_month_21 = (today.replace(day=1) - relativedelta(days=1)).replace(day=21)

    # Current month's 20th
    current_month_20 = today.replace(day=20)

    if not school:
        flash("School not found","danger")
        return redirect(url_for("school.index"))
    
    start_date = datetime.strptime(start_date,"%Y-%m-%d").date() if start_date else prev_month_21
    end_date = datetime.strptime(end_date,"%Y-%m-%d").date() if end_date else current_month_20 
    employe_entries = {}
    for emp in school.employees:
        con_end = min(end_date, (emp.end_date if emp.end_date else date.today()))
        con_start = max(start_date, emp.start_date)
        employe_entries[emp.id] = [entry for entry in emp.entries if con_start <= entry.date <= con_end]
    
    summary = {}
    registers = Register.query.filter_by(school_id=school.id).all()
    registers = [reg for reg in registers if start_date <= reg.work_week.end_date and reg.work_week.start_date <= end_date]
    notes = {reg.work_week.label: reg.notes for reg in registers if reg.notes}
    for status in entry_statuses:
        for emp_id, entries in employe_entries.items():

            count = len([entry for entry in entries if entry.status == status])
            if emp_id not in summary:
                summary[emp_id] = {}
            summary[emp_id][status] = count

    return render_template("school_register_summary.html",
                           school=school,
                           summary=summary,
                           start_date=start_date,
                           end_date=end_date,
                           employees=school.employees, 
                           statuses=entry_statuses,
                           notes=notes)

@register_bp.route("/report")
@login_required
def register_report():
    start_week = request.args.get("start_week")
    end_week = request.args.get("end_week")

    start_week = int(start_week) if start_week and start_week.isdigit() else 1
    end_week = int(end_week) if end_week and end_week.isdigit() else (date.today() - date(2025,6,2)).days//7

    schools = School.query.all()
    report_data =[]
    for school in schools:
        row = {"school":school}
        row["circuit"] = school.circuit if school.circuit else "N/A"
        submitted_registers = Register.query.filter_by(school_id=school.id).all()
        submitted_registers = [reg for reg in submitted_registers if start_week <= reg.week_id <= end_week]
        row["submitted_registers_count"] = len(submitted_registers)
        weeks = [week for week in WorkWeek.query.all() if start_week <= week.id <= end_week]
        row["needed_registers_count"] = len(weeks)-len(submitted_registers)
        not_submitted = []
        for week in weeks:
            if not any(reg.week_id == week.id for reg in submitted_registers):
                not_submitted.append(week)
        row["not_submitted"] = ", ".join(not_submitted[i].end_date.strftime("%d-%b") for i in range(len(not_submitted)))
        report_data.append(row)
    headers = ["EMIS","School","Circuit","Submitted Registers","Needed Registers","Not Submitted Weeks"]
    return render_template("register_report.html",report_data=report_data,
                           start_week=start_week,
                           headers=headers,
                           end_week=end_week,
                           weeks=WorkWeek.query.all())




