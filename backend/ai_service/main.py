from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from openai import OpenAI
import hashlib, time
from .db import SessionLocal
from .models import Contact, Conversation, Message
from .schemas import ChatTurn, ChatReply
from .settings import settings
from .pinecone_client import index as pindex

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "You are 'Hallo' for JuzoGO: friendly, concise, human. "
    "Greet casually, ask natural follow-ups, never sound robotic. "
    "Identify if the user is a driver, rider, partner, or general. "
    "Collect: name, email, phone, city/ZIP, role. "
    "If driver: vehicle type, experience, docs. If rider: preferred pickup areas. "
    "Offer to set a callback time if helpful. "
    "Confirm key details back briefly before moving on."
)

EXTRACT_PROMPT = (
    "From the conversation, extract any of: name, email, phone, city, zip, role, vehicle, experience, callback_time.\n"
    "Respond as JSON with those keys only when present."
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- helpers ---

def embed(text: str):
    vec = client.embeddings.create(model="text-embedding-3-small", input=text)
    return vec.data[0].embedding

def upsert_message_embedding(conversation_id: str, role: str, content: str, meta: dict):
    vector = embed(content)
    vid = hashlib.sha1(f"{conversation_id}-{time.time()}".encode()).hexdigest()
    pindex.upsert(vectors=[{
        "id": vid,
        "values": vector,
        "metadata": {"conversation_id": conversation_id, "role": role, "content": content, **(meta or {})}
    }])

@app.post("/chat", response_model=ChatReply)
def chat(turn: ChatTurn, db: Session = Depends(get_db)):
    # ensure contact + conversation
    contact = None
    if turn.contact_hint and (turn.contact_hint.get("email") or turn.contact_hint.get("phone")):
        q = db.query(Contact)
        if turn.contact_hint.get("email"):
            contact = q.filter(Contact.email == turn.contact_hint["email"]).first()
        if not contact and turn.contact_hint.get("phone"):
            contact = q.filter(Contact.phone == turn.contact_hint["phone"]).first()
    if not contact:
        contact = Contact(role=turn.contact_hint.get("role") if turn.contact_hint else None)
        db.add(contact); db.commit(); db.refresh(contact)

    if not turn.conversation_id:
        convo = Conversation(contact_id=contact.id, channel=turn.channel)
        db.add(convo); db.commit(); db.refresh(convo)
        conversation_id = str(convo.id)
    else:
        conversation_id = turn.conversation_id

    # store user message
    msg = Message(conversation_id=conversation_id, role="user", content=turn.message)
    db.add(msg); db.commit()
    upsert_message_embedding(conversation_id, "user", turn.message, {"contact_id": str(contact.id)})

    # generate assistant reply
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": turn.message}
        ],
        temperature=0.6
    )
    reply_text = completion.choices[0].message.content

    # extract structured fields
    extractor = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": EXTRACT_PROMPT},
            {"role": "user", "content": f"Conversation so far: {turn.message}\nAssistant: {reply_text}"}
        ],
        temperature=0
    )
    import json
    extracted = {}
    try:
        extracted = json.loads(extractor.choices[0].message.content)
    except Exception:
        extracted = {}

    # update contact with any extracted fields
    changed = False
    for k in ["name","email","phone","city","zip","role"]:
        if k in extracted and extracted[k]:
            seta
