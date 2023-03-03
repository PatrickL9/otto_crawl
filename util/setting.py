# -*- coding: UTF-8 -*-
#!/usr/bin/python3

"""
爬虫程序各项配置参数
@Author ：Patrick Lam
@Date ：2023-02-10
"""

from util import proxy_pool


# 代理API
PROXY_URL = 'http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=460e34f07cf041899a22e79353081288&orderno=YZ2021112078186AsWJy&returnType=1&count=1'
# ipPool = []
# 设置ip代理池
proxy_pool = proxy_pool.ProxyPool(PROXY_URL)

# 主站点链接
main_url = 'https://www.otto.de'
# 请求头
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


