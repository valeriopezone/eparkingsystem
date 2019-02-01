from flask import Flask, render_template,request,session,redirect,url_for
from models import Agency
import hashlib
from bson import ObjectId

def employeeAgencyController(action=None,resourceId=None):

    #keep non-logged users outside

    if ('employee' not in session) or (session['employee']['superAdmin'] is not True):
        return redirect(url_for('backoffice_auth'))

    #check resourceId validity
    agencyData = None

    if resourceId is not None:
        if ObjectId.is_valid(str(resourceId)):
            agencyData = Agency.objects(id=ObjectId(str(resourceId))).first()
            if not agencyData:
                return render_template('404.html',errorString="This Agency does not exist")
        else:
            return render_template('404.html',errorString="This AgencyID is not valid")

    errorString = ''
    agencyList = []
    validationErrors = []
    pageTitle = ""


    #switch action cases (add,edit,delete,list)

    if action == 'add' or action == 'edit':

        pageTitle = "Add Agency" if action == "add" else "Edit Agency"
        templatePath = 'agencies/add.html'

        if request.method == 'POST' and ('submit' in request.form):
            #validate username


            if 'email' in request.form:
                if not request.form['email']:
                    validationErrors.append("Field email is empty")
                else:
                    if not request.form['email'].find("@"):
                        validationErrors.append("Email field should contain at least one @")
                    if action == 'add':
                        if len(Agency.objects(email=request.form['email'])) > 0:
                            validationErrors.append("The email you've choose already exists")
                    else:
                        if len(Agency.objects(email=request.form['email'],email__ne=agencyData.email)) > 0:
                            validationErrors.append("The email you've choose already exists")
            else:
                validationErrors.append("Missing field email in request")

            #validate companyName
            if 'companyName' in request.form:
                if not request.form['companyName']:
                    validationErrors.append("Field companyName is empty")
            else:
                validationErrors.append("Missing field companyName in request")

            #validate phone
            if 'phone' in request.form:
                if not request.form['phone']:
                    validationErrors.append("Field phone is empty")
            else:
                validationErrors.append("Missing field phone in request")
            
            #validate phone
            if 'VAT' in request.form:
                if not request.form['VAT']:
                    validationErrors.append("Field VAT is empty")
            else:
                validationErrors.append("Missing field VAT in request")

            city = ''
            district = ''
            address = ''

            if 'city' in request.form:
                city = request.form['city']
            if 'district' in request.form:
                district = request.form['district']
            if 'address' in request.form:
                address = request.form['address']
           

            #validate password

            if 'password' in request.form:
                if not request.form['password']:
                    if(action == 'edit'):
                        hash = agencyData.password #keep old password
                    else:
                        validationErrors.append("Field password is empty")
                else:
                    if len(request.form['password']) < 8:
                        validationErrors.append("Password field should be min. 8 chars") 
                    else:
                        hash = hashlib.sha256(request.form['password'].encode()).hexdigest().upper()#make new hash
            else:
                validationErrors.append("Missing field password in request")

            

            #validate active
            
                

            if len(validationErrors) == 0:
                 #save

                 
                
    
                if action == 'add':
                    result = Agency(companyName = str(request.form['companyName']),
                                  city = str(city),
                                  district = str(district),
                                  address = str(address),
                                  email = str(request.form['email']),
                                  phone = str(request.form['phone']),
                                  profitRate = float(request.form['profitRate']),
                                  VAT = str(request.form['VAT']),
                                  password = hash,
                                  active = (True if int(request.form['active']) == 1 else False)
                                  ).save()
                    if result:
                        lastAgency = Agency.objects(email=request.form['email']).first()
                        return redirect(url_for('agencies',action='edit',resourceId=lastAgency.id))
                    else:
                        validationErrors.append("Unable to write this record")

                else:
                    result = Agency.objects(email=agencyData['email']).update(companyName = str(request.form['companyName']),
                                  city = str(city),
                                  district = str(district),
                                  address = str(address),
                                  email = str(request.form['email']),
                                  phone = str(request.form['phone']),
                                  profitRate = float(request.form['profitRate']),
                                  VAT = str(request.form['VAT']),
                                  password = hash,
                                  active = (True if int(request.form['active']) == 1 else False))
                    return redirect(url_for('agencies',action='edit',resourceId=resourceId))
                 
                


            else:
                errorString ='|'.join(validationErrors)






    elif action == 'delete':
        pageTitle = "Agencies"
        templatePath = 'agencies/list.html'
        Agency.objects(id=ObjectId(str(resourceId))).delete()
        agencyList = Agency.objects().order_by('companyName')

    else:
        pageTitle = "Agencies"
        templatePath = 'agencies/list.html'     
        agencyList = Agency.objects().order_by('companyName')


    

    


    return render_template(
        templatePath,
        pageTitle=pageTitle,
        employee=session['employee'],
        userType='employee',
        errorString=errorString,
        agencyList=agencyList,
        agencyData=agencyData,
        action=action,
        resourceId=resourceId
        )
