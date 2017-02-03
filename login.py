# coding=utf-8

# Created by lruoran on 17-2-3
from selenium import webdriver
import cPickle


def login():
    user = '823729390@qq.com'
    password = '823729390lrr'
    # 模拟登录
    driver = webdriver.PhantomJS(r'/home/lruoran/software/phantomjs/bin/phantomjs')
    driver.get("https://www.quora.com/")
    driver.find_element_by_xpath("//input[@placeholder='Email']").send_keys(user)
    driver.find_element_by_xpath("//input[@placeholder='Password']").send_keys(password)
    while driver.find_elements_by_xpath("//input[@value='Login']") != []:
        driver.find_element_by_xpath("//input[@value='Login']").click()

    cPickle.dump(driver.get_cookies(), open("data/cookies.pkl", "w"))


def add_cookies(driver):
    cookies = cPickle.load(open("data/cookies.pkl"))
    for cookie in cookies:
        driver.add_cookie({k: cookie[k] for k in ('name', 'value', 'domain', 'path')})
