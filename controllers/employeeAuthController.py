from flask import Flask, render_template,request,session,redirect,url_for
from models import Employee
import hashlib

def employeeAuthController():

    errorString = ''

    if ('employee' in session):
        return redirect(url_for('backoffice'))

    if request.method == 'POST' and ('username' in request.form) and ('password' in request.form):
        if request.form['username'] and request.form['password']:
            hash = hashlib.sha256(request.form['password'].encode()).hexdigest().upper()
            currentUser = Employee.objects(login = request.form['username'],password = hash).first()
            if currentUser:
                if currentUser.active == 1:
                    session['employee'] = currentUser
                    return redirect(url_for('backoffice'))
                else:
                    errorString = "Your account is not active"                       
            else:
                errorString = "Wrong data, unable to execute login"
        else:
            errorString = "Please insert username and password"


    return render_template(
        'auth/login_employee.html',
        errorString=errorString
        )
