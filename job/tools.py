# -*- coding: utf-8 -*-
# @Time: 2023-1-29 9:01
# @File: tools.py
# @IDE: PyCharm

import time
from lxml import etree
from multiprocessing.dummy import Pool
import pymysql

import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 指定 chromedriver 的路径
driver_path = os.path.join(current_dir, 'chromedriver.exe')


# 猎聘网爬虫
def lieSpider(key_word, city, all_page):
    city_dict = {'全国': '410', '北京': '010', '上海': '020', '天津': '030', '重庆': '040', '广州': '050020',
                 '深圳': '050090',
                 '苏州': '060080', '南京': '060020', '杭州': '070020', '大连': '210040', '成都': '280020',
                 '武汉': '170020',
                 '西安': '270020'}
    urls_list = get_urls(key_word, all_page, city_dict[city])
    pool = Pool(1)
    pool.map(get_pages, urls_list)
    return 0


def get_urls(key_word, all_page, city_code):
    urls_list = []
    for i in range(0, int(all_page)):
        url = 'https://www.liepin.com/zhaopin/?city={}&dq={}&currentPage={}&pageSize=40&key={}'.format(city_code,
                                                                                                       city_code, i,
                                                                                                       key_word)
        urls_list.append(url)
    return urls_list


def get_city():
    print('开始抓取城市列表...')
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    city_url = 'https://www.liepin.com/zhaopin/?inputFrom=head_navigation&scene=init&workYearCode=0&ckId=ayvlgrooqq8e4w2b3yoae69sd91dmbq9'
    driver.get(city_url)
    time.sleep(3)
    req_html = etree.HTML(driver.page_source)
    code_list = req_html.xpath('//li[@data-key="dq"]/@data-code')
    name_list = req_html.xpath('//li[@data-key="dq"]/@data-name')
    city_list = [[name_list[x], code_list[x]] for x in range(len(name_list))]
    print('抓取到的城市列表:', city_list)
    return city_list


