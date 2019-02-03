from flask import Flask, render_template,request,session,redirect,url_for
from models import Reservation,Parking,Agency
import hashlib
from bson import ObjectId
from datetime import datetime
import decimal
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import unescape,escape

def customerController(action="step1",config = {}):

    parkingList = Parking.objects().order_by('companyName')

    templatePath = "customer/index.html"

    errorString = ''
    validationErrors = []

    if action == 'step1':
        
        if request.method == 'POST' and ('submit' in request.form):
            #validate and show amount

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

                    
                 
             


                
                    session['reservation'] = {'user': {
                                                 'name' : request.form['name'],
                                                 'surname' : request.form['surname'],
                                                 'email' : request.form['email'],
                                                 'model' : model,
                                                 'plate' : plate,
                                                 'type' : type
                                             },
                                             'fromDate':fromDate,
                                             'toDate':toDate,
                                             'parking':str(relatedParking),
                                             'amount':float(amount),
                                             'paymentType':paymentType,
                                             'agencyProfit':float(agencyProfit),
                                             }
                    return redirect(url_for('customer',action='step2'))
                
               

                else:
                    
                    errorString ='|'.join(validationErrors)


    elif action == 'step2':
        templatePath = "customer/amount.html"
    elif action == 'step3':
        action = "error"
        templatePath = "customer/done.html"
        if "reservation" in session:
            executionDate = datetime.now()
            result = Reservation(status = "CONFIRMED",
                                             user= {
                                                 'name' : session['reservation']['user']['name'],
                                                 'surname' : session['reservation']['user']['surname'],
                                                 'email' : session['reservation']['user']['email'],
                                                 'model' : session['reservation']['user']['model'],
                                                 'plate' : session['reservation']['user']['plate'],
                                                 'type' : session['reservation']['user']['type']
                                             },
                                             fromDate=session['reservation']['fromDate'],
                                             toDate=session['reservation']['toDate'],
                                             parking=ObjectId(str(session['reservation']['parking'])),
                                             amount=session['reservation']['amount'],
                                             paymentType="online",
                                             executionDate=executionDate.isoformat()
                                             ).save()
            if result:
                action = "success"
                selectedParking = Parking.objects(id=ObjectId(str(session['reservation']['parking']))).first()
                try:
                    server = smtplib.SMTP(config['SMTP_CONFIG']['HOST'], config['SMTP_CONFIG']['PORT'])
                    server.starttls()
                    server.login(config['SMTP_CONFIG']['LOGIN'], config['SMTP_CONFIG']['PASSWORD'])
                    to = str(session['reservation']['user']['email'])
                    msg = MIMEMultipart()
                    msg['From'] = config['SMTP_CONFIG']['SEND_FROM']
                    msg['To'] = to
                    msg['Subject'] = "Well done! Parking reservation confirm"
                    body = "<p>Dear " + escape(session['reservation']['user']['name'] +  " " + session['reservation']['user']['surname']) + ",<br>this is your booking:<ul>\
                            <li>Code : " + str(result.id) + "</li>\
                            <li>Execution : " + executionDate.strftime('%d/%m/%Y %H:%M') + "</li>\
                            <li>From : " + session['reservation']['fromDate'].strftime('%d/%m/%Y %H:%M') + "</li>\
                            <li>To : " + session['reservation']['toDate'].strftime('%d/%m/%Y %H:%M') + "</li>\
                            <li>Amount : &euro;" + str(session['reservation']['amount']) + "</li>\
                            <li>Parking : " + escape(str(selectedParking.name)) + "</li>\
                            <li>Parking Address : " + escape(str(selectedParking.address) + "," + str(selectedParking.city) + " " + str(selectedParking.district)) + "</li>\
                            </ul><br><br>Best regards,<br><b>eparkingsystem</b></p>\
                            "
                    msg.attach(MIMEText(body, 'html'))
                    text = msg.as_string()
                    server.sendmail(config['SMTP_CONFIG']['SEND_FROM'], to,text)
                    server.quit()        
                except:
                    pass

                session.clear()
        




    return render_template(
        templatePath,
        parkingList=parkingList,
        errorString=errorString,
        action=action,
        reservation=session['reservation'] if "reservation" in session else {}
        )