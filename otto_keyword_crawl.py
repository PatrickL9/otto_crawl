# -*- coding: UTF-8 -*-
#!/usr/bin/python3

"""
otto平台根据关键词搜索，查询前3页查询结果的详情页信息
@Author ：Patrick Lam
@Date ：2023-01-31
"""
import os
import random
import time
import requests
import pandas as pd
from lxml import etree
from util import logging_util

# 代理API
proxy_url = 'http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=460e34f07cf041899a22e79353081288&orderno=YZ2021112078186AsWJy&returnType=1&count=5'
ipPool = []
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

# 日志文件前缀
logging_path = os.getcwd() + '.log'
# 设置日志级别
logging = logging_util.LoggingUtil("INFO", logging_path).get_logging()


def get_ip_pool():
    """
    获取IP代理池
    :param
    :return:
    """
    logging.info('获取IP代理，搭建代理IP池')
    ips = requests.get(proxy_url)
    for ip in ips.text.split('\r\n'):
        if len(ip) > 8:
            ipPool.append('http://' + ip)


def get_random_ip():
    """
    获取随机代理IP
    :param
    :return:随机代理IP
    """
    ip = random.choice(ipPool)
    logging.info('获取随机代理IP: ' + ip)
    return ip


def get_all_url(url_r):
    """
    爬取初始url页面中所有的产品url
    :param url_r: 初始url
    :return:product_list: 所有产品url
    """
    product_list = []
    proxies = {'http': get_random_ip()}
    resp = requests.get(url_r, headers=headers, proxies=proxies, timeout=5)
    text = resp.content.decode('utf-8')
    # print(text)
    html = etree.HTML(text)
    if html.xpath('//li[@id="san_pageInfo"]/span/text()'):
        max_pages = html.xpath('//li[@id="san_pageInfo"]/span/text()')
        max_page = int(''.join(max_pages).split('von')[1].strip())
    else:
        max_page = 1
    product_urls = html.xpath('//*[@id="san_resultSection"]/article//a/@href')
    # 爬取首页所有产品url
    for pl in product_urls:
        product_list.append(main_url + pl)
    logging.info('爬取首页成功，获取目标url共' + str(len(product_urls)) + '个')

    # 翻页爬取其他页数所有产品url
    if max_page >= 2:
        for i in range(2, max_page + 1):
            # otto德国站页码是以72为单位递增
            url_r2 = url_r + '?l=gq&o=' + str(72*(i-1))
            proxies = {'http': get_random_ip()}
            resp = requests.get(url_r2, headers=headers, proxies=proxies, timeout=5)
            text = resp.content.decode('utf-8')
            # print(text)
            html = etree.HTML(text)
            product_urls = html.xpath('//*[@id="san_resultSection"]/article//a/@href')
            for pl in product_urls:
                product_list.append(main_url + pl)
            logging.info('爬取第' + str(i) + '页成功，获取目标url共' + str(len(product_urls)) + '个')
    return product_list


