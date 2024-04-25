from pymongo import MongoClient


def iranian_ecommerce_db():
    client = MongoClient('localhost', 27017)
    db = client.iranian_ecommerce

    return db
