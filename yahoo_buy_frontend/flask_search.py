import sys, os
sys.path.append('.')

from flask import Flask, render_template
#  引入form類別
from search_form import SearchForm
from flask import request

app = Flask(__name__)

def _get_db_info():
    import os
    with open(str(os.getcwd()) + '/yahoo_buy_db.json', encoding='utf-8') as f:
        import json
        db_data = json.load(f)

    return db_data

def _select_update_from_db(sql, parameters=''):
    from time import sleep

    db_data = _get_db_info()
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

def _get_data_from_db(query_text):
    sql = "SELECT category,item_title,item_price,item_info,item_url FROM item_information WHERE CONCAT(category, item_title, item_info) LIKE '%" + query_text + "%'"
    results = _select_update_from_db(sql)
    return results

@app.route('/', methods=['GET', 'POST'])
def yahoo_buy_search():
    form = SearchForm()
    #  flask_wtf類中提供判斷是否表單提交過來的method，不需要自行利用request.method來做判斷
    if form.validate_on_submit():
        return render_template('yahoo_buy_search.html', form=form, result_div=_get_data_from_db(form.input_question.data))
    #  如果不是提交過來的表單，就是GET，這時候就回傳yahoo_buy_search.html網頁
    return render_template('yahoo_buy_search.html', form=form)

if __name__ == '__main__':
    app.debug = True
    app.config['SECRET_KEY'] = 'your key values'
    app.run(host='0.0.0.0')