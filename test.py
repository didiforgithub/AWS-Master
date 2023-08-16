import gradio as gr
import os
import time

# 上传file并存储到特定的路径之中
def file_Upload(file_obj):

    print(file_obj)

    SAVE_PATH = "files/"
    # 如果路径不存在，就创建文件夹
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    # gradio上传文件，name是一个极长的Path，提取basename
    # file_name = os.path.basename(file_obj.name)
    file_path = os.path.join(SAVE_PATH, file_obj.name)
    print(file_obj.name)

    # 存储到本地
    try:

        with open(file_path, "wb") as f:
            file_obj.seek(0)
            data = file_obj.read()
            if not data:
                return "Error: Uploaded file is empty!"
            f.write(data)
        return file_path
    except Exception as e:
        return f"Error: {str(e)}"

demo = gr.Interface(
    file_Upload,
    inputs = gr.File(file_types=["zip"],type='file'),
    outputs="text",
    live=True)

if __name__ == "__main__":
    demo.launch()

