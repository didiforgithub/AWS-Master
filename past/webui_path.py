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

with gr.Blocks() as demo:
    gr.Markdown("# welcome to use ZIP Deploy"),
    with gr.Row():
        file_input = gr.File(file_types=["zip"],type='binary',label="Please submit zip")
    with gr.Row():
        PATH = gr.Text(label="FILE PATH")
    btn = gr.Button("Deploy")
    btn.click(upload_file, inputs=[file_input], outputs=[PATH])

if __name__ == "__main__":
    demo.launch(share=True)