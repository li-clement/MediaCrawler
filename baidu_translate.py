import hashlib
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

# 你需要在这里填写自己的百度翻译appid和密钥
BAIDU_APPID = 'your_appid'
BAIDU_SECRET_KEY = 'your_secret_key'

def create_retry_session(retries=3, backoff_factor=0.3):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(500, 502, 504),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def baidu_translate(query, from_lang='auto', to_lang='en', max_retries=3):
    if not query:
        return ''
    
    session = create_retry_session(retries=max_retries)
    
    for attempt in range(max_retries):
        try:
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
            
            resp = session.get(url, params=params, timeout=15)  # 增加超时时间到15秒
            result = resp.json()
            
            if 'trans_result' in result:
                return result['trans_result'][0]['dst']
            elif 'error_code' in result:
                print(f'Baidu translate error (attempt {attempt + 1}/{max_retries}): {result}')
            else:
                print(f'Unexpected response format (attempt {attempt + 1}/{max_retries}): {result}')
            
            if attempt < max_retries - 1:
                time.sleep(backoff_factor * (2 ** attempt))  # 指数退避
                
        except Exception as e:
            print(f'Baidu translate error (attempt {attempt + 1}/{max_retries}): {e}')
            if attempt < max_retries - 1:
                time.sleep(backoff_factor * (2 ** attempt))  # 指数退避
            
    return ''  # 所有重试都失败后返回空字符串 