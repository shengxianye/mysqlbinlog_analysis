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
python mysqlbinlog_query.py --host localhost --user root --password agm43gadsg --mode redo --infile /www/env/mysql/arch/4.sql --outfile /www/env/mysql/arch/4.log  --filtertable istics_positions --filterdml UPDATE<br>  
mode 可选2个参数，分别时redo和undo   <br> 
infile      输入文件名<br> 
outfile     输出文件名<br> 
filtertable 过滤表名(TABLE1)<br> 
filterdml   过滤dml动作（DELETE INSERT UPDATE）<br> 

