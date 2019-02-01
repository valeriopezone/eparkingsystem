from flask import Flask, render_template,request,session,redirect,url_for
from models import Employee,Parking
import hashlib
from bson import ObjectId
import pprint
def employeeController(action=None,resourceId=None):

    #keep non-logged users outside

    if ('employee' not in session):
        return redirect(url_for('backoffice_auth'))
    
    if not session['employee']['superAdmin'] and not resourceId:
        return redirect(url_for('backoffice_auth'))
    #check resourceId validity
    employeeData = None

    if resourceId:
        if ObjectId.is_valid(str(resourceId)):
            employeeData = Employee.objects(id=ObjectId(str(resourceId))).first()
            if not session['employee']['superAdmin'] and not (action == 'edit' and resourceId == session['employee']['_id']['$oid']):
                return render_template('404.html',errorString="Cannot access this area")
            if not employeeData:
                return render_template('404.html',errorString="This Employee does not exist")
        else:
            return render_template('404.html',errorString="This EmployeeId is not valid")

    errorString = ''
    employeeList = []
    evaluatedEmployee = None
    parkingList = []
    validationErrors = []
    pageTitle = ""


    #switch action cases (add,edit,delete,list)

    if action == 'add' or action == 'edit':

        pageTitle = "Add Employee" if action == "add" else "Edit Employee"
        templatePath = 'employees/add.html'

        if request.method == 'POST' and ('submit' in request.form):
            #validate username


            if 'login' in request.form:
                if not request.form['login']:
                    validationErrors.append("Field username is empty")
                else:
                    if len(request.form['login']) < 5:
                        validationErrors.append("Username field should be min. 5 chars")
                    if action == 'add':
                        if len(Employee.objects(login=request.form['login'])) > 0:
                            validationErrors.append("The username you've choose already exists")
                    else:
                        if len(Employee.objects(login=request.form['login'],login__ne=employeeData.login)) > 0:
                            validationErrors.append("The username you've choose already exists")
            else:
                validationErrors.append("Missing field username in request")

            #validate name
            if 'name' in request.form:
                if not request.form['name']:
                    validationErrors.append("Field name is empty")
            else:
                validationErrors.append("Missing field name in request")


            #validate password

            if 'password' in request.form:
                if not request.form['password']:
                    if(action == 'edit'):
                        hash = employeeData.password #keep old password
                    else:
                        validationErrors.append("Field password is empty")
                else:
                    if len(request.form['password']) < 8:
                        validationErrors.append("Password field should be min. 8 chars") 
                    else:
                        hash = hashlib.sha256(request.form['password'].encode()).hexdigest().upper()#make new hash
            else:
                validationErrors.append("Missing field password in request")

            active = 0
            superAdmin = 0

            if 'active' in request.form:
                active = (True if int(request.form['active']) == 1 else False)
            if 'superAdmin' in request.form:
                superAdmin = (True if int(request.form['superAdmin']) == 1 else False)


            #validate parking
            if not (action == 'edit' and resourceId and not session['employee']['superAdmin'] and str(session['employee']['_id']['$oid']) == resourceId):
                if 'relatedParking' in request.form:
                
                    #request.form['relatedParking']
                    if request.form['relatedParking'] and ObjectId.is_valid(str(request.form['relatedParking'])): 
                        if not Parking.objects(id=ObjectId(str(request.form['relatedParking']))).first():
                            validationErrors.append("The parking you are referencing is not existing")
                        else:
                            relatedParking = str(request.form['relatedParking'])

                    else:
                        validationErrors.append("The parking you are referencing is not valid")
                else:
                    validationErrors.append("Missing parking reference in request")
            else:
                relatedParking = session['employee']['relatedParking']['$oid']
                active = session['employee']['active']
                superAdmin = session['employee']['superAdmin']
            #validate active
            

            if len(validationErrors) == 0:
                 #save

                if action == 'add':
                    result = Employee(name = request.form['name'],
                                  login = request.form['login'],
                                  password = hash,
                                  relatedParking = ObjectId(str(relatedParking)),
                                  active = active,
                                  superAdmin = superAdmin
                                  ).save()
                    if result:
                        lastEmployee = Employee.objects(login=request.form['login']).first()
                        return redirect(url_for('employees',action='edit',resourceId=lastEmployee.id))
                    else:
                        validationErrors.append("Unable to write this record")
                else:
                    result = Employee.objects(id=ObjectId(str(resourceId))).update(name = request.form['name'],
                                  login = request.form['login'],
                                  password = hash,
                                  relatedParking = ObjectId(str(relatedParking)),
                                  active = active,
                                  superAdmin = superAdmin
                                  )
                    return redirect(url_for('employees',action='edit',resourceId=resourceId))
                 
                


            else:
                errorString ='|'.join(validationErrors)






    elif action == 'delete':
        pageTitle = "Employees"
        templatePath = 'employees/list.html'
        Employee.objects(id=ObjectId(str(resourceId))).delete()
        employeeList = Employee.objects().order_by('name')

    else:
        pageTitle = "Employees"
        templatePath = 'employees/list.html'     
        employeeList = Employee.objects().order_by('name')


    

    
    parkingList = Parking.objects().order_by('name')


    return render_template(
        templatePath,
        pageTitle=pageTitle,
        employee=session['employee'],
        userType='employee',
        errorString=errorString,
        evaluatedEmployee=evaluatedEmployee,
        employeeList=employeeList,
        parkingList=parkingList,
        employeeData=employeeData,
        action=action,
        resourceId=resourceId
        )
