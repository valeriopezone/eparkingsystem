from flask import Flask, render_template,request,session,redirect,url_for
from models import Parking
import hashlib
from bson import ObjectId

def employeeParkingController(action=None,resourceId=None):

    #keep non-logged users outside

    if ('employee' not in session) or (session['employee']['superAdmin'] is not True):
        return redirect(url_for('backoffice_auth'))

    #check resourceId validity
    parkingData = None

    if resourceId is not None:
        if ObjectId.is_valid(str(resourceId)):
            parkingData = Parking.objects(id=ObjectId(str(resourceId))).first()
            if not parkingData:
                return render_template('404.html',errorString="This Parking does not exist")
            else:
                if (session['employee']['superAdmin'] is not True) and session['employee']['relatedParking'] != str(resourceId):
                    return render_template('404.html',errorString="You do not have access to this page")
        else:
            return render_template('404.html',errorString="This ParkingID is not valid")

    errorString = ''
    parkingList = []
    validationErrors = []
    pageTitle = ""


    #switch action cases (add,edit,delete,list)

    if action == 'add' or action == 'edit':

        pageTitle = "Add Parking" if action == "add" else "Edit Parking"
        templatePath = 'parkings/add.html'

        if request.method == 'POST' and ('submit' in request.form):
            #validate username




            if 'name' in request.form:
                if not request.form['name']:
                    validationErrors.append("Field name is empty")
                else:                    
                    if action == 'add':
                        if len(Parking.objects(name=request.form['name'])) > 0:
                            validationErrors.append("The name you've choose already exists")
                    else:
                        if len(Parking.objects(name=request.form['name'],name__ne=parkingData.name)) > 0:
                            validationErrors.append("The name you've choose already exists")
            else:
                validationErrors.append("Missing field name in request")

            #validate companyName
            if 'city' in request.form:
                if not request.form['city']:
                    validationErrors.append("Field city is empty")
            else:
                validationErrors.append("Missing field city in request")

            #validate phone
            if 'district' in request.form:
                if not request.form['district']:
                    validationErrors.append("Field district is empty")
            else:
                validationErrors.append("Missing field district in request")
            
            #validate phone
            if 'address' in request.form:
                if not request.form['address']:
                    validationErrors.append("Field address is empty")
            else:
                validationErrors.append("Missing field address in request")

            if 'phone' in request.form:
                if not request.form['phone']:
                    validationErrors.append("Field phone is empty")
            else:
                validationErrors.append("Missing field phone in request")


            if 'pricePerHour' in request.form:
                if not request.form['pricePerHour'] or float(request.form['pricePerHour']) <= 0:
                    validationErrors.append("Field pricePerHour is empty or invalid")
            else:
                validationErrors.append("Missing field pricePerHour in request")
    

            
            active = False
            maxPlaces = 1

            if 'maxPlaces' in request.form:
                maxPlaces = request.form['maxPlaces']
            if 'active' in request.form:
                active = (True if int(request.form['active']) == 1 else False)
            
           
            
                

            if len(validationErrors) == 0:
                 #save

                 


    
                if action == 'add':
                    result = Parking(name = str(request.form['name']),
                                  city = str(request.form['city']),
                                  district = str(request.form['district']),
                                  address = str(request.form['address']),
                                  phone = str(request.form['phone']),
                                  pricePerHour = float(request.form['pricePerHour']),
                                  maxPlaces = maxPlaces,
                                  active = active
                                  ).save()
                    if result:
                        lastParking = Parking.objects(name=str(request.form['name'])).first()
                        return redirect(url_for('parkings',action='edit',resourceId=lastParking.id))
                    else:
                        validationErrors.append("Unable to write this record")
                else:
                    result = Parking.objects(id=ObjectId(str(resourceId))).update(name = str(request.form['name']),
                                  city = str(request.form['city']),
                                  district = str(request.form['district']),
                                  address = str(request.form['address']),
                                  phone = str(request.form['phone']),
                                  pricePerHour = float(request.form['pricePerHour']),
                                  maxPlaces = maxPlaces,
                                  active = active)
                    return redirect(url_for('parkings',action='edit',resourceId=resourceId))
                 
                


            else:
                errorString ='|'.join(validationErrors)






    elif action == 'delete':
        pageTitle = "Parkings"
        templatePath = 'parkings/list.html'
        Parking.objects(id=ObjectId(str(resourceId))).delete()
        parkingList = Parking.objects().order_by('companyName')

    else:
        pageTitle = "Parkings"
        templatePath = 'parkings/list.html'     
        parkingList = Parking.objects().order_by('companyName')
        

    

    


    return render_template(
        templatePath,
        pageTitle=pageTitle,
        employee=session['employee'],
        userType='employee',
        errorString=errorString,
        parkingList=parkingList,
        parkingData=parkingData,
        action=action,
        resourceId=resourceId
        )
