import gradio as gr
import random
import time
import answer_generator_streaming as answer_generator

file_uploaded = False


# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.

def add_text(documentation, text):
    documentation = documentation + [(text, None)]
    return documentation, gr.update(value="", interactive=False)


def add_file(history, file):
    history = history + [((file.name,), None)]
    return history


def bot(history):
    response = "**That's cool!**"
    history[-1][1] = ""
    for character in response:
        history[-1][1] += character
        time.sleep(0.05)
        yield history

def bool_upload_file():
    global file_uploaded
    if not file_uploaded:
        return [("User","Sorry I haven't upload zip file"),("Chatbot","please upload zip first")]
    else:
        pass

# 在测试版本的Chatbot中，我们输入的是与文档相关的内容，其余的都是使用demo进行测试的
def LLM_answer(documentation):
    bool_upload_file()
    answer = answer_generator.tutorial_generation_chain(
        {"project_structure": answer_generator.demo_project_structure, 
        "aws_documentation": documentation, 
        "tutorial_template": answer_generator.tutorial_template})
    
    for chunk in answer:
        cunrrent_chunk = ""
        for character in chunk:
            cunrrent_chunk += character
            time.sleep(0.05) # 添加打字效果，但是为什么是这样的
            yield cunrrent_chunk

with gr.Blocks() as demo:
    chatbot = gr.Chatbot([], elem_id="chatbot",height=300)

    with gr.Row():
        with gr.Column(scale=0.85):
            txt = gr.Textbox(
                show_label=False,
                placeholder="upload the zip file ,and we'll tell you how to deploy it",
                container=False
            )
        with gr.Column(scale=0.15, min_width=0):
            btn = gr.UploadButton("📁", file_types=["zip"],type='bytes')

    # 在按钮被电击到的时候，触发Upload文件，传递参数，在执行完之后，使用LLM answer传递
    btn.upload(add_file,[chatbot,btn],[chatbot],queue = False).then(
        LLM_answer,chatbot,chatbot
    )
    # btn.click(LLM_answer, inputs=[txt], outputs=chatbot)

    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
        LLM_answer, chatbot, chatbot
    )
    # txt_msg.then(lambda: gr.update(interactive=True), None, [txt], queue=False)
    # file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False).then(
    #     bot, chatbot, chatbot
    # )

# 当前的逻辑是，提交文件之后，就应该马上向LLM执行命令请求返回结果，同时使用的是yield做流式输出
demo.queue()
if __name__ == "__main__":
    demo.launch(share=False)
