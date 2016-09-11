# -*- coding: UTF-8 -*-
#!/usr/bin/python
import re, hashlib, time, datetime
import MySQLdb
#Author: yeshengxian
#Mail: 635767825@qq.com
#Func: analysis mysql  binlog to redolog or undolog
#Version: 1.0


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def mysql_column_list(host,user,password):
    column_dict = {}
    conn = MySQLdb.connect(host, user, password, 'information_schema', charset="utf8");
    query = "select TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME,ORDINAL_POSITION from information_schema.COLUMNS where TABLE_SCHEMA not in ('test','information_schema','performance_schema') order by TABLE_SCHEMA,TABLE_NAME,ORDINAL_POSITION;"
    cursor = conn.cursor()
    cursor.execute(query)
    numrows = int(cursor.rowcount)
    for i in range(numrows):
        row = cursor.fetchone()
        database = row[0]
        table = row[1]
        column = row[2]
        order = row[3]
        if database in column_dict:
            if table in column_dict[database]:
                column_dict[database][table].update({ order : column })
            else:
                column_dict[database].update( { table : { order : column } })
        else:
            column_dict.update({ database : { table : { order : column } } })
    conn.close()
    return column_dict

def redo_sql(sql_action,column_dict,dbname,tablename,sql):
    dbname = dbname.replace("`",'')
    tablename = tablename.replace("`",'')
    column_num = len(column_dict[dbname][tablename])
    if sql_action == 'INSERT':
        sql = sql.replace("SET",'values(')
        for i in range(int(column_num),0,-1):
            if i == 1:
                sql = sql.replace('@'+str(i)+'=',"")
            else:
                sql = sql.replace('@'+str(i)+'=',",")
        sql = sql + ");"
    if sql_action == 'UPDATE':
        sql_set = sql.split('SET')[1]
        sql_where = sql.split('WHERE')[1].split('SET')[0]
        sql_head = sql.split('WHERE')[0]
        for i in range(int(column_num),0,-1):
            if i == 1:
                sql_set = sql_set.replace('@'+str(i) , "`"+column_dict[dbname][tablename][i]+"`")
                sql_where = sql_where.replace('@'+str(i) , "`"+column_dict[dbname][tablename][i]+"`")
            else:
                sql_set = sql_set.replace('@'+str(i) , ", "+"`"+column_dict[dbname][tablename][i]+"`")
                sql_where = sql_where.replace('@'+str(i) ,"AND " +"`"+column_dict[dbname][tablename][i]+"`")
        sql = sql_head + "SET" + sql_set + " WHERE" + sql_where + ";"
    if sql_action == 'DELETE':
        for i in range(int(column_num),0,-1):
            if i == 1:
                sql = sql.replace('@'+str(i) , "`"+column_dict[dbname][tablename][i]+"`")
            else:
                sql = sql.replace('@'+str(i) , "AND "+"`"+column_dict[dbname][tablename][i]+"`")
        sql = sql + ";"
    return sql

