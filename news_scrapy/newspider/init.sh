#/bin/bash

yum install openssl-devel bzip2-devel expat-devel gdbm-devel readline-devel sqlite-devel gcc gcc-c++ openssl-devel

pip install --upgrade pip
pip install html2text
pip install scrapy
pip install pymongo
pip install Twisted

systemctl start mongod
systemctl start crond

`chmod 774 schedule`
`crontab schedule`
`crontab -l`