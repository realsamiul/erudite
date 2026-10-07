from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AdvisorQueryRequest(BaseModel):
    question: str = Field(..., description="The query or question regarding university admissions/aid.")
    session_id: str = Field(..., description="Uniquely identifies the student's counseling session.")
    category: str = Field("statutes", description="Target datastore category: statutes | it_security | clinical_safety")

class MetricCard(BaseModel):
    label: str = Field(..., description="Brief visual metric title, e.g. 'Average Financial Aid'")
    value: str = Field(..., description="High-impact display value, e.g. '$66,093'")
    badge_type: str = Field("info", description="UI styling context: success | info | warning | danger")

class ChartSpec(BaseModel):
    type: str = Field("pie", description="Frontend widget type: pie | bar | gauge")
    title: str = Field(..., description="Descriptive title of the visualization.")
    data: Dict[str, Any] = Field(..., description="Key-value mapping of visualization slices/values.")

class AuditFeedback(BaseModel):
    loopholes: str = Field(..., description="Critical evaluation of potential document gaps, EFC inflation risks, or policy loopholes.")
    curriculum_warnings: str = Field(..., description="Guidance regarding SSC/HSC national curriculum vs Cambridge A-Level recognition barriers.")
    pipeline_alerts: str = Field(..., description="Analysis of known feeder high school pipelines and institutional familiarity biases.")

class AdvisorQueryResponse(BaseModel):
    greeting: str = Field(..., description="Warm, brief, empathetic counselor intro.")
    answer: str = Field(..., description="Main grounding-backed concise advisory response (Markdown supported).")
    quick_stats: List[MetricCard] = Field(default=[], description="Visual cards summarizing key admission/aid metrics.")
    charts: List[ChartSpec] = Field(default=[], description="Structured chart directives for clean, scannable frontend visual rendering.")
    audit_feedback: AuditFeedback = Field(..., description="Rigorous adversarial self-audit and reality checks on the output.")
    provenance_hash: str = Field(..., description="Cryptographic signature of the audited conversation chain.")
