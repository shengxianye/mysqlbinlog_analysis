# mysqlbinlog_analysis
Analysis Mysql Binlog to redolog or undolog <br>  
MySQL自带的mysqlbinlog工具解析的log阅读不方便，且字段名替换成了@1，@2等，不是很好理解<br>  

使用方法：<br>  
step1:<br>  
/www/env/mysql/bin/mysqlbinlog -v  --base64-output=DECODE-ROWS mysql-bin.002067 > 5.sql<br>  
step2:<br>  
python mysqlbinlog_query.py --host localhost --user root --password agm43gadsg --mode redo --infile /www/env/mysql/arch/5.sql --outfile /www/env/mysql/arch/5.log  --filtertable table1 --filterdml UPDATE<br>  
mode 可选2个参数，分别时redo和undo   <br> 
infile      输入文件名<br> 
outfile     输出文件名<br> 
filtertable 过滤表名(TABLE1)<br> 
filterdml   过滤dml动作（DELETE INSERT UPDATE）<br> 

