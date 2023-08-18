import gradio as gr
import os
import time
import get_step
import pdfqa
import answer_generator
import markdown
import re

TEMPLATE = answer_generator.tutorial_template

# part -1 将markdown code块 修改为 行内代码

def markdown_code_to_html(text):
    # 使用一个函数作为替换操作
    def replacer(matchobj):
        # 这是一个闭包，使用外部的counter变量来跟踪替换次数
        if replacer.counter % 2 == 0:
            replacement = "<code>"
        else:
            replacement = "</code>"
        replacer.counter += 1
        return replacement
    replacer.counter = 0
    
    # 使用正则表达式替换操作
    return re.sub(r"```", replacer, text)

# part 0 上传文件
def upload_file(zip_obj):

    ZIP_PATH = "zips/"
    if not os.path.exists(ZIP_PATH):
        os.makedirs(ZIP_PATH)
    
    file_name = f"{time.strftime('%Y%m%d%H%M%S')}.zip"
    zip_path = os.path.join(ZIP_PATH, file_name)

    try:
        with open(zip_path, 'wb') as f:
            if not zip_obj:
                return "No file"
            f.write(zip_obj)
    except Exception as e:
        return f"Error: {str(e)}"
    return zip_path

# part 1 获取步骤
def Get_steps(ZIP_PATH):

    # 文件存储路径
    FILEPATH = "files/"
    if not os.path.exists(FILEPATH):
        os.makedirs(FILEPATH)
        
    # 为当前解压的文件夹添加唯一名称
    FOLDER_NAME = f"{time.strftime('%Y%m%d%H%M%S')}"
    FOLDER_PATH = os.path.join(FILEPATH,FOLDER_NAME)

    get_step.unzip_file(ZIP_PATH, FOLDER_PATH) # 解压文件
    structure = get_step.parse_dir(FOLDER_PATH) # 生成目录结构
    steps = get_step.get_steps2deploy(structure) # 生成steps

    return steps,structure

# # part 2 向量检索
def PDF_QA(Querys):
    result = pdfqa.query_pdf_folder(queries=Querys, pdf_folder="./data")
    return result
# part 3 流式生成
def LLM_answer(structure,result):

    answer = answer_generator.tutorial_generation_chain({"project_structure": structure, 
                                        "aws_documentation": result, 
                                        "tutorial_template": TEMPLATE})['text']

    return answer

def Body(zip_obj):

    ZIP_PATH = upload_file(zip_obj)
    steps,structure = Get_steps(ZIP_PATH)
    result = PDF_QA(steps)
    answer = LLM_answer(structure,result)
    # answer = LLM_answer(structure,"AWS Documentation Unavailable")
    # 将其中的三个```修改
    answer = markdown_code_to_html(answer)  # 使用上面定义的函数转换
    print(answer)
    return answer


with gr.Blocks() as demo:
    gr.Markdown("# Welcome to use ZIP Deploy ⚡"),
    with gr.Row():
        file_input = gr.File(file_types=["zip"],type='binary',label="Please submit zip")
    btn = gr.Button("Deploy")
    with gr.Row():
        markdown_output = gr.Markdown()
    
    btn.click(Body, inputs=[file_input], outputs=[markdown_output])

if __name__ == "__main__":
    demo.launch(share=True)