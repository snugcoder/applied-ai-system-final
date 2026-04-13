"""
LLM-powered schedule verifier for PawPal+.

ScheduleVerifier takes the output of Scheduler.generate_plan() and asks Gemini
to check three rules:
  1. TIME       — total scheduled duration <= owner's time_available
  2. PRIORITY   — no high-priority task is excluded while a lower-priority one is included
                  AND the high-priority task would have fit
  3. COVERAGE   — no task was excluded simply because it was never considered

If any rule fails, the schedule is rejected and actionable suggestions are returned.

Requires GEMINI_API_KEY environment variable.
"""

import json
import os
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import List

import google.generativeai as genai

from pawpal_system import Owner, Task

load_dotenv(override=True)  # Load environment variables from .env file
# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class VerificationResult:
    approved: bool
    feedback: str
    suggestions: List[str] = field(default_factory=list)
    time_used: float = 0.0
    time_available: float = 0.0

    def is_valid(self) -> bool:
        """Returns True if the schedule passed verification."""
        return self.approved

    def summary(self) -> str:
        """One-line human-readable verdict."""
        status = "APPROVED" if self.approved else "REJECTED"
        return f"[{status}] {self.feedback}"


# ---------------------------------------------------------------------------
# Verifier
# ---------------------------------------------------------------------------

class ScheduleVerifier:
    """Uses the Gemini API to verify that a proposed schedule is correct."""

    def __init__(self, model: str = "gemini-2.0-flash"):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self._model = genai.GenerativeModel(
            model_name=model,
            system_instruction=(
                "You are a strict schedule verifier for a pet care planning app. "
                "Respond ONLY with valid JSON — no markdown, no extra text."
            ),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def verify_schedule(
        self,
        owner: Owner,
        plan: List[Task],
        all_tasks: List[Task],
    ) -> VerificationResult:
        """
        Verify a proposed schedule against the owner's constraints.

        Parameters
        ----------
        owner     : Owner whose time_available defines the hard cap.
        plan      : Ordered list of tasks the Scheduler chose to include.
        all_tasks : Every task across all pets (including excluded ones).

        Returns
        -------
        VerificationResult with .approved, .feedback, and .suggestions.
        """
        prompt = self._build_prompt(owner, plan, all_tasks)
        response = self._model.generate_content(prompt)
        return self._parse_response(response.text, owner, plan)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_prompt(
        self,
        owner: Owner,
        plan: List[Task],
        all_tasks: List[Task],
    ) -> str:
        time_available = owner.get_time_available()
        total_scheduled = sum(t.get_duration() for t in plan)
        remaining = time_available - total_scheduled

        excluded = [t for t in all_tasks if t not in plan]

        def task_line(t: Task) -> str:
            return (
                f"  - {t.get_name()}: duration={t.get_duration():.2f}h, "
                f"priority={t.get_priority()}, category={t.get_category()}"
            )

        all_tasks_block = "\n".join(task_line(t) for t in all_tasks) or "  (none)"
        plan_block = "\n".join(
            f"  {i+1}. {t.get_name()}: duration={t.get_duration():.2f}h, "
            f"priority={t.get_priority()}"
            for i, t in enumerate(plan)
        ) or "  (empty — no tasks were scheduled)"
        excluded_block = "\n".join(task_line(t) for t in excluded) or "  (none)"

        return f"""You are verifying a pet care schedule for {owner.get_name()}.

=== OWNER CONSTRAINTS ===
Time available today : {time_available:.2f} hours
Time used by schedule: {total_scheduled:.2f} hours
Time remaining       : {remaining:.2f} hours

=== ALL AVAILABLE TASKS ===
{all_tasks_block}

=== PROPOSED SCHEDULE ===
{plan_block}

=== EXCLUDED TASKS ===
{excluded_block}

=== VERIFICATION RULES ===
1. TIME     : total scheduled duration must NOT exceed {time_available:.2f} hours.
2. PRIORITY : if a task was excluded, NO lower-priority task may be included
              UNLESS the excluded task would NOT fit in the remaining time.
3. COVERAGE : if time still remains after scheduling, check whether any excluded
              task would fit — if so, it should have been included.

Check every rule. If any rule is violated, set "approved" to false.

Respond with this exact JSON structure:
{{
    "approved": true or false,
    "feedback": "one sentence explaining the overall verdict",
    "suggestions": ["specific fix 1", "specific fix 2"]
}}"""

    def _parse_response(
        self,
        response_text: str,
        owner: Owner,
        plan: List[Task],
    ) -> VerificationResult:
        time_used = sum(t.get_duration() for t in plan)
        time_available = owner.get_time_available()

        # Strip accidental markdown fences if the model wraps in ```json ... ```
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
            return VerificationResult(
                approved=bool(data.get("approved", False)),
                feedback=data.get("feedback", "No feedback provided."),
                suggestions=data.get("suggestions", []),
                time_used=time_used,
                time_available=time_available,
            )
        except (json.JSONDecodeError, KeyError):
            return VerificationResult(
                approved=False,
                feedback="Verification failed: could not parse the AI response.",
                suggestions=["Try regenerating the schedule and verifying again."],
                time_used=time_used,
                time_available=time_available,
            )
