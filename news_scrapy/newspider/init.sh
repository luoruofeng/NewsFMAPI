#/bin/bash

#other way start scrapy

systemctl start crond

`chmod 774 schedule`
`crontab schedule`
`crontab -l`