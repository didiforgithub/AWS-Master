def Vector_retrieval(Query):
    result = "text"
    return result

PROMPT_TEMPLATE = """Given Information:{context}

根据上述已知信息，简洁和专业的来回答用户的问题。如果无法从中得到答案，请说 “根据已知信息无法回答该问题” 或 “没有提供足够的相关信息”，不允许在答案中添加编造成分，答案请使用中文。 问题是：{question}"""

def Get_anwser(Context,Query,LLMmodel):
    if LLMmodel == "gpt3.5-turbo-32k":
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role":"system","content":PROMPT_TEMPLATE},
            {"role":"assistant","content":"Query"}
        ]  
        )
    return completion

def LocalChat(Query,LLMmodel):
    context = Vector_retrieval(Query)
    result = Get_anwser(context,Query,LLMmodel)
    return result