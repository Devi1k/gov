import asyncio
import json
from multiprocessing import Pipe, Process

import gensim
import websockets

from ai_wrapper import get_answer
from conf.config import get_config
from gov.running_steward import simulation_epoch
from message_sender import messageSender


async def main_logic(para, mod):
    response_json = '''
        {"type":101,"msg":{"conv_id":"1475055770457346048"}}
        '''
    user_json = json.loads(response_json)

    global first_utterance
    global service_name
    global conv_id
    while True:
        async with websockets.connect('wss://asueeer.com/ws?mock_login=123') as websocket:
            data = {"type": 101, "msg": {"conv_id": "1475055770457346048", "content": {
                "judge": True, "text": '护照丢了怎么办'
            }, }}
            s = json.dumps(data, ensure_ascii=False)
            await websocket.send(s)  # 测试接口
            response = await websocket.recv()

            # for res in test_text:
            # response = res
            user_json = json.loads(response)
            msg_type = user_json['type']
            msg = user_json['msg']
            conv_id = msg['conv_id']
            print(user_json)
            # 首次询问
            if conv_id not in pipes_dict:
                print("new conv")
                user_pipe, response_pipe = Pipe(), Pipe()
                pipes_dict[conv_id] = [user_pipe, response_pipe]
                Process(target=simulation_epoch, args=((user_pipe[1], response_pipe[0]), para, mod)).start()
                # Process(target=messageSender, args=(conv_id, end_flag, response_pipe[1], user_pipe[0])).start()
            else:
                if first_utterance == "":
                    first_utterance = msg['content']  # TODO:? 是放在这里还是上面
                user_pipe, response_pipe = pipes_dict[conv_id]
                user_text = msg['content']
                # 初始化会话后 向模型发送判断以及描述（包括此后的判断以及补充描述
                user_pipe[0].send(user_text)
                recv = response_pipe[1].recv()
                # 从模型接收模型的消息 消息格式为
                """
                {
                    "service": agent_action["inform_slots"]["service"] or ,   service为业务名
                    "end_flag": episode_over  会话是否结束
                }
                """
                # 没结束 继续输入
                if recv['end_flag'] is not True:
                    # todo: message_sender
                    msg = recv['service']
                    print(msg)
                    messageSender(conv_id, msg)
                # 结束关闭管道
                else:
                    user_pipe[0].close()
                    response_pipe[1].close()
                    service_name = recv['service']
                    break


if __name__ == '__main__':
    end_flag = "END"
    pipes_dict = {}
    first_utterance, service_name = "", ""
    model = gensim.models.Word2Vec.load('data/wb.text.model')
    config_file = './conf/settings.yaml'
    parameter = get_config(config_file)
    asyncio.get_event_loop().run_until_complete(main_logic(parameter, model))
    print("first_utterance: ", first_utterance)
    print("service_name: ", service_name)
    answer = get_answer(first_utterance, service_name)
    print(answer)
    # todo: 将字符串answer发给前端
    messageSender(conv_id, answer)
