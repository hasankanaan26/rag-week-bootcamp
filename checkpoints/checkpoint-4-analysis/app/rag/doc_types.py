# ============================================================
# Doc types — a small, fixed set of labels for every chunk
# ============================================================
# Each chunk gets a doc_type at ingest time, based on the file
# it came from. At query time the LLM picks one of these labels
# for the question, and retrieval searches only that doc type.
#
# WHY A FIXED LIST?
#   The classifier can only answer with a label we actually
#   stored. If it invents "hr" while the chunks say "policy",
#   the filter matches nothing. A closed list keeps both sides
#   in sync.
#
# TEACHING POINT:
#   A filter is a hard cut: chunks outside the doc type cannot
#   come back at all. The FAQ is a good example. It answers
#   policy questions too, but a "policy" filter skips it.
#   The no-filter fallback in retriever.py is the safety net.
#
# TODO (Lab exercise): Add a new file to data/knowledge, map it
# here, re-ingest, and ask a question the classifier should
# route to it.
# ============================================================

# The labels the classifier may choose, with a description it can read
DOC_TYPES = {
    "policy": "HR and company rules: annual leave, sick leave, expenses, reimbursements, remote work",
    "engineering": "coding standards, code review, Git workflow, testing, the technology stack and tools",
    "people": "the team directory: who someone is, their role, department, office or email",
    "onboarding": "what new employees do in their first days and weeks",
    "meetings": "meeting notes: decisions, plans, hiring and budget discussions",
    "faq": "short answers to common employee questions on mixed topics",
}

# Which doc type each knowledge file belongs to
SOURCE_DOC_TYPES = {
    "leave-policy.md": "policy",
    "expense-policy.md": "policy",
    "expense-policy-2024-update.md": "policy",
    "remote-work.md": "policy",
    "coding-standards.md": "engineering",
    "tech-stack.md": "engineering",
    "team-directory.csv": "people",
    "onboarding-checklist.md": "onboarding",
    "meeting-notes.md": "meetings",
    "company-faq.md": "faq",
}

# Files not listed above. Never chosen by the classifier, so these
# chunks are only found by unfiltered search.
UNKNOWN_DOC_TYPE = "other"


# Purpose:
# Looks up the doc type for a knowledge file by its filename.
def get_doc_type(source: str) -> str:
    """Return the doc type for a source filename, or 'other' if unmapped."""
    return SOURCE_DOC_TYPES.get(source, UNKNOWN_DOC_TYPE)
