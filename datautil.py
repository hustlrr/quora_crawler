# coding=utf-8

# Created by lruoran on 17-2-3

import MySQLdb

def dump_question_into_db(question_info, table):
    # 打开数据库连接
    conn = MySQLdb.connect("localhost", "root", "liuruoran", "papers", charset="utf8")
    conn.ping(True)
    # 使用cursor()方法获取操作游标
    cursor = conn.cursor()
    # SQL 插入语句
    sql = 'insert into ' + table + ' (url,title,asked_date,answer_cnt,view_cnt,follower_cnt,tags,question_details) values (%s, %s, %s, %s, %s, %s, %s, %s)'
    try:
        # 执行sql语句
        cursor.execute(sql, question_info)
        # 提交到数据库执行
        conn.commit()
    except MySQLdb.Error as e:
        print(e)
        conn.rollback()
    # 关闭数据库连接
    cursor.close()
    conn.close()

def dump_answer_into_db(answer_info, table):
    # 打开数据库连接
    conn = MySQLdb.connect("localhost", "root", "liuruoran", "papers", charset="utf8")
    conn.ping(True)
    # 使用cursor()方法获取操作游标
    cursor = conn.cursor()
    # SQL 插入语句
    sql = 'insert into ' + table + ' (q_title,user_name,user_url,write_date,views,upvote,content) values (%s, %s, %s, %s, %s, %s, %s)'
    try:
        # 执行sql语句
        cursor.executemany(sql, answer_info)
        # 提交到数据库执行
        conn.commit()
    except MySQLdb.Error as e:
        print(e)
        conn.rollback()
    # 关闭数据库连接
    cursor.close()
    conn.close()