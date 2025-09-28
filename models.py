from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

CREATED_SEED = False

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    @staticmethod
    def create_admin():
        user = User.query.filter_by(role="admin").first()
        if user:
            return user
        password = generate_password_hash("adminpass")
        user = User(username="admin",role="admin",password_hash = password)
        db.session.add(user)
        db.session.commit()
        return user

    def set_role(self, role):
        self.role = role

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Province(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    districts = db.relationship('District', back_populates='province')

    @staticmethod
    def create_northern_cape():
        prov_test = Province.query.filter_by(name="BEEI- Northern Cape").first()
        if prov_test:
            return prov_test
        province = Province(name="BEEI- Northern Cape")
        db.session.add(province)
        db.session.commit()
        return province


class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    province_id = db.Column(db.Integer, db.ForeignKey('province.id'), nullable=False)

    province = db.relationship('Province', back_populates='districts')
    schools = db.relationship('School', back_populates='district')

    @staticmethod
    def create_pixley_ka_seme():
        prov = Province.query.filter_by(name="BEEI- Northern Cape").first()
        if prov:
            dist_test = District.query.filter_by(name="Pixley Ka Seme (Pxl): Phase 5").first()
            if dist_test:
                return dist_test
            district = District(name="Pixley Ka Seme (Pxl): Phase 5", province_id=prov.id)
            db.session.add(district)
            db.session.commit()
            return district


class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emis = db.Column(db.String(9), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    payment_source = db.Column(db.String(3), nullable=False)
    circuit = db.Column(db.Integer, nullable=False)
    quintile = db.Column(db.Integer, nullable=False)
    allocation = db.Column(db.Integer, nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'), nullable=False)

    district = db.relationship("District", back_populates="schools")
    employees = db.relationship('Employee', back_populates='school')
    registers = db.relationship("Register", back_populates="school")

    def get_register(self,workweek):
        return next(
            filter(
                lambda register: register.week_id==workweek.id,
                self.registers),
                None)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_number = db.Column(db.String(13), unique=True, nullable=False)
    firstname = db.Column(db.String(150), nullable=False)
    surname = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    cellnumber = db.Column(db.String(10), nullable=True)
    contract_status = db.Column(db.String(15), nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    annual_leave_count = db.Column(db.Integer, default=0)
    sick_leave_count = db.Column(db.Integer, default=0)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)

    school = db.relationship("School", back_populates="employees")
    entries = db.relationship(
        "RegisterEntry",
        back_populates="employee",
        cascade="all, delete-orphan"
    )


class Register(db.Model):
    __tablename__ = "registers"

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    week_id = db.Column(db.Integer, db.ForeignKey("work_weeks.id"), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey("file.id"), nullable = True)





    notes = db.Column(db.String(255),nullable=True)

    entries = db.relationship(
        "RegisterEntry",
        back_populates="register",
        cascade="all, delete-orphan"
    )
    school = db.relationship("School", back_populates="registers")
    work_week = db.relationship("WorkWeek", back_populates="registers")

    __table_args__ = (
        db.UniqueConstraint("school_id", "week_id", name="uq_school_week"),
    )
    
    def get_status_count(self,status):
        return len([entry for entry in self.entries if entry.status == status])
    
    def get_file(self):
        if self.file_id:
            return File.query.filter_by(id=self.file_id).first()
        return None


class RegisterEntry(db.Model):
    __tablename__ = "register_entries"

    id = db.Column(db.Integer, primary_key=True)
    register_id = db.Column(db.Integer, db.ForeignKey("registers.id"), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)  
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)       

    register = db.relationship("Register", back_populates="entries")
    employee = db.relationship("Employee", back_populates="entries")


    __table_args__ = (
        db.UniqueConstraint("register_id", "day_of_week", "employee_id", name="uq_register_day"),
    )


class WorkWeek(db.Model):
    __tablename__ = "work_weeks"

    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    label = db.Column(db.String(20), unique=True, nullable=False)

    registers = db.relationship("Register", back_populates="work_week")


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    description = db.Column(db.String(255), nullable=True)
    file_type = db.Column(db.String(50), nullable=True, default="school_register")
    file_path = db.Column(db.String(500), nullable=False)

class BulkUploadLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    upload_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(500), nullable=True)

class BulkUploadError(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    log_id = db.Column(db.Integer, db.ForeignKey('bulk_upload_log.id'), nullable=False)
    row_number = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(500), nullable=False)

    log = db.relationship('BulkUploadLog', backref=db.backref('errors', lazy=True))

class RegisterFile(db.Model):
    __tablename__ = "register_file"

    register_id = db.Column(db.Integer, db.ForeignKey("registers.id"), primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey("file.id"), primary_key=True)

    register = db.relationship("Register")
    file = db.relationship("File")