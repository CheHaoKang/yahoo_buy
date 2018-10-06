# -*- coding: UTF-8 -*-

'''For the test purpose, unmark lines with '# for test' and mark '# formal'
new-stcok-fetching policy
1. run 'get_stockCodes.py'
2. accumulate new stocks and put them into stockCodes of stockClassInstance.py
3. run 'stockClassInstance.py retrieveStockData' with the parameter "" (python3 /home/pi/Python/pythonStockEvaluation/stockClassInstance.py retrieveStockData "")
4. run 'stockClassInstance.py computeStockKD' with the parameter "" (python3 /home/pi/Python/pythonStockEvaluation/stockClassInstance.py computeStockKD "")
'''

class YahooBuy(object):
    """This class is for retrieving stock-related data

    Attributes:
        timeout: webpage-fetching timeout
        threadAmount: thread number
    """

    def __init__(self):
        self.timeout = 10
        # self._renew_categories('https://tw.buy.yahoo.com/')
        self._fetch_categories()
        # self._get_item_description('https://tw.buy.yahoo.com/gdsale/AISURE-For-iPad-2018%E7%89%88-9-7-7810929.html')

    def _fetch_categories(self):
        results = self._select_update_from_db("SELECT category_name,sub_category_name FROM categories ORDER BY sno ASC")
        if results!='fetch_db_error':
            self._fetch_page_by_categories(results)
        else:
            print('Fetching database fails. Please check the log...')
            exit(1)

    def _fetch_page_by_categories(self, categories):
        for one_category in categories:
            web_url = 'https://tw.search.buy.yahoo.com/search/shopping/product?cid=0&cid_path=&clv=0&p=' + one_category[0] + '&qt=product&sort=-sales'
            res_text = self._fetch_web_page(web_url, proxy=True)

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(res_text, 'html.parser')
            item_list = soup.select('div[class*=ResultList__mainItemList] ul.gridList > li')
            for one_item in item_list:
                soup = BeautifulSoup(str(one_item), 'html.parser')

                try:
                    # print(soup.select('a[href]')[0]['href'])
                    # print(soup.select('span[class*=BaseGridItem__title]')[0].text)
                    # print(soup.select('[class*=BaseGridItem__price]')[0].text)
                    item_title = soup.select('span[class*=BaseGridItem__title]')[0].text

                    if soup.select('[class*=BaseGridItem__price] > em'):
                        item_price = soup.select('[class*=BaseGridItem__price] > em')[0].text
                    else:
                        item_price = soup.select('[class*=BaseGridItem__price]')[0].text

                    item_url = soup.select('a[href]')[0]['href']
                    item_info = self._get_item_description(item_url)

                    print(item_title)
                    print(item_price)
                    print(item_info)

                    return_code = self._insert_into_db({'category':one_category[0], 'item_title':item_title, 'item_price':item_price, 'item_info':item_info, 'item_url':item_url}, 'item_information')
                    if return_code=='insert_db_error':
                        print('Insertion fails. Please see the log...')

                    print('-------------------')
                except:
                    import traceback
                    traceback.print_exc()

            # category_tags = soup.find_all(class_="catRow yui3-g")
            # for one_tag in category_tags:
            #     soup = BeautifulSoup(str(one_tag), 'html.parser')
            #     tag_head = soup.select('.catLevel2.yui3-u > a[class*="highlight"]')
            #     tag_body = soup.select('.catLevel3.yui3-u > a[class*="highlight"]')
            #
            #     try:
            #         tag_head_text = tag_head[0].text
            #         tag_body_list = []
            #         for one_body in tag_body:
            #             tag_body_list.append(one_body.text)
            #
            #         self._insert_into_db({'category_name': tag_head_text, 'sub_category_name': ','.join(tag_body_list)},
            #                              'categories')
            #     except:
            #         import traceback
            #         traceback.print_exc()

            # exit(1)

    def _get_item_description(self, desc_url):
        res_text = self._fetch_web_page(desc_url, proxy=True)

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res_text, 'html.parser')
        desc_list = soup.select('li.desc.yui3-u-1')
        desc_return_list = []
        for one_desc in desc_list:
            # print(one_desc.text)
            desc_return_list.append(one_desc.text)

        return ';;;'.join(desc_return_list)

    def _fetch_web_page(self, web_url, proxy=False):
        import requests
        from time import sleep
        from fake_useragent import UserAgent
        ua = UserAgent()
        # header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}
        header = {'User-Agent': str(ua.random)}

        if proxy:
            now_proxy = self._get_proxy()
            proxies = {"http": "http://" + now_proxy}

        while True:
            try:
                if proxy:
                    import time
                    start = time.time()
                    res = requests.get(web_url, headers=header, proxies=proxies, timeout=10)
                    end = time.time()
                else:
                    res = requests.get(web_url, headers=header, timeout=10)

                if 'yahooLogo' not in res.text and 'ylogo' not in res.text:
                    print('Unvalid. Trying...')

                    if proxy:
                        self._update_proxy_info(now_proxy, False, 0)
                        now_proxy = self._get_proxy()
                        proxies = {"http": "http://" + now_proxy}

                    sleep(1)
                    continue
                else:
                    print('Fetching succeeds...')
                    print(web_url)

                    if proxy:
                        self._update_proxy_info(now_proxy, True, end-start)
                    res_text = res.text.replace('<!--', '').replace('-->', '')  # Since category items are commented, we need to uncomment it in order to find them

                    break
                    # with open('yahoo_buy.txt', 'w', encoding="utf-8") as the_file:
                    #     the_file.write(res.text)
                    # print(res.text)
                    # with open('yahoo_buy.txt', 'r', encoding="utf-8") as the_file:
                    #     res_text = the_file.read()
                    #     res_text = res_text.replace('<!--', '').replace('-->', '')  # Since category items are commented, we need to uncomment it in order to find them
            except:
                import traceback
                traceback.print_exc()

                if proxy:
                    self._update_proxy_info(now_proxy, False, 0)
                    now_proxy = self._get_proxy()
                    proxies = {"http": "http://" + now_proxy}

                sleep(1)
                continue

        return res_text

    def _get_proxy(self):
        import random
        import time
        random.seed(time.time())
        offset = random.randint(0, 50)  # prevent using the same proxy all the time
        sql = """SELECT proxyIPPort FROM (SELECT sno, proxyIPPort, proxyAvgReponseperiod, proxyUsedTimes, proxyFailtimes*proxyAvgReponseperiod AS formula FROM proxies)
                    AS proxyFormula WHERE proxyAvgReponseperiod<%s ORDER BY formula ASC, sno ASC LIMIT 1 OFFSET %s"""

        results = self._select_update_from_db(sql, (self.timeout, offset))
        return results[0][0]

    def _update_proxy_info(self, proxy, succeedOrFail, executionTime):
        sql = """UPDATE proxies
                             SET proxyAvgReponseperiod=(proxyAvgReponseperiod*proxyUsedTimes+%s)/(proxyUsedTimes+1),
             	                proxyUsedTimes=proxyUsedTimes+1,
             	                proxyFailtimes=proxyFailtimes+%s
                             WHERE proxyIPPort=%s"""
        self._select_update_from_db(sql, (executionTime if succeedOrFail else (executionTime + 10), 0 if succeedOrFail else 1, proxy))  # 10 is for penalty when failing

    def _renew_categories(self, category_page):
        res_text = self._fetch_web_page(category_page)

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res_text, 'html.parser')
        category_tags = soup.find_all(class_="catRow yui3-g")
        for one_tag in category_tags:
            soup = BeautifulSoup(str(one_tag), 'html.parser')
            tag_head = soup.select('.catLevel2.yui3-u > a[class*="highlight"]')
            tag_body = soup.select('.catLevel3.yui3-u > a[class*="highlight"]')

            try:
                tag_head_text = tag_head[0].text
                tag_body_list = []
                for one_body in tag_body:
                    tag_body_list.append(one_body.text)

                return_code = self._insert_into_db({'category_name':tag_head_text, 'sub_category_name':','.join(tag_body_list)}, 'categories')
                if return_code == 'insert_db_error':
                    print('Insertion fails. Please see the log...')
            except:
                import traceback
                traceback.print_exc()

    def _get_db_info(self):
        import os
        with open(str(os.getcwd()) + '/yahoo_buy_db.json', encoding='utf-8') as f:
            import json
            db_data = json.load(f)

        return db_data

    def _select_update_from_db(self, sql, parameters=''):
        from time import sleep

        db_data = self._get_db_info()
        conn = None
        cur = None
        retry_limit = 5
        count = 0
        while count < retry_limit:
            try:
                import pymysql
                conn = pymysql.connect(host=db_data['to_db']['host'],
                                       port=db_data['to_db']['port'],
                                       user=db_data['to_db']['user'],
                                       passwd=db_data['to_db']['pass'],
                                       db=db_data['to_db']['name'],
                                       charset=db_data['to_db']['charset'])
                cur = conn.cursor()
                if parameters:
                    cur.execute(sql, parameters)
                else:
                    cur.execute(sql)

                results = cur.fetchall()
                # for row in results:
                #     print(row)

                conn.commit()
                break
            except:
                import traceback
                traceback.print_exc()

                print('Fetching database fails. Trying...')
                count += 1
                sleep(1)

        cur.close()
        conn.close()

        if count >= retry_limit:
            return 'fetch_db_error'
        else:
            return results

    def _insert_into_db(self, insert_data, table_name):
        from time import sleep
        db_data = self._get_db_info()

        columns = []
        values = []
        for key, value in insert_data.items():
            columns.append(key)
            values.append(value)

        percent_s = ['%s' for _ in range(len(columns))]

        conn = None
        cur = None
        retry_limit = 5
        count = 0
        while count < retry_limit:
            try:
                import pymysql
                conn = pymysql.connect(host=db_data['to_db']['host'],
                                       port=db_data['to_db']['port'],
                                       user=db_data['to_db']['user'],
                                       passwd=db_data['to_db']['pass'],
                                       db=db_data['to_db']['name'],
                                       charset=db_data['to_db']['charset'])
                cur = conn.cursor()
                insert = "INSERT IGNORE INTO " + table_name +" (" + ",".join(columns) + ") VALUES (" + ','.join(percent_s) + ")"
                print(insert_data)
                cur.execute(insert, tuple(values))

                conn.commit()
                break
            except:
                import traceback
                traceback.print_exc()

                print('Inserting data into database fails. Trying...')
                count += 1
                sleep(1)

        cur.close()
        conn.close()

        if count >= retry_limit:
            return 'insert_db_error'

    @staticmethod
    def dummy():
        pass

if __name__ == "__main__":
    yahoo_buy_instance = YahooBuy()