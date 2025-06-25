import hashlib
import random
import requests

# 你需要在这里填写自己的百度翻译appid和密钥
BAIDU_APPID = 'your_appid'
BAIDU_SECRET_KEY = 'your_secret_key'

def baidu_translate(query, from_lang='auto', to_lang='en'):
    if not query:
        return ''
    salt = str(random.randint(32768, 65536))
    sign = BAIDU_APPID + query + salt + BAIDU_SECRET_KEY
    sign = hashlib.md5(sign.encode('utf-8')).hexdigest()
    url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
    params = {
        'q': query,
        'from': from_lang,
        'to': to_lang,
        'appid': BAIDU_APPID,
        'salt': salt,
        'sign': sign
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        result = resp.json()
        if 'trans_result' in result:
            return result['trans_result'][0]['dst']
        else:
            return ''
    except Exception as e:
        print(f'Baidu translate error: {e}')
        return '' 