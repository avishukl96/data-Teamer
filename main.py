from flask import Flask, render_template, request, redirect, flash, url_for, send_file
from datetime import datetime
import os
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, UserMixin, LoginManager, login_required, login_user, logout_user
import boto3
import pandas as pd
from flask_bcrypt import Bcrypt
from io import BytesIO
from werkzeug.utils import secure_filename


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask('__name__')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dtUser.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class dtUser(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    mobile = db.Column(db.String(10), unique=True)
    org = db.Column(db.String(100))
    role = db.Column(db.Integer)
    password = db.Column(db.String(100))
    isActive = db.Column(db.Integer)

    def __init__(self, name, email, mobile, password, org, role, isActive):
        self.name = name
        self.email = email
        self.mobile = mobile
        self.role = role
        self.org = org
        self.role = role
        self.isActive = isActive
        self.password = password  


    def set_password(self, password):
     self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return True

    def get_id(self):
        return self.id


class dtSubUser(db.Model, UserMixin):
    __tablename__ = 'sub_user'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer)
    name = db.Column(db.String(100))
    emp_email = db.Column(db.String(100))
    emp_mobile = db.Column(db.String(10))
    emp_org = db.Column(db.String(100))
    emp_role = db.Column(db.Integer)
    emp_password = db.Column(db.String(100))
    isActive = db.Column(db.Integer)

    def __init__(self, parent_id, name, emp_email, emp_mobile, emp_password, emp_org, emp_role, isActive):
        self.name = name
        self.parent_id = parent_id
        self.emp_email = emp_email
        self.emp_mobile = emp_mobile
        self.emp_role = emp_role
        self.emp_org = emp_org
        self.emp_role = emp_role
        self.isActive = isActive
        self.emp_password = emp_password


    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return True

    def get_id(self):
        return self.id



class data_Access(db.Model):
    __tablename__ = 'dt_access'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    date = db.Column(db.String(100))
    email = db.Column(db.String(100))
    folder_name = db.Column(db.String(100))
    action = db.Column(db.String(100))


class CsvTab(db.Model):
    __tablename__ = 'csv_tab'
    id = db.Column(db.Integer, primary_key=True)
    uploaded_by = db.Column(db.Integer)
    updated_by = db.Column(db.Integer)
    updated_date = db.Column(db.DateTime)
    filename = db.Column(db.String(100))
    data = db.Column(db.LargeBinary)
    file_status = db.Column(db.String(20))


with app.app_context():
    db.create_all()



@login_manager.user_loader
def load_user(user_id):
    return db.session.get(dtUser, int(user_id))


@app.route('/', methods=['GET', 'POST'])
def index():
    users = db.session.query(dtUser).all()
    # print(users)
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        pwd = request.form.get('password')
        data = db.session.query(dtUser).filter_by(email=email).first()
        if data and bcrypt.check_password_hash(data.password, pwd):
            login_user(data, remember=False)
            return redirect('/AI')
        else:
            flash("Invalid Credentials.","error")
            return redirect('/')
    else:
        return redirect('/')


@app.route('/AI', methods=['GET', 'POST'])
def AI():
    data = db.session.query(dtUser).filter_by(id=current_user.id).first()
    # print(current_user.name)
    return render_template('AI.html', data=data)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    data = db.session.query(dtUser).filter_by(id=current_user.id).first()
    # print(current_user.name)
    return render_template('dashboard.html', data=data)


@app.route('/marketing', methods=['GET', 'POST'])
def marketing():
    data = db.session.query(dtUser).filter_by(id=current_user.id).first()
    # print(current_user.name)
    return render_template('marketing.html', data=data)


@app.route('/marketing/csv', methods=['GET', 'POST'])
def csv():
    data = db.session.query(dtUser).filter_by(id=current_user.id).first()
    file_data = db.session.query(CsvTab).filter_by(file_status="uploaded", uploaded_by=current_user.id).all()
    # print(current_user.name)
    return render_template('csv.html', data=data, file_data=file_data)


@login_required
@app.route('/access_log', methods=['POST'])
def log_access():
    if request.method == 'POST':
        data = request.get_json()
        folder_name = data['folder_name']
        user_id = current_user.id
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        email = current_user.email
        data = data_Access(user_id=user_id,date=date,email=email,folder_name=folder_name)
        db.session.add(data)
        db.session.commit()
        return 'success'


