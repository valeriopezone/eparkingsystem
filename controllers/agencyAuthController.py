from flask import Flask, render_template,request,session,redirect,url_for
from models import Agency
import hashlib

def agencyAuthController():

    errorString = ''

    if ('agency' in session):
        return redirect(url_for('agency_panel'))

    if request.method == 'POST' and ('email' in request.form) and ('password' in request.form):
        if request.form['email'] and request.form['password']:
            hash = hashlib.sha256(request.form['password'].encode()).hexdigest().upper()
            currentUser = Agency.objects(email = request.form['email'],password = hash).first()
            if currentUser:
                if currentUser.active == 1:
                    session['agency'] = currentUser
                    return redirect(url_for('agency_panel'))
                else:
                    errorString = "Your account is not active"                       
            else:
                errorString = "Wrong data, unable to execute login"
        else:
            errorString = "Please insert username and password"


    return render_template(
        'auth/login_agency.html',
        errorString=errorString
        )
