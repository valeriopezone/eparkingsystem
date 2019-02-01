from flask import Flask, render_template,request,session,redirect,url_for
from models import Reservation,Parking,Agency
import hashlib
from bson import ObjectId
from datetime import datetime
import decimal

def employeeReservationController(action=None,resourceId=None):

    #keep non-logged users outside

    if ('employee' not in session):
        return redirect(url_for('backoffice_auth'))

    #check resourceId validity
    reservationData = None

    if resourceId:
        if ObjectId.is_valid(str(resourceId)):
            reservationData = Reservation.objects(id=ObjectId(str(resourceId))).first()
            if not reservationData:
                return render_template('404.html',errorString="This Reservation does not exist")
            else:
                if (session['employee']['superAdmin'] is not True) and session['employee']['relatedParking']['$oid'] != str(reservationData.parking):
                    return render_template('404.html',errorString="You do not have access to this page")
        else:
            return render_template('404.html',errorString="This ParkingID is not valid")

    errorString = ''
    parkingList = []
    validationErrors = []
    pageTitle = ""
    reservationList = []
    agencyList = []


    #switch action cases (add,edit,delete,list)

    if action == 'add' or action == 'edit':

        pageTitle = "Add Reservation" if action == "add" else "Edit Reservation"
        templatePath = 'reservations/add.html'
        parkingList = Parking.objects().order_by('name')
        agencyList = Agency.objects().order_by('companyName')



        if request.method == 'POST' and ('submit' in request.form):
            #return render_template("404.html",errorString=datetime.strptime("2019-02-01 15:26", '%Y-%m-%d %H:%M').isoformat())
            #validation 


            #validate name
            if 'name' in request.form:
                if not request.form['name']:
                    validationErrors.append("Field name is empty")
            else:
                validationErrors.append("Missing field name in request")

            #validate surname
            if 'surname' in request.form:
                if not request.form['surname']:
                    validationErrors.append("Field surname is empty")
            else:
                validationErrors.append("Missing field surname in request")
            
            #validate email
            if 'email' in request.form:
                if not request.form['email'] or not request.form['email'].find("@"):
                    validationErrors.append("Field email is empty or invalid")
            else:
                validationErrors.append("Missing field email in request")

            #validate parking

            relatedParking = None
            if 'parking' in request.form:
                
                #request.form['relatedParking']
                if request.form['parking'] and ObjectId.is_valid(str(request.form['parking'])): 
                    if not Parking.objects(id=ObjectId(str(request.form['parking']))).first():
                        validationErrors.append("The parking you are referencing is not existing")
                    else:
                        relatedParking = ObjectId(str(request.form['parking']))
                else:
                    validationErrors.append("The parking you are referencing is not valid")
            else:
                validationErrors.append("Missing parking reference in request")
            
            #validate agency

            relatedAgency = None

            if 'relatedAgency' in request.form:

                if request.form['relatedAgency'] and request.form['relatedAgency'] != 0 and ObjectId.is_valid(str(request.form['relatedAgency'])): 
                    if not Agency.objects(id=ObjectId(str(request.form['relatedAgency']))).first():
                        validationErrors.append("The agency you are referencing is not existing")  
                    else:
                        relatedAgency = ObjectId(str(request.form['relatedAgency']))

            #validate dates
            fromDate = None
            toDate = None
            if 'fromDate' in request.form:
                if not request.form['fromDate']:
                    validationErrors.append("Field fromDate is empty")
                else:
                    try:
                        fromDate = datetime.strptime(request.form['fromDate'], '%Y-%m-%d %H:%M')
                    except:
                        validationErrors.append("Field fromDate is empty")

            else:
                validationErrors.append("Missing field fromDate in request")

            if 'toDate' in request.form:
                if not request.form['toDate']:
                    validationErrors.append("Field toDate is empty")
                else:
                    try:
                        toDate = datetime.strptime(request.form['toDate'], '%Y-%m-%d %H:%M')
                    except:
                        validationErrors.append("Field toDate is empty")

            else:
                validationErrors.append("Missing field fromDate in request")

            
            #non-mandatory fields    
            model = ""
            plate = ""
            type  = "car"
            paymentType  = "online"
            amount = 0
            agencyProfit = 0

            if 'model' in request.form:
                model = request.form['model']
            if 'plate' in request.form:
                plate = request.form['plate']
            if 'type' in request.form:
                type = ("car" if str(request.form['type']) == "car" else "moto")
            if 'paymentType' in request.form:
                paymentType = ("online" if str(request.form['paymentType']) == "online" else "onsite")
            

            if fromDate and toDate:
                #check date difference
                dateDiff = toDate - fromDate
                reservationHours = dateDiff.total_seconds()/3600
                if reservationHours <= 0:
                   validationErrors.append("Distance between starting and ending date should be 1 hour")

            
            




            if len(validationErrors) == 0:

                #proceed calculating amount and (if needed) agencyProfit 

                selectedParking = Parking.objects(id=relatedParking).first()
                amount = decimal.Decimal(reservationHours) * selectedParking['pricePerHour']

                if relatedAgency:
                 #calc profit
                 selectedAgency = Agency.objects(id=relatedAgency).first()
                 agencyProfit = selectedAgency['profitRate'] * amount / 100
                 
             


                if action == 'add':
                    result = Reservation(status = "CONFIRMED",
                                         user= {
                                             'name' : request.form['name'],
                                             'surname' : request.form['surname'],
                                             'email' : request.form['email'],
                                             'model' : model,
                                             'plate' : plate,
                                             'type' : type
                                         },
                                         fromDate=fromDate.isoformat(),
                                         toDate=toDate.isoformat(),
                                         parking=relatedParking,
                                         amount=amount,
                                         paymentType=paymentType,
                                         agencyProfit=agencyProfit,
                                         agency=relatedAgency,
                                         executionDate=datetime.now().isoformat()
                                         ).save()
                    if result:
                        return redirect(url_for('reservations'))
                    else:
                        validationErrors.append("Unable to write this record")
                else:
                    result = Reservation.objects(id=ObjectId(str(resourceId))).update(status = "CONFIRMED",
                                         user= {
                                             'name' : request.form['name'],
                                             'surname' : request.form['surname'],
                                             'email' : request.form['email'],
                                             'model' : model,
                                             'plate' : plate,
                                             'type' : type
                                         },
                                         fromDate=fromDate.isoformat(),
                                         toDate=toDate.isoformat(),
                                         parking=relatedParking,
                                         amount=amount,
                                         paymentType=paymentType,
                                         agencyProfit=agencyProfit,
                                         agency=relatedAgency,
                                         executionDate=datetime.now().isoformat())
                    return redirect(url_for('reservations',action='edit',resourceId=resourceId))
                 
               

            else:
                errorString ='|'.join(validationErrors)






    elif action == 'delete':
        Reservation.objects(id=ObjectId(str(resourceId))).update(status = "DECLINED")
        return redirect(url_for('reservations'))

    else:
        pageTitle = "Reservations"
        templatePath = 'reservations/list.html'
        objectList = Reservation.objects(parking=session['employee']['relatedParking']['$oid']) if not session['employee']['superAdmin'] else Reservation.objects()

        reservationList = objectList.aggregate(*[
            {
                "$lookup":{
                "from": "parkings",       
                "localField": "parking",   
                "foreignField": "_id", 
                "as": "parkingData"         
                }
            },
            
            {
                "$lookup":{
                "from": "agencies",       
                "localField": "agency",   
                "foreignField": "_id", 
                "as": "agencyData"         
                }
            },
            {   
                "$unwind":"$parkingData" 
            },
            

            {
                "$project":{
                "_id" : 1,
                "status" : 1,
                "user" : 1,
                "fromDate" : 1,
                "toDate" : 1,
                "parking" : 1,
                "amount" : 1,
                "paymentType" : 1,
                "agencyProfit" : 1,
                "agency" : 1,
                "executionDate" : 1,
                "parkingName" : "$parkingData.name",
                "agencyCompanyName" : "$agencyData.companyName",
                } 
            }
        ])

        


    

    


    return render_template(
        templatePath,
        pageTitle=pageTitle,
        employee=session['employee'],
        userType='employee',
        errorString=errorString,
        parkingList=parkingList,
        agencyList=agencyList,
        reservationList=reservationList,
        reservationData=reservationData,
        action=action,
        resourceId=resourceId
        )
