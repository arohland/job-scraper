import json
import os
import anthropic
from .logger import get_logger
from .models import Job

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a job relevance classifier. You will be given a job posting and must decide
whether it is relevant for a specific candidate.

Candidate profile:
- Education: Master of Science in wildlife ecology / wildlife management + Diploma as veterinarian
- Target role: Professional position (no internships, no student jobs, no volunteer positions)
- Field: Wildlife ecology, wildlife management, conservation biology, wildlife veterinary medicine,
  nature conservation, environmental science, national park management
- Location preference: Salzburg region (Austria) and neighboring areas (Bavaria, Tyrol, Carinthia, Styria)
- Not relevant: maintenance/facility staff, administrative/office-only roles, tourism guides,
  IT roles, cooking/hospitality, cleaning, construction, purely agricultural roles

Respond with exactly this JSON format, nothing else:
{"relevant": true, "reason": "one short sentence"}
or
{"relevant": false, "reason": "one short sentence"}"""


def filter_jobs_by_relevance(jobs: list[Job], config: dict) -> list[Job]:
    """Return only jobs the LLM judges relevant for the candidate profile."""
    api_key = config.get("llm", {}).get("api_key") or os.getenv("ANTHROPIC_API_KEY")
    model = config.get("llm", {}).get("model", "claude-haiku-4-5-20251001")

    if not api_key:
        logger.warning("No ANTHROPIC_API_KEY found — skipping relevance filter, sending all jobs")
        return jobs

    client = anthropic.Anthropic(api_key=api_key)
    relevant = []

    for job in jobs:
        text = f"Title: {job.title}"
        if job.description:
            text += f"\nDescription: {job.description[:1000]}"

        try:
            message = client.messages.create(
                model=model,
                max_tokens=100,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": text}],
            )
            raw = message.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```", 2)[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            result = json.loads(raw.strip())
            job.llm_relevant = result.get("relevant")
            job.llm_reason = result.get("reason", "")
            if job.llm_relevant:
                logger.info(f"Relevant: '{job.title}' — {job.llm_reason}")
                relevant.append(job)
            else:
                logger.info(f"Filtered out: '{job.title}' — {job.llm_reason}")
        except Exception as e:
            logger.error(f"LLM filter failed for '{job.title}': {e} — including job to be safe")
            job.llm_relevant = None
            job.llm_reason = f"filter error: {e}"
            relevant.append(job)

    logger.info(f"Relevance filter: {len(relevant)}/{len(jobs)} jobs passed")
    return relevant
