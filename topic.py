# coding=utf-8

# Created by lruoran on 17-1-31

from selenium import webdriver
from login import add_cookies, login
from time import sleep

def get_topic_list(init_url, total=2000):
    '''
    :type init_url: str
    :type total: int
    根据大V关注的topic，获得所有要爬取的topic的url
    '''
    driver = webdriver.PhantomJS(r'/home/lruoran/software/phantomjs/bin/phantomjs')
    add_cookies(driver)
    driver.get(init_url)

    while True:
        # 把滚动条拖到最下面
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.implicitly_wait(5)  # 等待5秒

        question_elems = driver.find_elements_by_xpath("//a[contains(@class, 'TopicNameLink')]")
        cnt = len(question_elems)
        print(cnt)
        if cnt >= total:
            break

    with open("data/topic_url_list", "w") as fw:
        for elem in question_elems:
            fw.write("%s\n" % elem.get_attribute("href"))

    driver.quit()


def get_user_url_of_each_topic(topic_url):
    '''
    :type topic_url: str
    :return:
    获得某个topic下最活跃的用户profile url
    '''
    topic_url = topic_url.strip()
    topic = topic_url.split('/')[-1].strip()
    driver = webdriver.PhantomJS(r'/home/lruoran/software/phantomjs/bin/phantomjs')
    add_cookies(driver)
    driver.get(topic_url + "/writers")
    print(topic_url + "/writers")

    while True:
        # 把滚动条拖到最下面
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(5)  # 等待5秒

        user_elems = driver.find_elements_by_xpath(
            "//div[@class='LeaderboardListItem']//span[@class='photo_tooltip']//a")
        cnt = len(user_elems)
        if cnt == 0:  # 说明该topic可能已经不存在
            driver.quit()
            return
        print(cnt, topic)
        if cnt >= 10:
            break

    with open("data/user/user_url_list", "a") as fw:
        for elem in user_elems:
            fw.write("%s\n" % elem.get_attribute("href"))

    driver.quit()


def get_question_url_of_each_topic(topic_url):
    '''
    :type topic_url: str
    :return:
    '''
    topic_url = topic_url.strip()
    topic = topic_url.split('/')[-1].strip()
    driver = webdriver.PhantomJS(r'/home/lruoran/software/phantomjs/bin/phantomjs')
    add_cookies(driver)
    driver.get(topic_url)
    print(topic_url)

    while True:
        # 把滚动条拖到最下面
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(5)# 等待5秒

        user_elems = driver.find_elements_by_xpath("//a[@class='question_link']")
        cnt = len(user_elems)
        if cnt == 0:  # 说明该topic可能已经不存在
            return
        print(cnt, topic)
        if cnt >= 80:
            break

    with open("data/question/question_url_list", "a") as fw:
        for elem in user_elems:
            fw.write("%s\n" % elem.get_attribute("href"))

    driver.quit()


if __name__ == '__main__':
    # init_url = "https://www.quora.com/profile/Adam-Rifkin/topics"
    # get_topic_list(init_url, total=1000)

    # topic_url = "https://www.quora.com/topic/Baseball"
    # get_user_url_of_each_topic(topic_url)

    # with open("data/topic_url_list") as fr:
    #     topic_urls = fr.readlines()
    # for i, topic_url in enumerate(topic_urls[698:]):
    #     print(i + 1)
    #     get_user_url_of_each_topic(topic_url)

    with open("data/topic_url_list") as fr:
        topic_urls = fr.readlines()
    for i, topic_url in enumerate(topic_urls[312:]):
        print(i + 1)
        get_question_url_of_each_topic(topic_url)
