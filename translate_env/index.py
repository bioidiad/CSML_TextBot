import json, base64
import requests as req
from decouple import config

def translate(string, lang):
    text = str(string)
    jayson = json.dumps({
    "texts": [text],
    "targetLanguageCode": lang
    })
    translate_url = 'https://translate.api.cloud.yandex.net/translate/v2/translate'
    api_token=config('KEY')
    response = req.post(translate_url, headers={'Authorization': f'Api-Key {api_token}',
                                         'Content-Type': 'application/json'}, data=jayson)
    # print(response.status_code, response.reason)
    key = json.loads(response.text)["translations"][0]['text']
    return(key)#.encode('utf-8'))

def main(event, context):
    ret = translate(event["string"], event["lang"])
    try:
        return(ret.encode('latin1').decode('utf-8'))
    except:
        return(ret)

