import gradio as gr
import os

def MarkdownDisplay(Query):

    return f'''<div style="border:1px solid black; padding:10px; margin:10px;">
    
    \n{Query}\n
    
    </div>'''

with gr.Blocks() as demo:
    gr.Markdown("# Welcome to Markdown Display"),
    with gr.Row():
        text_input = gr.Text(label = "输入文本")
    btn = gr.Button("Deploy")
    with gr.Row():
        mark_output = gr.Markdown()
    
    btn.click(MarkdownDisplay, inputs=[text_input], outputs=[mark_output])

if __name__ == "__main__":
    demo.launch(share=False)