from selenium import webdriver
from win10toast import ToastNotifier
import time
import datetime
import argparse
import requests

SHOP_URL = r'https://www.nvidia.com/de-de/shop/geforce/?page=1&limit=9&locale=de-de&search=NVIDIA%20GEFORCE%20RTX%203080'
# SHOP_URL = r'https://www.nvidia.com/de-de/shop/geforce/nvlinks/?page=1&limit=9&locale=de-de&category=NVLINKS&category_filter=GPU~378,Laptop~444,Studio-Laptop~5,NVLINKS~4'
# SHOP_URL = r'https://www.nvidia.com/de-de/shop/geforce/?page=1&limit=9&locale=de-de&search=NVIDIA%20GEFORCE%20RTX%202060%20SUPER'

DEFAULT_REFRESH_RATE = 10 # in seconds
DEFAULT_MAX_BUYBUTTON_WAIT = 3 # in seconds
DEFAULT_WEBHOOK_EVENTNAME = 'NVIDIAShopBot'

OUTOFSTOCK_BUTTONTEXT = 'OUT OF STOCK'
INSTOCK_BUTTONTEXT = 'IN DEN EINKAUFSWAGEN'

def SendToastNotification():
    toaster = ToastNotifier()
    toaster.show_toast("NVIDIA RTX 3080 AVAILABLE", "Now, finish the buying process by yourself!", duration=86400)

def TryCheckOut(driver):
    try:
        cart = driver.find_element_by_id('cart')
        if (cart is None):
            return
        checkoutButton = cart.find_element_by_css_selector('div.nv-button.js-checkout.cart__checkout-button')
        if (checkoutButton is not None):
            checkoutButton.click()
    except Exception as ex:
        print('{0}: ERROR - {1}'.format(datetime.datetime.now(), ex))

def WaitForBuyingButton(buyButton, maxWait):
    try:
        index = 0
        while (index < maxWait and buyButton.text == ''):
            time.sleep(1)
            index += 1
    except Exception as ex:
        print('{0}: ERROR - {1}'.format(datetime.datetime.now(), ex))

def SendIFTTTWebhookRequest(eventName, key):
    if (eventName is not None and len(eventName) > 0 and key is not None and len(key) > 0):
        url = 'https://maker.ifttt.com/trigger/{0}/with/key/{1}'.format(eventName, key)
        requests.api.post(url)

def Start(args):
    driver = webdriver.Chrome()

    inStock = False
    while (not inStock):
        try:
            driver.get(SHOP_URL)
            try:
                buyLink = driver.find_element_by_css_selector('a.featured-buy-link')
            except:
                pass
            
            if (buyLink is None):
                print('{0}: ERROR - Could not get buy button. ==> waiting {1} seconds'.format(datetime.datetime.now(), args.RefreshRate))
                time.sleep(args.RefreshRate)
                continue
            
            if (buyLink.text == ''):
                WaitForBuyingButton(buyLink, args.MaxBuyButtonWait)

            if (buyLink.text != OUTOFSTOCK_BUTTONTEXT and buyLink.text == INSTOCK_BUTTONTEXT):
                inStock = True
                buyLink.click()
                TryCheckOut(driver)

            else:
                print('{0}: OUT OF STOCK ==> waiting {1} seconds'.format(datetime.datetime.now(), args.RefreshRate))
                time.sleep(args.RefreshRate)
        except Exception as ex:
            print('{0}: ERROR - {1}'.format(datetime.datetime.now(), ex))

    SendIFTTTWebhookRequest(args.WebhookEventName, args.WebhookKey)
    SendToastNotification()
    print('{0}: IN STOCK ==> Finish process by yourself in browser AND DO NOT CLOSE THIS WINDOW!'.format(datetime.datetime.now()))
    input() # do not close browser

parser = argparse.ArgumentParser(description='Bot for buying things in NVIDIA online shop.')
parser.add_argument('-r', action='store', dest='RefreshRate', help='The web refresh rate (in seconds). [Default={0}]'.format(DEFAULT_REFRESH_RATE), default=DEFAULT_REFRESH_RATE)
parser.add_argument('-w', action='store', dest='MaxBuyButtonWait', help='Max waiting time for buy button (in seconds). [Default={0}]'.format(DEFAULT_MAX_BUYBUTTON_WAIT), default=DEFAULT_MAX_BUYBUTTON_WAIT)
parser.add_argument('-k', action='store', dest='WebhookKey', help='The IFTTT webhook key.')
parser.add_argument('-e', action='store', dest='WebhookEventName', help='The IFTTT webhook event name. [Default={0}]'.format(DEFAULT_WEBHOOK_EVENTNAME), default=DEFAULT_WEBHOOK_EVENTNAME)
parser.add_argument('--testwebhook', action='store_true', dest='TestWebhook', help='Only test the IFTTT webhook.')
args = parser.parse_args()

if (args.TestWebhook):
    SendIFTTTWebhookRequest(args.WebhookEventName, args.WebhookKey)
else:
    Start(args)