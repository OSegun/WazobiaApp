from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import os

load_dotenv()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/translate")
async def translate(request: Request):
    form_data = await request.form()
    prompt = form_data.get("text")
    language = form_data.get("language")

    trans_template = PromptTemplate(
        input_variables=['trans'],
        template='Your task is to translate this text to ' + language + 'TEXT: {trans}'
    )

    # Memory
    memory = ConversationBufferMemory(input_key='trans', memory_key='chat_history')

    # LLMs
    llm = OpenAI(model_name="text-davinci-003", temperature=0)
    trans_chain = LLMChain(llm=llm, prompt=trans_template, verbose=True, output_key='translate', memory=memory)

    response = {}
    if prompt:
        response = trans_chain({'trans': prompt})

    return templates.TemplateResponse("translate.html", {"request": request, "response": response})

if __name__ == "__main__":
    load_dotenv()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
