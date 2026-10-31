from pydantic import BaseModel, Field
from typing import List, Optional


class TicketCreate(BaseModel):
    text: str = Field(
        ...,
        min_length=3,
        description="Customer support ticket text"
    )


class SimilarTicket(BaseModel):
    id: int
    text: str
    category: str
    priority: str
    similarity: float


class KnowledgeBaseResult(BaseModel):
    name: str
    content: str
    similarity: float


class TicketResponse(BaseModel):
    id: Optional[int] = None
    text: str
    category: str
    priority: str
    confidence: float
    method: str
    rule_prediction: str
    rule_confidence: float
    ml_prediction: str
    ml_confidence: float
    suggested_reply: str
    status: str
    similar_tickets: List[SimilarTicket]
    knowledge_base: List[KnowledgeBaseResult]

class TicketStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        description="Ticket status: Open, In Progress, or Resolved"
    )