def get_pages(url):
    mysql_conn = get_mysql()
    conn = mysql_conn[0]
    cur = mysql_conn[1]
    print('开始爬取 {}...'.format(url))
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)
    time.sleep(3)
    req_html = etree.HTML(driver.page_source)
    job = req_html
    name = job.xpath('//div[@class="jsx-2387891236 ellipsis-1"]/text()')
    salary = job.xpath('//span[@class="jsx-2387891236 job-salary"]/text()')
    address = job.xpath('//span[@class="jsx-2387891236 ellipsis-1"]/text()')
    education = job.xpath('//div[@class="jsx-2387891236 job-labels-box"]/span[2]/text()')
    experience = job.xpath('//div[@class="jsx-2387891236 job-labels-box"]/span[1]/text()')
    com_name = job.xpath('//span[@class="jsx-2387891236 company-name ellipsis-1"]/text()')
    tag_list = job.xpath('//div[@class="jsx-2387891236 company-tags-box ellipsis-1"]')
    label_list = []
    scale_list = []
    for tag in tag_list:
        span_list = tag.xpath('./span/text()')
        label_list.append(span_list[0])
        scale_list.append(span_list[-1])
    href_list = job.xpath('//a[@data-nick="job-detail-job-info"]/@href')
    href_list = [x.split('?')[0] for x in href_list]
    if len(name) == len(salary) == len(address) == len(education) == len(experience) == len(com_name) == len(
            label_list) == len(scale_list) == len(href_list):
        for i in range(0, len(name)):
            select_sql = '''SELECT href FROM job_data'''
            cur.execute(select_sql)
            href_list_mysql = cur.fetchall()
            href_list_mysql = [x[0] for x in href_list_mysql]
            if href_list[i] not in href_list_mysql:
                insert_sql = '''INSERT INTO job_data(name,salary,place,education,experience,company,label,scale,href,key_word) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                list_1 = [name[i], salary[i], address[i], education[i], experience[i], com_name[i], label_list[i],
                          scale_list[i], href_list[i], url.split('=')[-1]]
                print(list_1)
                try:
                    cur.execute(insert_sql, list_1)
                except Exception as e:
                    print(e)
                    conn.rollback()
    else:
        print('爬取数据有误，开始下一页...')
    time.sleep(3)
    cur.close()
    conn.close()
    driver.quit()


# 前程无忧爬虫
def Spider51job(key_word, city, all_page):
    city_dict = {
        '全国': '000000', '北京': '010000', '上海': '020000', '广州': '030200', '深圳': '040000',
        '天津': '050000', '重庆': '060000', '杭州': '080200', '南京': '070200', '苏州': '070300',
        '武汉': '180200', '成都': '200200', '西安': '230200', '大连': '210200'
    }
    urls_list = []
    for i in range(1, int(all_page) + 1):
        url = f'https://search.51job.com/list/{city_dict[city]},000000,0000,00,9,99,{key_word},2,{i}.html'
        urls_list.append(url)
    pool = Pool(1)
    pool.map(get_51job_pages, urls_list)
    return 0


def get_51job_pages(url):
    mysql_conn = get_mysql()
    conn = mysql_conn[0]
    cur = mysql_conn[1]
    print('开始爬取 {}...'.format(url))
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)
    time.sleep(3)
    req_html = etree.HTML(driver.page_source)
    job_nodes = req_html.xpath('//div[@id="resultList"]/div[@class="el"]')
    for job in job_nodes:
        name = job.xpath('./p/span/a/@title')
        if not name:
            continue
        name = name[0]
        salary = job.xpath('./span[@class="t4"]/text()')
        salary = salary[0] if salary else ''
        address = job.xpath('./span[@class="t3"]/text()')
        address = address[0] if address else ''
        education = ''
        experience = ''
        com_name = job.xpath('./span[@class="t2"]/a/@title')
        com_name = com_name[0] if com_name else ''
        label = ''
        scale = ''
        href = job.xpath('./p/span/a/@href')
        href = href[0] if href else ''

        select_sql = '''SELECT href FROM job_data'''
        cur.execute(select_sql)
        href_list_mysql = cur.fetchall()
        href_list_mysql = [x[0] for x in href_list_mysql]
        if href not in href_list_mysql:
            insert_sql = '''INSERT INTO job_data(name,salary,place,education,experience,company,label,scale,href,key_word) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            list_1 = [name, salary, address, education, experience, com_name, label, scale, href, url.split(',')[-2]]
            print(list_1)
            try:
                cur.execute(insert_sql, list_1)
            except Exception as e:
                print(e)
                conn.rollback()
    time.sleep(3)
    cur.close()
    conn.close()
    driver.quit()


# 智联招聘爬虫
def zhilianSpider(key_word, city, all_page):
    city_dict = {
        '全国': '全国', '北京': '北京', '上海': '上海', '广州': '广州', '深圳': '深圳',
        '天津': '天津', '重庆': '重庆', '杭州': '杭州', '南京': '南京', '苏州': '苏州',
        '武汉': '武汉', '成都': '成都', '西安': '西安', '大连': '大连'
    }
    urls_list = []
    for i in range(1, int(all_page) + 1):
        url = f'https://sou.zhaopin.com/?jl={city_dict[city]}&kw={key_word}&p={i}'
        urls_list.append(url)
    pool = Pool(1)
    pool.map(get_zhilian_pages, urls_list)
    return 0


