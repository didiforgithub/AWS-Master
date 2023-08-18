import gradio as gr
import random
import time

def respond(message,chat_history):
    bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
    chat_history.append((message, bot_message))
    time.sleep(2)
    return "", chat_history

def hello(message,chat_history):
    bot_message = "hello world"
    for chunk in bot_message:
        chat_history.append((message,bot_message))
        time.sleep(0.05)
        yield "",chat_history

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    msg.submit(hello,[msg,chatbot],[msg,chatbot])


if __name__ == "__main__":
    demo.queue().launch()