def undo_sql(sql_action,column_dict,dbname,tablename,sql):
    dbname = dbname.replace("`",'')
    tablename = tablename.replace("`",'')
    column_num = len(column_dict[dbname][tablename])
    if sql_action == 'INSERT':
        sql = sql.replace("INSERT",'DELETE')
        sql = sql.replace("INTO","FROM")
        sql = sql.replace("SET","WHERE")
        for i in range(int(column_num),0,-1):
            if i == 1:
                sql = sql.replace('@'+str(i),"`"+column_dict[dbname][tablename][i]+"`")
            else:
                sql = sql.replace('@'+str(i),"AND "+"`"+column_dict[dbname][tablename][i]+"`")
        sql = sql + ";"
    if sql_action == 'UPDATE':
        sql_set = sql.split('SET')[1]
        sql_where = sql.split('WHERE')[1].split('SET')[0]
        sql_head = sql.split('WHERE')[0]
        for i in range(int(column_num),0,-1):
            if i == 1:
                sql_set = sql_set.replace('@'+str(i) , "`"+column_dict[dbname][tablename][i]+"`")
                sql_where = sql_where.replace('@'+str(i) , "`"+column_dict[dbname][tablename][i]+"`")
            else:
                sql_set = sql_set.replace('@'+str(i) , "AND "+"`"+column_dict[dbname][tablename][i]+"`")
                sql_where = sql_where.replace('@'+str(i) ,", " +"`"+column_dict[dbname][tablename][i]+"`")
        sql = sql_head + "SET" + sql_where + " WHERE" + sql_set + ";"
    if sql_action == 'DELETE':
        sql = sql.replace("DELETE","INSERT")
        sql = sql.replace("FROM","INTO")
        sql = sql.replace("WHERE","VALUES (")
        for i in range(int(column_num),0,-1):
            if i == 1:
                sql = sql.replace('@'+str(i)+"=" , "")
            else:
                sql = sql.replace('@'+str(i)+"=" , ", "+"")
        sql = sql + ");"
    return sql


def read_slow_log(log_file,target_log,file_type,column_dict):
    regex_timestamp = re.compile('SET TIMESTAMP')
    sql_info = []
    sql = ''
    rsize = 1024 * 1024 * 10
    regex_sql = re.compile("###")
    regex_end = re.compile("COMMIT")
    regex_float = re.compile(r"(\d+\.\d+)")
    regex_table = re.compile("\`.*?\`")
    regex_float = re.compile(r"(\(\d+)\)")
    p = 0
    stdin_log = open(log_file, 'r')
    stdout_log = open(target_log, 'a+')
    try:
        while True:
            stdin_log.seek(p, )
            lines = stdin_log.readlines(rsize)
            p = stdin_log.tell()
            if lines:
                for line in lines:
                    if line.strip():
                        try:
                            line = line.encode('utf-8')
                        except:
                            line = line.decode('GB2312', 'ignore').encode('utf-8')
                    if regex_timestamp.match(line):
                        sql_info.append(line.strip())
                        time_stamp = sql_info[0].split('=')[1].split('/')[0]
                        timeArray = time.localtime(int(time_stamp))
                        date_time_raw = time.strftime("%Y%m%d %H%M%S", timeArray)
                    elif regex_sql.match(line):
                        sql = sql + line.strip()
                    elif regex_end.match(line):
                        sql = sql.replace("###",'')
                        sql = regex_float.sub("", sql)
                        sql_sp = sql.split()
                        sql_action = sql_sp[0]
                        table_info = regex_table.findall(sql)
                        dbname = table_info[0]
                        tablename = table_info[1]
                        if file_type == "redo":
                            sql_redo =   redo_sql(sql_action,column_dict,dbname,tablename,sql)
                            sql_redo = "###" +  date_time_raw + "\n" +sql_redo
                            stdout_log.write(str(sql_redo) + '\n')
                        if file_type == "undo":
                            sql_undo =   undo_sql(sql_action,column_dict,dbname,tablename,sql)
                            sql_undo = "\"" + sql_undo + "\""
                            sql_undo = "###" +  date_time_raw + "\n" +sql_undo
                            stdout_log.write(str(sql_undo) + '\n')
                        sql = ''
                        sql_info =  []
                    else:
                        pass
            if not lines:
                break
    finally:
        stdin_log.close()
        stdout_log.close()



def main():
    host = 'localhost'  #变量1
    user = 'root'       #变量2
    password = '123456' #变量3
    file_type = "redo"  #变量4
    log_file = '/www/env/mysql/arch/5.sql' #变量5
    target_log = '/www/env/mysql/arch/5.log' #变量6
    rsize = 1024 * 1024 * 10


    column_dict = mysql_column_list(host,user,password)
    read_slow_log(log_file,target_log,file_type,column_dict)

if __name__ == "__main__":
    main()
