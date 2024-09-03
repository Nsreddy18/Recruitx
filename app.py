from operator import methodcaller
from django.forms import DateField
from django.shortcuts import render
from flask import Flask, flash,render_template, request,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,LoginManager, login_required,logout_user,current_user 
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,FloatField,IntegerField,SelectField,TextAreaField,DateField
from wtforms.validators import InputRequired,Length,ValidationError
from datetime import date,datetime,timedelta
from sqlalchemy import func
import sqlite3




login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    rollno=db.Column(db.String(10),unique=True,nullable=False)
    dob=db.Column(db.String(10),nullable=False)
    year=db.Column(db.String(10),nullable=False)
    branch=db.Column(db.String(30),nullable=False)
    mail=db.Column(db.String(30),unique=True,nullable=False)
    phone=db.Column(db.String(10),unique=True,nullable=False)
    password=db.Column(db.String(80),nullable=False)

class Companies(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),unique=True,nullable=False)
    cgpa=db.Column(db.Float,nullable=False)
    package=db.Column(db.String(20),nullable=False)
    date=db.Column(db.String(20),nullable=False)

    
class AddCompany(FlaskForm):
    name=StringField('Name',validators=[InputRequired(),Length(min=1,max=20)],render_kw={"placeholder":"Name"})
    cgpa=FloatField('CGPA',validators=[InputRequired()],render_kw={"placeholder":"CGPA"})
    package=StringField('Package',validators=[InputRequired(),Length(min=1,max=20)],render_kw={"placeholder":"Package"})
    date=StringField('Date',validators=[InputRequired(),Length(min=1,max=20)],render_kw={"placeholder":"YYYY-MM-DD"})
    submit=SubmitField('Submit') 


