from utils.database import iranian_ecommerce_db
from pymongo.write_concern import WriteConcern
import requests
import re


db = iranian_ecommerce_db()

alibaba_trains_collection = db.alibaba_trains
alibaba_flights_collection = db.alibaba_flights

flight_cities = ["THR", "AWZ", "SYZ", "MHD", "BND", "IFN", "TBZ", "KIH"]
train_cities = ["THR", "MHD", "AZD", "BND", "QUM", "TBZ", "KER", "SYZ", "AWZ", "IFN"]
dates = ["2024-04-27", "2024-04-28", "2024-04-29", "2024-04-30", "2024-05-01", "2024-05-02", "2024-05-03"]

session = requests.Session()


def train():
    skipper = lambda origin, destination, departureDate: all([origin == 'AWZ', destination == 'MHD', departureDate == '2024-04-30'])
    skip = True
    for origin in train_cities:
        for destination in train_cities:
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
                                "passengerCount": 1,
                                "ticketType": "Family",
                                "isExclusiveCompartment": False,
                                "departureDate": departureDate,
                                "destination": destination,
                                "origin": origin,
                            }).json()['result']['requestId']

                        response = session.get('https://ws.alibaba.ir/api/v1/train/available/' + token).json()
                        print(response)
                        if error := response.get('error', {}).get('message'):
                            raise Exception(re.search(r"'>(.+?)</", error).group())
                        tickets = response['departing']
                        if tickets:
                            alibaba_trains_collection.with_options(write_concern=WriteConcern(w=0)).insert_many(tickets, ordered=False)
                        break

                    except Exception as err:
                        print(err)
                        print(origin, destination, departureDate, err)
                        retry += 1
                        if retry >= 3:
                            break

def flight():
    skipper = lambda origin, destination, departureDate: all([origin == 'AZD', destination == 'BND', departureDate == '2024-04-29'])
    skip = False
    for origin in flight_cities:
        for destination in flight_cities:
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
                            'https://ws.alibaba.ir/api/v1/flights/domestic/available',
                            json={
                                "adult": 1,
                                "child": 0,
                                "departureDate": departureDate,
                                "destination": destination,
                                "infant": 0,
                                "origin": origin,
                            }).json()['result']['requestId']

                        print(token)
                        response = session.get('https://ws.alibaba.ir/api/v1/flights/domestic/available/' + token).json()
                        print(response)
                        if error := response.get('error', {}):
                            raise Exception(re.search(r"'>(.+?)</", error.get('message')).group())
                        tickets = response.get('result').get('departing')
                        if tickets:
                            alibaba_flights_collection.with_options(write_concern=WriteConcern(w=0)).insert_many(tickets, ordered=False)
                        break

                    except Exception as err:
                        print(err)
                        print(origin, destination, departureDate, err)
                        retry += 1
                        if retry >= 3:
                            break


if __name__ == "__main__":
    flight()