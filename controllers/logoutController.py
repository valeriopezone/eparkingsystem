from flask import Flask, session,redirect,url_for


def logoutController(userType='employee'):

    session.clear()

    return redirect(url_for(('backoffice_auth' if userType == 'employee' else 'agency_auth')))


    