class RegisterForm(FlaskForm):
    username=StringField(validators=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder": "Username"})

    rollno=StringField(validators=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder": "Rollno"})

    dob=StringField(validators=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder": "YYYY-MM-DD"})

    year=StringField(validators=[InputRequired(),Length(min=1,max=4)], render_kw={"placeholder": "Year"})

    branch=StringField(validators=[InputRequired(),Length(min=4,max=30)], render_kw={"placeholder": "Branch"})

    mail=StringField(validators=[InputRequired(),Length(min=4,max=30)], render_kw={"placeholder": "Mail"})

    phone=StringField(validators=[InputRequired(),Length(min=10,max=10)], render_kw={"placeholder": "Phone"})
    
    password=PasswordField(validators=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder": "Password"})

    submit=SubmitField('Sign Up')

    def validate_username(self,username):
        u=User.query.filter_by(username=username.data).first()
        
        if u:
            flash('Username already taken')

class LoginForm(FlaskForm):
    username=StringField(validators=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder": "Username"})

    password=PasswordField(validators=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder": "Password"})

    submit=SubmitField('Sign In')

class Eligibility(FlaskForm):
    cgpa=StringField(validators=[InputRequired(),Length(min=1,max=20)], render_kw={"placeholder": "CGPA"})
    submit=SubmitField('Submit')


@app.route('/',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.username.data=='admin':
        return redirect(url_for('dashboard_admin'))
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user and user.password==form.password.data:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html',form=form)


@app.route('/view',methods=['GET','POST'])
@login_required
def view():
    data=User.query.all()
    return render_template('viewstudents.html',data=data)



@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')



@app.route('/dashboard_admin',methods=['GET','POST'])
@login_required
def dashboard_admin():
    return render_template('dashboard_admin.html')



@app.route('/previous-year-records',methods=['GET','POST'])
@login_required
def previous_year_records():
    return render_template('previous.html')



@app.route('/previous_admin',methods=['GET','POST'])
@login_required
def previous_admin():
    return render_template('previous_admin.html')



@app.route('/profile',methods=['GET','POST'])
@login_required
def profile():
    return render_template('profile.html')


@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    return redirect(url_for('login'))



@app.route('/placement',methods=['GET','POST'])
@login_required
def placements():
    if current_user.username=='admin':
        return redirect(url_for('placementadd'))
    return render_template('placement.html')



@app.route('/placementadd',methods=['GET','POST'])
@login_required
def placementadd():
    form=AddCompany()
    def v(name):
        c=Companies.query.filter_by(name=name.data).first()
        if c:
            return False
        return True
    if not v(form.name):
        flash('Company already exists')
        return redirect(url_for('placementadd'))
    if form.validate_on_submit():
        company=Companies(name=form.name.data,cgpa=form.cgpa.data,package=form.package.data,date=form.date.data)
        db.session.add(company)
        db.session.commit()
        flash('Company added')
    return render_template('placementadd.html',form=form)



@app.route('/upcoming',methods=['GET','POST'])
@login_required
def upcoming():
    d=date.today()
    d1=d+timedelta(days=1)
    d2=d1+timedelta(days=1)
    d3=d2+timedelta(days=1)
    s1=str(d1)
    s2=str(d2)
    s3=str(d3)
    data=Companies.query.filter_by(date=s1).all()
    data1=Companies.query.filter_by(date=s2).all()
    data2=Companies.query.filter_by(date=s3).all()
    return render_template('upcoming.html',data=data,data1=data1,data2=data2)



@app.route('/upcoming_admin',methods=['GET','POST'])
@login_required
def upcoming_admin():
    d=date.today()
    d1=d+timedelta(days=1)
    d2=d1+timedelta(days=1)
    d3=d2+timedelta(days=1)
    s1=str(d1)
    s2=str(d2)
    s3=str(d3)
    data=Companies.query.filter_by(date=s1).all()
    data1=Companies.query.filter_by(date=s2).all()
    data2=Companies.query.filter_by(date=s3).all()
    return render_template('upcoming_admin.html',data=data,data1=data1,data2=data2)



@app.route('/ongoing_admin',methods=['GET','POST'])
@login_required
def ongoing_admin():
    d=date.today()
    s=str(d)
    data=Companies.query.filter_by(date=d).all()
    return render_template('ongoing_admin.html',data=data)



@app.route('/ongoing',methods=['GET','POST'])
@login_required
def ongoing():
    d=date.today()
    s=str(d)
    data=Companies.query.filter_by(date=d).all()
    return render_template('ongoing.html',data=data)



@app.route('/eligibility',methods=['GET','POST'])
@login_required
def eligibility():
    form=Eligibility()
    if form.validate_on_submit():
        if float(form.cgpa.data)>10 or float(form.cgpa.data)<4:
            flash('Invalid CGPA','info')
            return redirect(url_for('eligibility'))
        data=Companies.query.filter(Companies.cgpa<=form.cgpa.data).all()
        return render_template('eligibility.html',data=data,form=form)
    return render_template('eligibility.html',form=form)



@app.route('/eligibility_admin',methods=['GET','POST'])
@login_required
def eligibility_admin():
    form=Eligibility()
    if form.validate_on_submit():
        if float(form.cgpa.data)>10 or float(form.cgpa.data)<4:
            flash('Invalid CGPA','info')
            return redirect(url_for('eligibility'))
        data=Companies.query.filter(Companies.cgpa<=form.cgpa.data).all()
        return render_template('eligibility_admin.html',data=data,form=form)
    return render_template('eligibility_admin.html',form=form)



@app.route('/register',methods=['GET','POST'])
def register():
    form=RegisterForm()
    def v(username):
        u=User.query.filter_by(username=username.data).first()
        if u:
            return False
        return True
    if not v(form.username):
        flash('Username already taken')
        return redirect(url_for('register'))
    if form.validate_on_submit():
        new_user=User(username=form.username.data,rollno=form.rollno.data,dob=form.dob.data,year=form.year.data,branch=form.branch.data,mail=form.mail.data,phone=form.phone.data,password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html',form=form)



if(__name__=='__main__'):
    app.run(debug=True)
