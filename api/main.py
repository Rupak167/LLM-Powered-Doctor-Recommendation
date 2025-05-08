import os
from environs import Env
from fastapi import FastAPI
from scripts import DoctorFaissIndex
from mistralai import Mistral

from model import UserQuery

env = Env()
env.read_env()


app = FastAPI()

# Initialize FAISS searcher and Mistral client
searcher = DoctorFaissIndex()
searcher.load_index()
mistral = Mistral(api_key=env.str("LLM_API_KEY"))
MODEL_NAME = "mistral-large-latest"



def format_doctor_data(doctors):
    return "\n\n".join([
        f"Name: {doc['name']}\n"
        f"Specialization: {doc.get('specialization', 'N/A')}\n"
        f"Hospital: {doc.get('hospital_info', '')}\n"
        f"Address: {doc.get('hospital_address', '')}\n"
        f"Available: {', '.join([a for a in doc.get('availability', []) if a])}\n"
        f"Tags: {', '.join(doc.get('tags', []))}\n"
        f"URL: {doc['doctor_url']}"
        for doc in doctors
    ])

@app.post("/search/")
async def search_doctor(query: UserQuery):
    print(f"Got query: {query}")
    search_string = f"{query.symptom} {query.location} {query.specialization or ''}"
    matched_doctors = searcher.search(search_string.strip(), k=5)

    # If no results, return early
    if not matched_doctors:
        return {"message": "No matching doctors found."}

    # Format prompt for Mistral
    doc_text = format_doctor_data(matched_doctors)
    prompt = f"""
    User is located in {query.location} and experiencing: {query.symptom}.
    Specialization: {query.specialization or 'Not provided'}.

    Using the following doctor options, recommend the most relevant ones with address and availability with time if there is time available and url don't include tags and explain briefly why.

    Doctors:
    {doc_text}
    """

    # Call Mistral
    response = mistral.chat.complete(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You're a medical assistant helping users find the right doctor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return {
        "raw_doctors": matched_doctors,
        "llm_summary": response.choices[0].message.content.strip()
    }
