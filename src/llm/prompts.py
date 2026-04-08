"""Prompt templates for LLM-powered recommendation explanations."""

RECOMMENDATION_PROMPT = """\
You are an academic advisor at a university. A student needs course recommendations.

Student Profile:
- Name: {student_name}
- Major: {major}
- Year: {year}
- Interests: {interests}

Based on a similarity search, these courses were identified as potential matches:

{course_list}

For each course, write a brief (1-2 sentence) personalized explanation of why \
this course would be a good fit for this specific student. Focus on how the course \
connects to their interests and academic goals.

Respond in this exact JSON format:
[
  {{"course_id": "...", "explanation": "..."}},
  ...
]

Return ONLY the JSON array, no other text."""


def build_recommendation_prompt(
    student_name: str,
    major: str,
    year: int,
    interests: list[str],
    courses: list[dict],
) -> str:
    """Format the recommendation prompt with student and course data."""
    course_lines = []
    for i, c in enumerate(courses, 1):
        course_lines.append(
            f"{i}. [{c['id']}] {c['title']} (Score: {c['score']:.2f})\n"
            f"   {c['description']}"
        )
    course_list = "\n\n".join(course_lines)

    return RECOMMENDATION_PROMPT.format(
        student_name=student_name,
        major=major,
        year=year,
        interests=", ".join(interests),
        course_list=course_list,
    )