def get_product_detail(product_list):
    """
    获取产品url，爬取产品url中的产品信息
    :param product_list: 所有产品url的列表
    :return:df_result 详情页信息明细
    """

    # 构造一个datafrome用于存储结果数据
    df_result = pd.DataFrame(columns=('product_url', 'title', 'reviews', 'stars', 'price', 'brand', 'variant', 'ad_tag',
                               'catalog_full', 'seller', 'product_id', 'description'))
    for product_url in product_list:
        i = 0
        logging.info('开始解析产品详情页，解析url ' + product_url)
        while i <= 3:
            # noinspection PyBroadException
            try:
                proxies = {'http': get_random_ip()}
                resp = requests.get(product_url, headers=headers, proxies=proxies, timeout=5)
                if resp.status_code == 200:
                    text = resp.content.decode('utf-8')
                    # print(text)
                    html = etree.HTML(text)

                    # 标题
                    title = html.xpath('//*[@class="gridContainer mo-frame wrapper"] \
                                        /div[@class="pl_grid-lane pdp-content"]/div/div/div/h1[1]/text()')
                    # 品牌 取标题第一段
                    brand = ''.join(title).strip().split(' ')[0]
                    # 评论数
                    reviews = html.xpath('//div[@class="cr_aggregation"]/a/div/span[2]/text()')
                    # 星级
                    stars = html.xpath('//div[@class="cr_aggregation"]/a/div/span[1]/@content')
                    # 价格
                    if html.xpath('//div[@class="pdp_price__inner"]//div[@class="pdp_price__price pl_mt100"]/div/div \
                                        /span[@class="pl_headline300"]/text()'):
                        price = html.xpath('//div[@class="pdp_price__inner"]//div[@class="pdp_price__price pl_mt100"]/div/div \
                                        /span[@class="pl_headline300"]/text()')
                    elif html.xpath('//div[@class="pdp_price__inner"]//div[@class="pdp_price__price pl_mt100 pl_hidden"]/div/div \
                                        /span[@class="pl_headline300"]/text()'):
                        price = html.xpath('//div[@class="pdp_price__inner"]//div[@class="pdp_price__price pl_mt100 pl_hidden"] \
                                        /div/div/span[@class="pl_headline300"]/text()')
                    else:
                        price = html.xpath('//div[@class="pdp_price__inner"] \
                                        //div[@class="pdp_price__price pl_mt100 js_pdp_price__price"]/div/div \
                                        /span[@class="pl_headline300"]/text()')
                    # 变体
                    variant = []
                    if html.xpath('//div[@class="pdp_dimensions__values"]'):
                        variant = html.xpath('//div[@class="pdp_dimensions__values"]/div/input/@value')
                    # 类目路径
                    catalog_list = html.xpath('//div[@class="nav_grimm-breadcrumb-container__breadcrumb"]/ul/li/a/text()')
                    # 卖家形式
                    seller = html.xpath('//div[@class="pdp_seller"]/span/span/span/text()')
                    # 产品编码
                    product_id = html.xpath('//span[@itemprop="productID"]/text()')
                    # 产品描述
                    descriptions = html.xpath('//div[@class="pl_grid-col-12 pl_grid-col-lg-7 pl_grid-col-lg--fill-remaining-space-with-block-color"] \
                                            /div[contains(@class,"pl_block pl_block")]//text()')

                    # print(''.join(title).strip())
                    # print(brand)
                    # print(''.join(reviews).strip())
                    # print(''.join(stars).strip().replace('(', '').replace(')', ''))
                    # print(''.join(price).strip())
                    catalog_full = ''
                    for cata in catalog_list:
                        if cata == '…':
                            continue
                        catalog_full = catalog_full + '|' + cata
                    # print(catalog_full)
                    # print(''.join(seller).strip())
                    # print(''.join(product_id).strip())
                    description = ''
                    for d in descriptions:
                        if len(d.strip()) > 0:
                            description = description + '\n' + d.strip()
                    # print(description)

                    temp_dict = {
                        'product_url': product_url,
                        'title': ''.join(title).strip(),
                        'reviews': ''.join(reviews).strip(),
                        'stars': ''.join(stars).strip().replace('(', '').replace(')', ''),
                        'price': ''.join(price).strip(),
                        'brand': brand,
                        'variant': variant,
                        # 'ad_tag': ,
                        'catalog_full': catalog_full,
                        'seller': ''.join(seller).strip(),
                        'product_id': ''.join(product_id).strip(),
                        'description': description
                    }
                    # 把爬取结果插入到dataframe最后一行
                    df_result.loc[len(df_result)] = temp_dict
                    break
            except Exception:
                logging.error('页面解析失败，重新获取代理解析')
                i += 1
        # 涉及解析页面延迟3秒
        time.sleep(3)
    return df_result


def save_to_csv(df, key_word):
    """
    结果保存到csv
    :param df: 结果明细
    :param key_word: 查询的关键词
    :return:
    """
    file_name = 'otto平台' + key_word + '爬取结果.csv'
    file_path = os.path.join(os.getcwd(), file_name)
    df.to_csv(file_path, index=False, sep=',')
    logging.info('保存结果到CSV文件，保存路径： ' + file_path)


def run(url_f, key_word):
    """
    程序运行本体
    :param url_f: 网址前缀
    :param key_word: 查询的关键词
    :return:
    """
    get_ip_pool()
    logging.info('开始otto爬取。初始url: ' + url_f + key_word + ' 关键词： ' + key_word)
    df = get_product_detail(get_all_url(url_f + key_word))
    save_to_csv(df, key_word)
    # print(df)


if __name__ == '__main__':
    # 初始网页前缀
    url_front = 'https://www.otto.de/babys/ausstattung/kinderwagen/'
    # 搜索关键词
    ky = 'Geschwisterwagen'
    # 传入网址和关键词，开始爬取
    run(url_front, ky)
