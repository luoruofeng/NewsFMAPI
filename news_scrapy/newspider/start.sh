#/bin/bash

pip install html2text
pip install scrapy
pip install pymongo

systemctl start mongod
systemctl start crond

crontab schedule