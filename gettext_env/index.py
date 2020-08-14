import base64, json, re
import requests as req
from decouple import config
from requests.exceptions import Timeout


def encode_file(url):
    if url.startswith("'") and url.endswith("'"):
        url = url[1:-1]
    url = url.replace("\n", "")
    try:
        file = req.get(url, allow_redirects=True)
    except Timeout:
        print('The request timed out')
    file_content = file.content
    if re.match('.*\.pdf$', url) != None:
        file_type = "application/pdf"
    else:
        file_type = "image"
    result = [base64.b64encode(file_content).decode('utf-8'), file_type]
    return(result)

def provide_json(data):
    res = json.dumps({'analyze_specs': [{'content': data[0], "mime_type": data[1], 'features': [{'type': 'TEXT_DETECTION', 'text_detection_config': {'language_codes': ['*']}}]}]})
    return(res)

def request_analyze(jayson):
    vision_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'
    api_key=config('KEY')
    try:
        response = req.post(vision_url, headers={'Authorization': f'Api-Key {api_key}',
                                         'Content-Type': 'application/json'}, data=jayson)
    except Timeout:
        return("Timeout")
    # print(response.status_code, response.reason)
    return(response.text)

def parser(jayson):
    text = json.loads(jayson)
    # print(ujson.dumps(text, indent=4, sort_keys=True))
    # fd = open("output.txt", mode='a', encoding='utf-8')
    buffer = ""

    if 'error' in text['results'][0]:
        return text['results'][0]['error']['message']

    pages = text['results'][0]['results'][0]['textDetection']['pages']
    for page in range(len(pages)):
        y = 0
        space = 0
        for block in range(len(pages[page]['blocks'])):
            current_block = pages[page]['blocks'][block]
            y0 = int(pages[page]['blocks'][block]['boundingBox']['vertices'][0]['y'])
            if y0 + 5 <= y or y0 - 5 >= y and y != 0:
                buffer += '\n'
                space = 0
            y = int(pages[page]['blocks'][block]['boundingBox']['vertices'][0]['y'])
            for line in current_block['lines']:
                for word in line['words']:
                    buffer += ' ' + word['text'] if space == 1 else word['text']
                    space = 1
    return buffer


def main(event, context):
    data = encode_file(event['url'])
    result = provide_json(data)
    jayson = request_analyze(result)
    ret = parser(jayson)
    # print(ret)
    return ret

# if __name__=='__main__':
#     url = { "url": ""}
#     context = {}
#     main(url, context)


