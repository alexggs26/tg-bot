from requests import Session, post, get
from tg_bot.app import config
from urllib import parse
from tg_bot.app.dbworker import Storage
 

def update_token():
    for acc in config.PLATFORMS_WIALON:
        with Session() as s:
            try:
                response = get(url="http://hosting.wialon.com/login.html")
                sign = response.content.decode("utf-8").split("input type=\"hidden\" name=\"sign\" value=\"")[1]
                sign = sign.split("\">")[0]
                response = post(
                    url="https://hosting.wialon.com/oauth.html",
                    data = {
                        "response_type": "token",
                        "wialon_sdk_url": "https://hst-api.wialon.com",
                        "success_uri": "",
                        "client_id": "tg_proverka",
                        "redirect_uri": "https://hosting.wialon.com/login.html",
                        "access_type": 0x100 | 0x200,
                        "activation_time": 0,
                        "duration": 0,
                        "flags": 6,
                        "sign": sign,
                        "login": config.WIALON_STAVROS_LOGIN if acc == 'stavros' else (config.WIALON_STAVROS2_LOGIN if acc == 'stavros2' else config.WIALON_STAVROS_KZ_LOGIN),
                        "passw": config.WIALON_STAVROS_PW if acc == 'stavros' else (config.WIALON_STAVROS2_PW if acc == 'stavros2' else config.WIALON_STAVROS_KZ_PW)
                    }
                )
                token = dict(parse.parse_qsl(parse.urlsplit(response.url).query))["access_token"]
            except KeyError:
                token = ""
                return None

            else:
                response = Storage.update_token(token, acc)
                print(response)
    return 'ok'
            