def get_zhilian_pages(url):
    mysql_conn = get_mysql()
    conn = mysql_conn[0]
    cur = mysql_conn[1]
    print('开始爬取 {}...'.format(url))
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)
    time.sleep(3)
    req_html = etree.HTML(driver.page_source)
    job_nodes = req_html.xpath('//div[@class="joblist-box__item"]')
    for job in job_nodes:
        name = job.xpath('.//span[@class="jobname__title"]/@title')
        if not name:
            continue
        name = name[0]
        salary = job.xpath('.//p[@class="jobinfo__salary"]/text()')
        salary = salary[0] if salary else ''
        address = job.xpath('.//span[@class="job-card-left__content"]/text()')
        address = address[0] if address else ''
        education = ''
        experience = ''
        com_name = job.xpath('.//a[@class="company__title"]/@title')
        com_name = com_name[0] if com_name else ''
        label = ''
        scale = ''
        href = job.xpath('.//a[@class="joblist-box__item-info"]/@href')
        href = href[0] if href else ''

        select_sql = '''SELECT href FROM job_data'''
        cur.execute(select_sql)
        href_list_mysql = cur.fetchall()
        href_list_mysql = [x[0] for x in href_list_mysql]
        if href not in href_list_mysql:
            insert_sql = '''INSERT INTO job_data(name,salary,place,education,experience,company,label,scale,href,key_word) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            list_1 = [name, salary, address, education, experience, com_name, label, scale, href, url.split('=')[-2]]
            print(list_1)
            try:
                cur.execute(insert_sql, list_1)
            except Exception as e:
                print(e)
                conn.rollback()
    time.sleep(3)
    cur.close()
    conn.close()
    driver.quit()


# 应届生求职网爬虫
def yingjieshengSpider(key_word, city, all_page):
    urls_list = []
    for i in range(1, int(all_page) + 1):
        url = f'https://www.yingjiesheng.com/search.php?keyword={key_word}&page={i}'
        if city != '全国':
            url += f'&city={city}'
        urls_list.append(url)
    pool = Pool(1)
    pool.map(get_yingjiesheng_pages, urls_list)
    return 0


def get_yingjiesheng_pages(url):
    mysql_conn = get_mysql()
    conn = mysql_conn[0]
    cur = mysql_conn[1]
    print('开始爬取 {}...'.format(url))
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)
    time.sleep(3)
    req_html = etree.HTML(driver.page_source)
    job_nodes = req_html.xpath('//div[@class="job-list"]/div[@class="job-item"]')
    for job in job_nodes:
        name = job.xpath('.//a[@class="job-name"]/text()')
        if not name:
            continue
        name = name[0].strip()
        salary = ''
        address = job.xpath('.//span[@class="job-location"]/text()')
        address = address[0].strip() if address else ''
        education = ''
        experience = ''
        com_name = job.xpath('.//a[@class="company-name"]/text()')
        com_name = com_name[0].strip() if com_name else ''
        label = ''
        scale = ''
        href = job.xpath('.//a[@class="job-name"]/@href')
        href = href[0] if href else ''

        select_sql = '''SELECT href FROM job_data'''
        cur.execute(select_sql)
        href_list_mysql = cur.fetchall()
        href_list_mysql = [x[0] for x in href_list_mysql]
        if href not in href_list_mysql:
            insert_sql = '''INSERT INTO job_data(name,salary,place,education,experience,company,label,scale,href,key_word) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            list_1 = [name, salary, address, education, experience, com_name, label, scale, href, url.split('=')[-2]]
            print(list_1)
            try:
                cur.execute(insert_sql, list_1)
            except Exception as e:
                print(e)
                conn.rollback()
    time.sleep(3)
    cur.close()
    conn.close()
    driver.quit()


def get_mysql():
    conn = pymysql.connect(host='localhost',
                           port=3306,
                           user='root',
                           passwd='123456',
                           database='recommend_job',
                           autocommit=True,
                           charset='utf8mb4')
    cur = conn.cursor()
    return conn, cur


def spider_engine_choice(engine_id, key_word, city, all_page):
    if engine_id == '猎聘网':
        lieSpider(key_word, city, all_page)
    elif engine_id == '前程无忧':
        Spider51job(key_word, city, all_page)
    elif engine_id == '智联招聘':
        zhilianSpider(key_word, city, all_page)
    elif engine_id == '应届生求职网':
        yingjieshengSpider(key_word, city, all_page)
    else:
        print("无效的引擎 ID，请输入 '猎聘网'、'前程无忧'、'智联招聘' 或 '应届生求职网'。")


if __name__ == '__main__':
    try:
        spider_engine_choice('猎聘网', 'java', '北京', '1')
    except ValueError:
        print("输入的内容有误，请检查。")

