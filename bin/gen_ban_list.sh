more /var/log/syslog | grep fail2ban | grep WARNING > /home/hass/.homeassistant/ip_ban_list.log
sed -i 's/dragonstone fail2ban\.actions\[[^]]*\]: WARNING//g;s/\[//g;s/\]//g;s/  / /g' /home/hass/.homeassistant/ip_ban_list.log
python3 /home/hass/.homeassistant/bin/read_ban_list.py '/home/hass/.homeassistant/ip_ban_list.log' '/home/hass/.homeassistant/ip_ban_list.json'
rm /home/hass/.homeassistant/ip_ban_list.log
