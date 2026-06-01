"""Backward-compatible re-export. Prefer backend.agents.prompts.templates."""
from backend.agents.prompts.templates import (
    analysisJsonPrompt,
    jobReaderTemplate,
    systemInstructionTemplate,
)

__all__ = ["analysisJsonPrompt", "jobReaderTemplate", "systemInstructionTemplate"]
