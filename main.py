from fastapi import FastAPI, Depends, HTTPException, Request
# import sqlalchemy
# from sqlalchemy import create_engine, Column, Integer, String, Sequence
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
from fastapi.responses import StreamingResponse
import openai
from openai import OpenAI

import os
from pydantic import BaseModel

# from fastapi.utils import jsonable_encoder

class Question(BaseModel):
    question: str
    
from dotenv import load_dotenv # uncomment for local development, loads key from .env file.
load_dotenv()  # <-- Add this line to load environment variables from .env

# Fetch environment variables
DATABASE_URL = os.getenv('DATABASE_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Database setup
# database = sqlalchemy.create_engine(DATABASE_URL)
# metadata = sqlalchemy.MetaData()
# Base = declarative_base()

# class Document(Base):
#     __tablename__ = 'documents'
#     id = Column(Integer, Sequence('doc_id_seq'), primary_key=True)
#     vectorized_content = Column(String)

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(bind=engine)
# Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()
client = OpenAI(api_key=OPENAI_API_KEY)

# OpenAI API setup


# Middleware for Authorization (very basic)
# @app.middleware("http")
# async def check_auth(request: Request, call_next):
#     # Implement your own auth-check logic here
#     authorized = request.headers.get("Authorization")
#     if not authorized:
#         raise HTTPException(status_code=400, detail="Not authorized")
#     response = await call_next(request)
#     return response

@app.post("/ask/")
async def ask_car_question(question_data: Question):
    question = question_data.question
    # Search in vectorized documents
    relevant_docs = []

    # with SessionLocal() as session:
    #     # For simplicity, I'm just getting all docs. You should implement vector search.
    #     docs = session.query(Document).all()
    #     for doc in docs:
    #         # This is a placeholder for your vector search logic.
    #         if any(word in doc.vectorized_content for word in question.split()):
    #             relevant_docs.append(doc.vectorized_content)

    # # Send question and relevant_docs to OpenAI API
    # response = openai.Completion.create(
    #     engine="davinci",
    #     prompt=question + "\n" + "\n".join(relevant_docs),
    #     max_tokens=150
    # )
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ],
        stream=True,
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    import sys
    def generate_response():
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content is not None:
                sys.stdout.write(content)
                sys.stdout.flush()
                yield content

    # Use the generator with StreamingResponse
    return StreamingResponse(generate_response(), media_type="text/plain")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

