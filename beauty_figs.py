# -*- encoding: utf-8 -*-
# @Version : 2.0
# @time: 2020年4月24日16:24:50

import os
import re
import time
import random

import requests
from bs4 import BeautifulSoup as bb
from multiprocessing import Pool
from tqdm import tqdm
from fake_useragent import UserAgent
from daili import find_proxy


def get_response(target_url, useproxy=False, retry_counter=0):
    """
    :param target_url:
    :param useproxy:
    :param retry_counter: 最大重试次数，0意味着在初始不用代理情况下，如果连接不成功，不会使用代理重试
    :return:
    """
    headers = {'User-Agent': UserAgent(verify_ssl=False).chrome}
    while -1 < retry_counter < 100:
        if useproxy:
            try:
                proxy_dict = find_proxy()
                response = requests.get(target_url, headers=headers, proxies=proxy_dict, timeout=30)
                response.raise_for_status()
                return response
            except requests.HTTPError:
                retry_counter -= 1
                get_response(target_url, useproxy=True, retry_counter=retry_counter)
        else:
            try:
                response = requests.get(target_url, headers=headers)
                response.raise_for_status()
                return response
            except requests.HTTPError:
                retry_counter -= 1
                get_response(target_url, useproxy=True, retry_counter=retry_counter)


main_domain = "https://qqk19.com"


def bianli_pages(offset, fig_type=5):
    fig_type_map = {
        5: "luyilu",
        7: "feilin",
        14: "xiurenwang",  # 秀人网
        2: "zhaifuli",  # 宅福利
        12: "MiiTao",  # 蜜桃社
    }
    global FIG_BASE
    FIG_BASE = os.path.join(os.getcwd(), fig_type_map[fig_type])
    if not os.path.exists(FIG_BASE):
        os.makedirs(FIG_BASE)
    index_page = f"{main_domain}/{fig_type_map[fig_type]}/list_{fig_type}_{offset}.html"  # 引导页
    # url_reponse = requests.get(index_page, headers=headers)
    url_reponse = get_response(index_page, useproxy=False, retry_counter=2)
    if url_reponse.url == f"{main_domain}/cip.asp":
        print(url_reponse.url)
    else:
        with open(os.path.join(FIG_BASE, "nav_index_urls.txt"), 'a') as f:
            f.write(f"{index_page} \n")
        get_nav_links(index_page)
        time.sleep(random.randint(1, 3))


def get_nav_links(index_url):
    # 从引导页获得该页面中的所有相册链接
    # html = requests.get(index_url, headers=headers)
    html = get_response(index_url, useproxy=False, retry_counter=2)
    html.encoding = 'gbk'
    soup = bb(html.text, 'lxml')
    neirong = soup.find_all('h2')
    print(neirong)
    with open(os.path.join(FIG_BASE, "page_urls.txt"), 'a') as f:
        for i in neirong:
            print(i.a.get("href"), i.text)
            link = f"{main_domain}/" + i.a.get("href")
            f.write(f"{link}  {i.text} \n")
            get_figs(link)


def get_figs(page_url):
    for page_i in range(1, 26):
        if page_i == 1:
            multi_page = page_url
        else:
            multi_page = "{}_{}.html".format(page_url.split(".html")[0], page_i)
        page = get_response(multi_page, useproxy=False, retry_counter=10)
        if page.url == f"{main_domain}/cip.asp":
            break
        page.encoding = 'gbk'
        soup = bb(page.text, 'lxml')
        dir_name = soup.title.text.split("P]")[0]
        dir_name = re.sub(r'[/:*?"<>|]', '-', dir_name)  # 验证是否包含不合法字符，并替换
        xiangce_dir = os.path.join(FIG_BASE, dir_name)
        if not os.path.exists(xiangce_dir):
            os.mkdir(xiangce_dir)
        neirong = soup.find_all('p')
        with open(os.path.join(xiangce_dir, "fig_urls.txt"), 'a') as f:
            for i in tqdm(neirong):
                # tqdm 来展示当前页面下载进度
                try:
                    # print(i.img.get("src"))
                    fig_url = i.img.get("src")
                    # 增加判断本地文件是否存在，存在则跳过
                    fig_path = os.path.join(xiangce_dir, f'{fig_url.split("/")[-1]}')
                    if os.path.exists(fig_path):
                        continue
                    else:
                        with open(fig_path, 'wb') as fig_f:
                            fig_f.write(get_response(fig_url, useproxy=False, retry_counter=3).content)
                        f.write(f"{fig_url} \n")
                except requests.Timeout:
                    continue
                except AttributeError:
                    # 第一个p标签存着人物介绍
                    with open(os.path.join(xiangce_dir, "profile.txt"), "a", encoding="utf-8") as profile_f:
                        profile_f.writelines(i.text)
                    continue


if __name__ == '__main__':
    pool = Pool()
    pool.starmap(bianli_pages, zip(range(1, 4), [5, 7, 14, 2, 12]))
