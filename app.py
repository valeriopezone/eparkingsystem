from flask import Flask, render_template,send_from_directory,request,session
import babel

from models import db, Parking,Agency,Employee,Reservation
from controllers.indexController import indexController
from controllers.logoutController import logoutController

from controllers.employeeAuthController import employeeAuthController
from controllers.employeeController import employeeController
from controllers.employeeParkingController import employeeParkingController
from controllers.employeeAgencyController import employeeAgencyController
from controllers.employeeReservationController import employeeReservationController

from controllers.agencyAuthController import agencyAuthController
from controllers.agencyReservationController import agencyReservationController

from controllers.customerController import customerController

# initialize instance of WSGI application
# act as a central registry for the view functions, URL rules, template configs
app = Flask(__name__,static_url_path='')

## include db name in URI; _HOST entry overwrites all others
app.config['MONGODB_SETTINGS'] = {
    'db': 'eparkingsystem',
    'host': '127.0.0.1',
    'port': 27017
}
app.debug = True

app.secret_key = '57048880436147513580'
app.config['SESSION_TYPE'] = 'filesystem'



# initalize app with database
db.init_app(app)

@app.route("/")
def index():
    return indexController()


#Backoffice routes

@app.route("/backoffice")
def backoffice():
    return employeeReservationController()

@app.route("/backoffice/auth", methods = ['GET','POST'])
def backoffice_auth():
    return employeeAuthController()

@app.route("/backoffice/parkings/")
@app.route("/backoffice/parkings/<string:action>/", methods = ['GET','POST'])
@app.route("/backoffice/parkings/<string:action>/<string:resourceId>", methods = ['GET','POST'])
def parkings(action=None,resourceId=None):
    return employeeParkingController(action,resourceId)

@app.route("/backoffice/agencies/")
@app.route("/backoffice/agencies/<string:action>/", methods = ['GET','POST'])
@app.route("/backoffice/agencies/<string:action>/<string:resourceId>", methods = ['GET','POST'])
def agencies(action=None,resourceId=None):
    return employeeAgencyController(action,resourceId)

@app.route("/backoffice/employees/")
@app.route("/backoffice/employees/<string:action>/", methods = ['GET','POST'])
@app.route("/backoffice/employees/<string:action>/<string:resourceId>", methods = ['GET','POST'])
def employees(action=None,resourceId=None):
    return employeeController(action,resourceId)

@app.route("/backoffice/reservations/")
@app.route("/backoffice/reservations/<string:action>/", methods = ['GET','POST'])
@app.route("/backoffice/reservations/<string:action>/<string:resourceId>", methods = ['GET','POST'])
def reservations(action=None,resourceId=None):
    return employeeReservationController(action,resourceId)


#Agency panel routes
@app.route("/agencyPanel")
def agency_panel():
    return agencyReservationController()

@app.route("/agencyPanel/auth", methods = ['GET','POST'])
def agency_auth():
    return agencyAuthController()

@app.route("/agencyPanel/reservations/")
@app.route("/agencyPanel/reservations/<string:action>/", methods = ['GET','POST'])
@app.route("/agencyPanel/reservations/<string:action>/<string:resourceId>", methods = ['GET','POST'])
def agency_reservations(action=None,resourceId=None):
    return agencyReservationController(action,resourceId)

#Customer routes

@app.route("/customer", methods = ['GET','POST'])
@app.route("/customer/<string:action>/", methods = ['GET','POST'])
def customer(action=None):
    return customerController(action)


@app.route("/logout/<string:userType>")
def logout(userType='employee'):
    return logoutController(userType)



#Serving static files

@app.route('/assets/<path:path>')
def serve_assets(path):
    return send_from_directory('assets', path)

app.jinja_env.add_extension('jinja2.ext.loopcontrols')


if __name__ == '__main__':
    app.run(debug=True)
