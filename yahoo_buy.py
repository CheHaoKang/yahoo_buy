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
        pass
        # self._renew_categories('https://tw.buy.yahoo.com/')

    

    def _renew_categories(self, category_page):
        import requests
        from time import sleep
        from fake_useragent import UserAgent
        ua = UserAgent()
        # header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}
        header = {'User-Agent': str(ua.random)}

        while True:
            try:
                res = requests.get(category_page, headers=header, timeout=10)  # , proxies=proxies, timeout=self.timeout)
                if 'yahooLogo' not in res.text:
                    print('Unvalid. Trying...')
                    sleep(1)
                else:
                    print('Fetching succeeds...')
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
                sleep(1)

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

                self._insert_into_db({'category_name':tag_head_text, 'sub_category_name':','.join(tag_body_list)}, 'categories')
            except:
                import traceback
                traceback.print_exc()

    def _insert_into_db(self, insert_data, table_name):
        import os
        with open(str(os.getcwd()) + '/yahoo_buy_db.json', encoding='utf-8') as f:
            import json
            db_data = json.load(f)

        columns = []
        values = []
        for key, value in insert_data.items():
            columns.append(key)
            values.append(value)

        percent_s = ['%s' for _ in range(len(columns))]

        conn = None
        cur = None
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

            cur.close()
            conn.commit()
            conn.close()
        except:
            import traceback
            traceback.print_exc()
            cur.close()
            conn.close()

    @staticmethod
    def make_car_sound():
        pass

if __name__ == "__main__":
    yahoo_buy_instance = YahooBuy()