"""Backward-compatible re-export. Prefer backend.agents.prompts.templates."""
from backend.agents.prompts.templates import jobReaderTemplate, systemInstructionTemplate

__all__ = ["jobReaderTemplate", "systemInstructionTemplate"]
