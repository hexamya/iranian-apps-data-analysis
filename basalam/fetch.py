import json
import time
import requests


session = requests.Session()

# session.headers.update({
#     "Accept": "application/json, text/plain, */*",
#     "Accept-Encoding": "gzip, deflate, zstd",
#     "Content-Type": "application/json",
#     "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
#     "Content-Length": "60",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
# })

items = []
for cat in range(1,13):
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
            items += products

            if not products:
                break
        except Exception as err:
            print(err)
            print(len(items))

with open(f"rawData/basalam{int(time.time())}.json", "w", encoding="utf-8") as fp:
    json.dump(items, fp, ensure_ascii=False, indent=4)