@login_required
@app.route('/access_data', methods=['GET'])
def getdata():
    data = db.session.query(data_Access).all()
    return render_template('analytics.html', data=data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        org = request.form.get('org')
        role = "Admin"
        password = request.form.get('password')
        password = bcrypt.generate_password_hash(password).decode('utf-8')
        isActive = 1
        user = dtUser(name=name, email=email, mobile=mobile, org=org, role=role, password=password, isActive=isActive)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    else:
        data = db.session.query(data_Access).all()
        return render_template('register-v2.html', data=data)




@login_required
@app.route('/employee', methods=['GET', 'POST'])
def employee():
    if request.method == 'POST':
        name = request.form.get('emp_name')
        email = request.form.get('emp_email')
        mobile = request.form.get('emp_mobile')
        org = current_user.org
        role = "user"
        password = bcrypt.generate_password_hash("Welcome@2024").decode('utf-8')
        isActive = 1
        sub_user = dtSubUser(parent_id=current_user.id, name=name, emp_email=email, emp_mobile=mobile, emp_org=org, emp_role=role, emp_password=password, isActive=isActive)
        db.session.add(sub_user)
        db.session.commit()
        return redirect('/employee')
    else:
        parent_id = current_user.id
        data = db.session.query(dtSubUser).filter_by(parent_id=parent_id, isActive=1).all()
        return render_template('/employee.html', data=data)


@app.route('/getEmp', methods=['POST'])
def get_emp():
    data = request.get_json()
    user_dict = {}
    if data['emp_id']:
        user_data = db.session.query(dtSubUser).filter_by(id=data['emp_id']).first()
        if user_data:
            user_dict['emp_id'] = user_data.id
            user_dict['emp_name'] = user_data.name
            user_dict['emp_email'] = user_data.emp_email
            user_dict['emp_mobile'] = user_data.emp_mobile

            return user_dict
        else:
            return "Error"


@app.route('/editEmp', methods=['POST'])
def edit_emp():
    if request.method == 'POST':
        data = db.session.query(dtSubUser).filter_by(id=request.form.get('emp_id')).first()
        if data:
            data.name = request.form.get('emp_name')
            data.emp_email = request.form.get('emp_email')
            data.emp_mobile = request.form.get('emp_mobile')
            db.session.commit()
            return redirect('/employee')
        else:
            return redirect('/employee')


@app.route('/deleteEmp/<id>')
def delete_emp(id):
    if id:
        user_data = db.session.query(dtSubUser).filter_by(id=id).first()
        if user_data:
            user_data.isActive = 0
            db.session.commit()
            return redirect('/employee')
        else:
            return redirect('/employee')


@app.route('/deleteCSV', methods=['POST'])
def delete_csv():
    if request.method == 'POST':
        data = request.get_json()
        id = data['id']
        if id:
            user_data = db.session.query(CsvTab).filter_by(id=id).first()
            if user_data:
                user_data.file_status = "Deleted"
                user_data.updated_date = datetime.now()
                user_data.updated_by = current_user.id
                # db.session.delete(user_data)
                db.session.commit()
                # start adding data into access table
                date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                email = current_user.email
                action = "deleted"
                data = data_Access(user_id=current_user.id, date=date, email=email, folder_name=data['filename'],action=action)
                db.session.add(data)
                db.session.commit()
                # end
                data ={"result":"File Deleted Successfully"}
                return data
    return redirect('/marketing/csv')

@app.route('/uploadCsv', methods=['POST'])
def uploadFile():
    if request.method == 'POST':
        file = request.files.get('file')
        date = datetime.now()
        file_status = "uploaded"
        upload = CsvTab(uploaded_by=current_user.id, updated_by=current_user.id,updated_date=date,filename=file.filename, data=file.read(), file_status=file_status)
        db.session.add(upload)
        db.session.commit()
        return redirect('/marketing/csv')

@app.route('/download/<id>')
def downloadFile(id):

    upload = CsvTab.query.filter_by(id=id).first()
    # start adding data into access table
    date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    email = current_user.email
    action = "downloaded"
    data = data_Access(user_id=current_user.id, date=date, email=email, folder_name=upload.filename, action=action)
    db.session.add(data)
    db.session.commit()
    # end
    return send_file(BytesIO(upload.data), download_name=upload.filename, as_attachment=True)


@app.route('/base', methods=['GET'])
def base():
    data = db.session.query(data_Access).all()
    return render_template('base.html', data=data)



@app.route('/reports', methods=['GET'])
def reports():
    data = db.session.query(data_Access).all()
    ac_data = db.session.query(data_Access).filter_by(user_id=current_user.id).all()
    return render_template('analytics.html', data=data, ac_data=ac_data)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/forgot', methods=['GET'])
def forgot():
    return render_template('forgot-pass.html')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=3000)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
