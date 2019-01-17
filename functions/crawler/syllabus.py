from selenium import webdriver
from bs4 import BeautifulSoup

from time import sleep
from datetime import datetime
import json
import re
import codecs


HEADLESS = True

BASE_URL = 'http://syllabus.center.wakayama-u.ac.jp/ext_syllabus'
START_URL = BASE_URL + '/syllabusSearchDirect.do?nologin=on'
INPUT_NAMES = [
    'syllabusTitleID',
    'indexID'
]

if HEADLESS:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
else:
    options = None

now = datetime.now().strftime('%Y-%m-%d %H:%M')

driver = webdriver.Chrome(options=options)
driver.get(START_URL)


def set_title(t):
    driver.execute_script(
        f'document.getElementsByName("{INPUT_NAMES[0]}")[0].value = "{t}"'
    )
    driver.execute_script(
        'changeComponent("rAco9f3OFHHBpwt3b5v1D3Pg.kmap1", "titleID")'
    )


def set_folder(f):
    driver.execute_script(
        f'document.getElementsByName("{INPUT_NAMES[1]}")[0].value = "{f}"'
    )


def submit():
    driver.execute_script(
        'return changeComponent("PQH4lc0ny21Gz-w9-tmiwiUM.kmap1", "search")'
    )


def sub_folder_check_off():
    driver.execute_script(
        'i=document.querySelector("input[name=subFolderFlag]");if(i.checked) i.click();'
    )


def back():
    driver.execute_script('window.history.back(-1)')


def get_soup(html):
    return BeautifulSoup(html, 'lxml')


def shaped(text: str, split_str=None):
    shaped_text = text.replace('　', ' ').strip()
    if split_str is not None:
        return shaped_text.split(split_str)
    return shaped_text


# ---------------------------------------------------------------
try:
    with open('../db/select.json', 'r', encoding='utf-8') as f:
        j = json.load(f)

    j['updated_at'] = now

    with codecs.open('../db/select.json', 'w', encoding='utf-8') as f:
        json.dump(j, f, ensure_ascii=False, indent=2)

    select_values = j['result']
    print('jsonをロード')

except FileNotFoundError:
    select_values = []
    title_section = driver.find_element_by_name(INPUT_NAMES[0])
    title_choices = [
        [i.get_attribute('value'), i.text]
        for i in title_section.find_elements_by_tag_name('option')
        if i.get_attribute('value')
    ]

    for title_choice, title_text in title_choices:
        set_title(title_choice)

        folder_section = driver.find_element_by_name(INPUT_NAMES[1])
        folder_choices = []

        for i in folder_section.find_elements_by_tag_name('option'):
            if i.get_attribute('value'):
                folder_choices.append(
                    dict(
                        name=shaped(i.text),
                        value=i.get_attribute('value')
                    )
                )

        select_values.append(
            dict(
                value=title_choice,
                name=shaped(title_text),
                folders=folder_choices
            )
        )

    with codecs.open('db/select.json', 'w', 'utf-8') as f:
        json.dump({'result': select_values, 'updated_at': now}, f, ensure_ascii=False, indent=2)

# ---------------------------------------------------------------

result = []
for i in select_values:
    title_value = i['value']
    folders = i['folders']

    # if not re.findall('教養', i['name']):
    #     continue
    print(f'タイトル: {i["name"]}')

    for folder in folders:
        print(f'フォルダー: {folder["name"]}')
        folder_value = folder['value']

        driver.get(START_URL)

        set_title(title_value)
        set_folder(folder_value)
        sub_folder_check_off()
        submit()

        if re.findall('エラーメッセージ', driver.page_source):
            print('検索結果無し')
            continue

        data = [
            'title',
            'folder',
            'code',
            'name',
            'editors',
            'grade',
            'class',
            'semester',
            'period',
        ]

        # 現在のページのデータ収集
        soup = get_soup(driver.page_source)
        table = soup.find('table', class_='txt12')
        trs = table.find_all('tr')
        # 一行目を除く
        del trs[0]

        page_result = []
        # 各行について
        for index, tr in enumerate(trs):
            # 一行の結果
            result_data = {}

            tds = tr.find_all('td')

            # seleniumはページ遷移前のオブジェクトを扱えないため
            # 事前に詳細ページのリンク(onclick)を保存しておく
            detail = tds[4].find('a')
            result_data['_link'] = detail.attrs['onclick']

            # 4番と5番(日本語と英語)を削除
            del tds[4:6]

            # 対応する名前にテーブルの値を挿入
            for td, label in zip(tds, data):
                if label in ['grade', 'period']:
                    result_data[label] = td.text.strip().replace('年', '').split(',')
                else:
                    result_data[label] = shaped(td.text)

            result_data['title'] = {
                'name': result_data['title'],
                'value': title_value
            }
            result_data['folder'] = {
                'name': result_data['folder'],
                'value': folder_value
            }
            page_result.append(result_data)

            print(f'({str(index+1)}/{str(len(trs))}): {result_data["name"]}')

        # 現在のページから詳細情報を収集
        # 保存した_linkを使用
        for index, r in enumerate(page_result):
            driver.execute_script(r['_link'])
            print(f'詳細({str(index+1)}/{str(len(page_result))}): {r["name"]}')
            sleep(0.5)

            detail = {}

            data = [
                ['editors', 3],
                ['classroom', 9],
                ['credit', 19],
                ['credit_type', 15],
                ['class_form', 17],
                ['overview', 27],
                ['reaching_target', 63],
                ['result_evaluation', 65],
                ['textbook', 67],
            ]

            data_no_lessons = [
                ['editors', 3],
                ['classroom', 9],
                ['credit', 19],
                ['credit_type', 15],
                ['class_form', 17],
                ['overview', 27],
                ['lessons', 29],
                ['reaching_target', 31],
                ['result_evaluation', 33],
                ['textbook', 35],
            ]

            soup = get_soup(driver.page_source)
            tables = soup.find_all('table', class_='txt12')
            tds = tables[0].find_all('td')

            # 教科IDとURL収集
            subject_id_str = re.findall('subjectId=[0-9]+', driver.current_url)[0].replace('subjectId=', '')
            detail['subject_id'] = subject_id_str
            detail['page_url'] = BASE_URL + f'/referenceDirect.do?nologin=on&subjectID={subject_id_str}&formatCD=1'

            # 授業計画が文章のとき
            if len(tables) == 1:
                data = data_no_lessons

            # 授業計画が15回分のテーブルのとき
            else:
                lesson_tables = tables[1]

                # tdを全部取る
                lesson_tds = lesson_tables.find_all('td')
                lesson_tds = [t for t in lesson_tds if not t.attrs.get('class') == ['enablecolor']]

                lessons = []
                for lesson_td in lesson_tds:
                    lessons.append(shaped(lesson_td.text))
                detail['lessons'] = lessons

            # テーブルから収集する
            for label, m in data:
                if label == 'editors':
                    detail[label] = shaped(tds[m].text, split_str=',')
                else:
                    detail[label] = shaped(tds[m].text)

            r.update(detail)

            del r['_link']
            # back()

        result.extend(page_result)

# 重複を消す
with codecs.open('db/data.json', 'w', encoding='utf-8') as f:
    json.dump({'result': result, 'updated_at': now}, f, ensure_ascii=False, indent=2)
