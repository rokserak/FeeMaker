#systemd service for script

copy bitmex_app.service in /lib/systemd/system/

change name in file depending on what app you running
change User value for your user


sudo chmod 644 /lib/systemd/system/bitmex_app.service


sudo systemctl daemon-reload

sudo systemctl enable bitmex_app.service

sudo systemctl status bitmex_app.service
