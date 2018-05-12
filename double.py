#!/usr/bin/env python2
# Fade each half of lamp to 2 random colors.

import opc, time, colorsys, random

numpixels = 47 
client = opc.Client('localhost:7890')

pixels = [ (0,0,0) ] * numpixels

client.put_pixels(pixels)
client.put_pixels(pixels)

while 1:
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    r2 = random.randint(0, 255)
    g2 = random.randint(0, 255)
    b2 = random.randint(0, 255)


    for i in range(0,22):
        pixels[i] = (r,g,b)

    for i in range(23,46):
        pixels[i] = (r2,g2,b2)

    client.put_pixels(pixels)

    time.sleep(4)
