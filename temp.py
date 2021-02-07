#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 查询昨天任务情况
import MySQLdb
import time
import datetime

def read():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_start_time = int(time.mktime(time.strptime(str(yesterday), '%Y-%m-%d'))*1000)
    # 打开数据库连接   
    db = MySQLdb.connect("rm-8vb8l4m6o1ef63oh5qo.mysql.zhangbei.rds.aliyuncs.com", "onlyread", "GL2JSHDHDUIDS%65SD", "tsmk_service", charset='utf8', port=3306)
    # 使用cursor()方法获取操作游标 
    cursor = db.cursor()
    sql="SELECT COUNT(if(`status`='TS_5',true,null)) as 'finish'\
         FROM t_task\
         WHERE updated_datetime> " + str(yesterday_start_time)

    cursor.execute(sql)

    # 使用 fetchone() 方法获取一条数据
    results = cursor.fetchall()
    for row in results:
        finish = row[0]
    # 关闭数据库连接

    sql="SELECT COUNT(id) as 'create' \
         FROM t_task \
        WHERE created_datetime> " + str(yesterday_start_time)

    cursor.execute(sql)

    # 使用 fetchone() 方法获取一条数据
    results = cursor.fetchall()
    for row in results:
        create = row[0]
        # 打印结果
    db.close()
    print("创建任务数:%s,完成任务数:%s" % (create, finish))
read()


#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 未来7天过期学校的列表
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def read():
    # 打开数据库连接   
    db = MySQLdb.connect("rm-8vb8l4m6o1ef63oh5qo.mysql.zhangbei.rds.aliyuncs.com", "onlyread", "GL2JSHDHDUIDS%65SD", "auth_service", charset='utf8', port=3306)
    # 使用cursor()方法获取操作游标 
    cursor = db.cursor()
    sql="SELECT \
                t.`name`, \
                FROM_UNIXTIME( CAST( t.expired AS SIGNED )/ 1000, '%Y-%m-%d-%H:%i:%S' ) 过期时间 \
        FROM t_tenant t \
        WHERE \
                t.expired < UNIX_TIMESTAMP( DATE_ADD( CURRENT_DATE (), INTERVAL 7 DAY )) * 1000 AND t.expired > UNIX_TIMESTAMP() * 1000 \
        ORDER BY \
                t.expired"
    cursor.execute(sql)
    # 使用 fetchone() 方法获取一条数据
    results = cursor.fetchall()
    for row in results:
        school = row[0]
        time = row[1]
        print("%s,%s;" %(school,time))
    # 关闭数据库连接
    db.close()

read()
