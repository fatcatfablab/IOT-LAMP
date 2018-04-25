IOT Lamp project using adafruit.io as an MQTT broker.

Uses fadecandy to control RGB neopixel strip and the Adafruit_DotStar_Pi python library to control a warm white Dotstar strip.

NB: Dotstar lib needs root privs and is currently broken for Pi Zero W. Run `git reset --hard a470133`

add `/home/pi/fadecandy/bin/fcserver-rpi /home/pi/fadecandy/server/default.json` to `/etc/rc.local`

