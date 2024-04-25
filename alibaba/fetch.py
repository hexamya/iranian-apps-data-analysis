from utils.database import iranian_ecommerce_db
from pymongo.write_concern import WriteConcern
import requests
import re


db = iranian_ecommerce_db()

alibaba_train_tickets_collection = db.alibaba_train_tickets

cities = ["THR", "MHD", "AZD", "BND", "QUM", "TBZ", "KER", "SYZ", "AWZ", "IFN"]
dates = ["2024-04-27", "2024-04-28", "2024-04-29", "2024-04-30", "2024-05-01", "2024-05-02", "2024-05-03"]

session = requests.Session()

skip = True
skipper = lambda origin, destination, departureDate: all([origin == 'AZD', destination == 'BND', departureDate == '2024-04-29'])

for origin in cities:
    for destination in cities:
        if origin == destination:
            continue

        retry = 0
        for departureDate in dates:
            while True:
                try:
                    if skipper(origin, destination, departureDate):
                        skip = False
                    if skip:
                        break

                    token = session.post(
                        'https://ws.alibaba.ir/api/v2/train/available',
                        json={
                            "passengerCount": "1",
                            "ticketType": "Family",
                            "isExclusiveCompartment": "false",
                            "departureDate": departureDate,
                            "destination": destination,
                            "origin": origin,
                        }).json()['result']['requestId']

                    print(token)
                    response = session.get('https://ws.alibaba.ir/api/v1/train/available/' + token).json()
                    if error := response.get('error', {}).get('message'):
                        raise Exception(re.search(r"'>(.+?)</", error).group())
                    tickets = response.get('departing')
                    alibaba_train_tickets_collection.with_options(write_concern=WriteConcern(w=0)).insert_many(tickets, ordered=False)
                    break

                except Exception as err:
                    print(err)
                    print(origin, destination, departureDate, err)
                    retry += 1
                    if retry >= 3:
                        break
