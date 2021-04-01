import os
from time import sleep
import ally
from phue import Bridge
from dotenv import load_dotenv

load_dotenv()


SYMBOL = 'ge'
LIGHT_NAME = 'Unfinished room light'

RED = 0
GREEN = 25500
BLUE = 46920
MIN_SAT = 170
MAX_SAT = 254
BRIGHTNESS = 30


def hue(bid_price, open_price):
    if bid_price > open_price:
        return GREEN
    elif bid_price < open_price:
        return RED
    else:
        return BLUE

def saturation(bid_price, open_price):
    diff = bid_price - open_price
    perc_change = round(abs(diff / open_price), 3)
    new_sat = (int((MAX_SAT - MIN_SAT) * perc_change) * 10) + MIN_SAT
    return new_sat if new_sat < MAX_SAT else MAX_SAT

def update_light(light, bid_price, open_price):
    old_hue = light.hue
    new_hue = hue(bid_price, open_price)

    light.hue = new_hue
    light.saturation = saturation(bid_price, open_price)

    if old_hue != new_hue:
        sleep(0.5)  # allow the light to change color before flashing
        light.alert = 'select'

def execute():
    a = ally.Ally()
    b = Bridge(os.getenv('BRIDGE_IP'))
    b.connect()

    light_names = b.get_light_objects('name')
    light = light_names[LIGHT_NAME]

    try:
        light.on = True
        light.brightness = BRIGHTNESS
        light.hue = BLUE

        quotes = a.quote(
            symbols=SYMBOL,
            fields=['opn', 'bid'],
            dataframe=False
        )

        open_price = float(quotes[0]['opn'])
        bid_price = float(quotes[0]['bid'])

        update_light(light, bid_price, open_price)

        for quote in a.stream(SYMBOL):
            print(open_price)
            print(quote)
            bid_price = float(quote['bid'])
            update_light(light, bid_price, open_price)
    finally:
        light.on = False


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    execute()
