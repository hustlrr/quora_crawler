# coding=utf-8

# Created by lruoran on 17-1-29

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_answer_views_upvotes(cnt):
    '''
    :type cnt: str
    :return:
    eg, 将54.8K转为 54800
    '''
    if cnt[-1].isdigit():
        cnt = int(cnt)
    elif cnt[-1] == 'k':
        cnt = int(float(cnt[:-1]) * 1000)
    elif cnt[-1] == 'm':
        cnt = int(float(cnt[:-1]) * 1000000)
    return cnt


def get_question_followers_views(follower):
    '''
    :type follower: str
    :return:
    eg, 9 Followers 返回9
    '''
    follower = follower.strip().split()[0]
    mul = 1
    factors = follower.split(',')
    res = 0
    for factor in factors[::-1]:
        res += (int(factor) * mul)
        mul *= 1000
    return res


import calendar


def get_write_date(date_str):
    '''
    :type date_str: str
    :return:
    '''
    date_str = date_str.strip().split(',')
    if date_str[0].split()[-1] == 'ago':
        return '2017-02-03 00:00:00'

    months = {v: k for k, v in enumerate(calendar.month_abbr)}
    if date_str[0].split()[-2] not in months:
        res = {'Mon': '2017-01-30 00:00:00', 'Tue': '2017-01-30 00:00:00',
               'Wed': '2017-02-01 00:00:00', 'Thu': '2017-02-02 00:00:00',
               'Fri': '2017-02-03 00:00:00', 'Sat': '2017-02-04 00:00:00',
               'Sun': '2017-01-29 00:00:00'}[date_str[0].split()[-1]]
        return res
    res = "{:s}-{:02d}-{:s} 00:00:00"

    if len(date_str) > 1:
        year = date_str[-1]
    else:
        year = '2017'
    month = months[date_str[0].split()[-2]]
    day = date_str[0].split()[-1]
    return res.format(year, month, day)


from datautil import dump_question_into_db, dump_answer_into_db


def get_info_of_each_question(question_url):
    '''
    :type question_url: str
    :return:
    '''
    # 模拟登录
    driver = webdriver.PhantomJS(r'/home/lruoran/software/phantomjs/bin/phantomjs')
    from login import add_cookies
    add_cookies(driver)

    # 加载问题页
    # driver.get('https://www.quora.com/Who-is-Roger-Federer')
    driver.get(question_url)
    # 答案数目
    cnt_answers = driver.find_element_by_xpath("//div[@class='answer_count']").text.encode('utf-8').strip().split()[0]
    if cnt_answers[-1].isdigit():
        cnt_answers = int(cnt_answers)
    else:
        cnt_answers = int(cnt_answers[:-1])

    # 问题标题
    title = driver.find_element_by_xpath("//div[@class='header']//span[@class='rendered_qtext']").text.encode('utf-8')
    print("问题:{:s}".format(title))
    # 问题的详细描述
    question_details = driver.find_element_by_xpath("//div[@class='question_details']").text.encode('utf-8')
    print("问题详细描述:{:s}".format(question_details))
    print("答案数目:{:d}".format(cnt_answers))

    stats_elem = driver.find_element_by_xpath("//div[@class='QuestionStats']")
    followers = get_question_followers_views(stats_elem.find_element_by_xpath("./span[1]").text.encode('utf-8'))
    print("问题关注量:{:d}".format(followers))
    views = get_question_followers_views(stats_elem.find_element_by_xpath("./span[2]").text.encode('utf-8'))
    print("问题浏览量:{:d}".format(views))
    asked_date = get_write_date(stats_elem.find_element_by_xpath("./span[3]").text.encode('utf-8'))
    print("提问时间:{:s}".format(asked_date))
    tag_elems = driver.find_elements_by_xpath("//span[contains(@class, 'TopicNameSpan')]")
    tags = ""
    if len(tag_elems):
        tags = ','.join([elem.text.encode('utf-8') for elem in tag_elems])
        print("问题标签:{:s}".format(tags))

    ans_info = []
    while True:
        # 把滚动条拖到最下面
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.implicitly_wait(5)  # 等待5秒

        user_elems = driver.find_elements_by_xpath(
            "//div[@class='pagedlist_item']//a[starts-with(@name,'answer_')]/following-sibling::div[@class='Answer AnswerBase']")
        cnt = len(user_elems)
        print(title, cnt)
        if cnt >= cnt_answers:
            break

    true_ans_num = 0
    for idx, elem in enumerate(user_elems):
        # 回答者名字
        try:
            link_elem = elem.find_element_by_xpath(".//a[starts-with(@class,'user')]")
            user_name = link_elem.text.encode('utf-8')
            user_url = link_elem.get_attribute("href")
            print('name:{:s},link:{:s}'.format(user_name, user_url))
        except NoSuchElementException:
            user_name = elem.find_element_by_xpath(".//span[contains(@class,'anon_user')]").text.encode('utf-8')
            user_url = ''
            print('name:{:s}'.format(user_name))

        # 答案正文
        text = elem.find_element_by_xpath(".//span[@class='rendered_qtext']").text.encode('utf-8')
        print("text:{:s}".format(' '.join(map(lambda x: x.strip(), text.split()))))
        # 答案编辑日期
        write_date = get_write_date(elem.find_element_by_xpath(".//a[@class='answer_permalink']").text.encode('utf-8'))
        print("date:{:s}".format(write_date))
        # 浏览量
        try:
            ans_views = get_answer_views_upvotes(
                elem.find_element_by_xpath(".//span[@class='meta_num']").text.encode('utf-8'))
            print("views:{:d}".format(ans_views))
        except NoSuchElementException:
            # while elem.find_elements_by_xpath(".//a[@class='more_link']") != []:
            #     elem.find_element_by_xpath(".//a[@class='more_link']").click()
            ans_views = 0
            print("views:{:d}".format(ans_views))
        # 点赞数
        try:
            ans_up = get_answer_views_upvotes(
                elem.find_element_by_xpath(".//a[@action_click='AnswerUpvote']//span[@class='count']").
                    text.encode('utf-8'))
            print("upvote:{:d}".format(ans_up))
        except NoSuchElementException:
            ans_up = 0
            print("upvote:0")
        ans_info.append((title, user_name, user_url, write_date, str(ans_views), str(ans_up), text))
        # dump_answer_into_db(ans_info, 'answer')
        true_ans_num += 1

        print '我是分割线------------------我是分割线'
    dump_question_into_db((question_url, title, asked_date, str(true_ans_num),
                           str(views), str(followers), tags, question_details), 'question')
    dump_answer_into_db(ans_info, 'answer')
    driver.quit()


if __name__ == '__main__':
    with open('data/question/question_url_list') as fr:
        q_urls = fr.readlines()
    start = 18
    batch = 982
    with open('data/question/has_crawlered', 'a') as fw:
        for q_url in q_urls[start:start + batch]:
            get_info_of_each_question(q_url)
            fw.write('%s\n' % q_url)
