from selenium import webdriver
from win10toast import ToastNotifier
import time
import datetime

REFRESH_RATE = 10 # in seconds
MAX_BUYBUTTON_WAIT = 3 # in seconds
url = r'https://www.nvidia.com/de-de/shop/geforce/?page=1&limit=9&locale=de-de&search=NVIDIA%20GEFORCE%20RTX%203080'
# url = r'https://www.nvidia.com/de-de/shop/geforce/nvlinks/?page=1&limit=9&locale=de-de&category=NVLINKS&category_filter=GPU~378,Laptop~444,Studio-Laptop~5,NVLINKS~4'
# url = r'https://www.nvidia.com/de-de/shop/geforce/?page=1&limit=9&locale=de-de&search=NVIDIA%20GEFORCE%20RTX%202060%20SUPER'
outOfStockButtonText = 'OUT OF STOCK'
inStockButtonText = 'IN DEN EINKAUFSWAGEN'

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

def WaitForBuyingButton(buyButton):
    try:
        index = 0
        while (index < MAX_BUYBUTTON_WAIT and buyButton.text == ''):
            time.sleep(1)
            index += 1
    except Exception as ex:
        print('{0}: ERROR - {1}'.format(datetime.datetime.now(), ex))

def Start():
    driver = webdriver.Chrome()

    inStock = False
    while (not inStock):
        try:
            driver.get(url)
            try:
                buyLink = driver.find_element_by_css_selector('a.featured-buy-link')
            except:
                pass
            
            if (buyLink is None):
                print('{0}: ERROR - Could not get buy button. ==> waiting {1} seconds'.format(datetime.datetime.now(), REFRESH_RATE))
                time.sleep(REFRESH_RATE)
                continue
            
            if (buyLink.text == ''):
                WaitForBuyingButton(buyLink)

            if (buyLink.text != outOfStockButtonText and buyLink.text == inStockButtonText):
                inStock = True
                buyLink.click()
                TryCheckOut(driver)

            else:
                print('{0}: OUT OF STOCK ==> waiting {1} seconds'.format(datetime.datetime.now(), REFRESH_RATE))
                time.sleep(REFRESH_RATE)
        except Exception as ex:
            print('{0}: ERROR - {1}'.format(datetime.datetime.now(), ex))

    SendToastNotification()
    print('{0}: IN STOCK ==> Finish process by yourself in browser AND DO NOT CLOSE THIS WINDOW!'.format(datetime.datetime.now()))
    input() # do not close browser

Start()