from utils.database import iranian_ecommerce_db
from pymongo.write_concern import WriteConcern
import requests


db = iranian_ecommerce_db()

basalam_products_collection = db.basalam_products


session = requests.Session()

for cat in range(1, 13):
    from_ = 0
    while True:
        try:
            respnose = session.get(
                "https://search.basalam.com/ai-engine/api/v2.0/product/search",
                params={
                    "from": from_,
                    "f.cat": cat,
                    # "q": "",
                    "dynamicFacets": True,
                    "size": 1000,
                    "adsImpressionDisable": False,
                    "exp_ws": 0,
                    "filters.isExists": True
                },
            )
            if respnose.text == '"Not Found"':
                break
            products = respnose.json()['products']
            from_ += len(products)
            if not products:
                break
            basalam_products_collection.with_options(write_concern=WriteConcern(w=0)).insert_many(products, ordered=False)

        except Exception as err:
            print(err)