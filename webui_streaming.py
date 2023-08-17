import gradio as gr
import os
import time
def upload_file(zip_obj):

    SAVE_PATH = "zips/"
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
    
    file_name = f"{time.strftime('%Y%m%d%H%M%S')}.zip"
    file_path = os.path.join(SAVE_PATH, file_name)

    try:
        with open(file_path, 'wb') as f:
            if not zip_obj:
                return "No file"
            f.write(zip_obj)
    except Exception as e:
        return f"Error: {str(e)}"
    return file_path

def LS(FILEPATH):
    with open("/Users/mac/Project/AWS/hello.md", 'r',encoding='utf-8') as f:
        content = f.read()

    return content

def LLM_answer(content):
    result = content

    return f'''<div style="border:1px solid black; padding:10px; margin:10px;">

    \n{result}\n

    '''

def Body(zip_obj):
    FILEPATH = upload_file(zip_obj)
    content = LS(FILEPATH)
    result = LLM_answer(content)
    return result

with gr.Blocks() as demo:
    gr.Markdown("# Welcome to use ZIP Deploy ⚡"),
    with gr.Row():
        file_input = gr.File(file_types=["zip"],type='binary',label="Please submit zip")
    btn = gr.Button("Deploy")
    with gr.Row():
        mark_output = gr.Markdown()
    
    btn.click(Body, inputs=[file_input], outputs=[mark_output])

if __name__ == "__main__":
    demo.launch(share=False)