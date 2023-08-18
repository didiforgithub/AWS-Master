import gradio as gr
import polly2audio

def txt2audio(text):
    t_audio = polly2audio.text_to_speech(text)  # 使用函数的text参数
    return t_audio

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            gr.Audio(source=txt2audio, label="txt Audio", type="auto")  # 添加type="auto"以自动检测音频类型

if __name__ == "__main__":
    demo.launch()


import gradio as gr
import io

def play_audio(text):
    # 使用你的polly函数将文本转换为音频
    audio_data = polly(text)  # 假设polly函数返回一个音频数据流或文件路径

    # 如果polly返回的是文件路径，你可以这样读取它：
    # with open(audio_data, 'rb') as f:
    #     audio_data = f.read()

    # 返回音频数据
    return audio_data

def polly(text):
    # 这里是你的polly函数实现，返回音频数据或文件路径
    pass

# 创建Gradio界面
iface = gr.Interface(
    fn=play_audio, 
    inputs="text", 
    outputs=gr.outputs.Audio(source="URL", label="Audio", type="auto",visible = False),
    live=True
)
