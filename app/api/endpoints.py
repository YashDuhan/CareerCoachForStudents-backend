from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from pydantic import BaseModel
from .pdf_handler import extract_text_from_pdf
import os
from dotenv import load_dotenv
from groq import Groq

# Load env
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

# response schema
class AskQuestionRequest(BaseModel):
    extracted_text: str
    question: str
    previous_convo: list[list[str]]

# endpoint for upload
@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
):
    MAX_FILE_SIZE = 4 * 1024 * 1024 # size cap of 4 mb

    # validation
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    # size check
    file_data = await file.read()
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds the 4 MB limit")
    await file.seek(0)

    text = extract_text_from_pdf(file_data)


    return {"filename": file.filename, "extracted_text": text}

# endpoit for /ask
@app.post("/ask")
async def ask_question(request: AskQuestionRequest):
    try:
        completion = client.chat.completions.create(
            model="mistral-saba-24b",
            messages=[
                {"role": "system", "content": "You are an AI career coach advisor. Your role is to analyze the provided resume or job description context and offer professional career advice, job search strategies, interview preparation tips, and resume improvement suggestions. Be specific, actionable, and supportive in your guidance."},
                {"role": "user", "content": f"Context: {request.extracted_text}"},
                {"role": "user", "content": f"Question: {request.question}"},
                {"role": "user", "content": f"Previous Conversation: {request.previous_convo}"}
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        answer = completion.choices[0].message.content if completion.choices else None
        if answer:
            return {"answer": answer}
        else:
            raise HTTPException(status_code=500, detail="No response, try again")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {e}")
