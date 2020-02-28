cp new-*.service /etc/systemd/system
systemctl daemon-reload
systemctl start new-voice
systemctl start new-scrapy

systemctl status new-voice
systemctl status new-scrapy