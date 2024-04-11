import json
import time
import requests


session = requests.Session()

session.headers.update({
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, zstd",
    "Content-Type": "application/json",
    "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
    "Content-Length": "60",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
})

pre_response = session.get(
    "https://account.jobvision.ir/.well-known/openid-configuration",
    timeout=10
)

session.headers.update(pre_response.request.headers)

items = []
page = 0
while True:
    try:
        respnose = session.post(
            "https://candidateapi.jobvision.ir/api/v1/JobPost/List",
            data=f'{{"pageSize": 30,"requestedPage": {page},"sortBy": 1,"searchId": null}}',
        )
        data = respnose.json()['data']
        page_break = data['jobPostCount'] // 30 + 1
        items += data['jobPosts']

        if page > page_break:
            break
        else:
            page += 1
            time.sleep(1)
    except Exception as err:
        print(err)

with open(f"rawdata/jobvision{int(time.time())}.json", "w", encoding="utf-8") as fp:
    json.dump(items, fp, ensure_ascii=False, indent=4)