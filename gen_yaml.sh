docker exec -it home-assistant /bin/bash -c "cd /config;bash bin/smash.sh;python lovelace/lovelace-gen.py;exit"
echo "Done"
