import requests


def get_answer(first_utterance, service_name):
    # --FAQ
    faq_path = "https://miner.picp.net/FAQ?First_utterance={}&Service_name={}"
    faq_res = requests.get(faq_path.format(first_utterance, service_name)).json()
    similar_score, answer = faq_res['Similarity_score'], faq_res['answer']
    # print("FAQ:", similar_score, answer)

    if float(similar_score) > 0.5:
        return answer
    else:
        # --intention detection
        intent_path = "https://miner.picp.net/intent?text={}"
        intent_res = requests.get(intent_path.format(first_utterance)).json()
        intent_class = intent_res['data']
        # print("intention:", intent_class)

        if intent_class == "qa":  # --QA match
            qamatch_path = "https://burninghell.xicp.net/QAMatch?serviceName={}&question={}"
            context = requests.get(qamatch_path.format(service_name, first_utterance)).text
            # print("QA match: ", context)
            # --QA
            qa_path = "https://miner.picp.net/qa?context={}&question={}"
            res = requests.get(qa_path.format(context, first_utterance)).json()
            score, answer = res['score'], res['answer']
            # print("QA: ", score, answer)
            return answer

        elif intent_class == "infer":  # --NLI
            nli_path = "https://burninghell.xicp.net/zmytest?Service_name={}&First_utterance={}"
            nli_res = requests.get(nli_path.format(service_name, first_utterance)).text
            # print("NLI: ", nli_res)
            return nli_res

        elif intent_class == "retrieval":  # --IR
            ir_path = "https://burninghell.xicp.net/IR?serviceName={}&firstUtterance={}"
            ir_res = requests.get(ir_path.format(service_name, first_utterance)).json()['abs']
            # print("IR: ", ir_res)
            return ir_res

        else:  # --diagnose
            # print("diagnosis: ", service_name)
            return service_name
