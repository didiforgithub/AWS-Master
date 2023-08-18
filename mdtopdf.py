import hashlib
from s3up import up_load_s3
from md2pdf.core import md2pdf

def md_to_s3(markdown_text):
    """
    输入一个markdown字符串，返回一个s3的md地址
    """
    # Generate a unique filename based on the content of the Markdown text
    md5_hash = hashlib.md5(markdown_text.encode()).hexdigest()
    md_filename = f"{md5_hash}.md"
    pdf_filename = f"{md5_hash}.pdf"

    with open(md_filename, 'w') as f:
        f.write(markdown_text)
    # md2pdf(pdf_filename,
    #    md_content=markdown_text,
    #    md_file_path=None,
    #    css_file_path=None,
    #    base_url=None)
    url = up_load_s3(md_filename)
    return url
