import os
from langchain.llms import OpenAI
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from app.modules.web_application.models import PromptLog
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
db = SQLAlchemy(app)


class PromptService:
    def __init__(self):
        self.llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7)

    def process_prompt(self, url, user_prompt):
        try:
            loader = WebBaseLoader(url)
            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )
            split_docs = text_splitter.split_documents(documents)
            summarize_chain = load_summarize_chain(self.llm, chain_type="map_reduce")
            summary = summarize_chain.run(split_docs)
            full_context = f"Website Summary: {summary}\n\nUser Prompt: {user_prompt}"
            response = self.llm(full_context)
            input_tokens = len(full_context.split())
            output_tokens = len(response.split())
            prompt_log = PromptLog(
                prompt=user_prompt,
                response=response,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

            db.session.add(prompt_log)
            db.session.commit()

            return {
                "response": "Generating answer for your query as " + response,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            }

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Processing error: {str(e)}")
