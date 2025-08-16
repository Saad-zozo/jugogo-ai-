from sqlalchemy import Column, String, Text, Numeric, Boolean, ForeignKey, JSON, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .db import Base

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id = Column(UUID(as_uuid=True), nullable=True)
    role = Column(String)
    name = Column(Text)
    email = Column(Text)
    phone = Column(Text)
    city = Column(Text)
    zip = Column(Text)
    verified_email = Column(Boolean, default=False)
    verified_phone = Column(Boolean, default=False)
    sentiment_avg = Column(Numeric, default=0)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"))
    channel = Column(String)
    status = Column(String)
    last_intent = Column(Text)
    last_summary = Column(Text)

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    role = Column(String)
    content = Column(Text)
    sentiment = Column(Numeric)
    meta = Column(JSON)

class Event(Base):
    __tablename__ = "events"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"))
    type = Column(String)
    run_at = Column(Text)  # store ISO string; or use TIMESTAMPTZ with SQLAlchemy types
    payload = Column(JSON)
    status = Column(String)
