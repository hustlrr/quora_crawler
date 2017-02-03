# coding=utf-8

# Created by lruoran on 17-1-30

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from login import add_cookies


def get_question_of_one_user(user_url):
    driver = webdriver.PhantomJS(r'/home/lruoran/software/phantomjs/bin/phantomjs')
    add_cookies(driver)
    driver.get(user_url)
    user_name = user_url.split('/')[-1]

    elems = driver.find_elements_by_xpath("//div[@class='primary']//span[@class='list_count']")
    for elem in elems:
        print(elem.text)
    total = elems[0].text.encode('utf-8')
    if total[-1].isdigit():
        total = int(total)
    else:
        total = int(total[:-1])
    total = min(total, 1000)    # 每个用户最多爬取1000个问题
    print(user_name, total)

    # elems = driver.find_elements_by_xpath("//div[@class='secondary']//span[@class='list_count']")
    # for elem in elems:
    #     print(elem.text)
    # try:
    #     elem = driver.find_element_by_link_text("Twitter")
    #     print(elem.get_property("href"))
    # except NoSuchElementException:
    #     pass

    while True:
        # 把滚动条拖到最下面
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.implicitly_wait(5)  # 等待5秒

        question_elems = driver.find_elements_by_xpath("//a[@class='question_link']")
        cnt = len(question_elems)
        print(cnt)
        if cnt >= total:
            break
    with open("data/question/question-%s" % user_name, "w") as fw:
        for elem in question_elems:
            fw.write("%s\n" % elem.get_attribute("href"))

    driver.quit()

if __name__ == '__main__':
    user_url = "https://www.quora.com/profile/Shashank-Nadig"
    get_question_of_one_user(user_url)