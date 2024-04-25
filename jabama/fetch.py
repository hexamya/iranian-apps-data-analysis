from utils.database import iranian_ecommerce_db
from pymongo.write_concern import WriteConcern
import requests


db = iranian_ecommerce_db()

jabama_residences_collection = db.jabama_residences


session = requests.Session()

session.headers.update({
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, zstd",
    "Content-Type": "application/json",
    "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
    "Content-Length": "60",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
})

types = ['villas', 'cottage', 'ecotourism', 'pool', 'coastal', 'apartment']

for item_type in types:
    page = 1
    while True:
        try:
            respnose = session.post(
                f"https://gw.jabama.com/api/v4/keyword/all-{item_type}?allowEmptyCity=true&hasUnitRoom=true&guarantees=false&platform=desktop",
                json={
                    "page-size": 16,
                    "page-number": page
                },
            )
            data = respnose.json()['result']
            page_break = (data['total'] // 16) + (data['total'] % 16 > 0)
            jabama_residences_collection.with_options(write_concern=WriteConcern(w=0)).insert_many(data['items'], ordered=False)

            if page >= page_break:
                break
            else:
                page += 1
        except Exception as err:
            print(err)