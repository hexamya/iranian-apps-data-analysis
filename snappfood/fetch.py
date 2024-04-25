from utils.database import iranian_ecommerce_db
from pymongo.write_concern import WriteConcern
import requests


db = iranian_ecommerce_db()

snappfood_products_collection = db.snappfood_products
snappfood_vendors_collection = db.snappfood_vendors
snappfood_full_vendors_collection = db.snappfood_full_vendors


session = requests.Session()

session.headers.update({
    "Accept": "application/json",
    "Accept-Encoding": "gzip",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "DNT": "1",
    "Origin": "https://snappfood.ir",
    "Referer": "https://snappfood.ir",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "TE": "trailers",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
})

page = 1
while True:
    try:
        respnose = session.get(
            f"https://snappfood.ir/search/api/v1/desktop/vendors-list",
            params={
                "page": page-1,
                "page_size": 10000,
                "sp_alias": "restaurant",
                "city_name": "Tehran",
            }
        )
        data = respnose.json()['data']
        page_break = (data['count'] // 10000) + (data['count'] % 10000 > 0)
        vendors = list(map(lambda item: item['data'], data['finalResult']))
        snappfood_vendors_collection.with_options(write_concern=WriteConcern(w=0)).insert_many(vendors, ordered=False)
        if page >= page_break:
            break
        else:
            page += 1
    except Exception as err:
        print(err)

for vendor in vendors:
    try:
        respnose = session.get(
            f"https://snappfood.ir/mobile/v2/restaurant/details/dynamic",
            params={
                "optionalClient": "WEBSITE",
                "vendorCode": vendor["code"],
                "fetch-static-data": 1,
            }
        )
        data = respnose.json()['data']
        snappfood_full_vendors_collection.with_options(write_concern=WriteConcern(w=0)).insert_many(data['vendor'], ordered=False)
        products = [i | {'vendorCode': vendor['code']} for j in data['menus'] for i in j['products']]
        snappfood_products_collection.with_options(write_concern=WriteConcern(w=0)).insert_many(products, ordered=False)
    except Exception as err:
        print(err)