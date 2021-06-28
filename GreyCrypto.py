import json
import time
import telegram
import requests
from telegram import ParseMode
from config import Config as SETTING
from PIL import Image, ImageDraw
from prettytable import PrettyTable
from apscheduler.schedulers.blocking import BlockingScheduler
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects


def apiFetch():
    params = {
        "symbol":",".join(SETTING.COIN_LIST),
        "convert":"INR",
    }
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": SETTING.COIN_MARKET_CAP_API,
    }
    response = requests.get(SETTING.COIN_MARKET_CAP_URL, params = params, headers = headers)
    return json.loads(response.text)


def createTable(jsonData):
    cryptoTable = PrettyTable()
    cryptoTable.field_names = ["COIN", "Price", "1h", "24h", "7d", "30d", "60d", "90d"]

    for coin in SETTING.COIN_LIST:
        cryptoTable.add_row(
            [
                jsonData["data"][coin]["symbol"],
                round(jsonData["data"][coin]["quote"]["INR"]["price"], 3),
                round(jsonData["data"][coin]["quote"]["INR"]["percent_change_1h"], 3),
                round(jsonData["data"][coin]["quote"]["INR"]["percent_change_24h"], 3),
                round(jsonData["data"][coin]["quote"]["INR"]["percent_change_7d"], 3),
                round(jsonData["data"][coin]["quote"]["INR"]["percent_change_30d"], 3),
                round(jsonData["data"][coin]["quote"]["INR"]["percent_change_60d"], 3),
                round(jsonData["data"][coin]["quote"]["INR"]["percent_change_90d"], 3)
            ]
        )
    if SETTING.DEBUG == True:
        print(cryptoTable.get_string(title="Grey Crypto - @gryecryptobot"))
    return cryptoTable


def createImage(cryptoTable):
    img = Image.new("RGB", (512, 250), color = (30, 30, 30))
    drawimg = ImageDraw.Draw(img)
    drawimg.text((10,10), text=cryptoTable.get_string(title="Grey Crypto - @gryecryptobot"), fill=(225, 225, 225), align="center")
    img.save("image.png")


def sendMessage():
    auth = telegram.Bot(token=SETTING.TOKEN)
    for CHAT_ID in SETTING.CHAT_IDS:
        telegram.Bot.send_photo(auth, chat_id=CHAT_ID, photo=open("image.png", "rb"), caption="@greycryptobot")


def sendError(msg):
    auth = telegram.Bot(token=SETTING.TOKEN)
    telegram.Bot.sendMessage(auth, SETTING.ADMIN_ID, text=msg, parse_mode=ParseMode.HTML)


def mainFunc():
    try:
        jsonData = apiFetch()
        cryptoTable = createTable(jsonData = jsonData)
        createImage(cryptoTable = cryptoTable)
        sendMessage()
    except telegram.error.BadRequest as e:
        print(e)
        sendError("Bad Request in Grey Crypto")
    except telegram.error.Unauthorized as e:
        print(e)
        sendError("Unauthorized in Grey Crypto\nSomeone block me ☹️\nKya me itna bura hu 😣")
    except Exception as e:
        sendError("Error in Grey Crypto")
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        if SETTING.DEBUG == True:
            print(e)
        else:
            sendError("<b>Boss</b> too many request in Grey Crypto :(")


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(mainFunc, 'interval', minute='1')
    scheduler.start()