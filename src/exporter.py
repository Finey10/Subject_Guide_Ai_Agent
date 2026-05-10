from datetime import datetime


def export_answer(query: str, answer: str, intent: str, sources: list) -> str:
    timestamp = datetime.now().strftime("%d %b %Y %H:%M")
    sources_text = "\n".join(f"- {s}" for s in sources) if sources else "N/A"

    return f"""SUBJECT GUIDE AI AGENT — EXPORT
{'=' * 50}
Date: {timestamp}
Type: {intent}
Query: {query}

{'=' * 50}
ANSWER
{'=' * 50}
{answer}

{'=' * 50}
SOURCES USED
{'=' * 50}
{sources_text}
"""


def export_exam_prep(topic: str, content: str) -> str:
    timestamp = datetime.now().strftime("%d %b %Y %H:%M")

    return f"""SUBJECT GUIDE AI AGENT — EXAM PREP EXPORT
{'=' * 50}
Date: {timestamp}
Topic: {topic}

{'=' * 50}
EXAM PREPARATION PACKAGE
{'=' * 50}
{content}
"""


def export_quiz_results(topic: str, results: list, score: int,
                        total: int, percentage: int, weak_analysis: str) -> str:
    timestamp = datetime.now().strftime("%d %b %Y %H:%M")

    questions_text = ""
    for i, r in enumerate(results, 1):
        status = "✓ CORRECT" if r["is_correct"] else "✗ WRONG"
        questions_text += f"""
Q{i}. {r['question']}
Your Answer: {r['user_answer']}
Correct Answer: {r['correct_answer']}
Result: {status}
Explanation: {r['explanation']}
{'-' * 40}"""

    return f"""SUBJECT GUIDE AI AGENT — QUIZ RESULTS EXPORT
{'=' * 50}
Date: {timestamp}
Topic: {topic}
Score: {score}/{total} ({percentage}%)

{'=' * 50}
QUESTION-WISE RESULTS
{'=' * 50}
{questions_text}

{'=' * 50}
WEAK AREA ANALYSIS
{'=' * 50}
{weak_analysis}
"""


def export_study_plan(subject: str, days: int, plan: str) -> str:
    timestamp = datetime.now().strftime("%d %b %Y %H:%M")

    return f"""SUBJECT GUIDE AI AGENT — STUDY PLAN EXPORT
{'=' * 50}
Date: {timestamp}
Subject: {subject}
Duration: {days} days

{'=' * 50}
YOUR PERSONALISED STUDY PLAN
{'=' * 50}
{plan}
"""


def export_progress(stats: dict) -> str:
    timestamp = datetime.now().strftime("%d %b %Y %H:%M")

    topics = "\n".join(f"- {t}" for t in stats["topics_studied"]) or "None yet"

    history_text = ""
    for i, q in enumerate(stats["quiz_history"], 1):
        history_text += f"""
Quiz {i}: {q['topic']}
Score: {q['score']}/{q['total']} ({q['percentage']}%)
Date: {q['date']}
{'-' * 30}"""

    return f"""SUBJECT GUIDE AI AGENT — PROGRESS REPORT
{'=' * 50}
Generated: {timestamp}

{'=' * 50}
OVERALL PERFORMANCE
{'=' * 50}
Total Questions Attempted: {stats['total_questions']}
Total Correct Answers: {stats['total_correct']}
Overall Score: {stats['overall_percentage']}%
Last Active: {stats['last_active']}

{'=' * 50}
TOPICS STUDIED
{'=' * 50}
{topics}

{'=' * 50}
QUIZ HISTORY
{'=' * 50}
{history_text}
"""