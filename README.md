# mysqlbinlog_analysis
Analysis Mysql Binlog to redolog or undolog <br>  
MySQL自带的mysqlbinlog工具解析的log阅读不方便，且字段名替换成了@1，@2等，不是很好理解<br>  
这个脚本主要的功能是再次对mysqlbinlog解析出来的文件进行再次处理，可以通过参数调控，生成redolog或者undolog<br>  
这个脚本需要修改6个变量<br>  
host,user,password,（因为需要替换成具体的字段名，所以需要连接数据库，建议在从库上运行）<br>  
file_type：redo或者undo<br>  
log_file： mysqlbinlog处理后日志名<br>  
target_log：本脚本处理后的日志名<br>  
具体用法案例：<br>  
step1:<br>  
/www/env/mysql/bin/mysqlbinlog -v  --base64-output=DECODE-ROWS mysql-bin.002067 > 5.sql<br>  
step2:<br>  
修改脚本变量<br>  
file_type = redo<br>  
logfile = /data/5.sql<br>  
target_log = /data/5.log<br>  
step3:<br>  
python ／data/mysqlbinlog_query.py<br>  
在data下会生成5.log,进入数据库可直接source 5.log,进行redo动作。<br>  
PS:<br>  
1.这个脚本只能提取update，delete，insert语句，如果有alter语句，不会做处理，有未知的情况，具体还没测试<br>  
2.提取undo的时候，具体执行sql顺去请从文件尾往上执行，后期待完善<br>  
