import requests
import pandas as pd
from lxml import etree

url = 'https://www.otto.de/p/ergobaby-babytrage-embrace-heather-grey-ergonomische-bauchtrage-fuer-neugeborene-CS01090RC/#variationId=S01090RC2CS1'
headers = {
    'authority': 'www.otto.de',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng, \
                */*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'max-age=0',
    # 'referer': 'https://www.otto.de/suche/Wandladeger%C3%A4t/',
    'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Microsoft Edge";v="104"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)  \
                Chrome/109.0.0.0 Safari/537.36',
}

resp = requests.get(url, headers=headers)
text = resp.content.decode('utf-8')
# print(text)
html = etree.HTML(text)
price = html.xpath('//div[@class="pdp_price__inner"]//div[@class="pdp_price__price pl_mt100"]/div/div \
                            /span[@class="pl_headline300"]/text()')
price1 = html.xpath('//div[@class="pdp_price__inner"]//div[@class="pdp_price__price pl_mt100 js_pdp_price__price"]/div/div \
                            /span[@class="pl_headline300"]/text()')
stars = html.xpath('//div[@class="cr_aggregation"]/a/div/span[1]/@content')
reviews = html.xpath('//div[@class="cr_aggregation"]/a/div/span[2]/text()')
variant = html.xpath('//div[@class="pdp_dimensions__values"]/div/input/@value')
descriptions = html.xpath('//div[@class="pl_grid-col-12 pl_grid-col-lg-7 pl_grid-col-lg--fill-remaining-space-with-block-color"] \
                                /div[contains(@class,"pl_block pl_block")]//text()')
print(''.join(reviews).strip())
print(variant)
print(price)
print(price1)
# description = ''
# for d in descriptions:
#     if len(d.strip()) > 0:
#         description = description + '\n' + d.strip()
# print(description)
