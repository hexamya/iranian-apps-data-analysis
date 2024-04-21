import json
import time
import requests


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

vendors = []
page = 0
while True:
    try:
        respnose = session.get(
            f"https://snappfood.ir/search/api/v1/desktop/vendors-list",
            params={
                "page": page,
                "page_size": 10000,
                "sp_alias": "restaurant",
                "city_name": "Tehran",
            }
        )
        data = respnose.json()['data']
        page_break = data ['count'] // 10000 + 1
        vendors += list(map(lambda item: item['data'], data['finalResult']))

        # if page >= page_break:
        break
        # else:
        #     page += 1
        #     time.sleep(1)
    except Exception as err:
        print(err)

with open(f"snappfoodVendors{int(time.time())}.json", "w", encoding="utf-8") as fp:
    json.dump(vendors, fp, ensure_ascii=False, indent=4)

print(len(vendors))

full_vendors = []
products = []
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
        full_vendors.append(data['vendor'])
        products += [i | {'vendorCode': vendor['code']} for j in data['menus'] for i in j['products']]
    except Exception as err:
        print(err)
        time.sleep(1)

with open(f"snappfoodProducts{int(time.time())}.json", "w", encoding="utf-8") as fp:
    json.dump(products, fp, ensure_ascii=False, indent=4)

with open(f"snappfoodFullVendors{int(time.time())}.json", "w", encoding="utf-8") as fp:
    json.dump(full_vendors, fp, ensure_ascii=False, indent=4)