import requests

load= {
        "vin_number": "0722222",
        "production_date": "2023-10-11",
        "producer": "editedFord",
        "model": "ThroughPython_Focus",
        "version": "-",
        "generation": "2013",
        "horsepowers": "98",
        "color": "Czarny",
        "displacement_in_litres": "1.0",
        "mileage": "200000",
        "owner": 1
    }

r = requests.post('http://127.0.0.1:8000/api/cars',data=load)
