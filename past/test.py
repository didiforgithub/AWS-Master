import gradio as gr
import random
import time

# 判断是否已经执行过部署
def is_depolyed():
    deployed = False
    return deployed

# 定义聊天机器人的回答函数
def get_response(msg, deployed):
    if not deployed:
        return "请先点击deploy按钮"
    response = 'ok'
    return response

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.Button("清除")

    def respond(message, chat_history):
        bot_message = get_response(msg, is_deployed)
        chat_history.append((message, bot_message))
        time.sleep(1)
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

demo.launch(share=True)
