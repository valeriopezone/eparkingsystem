from flask_mongoengine import MongoEngine
db = MongoEngine()

class Parking(db.Document): 
    name = db.StringField(max_length=32, required=True)
    city = db.StringField(max_length=32, required=True)
    district = db.StringField(max_length=32, required=True)
    address = db.StringField(max_length=64, required=True)
    phone = db.StringField(max_length=32, required=True)
    pricePerHour = db.DecimalField(precision=2,required=True)
    maxPlaces = db.IntField(required=True,default=0)
    active = db.BooleanField(required=True,default=0)
    
    meta = {
        'collection': 'parkings'
        }

class Agency(db.Document): 
    companyName = db.StringField(max_length=64, required=True)
    city = db.StringField(max_length=32, required=False)
    district = db.StringField(max_length=32, required=False)
    address = db.StringField(max_length=64, required=False)
    email = db.EmailField(max_length=64, required=True)
    password = db.StringField(max_length=64, required=True)
    phone = db.StringField(max_length=32, required=True)
    profitRate = db.DecimalField(precision=2)
    VAT = db.StringField(max_length=20)
    active = db.BooleanField(required=True,default=0)
    
    meta = {
        'collection': 'agencies'
        }

class Employee(db.Document): 
    name = db.StringField(max_length=64, required=True)
    login = db.StringField(max_length=64, required=True)
    password = db.StringField(max_length=64, required=True)
    active = db.BooleanField(required=True,default=0)
    superAdmin = db.BooleanField(required=True,default=0)
    relatedParking = db.ObjectIdField()
    meta = {
        'collection': 'employees'
        }


class Reservation(db.Document):
    status = db.StringField(max_length=32, required=True, default = "CONFIRMED")
    user = db.DynamicField(required=True)
    fromDate = db.DateTimeField(required=True)
    toDate = db.DateTimeField(required=True)
    parking = db.ObjectIdField()    
    amount = db.DecimalField(precision=2, required=True)
    paymentType = db.StringField(max_length=16, required=True,default = "ONLINE")
    agencyProfit = db.DecimalField(precision=2)
    agency = db.ObjectIdField()
    executionDate = db.DateTimeField(required=True)

    meta = {
        'collection': 'reservations'
        }

"""
db.createCollection("parkings")

db.parkings.insert({
name : "Parcheggio Rosso",
city : "Napoli",
district : "NA",
address : "Corso Vittorio Emanuele, 11",
phone : "0812983312",
pricePerHour : 3.2,
maxPlaces : 545,
active : 1,
payOnsite : 1,
payOnline : 1
})

db.parkings.insert({
name : "Parcheggio Viola",
city : "Salerno",
district : "SA",
address : "via Armando Diaz, 144",
phone : "0817728394",
pricePerHour : 4.1,
maxPlaces : 1298,
active : 1,
payOnsite : 1,
payOnline : 1
})

db.createCollection("employees")

db.employees.insert({
name : "Valerio", 
login : "administrator", 
password : "8C6976E5B5410415BDE908BD4DEE15DFB167A9C873FC4BB8A81F6F2AB448A918",
active : 1,
superAdmin : 1,
relatedParking : {}})

db.createCollection("agencies")


db.agencies.insert({
companyName : "ParkingForYou SRL",
city : "Milan",
district : "MI",
address : "via Guelfa, 18",
email : "info@parkingforyou.com",
password : "8C6976E5B5410415BDE908BD4DEE15DFB167A9C873FC4BB8A81F6F2AB448A918",
phone : "029332345",
profitRate : 5.4,
VAT : "0011928392",
active : 1
})

db.agencies.insert({
companyName : "CustomerFinder SPA",
city : "Bari",
district : "BA",
address : "Gran via dei Gerani, 110",
email : "info@customerfinder.com",
password : "8C6976E5B5410415BDE908BD4DEE15DFB167A9C873FC4BB8A81F6F2AB448A918",
phone : "83829183944",
profitRate : 12.5,
VAT : "00293821132",
active : 1
})

db.createCollection("reservations")
    status = db.StringField(max_length=32, required=True, default = "DRAFT")
    user = db.DynamicField(required=True)
    fromDate = db.DateTimeField(required=True)
    toDate = db.DateTimeField(required=True)
    parking = db.ObjectIdField()    
    amount = db.DecimalField(precision=2, required=True)
    paymentType = db.StringField(max_length=16, required=True,default = "ONLINE")
    agencyProfit = db.DecimalField(precision=2)
    agency = db.ObjectIdField()
    executionDate = db.DateTimeField(required=True)

    db.reservations.insert({
    status : "DRAFT",
    user : {
        name : "Valerio", 
        surname : "Pezone", 
        type : "car", 
        model : "Opel Astra",
        plate : "AA456NN"
        },
    fromDate : "2019-30-01 15:00:00",
    toDate : "2019-31-01 12:00:00",
    parking : ObjectId("5c51e38f5bd15cb4e29ebec5"),
    amount : 5,
    paymentType : "ONLINE",
    agencyProfit : 1.2,
    agency : ObjectId("5c51f1af5bd15cb4e29ebec9"),
    executionDate : "2019-29-01 11:30:00"
    })
"""