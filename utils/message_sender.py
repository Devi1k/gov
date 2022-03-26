import json
import time

import requests


def messageSender(conv_id, msg, log, link=None):
    # while True:
    # recv = out_pipe.recv()
    # 从模型接收模型的消息 消息格式为
    # print("messageSender getting", recv)
    # if recv['end_flag'] is True:
    #     break
    now_time = round(time.time() * 1000)
    # msg = recv['service']
    if link is not None:
        response = {"conv_id": conv_id, "content": {"text": msg, "link": link}, "type": "text", "timestamp": now_time}
    else:
        response = {"conv_id": conv_id, "content": {"text": msg, "link": ""}, "type": "text", "timestamp": now_time}
    response_json = json.dumps(response)
    # print("sending msg", response_json)
    headers = {'Content-Type': 'application/json'}
    r = requests.post("https://asueeer.com/api/im/send_message?mock_login=123", data=response_json,
                      headers=headers)
    log.info(response['content'])
    log.info(r.json()['meta'])
    # except EOFError:
    #     break
