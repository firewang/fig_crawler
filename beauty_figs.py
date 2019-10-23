# -*- encoding: utf-8 -*-
# @Version : 1.0
# @time: 2019年10月22日21:47:19

import os
import sys

import requests
from bs4 import BeautifulSoup as bb
import urllib
import time
import random
import socket
from multiprocessing import Pool

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}


def bianli_pages(offset):
    index_page = f"https://qqh225.com/luyilu/list_5_{offset}.html"  # 引导页
    url_reponse = requests.get(index_page, headers=headers)
    if url_reponse.url == "https://qqi668.com/cip.asp":
        print(url_reponse.url)
    else:
        with open("nav_index_urls.txt", 'a') as f:
            f.write(index_page)
            f.write("\r\n")
        get_nav_links(index_page)
        time.sleep(random.randint(1, 9))


def get_nav_links(index_url):
    # 从引导页获得该页面中的所有相册链接
    html = requests.get(index_url, headers=headers)
    html.encoding = 'gbk'
    soup = bb(html.text, 'lxml')
    neirong = soup.find_all('h2')
    print(neirong)
    with open("page_urls.txt", 'a') as f:
        for i in neirong:
            print(i.a.get("href"), i.text)
            link = "https://qqh225.com/" + i.a.get("href")
            f.write(f"{link}  {i.text} \n")
            get_figs(link)


def progress(blocknum, blocksize, totalsize):
    """
    https://blog.csdn.net/pursuit_zhangyu/article/details/80556275
    blocknum:当前的块编号
    blocksize:每次传输的块大小
    totalsize:网页文件总大小
    """
    sys.stdout.write('\r>> Downloading %.1f%%' % (float(blocknum * blocksize) / float(totalsize) * 100.0))
    sys.stdout.flush()


def get_figs(page_url):
    for page_i in range(1, 26):
        if page_i == 1:
            multi_page = page_url
        else:
            multi_page = "{}_{}.html".format(page_url.split(".html")[0], page_i)
        page = requests.get(multi_page, headers=headers)
        page.encoding = 'gbk'
        soup = bb(page.text, 'lxml')
        dir_name = soup.title.text.split("P]")[0]
        if page.url == "https://qqi668.com/cip.asp":
            break
        xiangce_dir = os.path.join(os.getcwd(), dir_name)
        if not os.path.exists(xiangce_dir):
            os.mkdir(xiangce_dir)
        neirong = soup.find_all('p')
        # print(neirong)
        with open(os.path.join(xiangce_dir, "fig_urls.txt"), 'a') as f:
            for i in neirong:
                try:
                    print(i.img.get("src"))
                    fig_url = i.img.get("src")
                    # 增加判断本地文件是否存在，存在则跳过
                    fig_path = os.path.join(xiangce_dir, f'{fig_url.split("/")[-1]}')
                    if os.path.exists(fig_path):
                        continue
                    else:
                        socket.setdefaulttimeout(300)
                        opener = urllib.request.build_opener()
                        opener.addheaders = [('User-Agent',
                                              'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
                        urllib.request.install_opener(opener)
                        urllib.request.urlretrieve(fig_url, fig_path, progress)
                        f.write(fig_url)
                        f.write("\r\n")
                except:
                    continue


if __name__ == '__main__':
    pool = Pool()
    pool.map(bianli_pages, range(1, 230))
