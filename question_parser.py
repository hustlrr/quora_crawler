# coding=utf-8

from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from datautil import dump_question_into_db, dump_answer_into_db
import re
import time


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
import datetime


def get_write_date(date_str):
    '''
    :type date_str: str
    :return:
    '''
    date_str = date_str.strip().split(',')
    if date_str[0].split()[-1] == 'ago':  # 说明在当前时间的24小时之内
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    months = {v: k for k, v in enumerate(calendar.month_abbr)}
    day_abbr = [d for d in calendar.day_abbr]
    now_datetime = datetime.datetime.now()
    week2date = {}
    for i in range(1, 8):
        before_datetime = now_datetime - datetime.timedelta(days=i)
        week2date[day_abbr[before_datetime.weekday()]] = before_datetime.strftime("%Y-%m-%d %H:%M:%S")

    if date_str[0].split()[-2] not in months:
        try:
            res = week2date[date_str[0].split()[-1]]
            return res
        except KeyError:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    res = "{:s}-{:02d}-{:s} 00:00:00"

    month = months[date_str[0].split()[-2]]
    day = date_str[0].split()[-1]
    if len(date_str) > 1:
        year = date_str[-1]
    else:   # 不能存在年份信息
        year = '2016' if month > now_datetime.month or (
        month == now_datetime.month and int(day) > now_datetime.day) else '2017'
    return res.format(year, month, day)


def parse_by_selenium(driver, user_elems, question_url):
    # 答案数目
    cnt_answers = driver.find_element_by_xpath("//div[@class='answer_count']").text.encode('utf-8').strip().split()[0]
    if cnt_answers[-1].isdigit():
        cnt_answers = int(cnt_answers)
    else:
        cnt_answers = int(cnt_answers[:-1])

    # 问题标题
    title = driver.find_element_by_xpath("//div[@class='header']//span[@class='rendered_qtext']").text.encode(
        'utf-8').strip()
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
    true_ans_num = 0
    for idx, elem in enumerate(user_elems):
        # 回答者名字
        try:
            link_elem = elem.find_element_by_xpath(".//a[starts-with(@class,'user')]")
            user_name = link_elem.text.encode('utf-8').strip()
            user_url = link_elem.get_attribute("href").strip()
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
        if dump_question_into_db((question_url.strip(), title, asked_date, str(true_ans_num),
                                  str(views), str(followers), tags, question_details), 'question'):
            dump_answer_into_db(ans_info, 'answer')


def parse_by_bs(source, question_url):
    # with open("data/question/page_source") as fr:
    #     source = ''.join(fr.readlines())

    # source = driver.page_source
    soup = BeautifulSoup(source, "html.parser")

    # 标题
    title = soup.find("div", {"class": "header"}).find("span", {"class": "rendered_qtext"}).text.encode("utf-8")
    print("标题:{:s}".format(title))
    # 答案数目
    print("答案数目:{:s}".format(soup.find("div", {"class": "answer_count"}).text))
    stats = soup.find("div", {"class": "QuestionStats"}).find_all("span")
    # followers, views, date
    followers = get_question_followers_views(stats[0].text)
    views = get_question_followers_views(stats[3].text)
    asked_date = get_write_date(stats[5].text)
    print(followers, views, asked_date)
    # tags
    tags = soup.find_all("span", {"class": "TopicNameSpan TopicName qserif-bold"})
    tags = ','.join([tag.text for tag in tags])
    print(tags)
    # question details
    question_details = soup.find("div", {"class": "question_details"}).text.encode("utf-8")
    print(question_details)

    # answers
    answers = soup.find_all("a", {"name": re.compile(r"answer_\d*?")})
    true_ans_num = 0
    ans_info = []
    for answer in answers:
        answer = answer.next_sibling
        # 回答者姓名
        name_elem = answer.find_all("a")[1]
        user_name = name_elem.text.encode("utf-8")
        user_url = name_elem.attrs["href"].encode("utf-8")
        if user_url.strip() == '#':
            user_name = answer.find("span", {"class": "anon_user qserif"}).text.encode("utf-8")
            user_url = ""
        else:
            user_url = "https://www.quora.com" + user_url
        print("name:{:s}, link:{:s}".format(user_name, user_url))
        # 正文
        text = answer.find("span", {"class": "rendered_qtext"}).text.encode("utf-8")
        print("text:{:s}".format(' '.join(map(lambda x: x.strip(), text.split()))))
        # 答案编辑日期
        write_date = get_write_date(answer.find("a", {"class": "answer_permalink"}).text.encode("utf-8"))
        print("date:{:s}".format(write_date))
        # 浏览量
        views_elem = answer.find("span", {"class": "meta_num"})
        if views_elem:
            ans_views = get_answer_views_upvotes(views_elem.text.encode("utf-8"))
        else:
            ans_views = 0
        print("views:{:d}".format(ans_views))
        # 点赞数
        upvote_elem = answer.find("a", {"action_click": "AnswerUpvote"}).find("span", {"class": "count"})
        if upvote_elem:
            ans_up = get_answer_views_upvotes(upvote_elem.text.encode("utf-8"))
        else:
            ans_up = 0
        print("upvote:{:d}".format(ans_up))

        print("我是分割线------------------我是分割线")
        true_ans_num += 1
        ans_info.append((title, user_name, user_url, write_date, str(ans_views), str(ans_up), text))

    question_info = (question_url.strip(), title, asked_date, str(true_ans_num),
                     str(views), str(followers), tags, question_details)
    if dump_question_into_db(question_info, 'question_user'):
        dump_answer_into_db(ans_info, 'answer_user')


if __name__ == '__main__':
    with open("data/question/page_source") as fr:
        source = ''.join(fr.readlines())
    question_url = "https://www.quora.com/How-can-I-destroy-my-ego-self"
    parse_by_bs(source, question_url)
