import gradio as gr
import os
import time
import get_step
import pdfqa
import answer_generator

TEMPLATE = answer_generator.tutorial_template

# part -1 替换字符
def replace_multiple_backticks(s):
    while '```' in s:
        s = s.replace('```', '`')
    return s

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
    result = pdfqa.query_folder(queries=Querys, file_folder="./data", model_name='paraphrase-multilingual-mpnet-base-v2',dim = 768, chunk_size=2000, chunk_overlap=20, k=10, thresh=0.5)
    #file_folder="./data", model_name='paraphrase-multilingual-mpnet-base-v2',dim = 768, chunk_size=2000, chunk_overlap=20, k=10, thresh=0.5
    return result
# part 3 流式生成
def LLM_answer(structure,result):

    answer = answer_generator.tutorial_generation_chain({"project_structure": structure, 
                                        "aws_documentation": result, 
                                        "tutorial_template": TEMPLATE})['text']

    return answer

def Body(zip_obj):
    try:
        ZIP_PATH = upload_file(zip_obj)
        steps,structure = Get_steps(ZIP_PATH)
        result = PDF_QA(steps)
        answer = LLM_answer(structure,result)
        return answer
    except Exception as e:
        print (str(e))
        return str(e)


with gr.Blocks() as demo:
    gr.Markdown("# Welcome to use ZIP Deploy ⚡"),
    with gr.Row():
        file_input = gr.File(file_types=["zip"],type='binary',label="Please submit zip")
    btn = gr.Button("Deploy")
    with gr.Row():
        markdown_output = gr.Markdown()
    
    btn.click(Body, inputs=[file_input], outputs=[markdown_output])

if __name__ == "__main__":
    demo.queue().launch(share=True)