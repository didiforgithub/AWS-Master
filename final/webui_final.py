import gradio as gr
import os
import time
import get_step
import pdfqa
import markdown
import pdfkit
import answer_generator
import s3up

# 全局变量部分

IF_UPlOADFILE = False
global REPORT
REPORT = ""
TEMPLATE = answer_generator.tutorial_template

# Tool 1 将Textbox的值重置为空
def reset_textbox():
    return gr.update(value="")

# body part
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

# # # part 2 向量检索
def PDF_QA(Querys):
    result = pdfqa.query_folder(queries=Querys, file_folder="./data", model_name='paraphrase-multilingual-mpnet-base-v2',dim = 768, chunk_size=2000, chunk_overlap=20, k=10, thresh=0.5)
    #file_folder="./data", model_name='paraphrase-multilingual-mpnet-base-v2',dim = 768, chunk_size=2000, chunk_overlap=20, k=10, thresh=0.5
    return result
# part 3 答案生成
def LLM_answer(structure,result):

    answer = answer_generator.tutorial_generation_chain({"project_structure": structure, 
                                        "aws_documentation": result, 
                                        "tutorial_template": TEMPLATE})['text']

    return answer
# 修改body形成chatbot格式
def Body(zip_obj,history = []):
    try:
        # ZIP_PATH = upload_file(zip_obj)
        # steps,structure = Get_steps(ZIP_PATH)
        # result = PDF_QA(steps)
        # res = str(result)[:4000]
        # answer = LLM_answer(structure,res)
        answer = "# hello world"
        REPORT = answer
        history.append(("please show me the Deploy documentation", answer))
        return "",history
    except Exception as e:
        print (str(e))
        return str(e)


# Download Part
def Download():
    output_path = "documents/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    html = markdown.markdown(REPORT)
    file_name = f"{time.strftime('%Y%m%d%H%M%S')}.pdf"
    print(file_name)
    print(output_path)
    PDFPATH = os.path.join(output_path, file_name)
    pdfkit.from_string(html, PDFPATH)
    DOWNPATH = s3up.upload_file(PDFPATH)

    return DOWNPATH

# gradio部分

with gr.Blocks() as demo:
    gr.Markdown("## document Part 📃")
    with gr.Row():
        filebot = gr.Chatbot([],elem_id="filebot",height = 500)
    with gr.Row():
        with gr.Column():
            UploadBtn = gr.UploadButton(
                "upload the zip file 📁",
                file_types=["zip"],
                type='bytes'
            )
        with gr.Column():
            DownloadBtn = gr.Button(
                "down load the deploy documentation ⬇️")
    with gr.Row():
        Link = gr.Textbox(
                label = "link",
                container= False,
                placeholder= "Download link here")
    gr.Markdown("## QA Part ❓")
    with gr.Row():
        chatbot = gr.Chatbot([],elem_id="chatbot",height = 300)
    with gr.Row():
        with gr.Column():
            query = gr.Textbox(
                placeholder="upload the zip file ,and we'll tell you how to deploy it",
                container= False
            )

    # demo设计
    # 1. 首先构建一个基础的LLM回复的代码，理清楚Chatbot触发的逻辑
    # 2. 构建body函数的逻辑
    # 3. 拼接与实现
    # 调用LLM，传递两个参数给LLMdemo，一个Query，一个是Chatbot对象

    # Gradio 逻辑设计
    # 1. 点击Upload按钮，上传文件。上传文件结束之后触发Body函数，yield输出report，并保存整体作为一个全局变量，方便之后下载
    UploadBtn.upload(Body, [UploadBtn,filebot], [UploadBtn,filebot])
    # 2. 点击download按钮，调用全局变量report作为输入，调用md转PDF函数进行输出
    DownloadBtn.click(Download,outputs = [Link])
    # 3. 点击txtsubmit按钮，调用全局变量History作为输入，需要包含对话格式，调用LLM进行输出
    query.submit()

demo.queue()
if __name__ == "__main__":
    demo.queue().launch(share=True)