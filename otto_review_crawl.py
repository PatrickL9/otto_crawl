# -*- coding: UTF-8 -*-
#!/usr/bin/python3

"""
otto平台根据关键词搜索，查询前1页查询结果的星级、评论数和价格
@Author ：Patrick Lam
@Date ：2023-03-03
"""
import datetime
import os
import requests
import time
import pandas as pd
from lxml import etree
from xml.etree import ElementTree
from playwright.sync_api import Playwright, sync_playwright, expect
from util.logging_conf import logging
from util.setting import proxy_pool, main_url, headers


def parse_all_url(url_list):
    for ul in url_list:
        retry_cnt = 0
        while retry_cnt <= 3:
            retry_cnt += 1
            logging.info('解析搜索页面，url链接： ' + ul)
            proxies = {'http': proxy_pool.get_random_ip()}
            resp = requests.get(ul, headers=headers, proxies=proxies, timeout=5)
            text = resp.content.decode('utf-8')
            if 'Robot or human' in text:
                logging.info('遇到验证码，重试第{}次'.format(str(retry_cnt)))
            else:
                # 解析页面text
                # print(text)
                df_result = get_item_detail(ul, text)
                logging.info('解析完成，保存结果到CSV')
                save_to_csv(df_result)
                break
            # 防反爬，每次解析暂停5秒
            time.sleep(5)


def get_item_detail(url, h_text):
    # print(url)
    # print(h_text)
    # 定义一个dataframe，用于保存爬取结果
    df_result = pd.DataFrame(columns=('search_url', 'result_total', 'product_url', 'title',
                                      'stars', 'reviews', 'price'))

    html = etree.HTML(h_text)
    result_total = html.xpath('//span[@class="reptile_tilelist__itemCount"]/text()')
    print(result_total)
    product_lists = html.xpath('//section[@id="san_resultSection"]/article/ul[@class="find_tile__container"]/li')
    print('一共有{}个链接'.format(len(product_lists)))
    # print(product_lists)
    for pl in product_lists:
        title = pl.xpath('.//a[@class="find_tile__productLink"]/@title')
        product_url = pl.xpath('.//a[@class="find_tile__productLink"]/@href')
        price = pl.xpath('.//span[@class="find_tile__priceValue"]/text()')
        reivews = pl.xpath('.//span[@class="find_tile__ratingNumber"]/text()')
        stars = pl.xpath('.//span[@class="find_tile__ratingStars"]/svg')
        print(title)
        print(main_url + ''.join(product_url))
        print(reivews)
        print(price)
        # print(stars)
        start_point = 0
        for star in stars:
            star_text = ElementTree.tostring(star).decode('utf-8')
            # print(star_text)
            if 'filled' in star_text:
                start_point += 1
            if 'half' in star_text:
                start_point += 0.5
            if 'empty' in star_text:
                start_point += 0
        print(start_point)

        temp_dict = {
            'search_url': url,
            'result_total': result_total,
            'product_url': main_url + ''.join(product_url),
            'title': ''.join(title),
            'stars': start_point,
            'reviews': ''.join(reivews).replace('(', '').replace(')', ''),
            'price': ''.join(price)
        }
        # 把爬取结果插入到dataframe最后一行
        df_result.loc[len(df_result)] = temp_dict
    # 防反爬，暂停5秒
    logging.info('防反爬，暂停5秒')
    time.sleep(5)
    return df_result


def save_to_csv(df):
    """
    结果保存到csv
    :param df: 结果明细
    :return:
    """
    to_day = datetime.datetime.now()
    file_name = 'otto平台类目评论爬取结果_{}{:02}{:02}.csv'.format(to_day.year, to_day.month, to_day.day)
    file_path = os.path.join(os.getcwd(), file_name)
    df.to_csv(file_path, mode='a', index=False, sep=',')
    logging.info('保存结果到CSV文件，保存路径： ' + file_path)


def run(url_list):
    """
    程序运行本体
    :param url_list: 需爬取的目标链接
    :return:
    """
    # 构建代理池
    proxy_pool.get_ip_pool()
    # 开始爬取
    parse_all_url(url_list)
    logging.info('运行成功，退出程序')


def run1(playwright: Playwright, url_list) -> None:
    for ul in url_list:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        # if ''
        context.set_default_timeout(800000)
        page = context.new_page()
        page.goto(ul, wait_until="domcontentloaded")
        page.reload()
        time.sleep(3)
        for i in range(600):
            time.sleep(0.3)
            page.keyboard.press("ArrowDown")
        # 暂停1秒等待页面加载
        time.sleep(1)
        text = page.content()
        df_result = get_item_detail(ul, text)
        page.close()
        context.close()
        browser.close()
        time.sleep(0.9)
        logging.info('解析完成，保存结果到CSV')
        save_to_csv(df_result)
    logging.info('运行成功，退出程序')


if __name__ == '__main__':
    target_url = []
    # 从txt中读取目标asin
    with open('review_target.txt', 'r') as f:
        arr = f.readlines()
        for tg in arr:
            a = tg.strip()
            target_url.append(a)
    logging.info('读取目标txt完毕，一共有{}个链接需要爬取'.format(len(target_url)))

    with sync_playwright() as playwright:
        run1(playwright, target_url)

    # run(target_url)
