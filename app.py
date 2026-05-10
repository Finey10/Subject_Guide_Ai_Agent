import streamlit as st

from src.file_loader import load_file
from src.text_chunker import chunk_text_with_metadata
from src.vector_store import create_vector_store
from src.retriever import search_chunks
from src.intent_router import route_intent
from src.topic_engine import explain_topic
from src.question_solver import solve_question
from src.learning_path import generate_learning_stage, STAGES
from src.cross_ref import cross_reference
from src.exam_workflow import generate_exam_prep
from src.quiz_engine import generate_quiz, parse_quiz
from src.weak_area_detector import detect_weak_areas
from src.study_plan_generator import generate_study_plan
from src.progress_tracker import (
    init_progress, record_quiz_result,
    record_topic_studied, get_overall_stats,
    get_performance_level
)
from src.validator import (
    validate_query, validate_file,
    validate_quiz_topic, validate_study_plan,
    get_friendly_error
)
from src.exporter import (
    export_answer, export_exam_prep,
    export_quiz_results, export_study_plan,
    export_progress
)

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Subject Guide Assistant",
    page_icon="📘",
    layout="wide"
)

# ── Session state ─────────────────────────────────────────────
for key in ["all_chunks", "index", "subject", "chapters",
            "quiz_questions", "quiz_results", "quiz_topic",
            "quiz_submitted", "last_answer", "last_intent",
            "last_sources", "exam_result", "study_result",
            "weak_analysis"]:
    if key not in st.session_state:
        st.session_state[key] = None

init_progress()

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.header("📚 Subject Organisation")
    subject = st.text_input("Subject name", placeholder="e.g. DBMS")
    chapter = st.text_input("Chapter / Unit", placeholder="e.g. Unit 1")

    if subject:
        st.session_state.subject = subject

    st.markdown("---")
    mode = st.selectbox("Mode", ["Exam Mode", "Quick Answer Mode"])
    filter_category = st.selectbox(
        "Filter category",
        ["All", "Textbook", "Notes", "Question Paper", "Lab Material"]
    )

    # ── Sidebar progress summary ───────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    stats = get_overall_stats()
    if stats["total_questions"] > 0:
        st.metric("Overall Score", f"{stats['overall_percentage']}%")
        st.metric("Topics Studied", len(stats["topics_studied"]))
        st.metric("Quizzes Taken", len(stats["quiz_history"]))
    else:
        st.caption("No activity yet. Start by asking a question!")

# ── Header ────────────────────────────────────────────────────
st.title("📘 Subject Guide Assistant")
st.markdown("Upload academic files and get structured AI-generated answers.")

# ── File upload ───────────────────────────────────────────────
uploaded_files = st.file_uploader(
    "Upload your files (PDF, DOCX, PPTX)",
    type=["pdf", "docx", "pptx"],
    accept_multiple_files=True
)

# ── File validation ───────────────────────────────────────────
file_categories = {}
if uploaded_files:
    invalid_files = []
    for file in uploaded_files:
        validation = validate_file(file)
        if not validation["valid"]:
            invalid_files.append(validation["error"])

    if invalid_files:
        for err in invalid_files:
            st.error(f"❌ {err}")
    else:
        st.markdown("### Assign category for each file")
        for file in uploaded_files:
            file_categories[file.name] = st.selectbox(
                f"{file.name}",
                ["Textbook", "Notes", "Question Paper", "Lab Material"],
                key=file.name
            )

# ── Cache helpers ─────────────────────────────────────────────
@st.cache_data
def process_files(uploaded_files, file_categories):
    all_chunks = []
    for file in uploaded_files:
        text = load_file(file)
        if text.strip():
            all_chunks.extend(
                chunk_text_with_metadata(
                    text, file.name, file_categories[file.name]
                )
            )
    return all_chunks


@st.cache_resource
def build_index(texts):
    return create_vector_store(texts)

# ── Process button ────────────────────────────────────────────
if uploaded_files and file_categories:
    if st.button("🚀 Process Files"):
        with st.spinner("Processing files and building knowledge base..."):
            all_chunks = process_files(uploaded_files, file_categories)
            if not all_chunks:
                st.error(
                    "❌ Could not extract text from uploaded files. "
                    "Make sure files are not scanned images or password protected."
                )
            else:
                texts = [c["text"] for c in all_chunks]
                index, _ = build_index(texts)
                st.session_state.all_chunks = all_chunks
                st.session_state.index = index
                st.success(
                    f"✅ Ready — {len(all_chunks)} chunks from "
                    f"{len(uploaded_files)} file(s)"
                )

# ── Main tabs ─────────────────────────────────────────────────
if st.session_state.index is not None:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 Ask Question",
        "📝 Exam Prep",
        "🧪 Quiz Mode",
        "📅 Study Plan",
        "📊 My Progress"
    ])

    # ════════════════════════════════════════════════════════
    # TAB 1 — ASK QUESTION
    # ════════════════════════════════════════════════════════
    with tab1:
        st.markdown("---")
        query = st.text_input(
            "Ask a question or enter a topic:",
            placeholder="e.g. Explain ER diagrams / List advantages of DBMS"
        )

        if query:
            # Validate query
            v = validate_query(query)
            if not v["valid"]:
                st.warning(f"⚠️ {v['error']}")
            else:
                route = route_intent(query)
                intent = route["intent"]

                intent_labels = {
                    "topic":    "📖 Topic Explanation",
                    "solver":   "🧮 Question Solver",
                    "learning": "🎓 Learning Path",
                    "crossref": "🔗 Cross-Reference",
                }
                st.caption(f"Detected mode: **{intent_labels[intent]}**")

                with st.spinner("Retrieving relevant content..."):
                    chunks = search_chunks(
                        query=query,
                        index=st.session_state.index,
                        all_chunks=st.session_state.all_chunks,
                        selected_category=filter_category,
                        k=5
                    )

                if not chunks:
                    st.warning(
                        "⚠️ No relevant content found for this query. "
                        "Try different keywords or change the filter category."
                    )
                else:
                    try:
                        answer_text = ""
                        sources_list = list(set(
                            f"{c['source']} ({c['category']})" for c in chunks
                        ))

                        if intent == "topic":
                            with st.spinner("Generating topic explanation..."):
                                answer_text = explain_topic(query, chunks, mode)
                            st.subheader("📖 Topic Explanation")
                            st.markdown(answer_text)
                            record_topic_studied(query)

                        elif intent == "solver":
                            with st.spinner("Solving question..."):
                                result = solve_question(query, chunks, mode)
                            answer_text = result["solution"]
                            st.subheader("🧮 Solution")
                            st.caption(f"Solution type: `{result['solution_type']}`")
                            st.markdown(answer_text)

                        elif intent == "learning":
                            st.subheader("🎓 Learning Path")
                            topic_name = query.replace(
                                "teach me", ""
                            ).replace("learn", "").strip()
                            learning_tabs = st.tabs(STAGES)
                            full_content = ""
                            for ltab, stage in zip(learning_tabs, STAGES):
                                with ltab:
                                    with st.spinner(f"Generating {stage}..."):
                                        content = generate_learning_stage(
                                            topic_name, stage, chunks
                                        )
                                    st.markdown(content)
                                    full_content += f"\n\n## {stage}\n{content}"
                            answer_text = full_content
                            record_topic_studied(topic_name)

                        elif intent == "crossref":
                            with st.spinner("Synthesizing across all sources..."):
                                result = cross_reference(query, chunks)
                            answer_text = result["answer"]
                            st.subheader("🔗 Cross-Document Answer")
                            st.caption(
                                f"Sources used: {', '.join(result['sources_used'])}"
                            )
                            st.markdown(answer_text)

                        # Save for export
                        st.session_state.last_answer = answer_text
                        st.session_state.last_intent = intent_labels[intent]
                        st.session_state.last_sources = sources_list

                    except RuntimeError as e:
                        st.error(get_friendly_error(e))
                    except Exception as e:
                        st.error(get_friendly_error(e))

                    # ── Export button ──────────────────────
                    if st.session_state.last_answer:
                        st.markdown("---")
                        export_content = export_answer(
                            query=query,
                            answer=st.session_state.last_answer,
                            intent=st.session_state.last_intent or "",
                            sources=st.session_state.last_sources or []
                        )
                        st.download_button(
                            label="⬇️ Download Answer",
                            data=export_content,
                            file_name=f"answer_{query[:30].replace(' ', '_')}.txt",
                            mime="text/plain"
                        )

                    # ── Sources footer ─────────────────────
                    st.markdown("---")
                    with st.expander("📚 Sources used"):
                        seen = set()
                        for c in chunks:
                            label = f"{c['source']} ({c['category']})"
                            if label not in seen:
                                seen.add(label)
                                st.write(f"- {label}")

                    with st.expander("🔍 Retrieved chunks"):
                        for i, c in enumerate(chunks, 1):
                            st.write(f"**{i}. {c['source']}** — {c['category']}")
                            st.write(c["text"])
                            st.markdown("---")

    # ════════════════════════════════════════════════════════
    # TAB 2 — EXAM PREP
    # ════════════════════════════════════════════════════════
    with tab2:
        st.subheader("📝 Exam Preparation")
        st.markdown("Generate a complete exam prep package for any topic.")

        exam_topic = st.text_input(
            "Enter topic for exam prep:",
            placeholder="e.g. Normalization in DBMS",
            key="exam_topic_input"
        )

        if st.button("📝 Generate Exam Prep", key="exam_prep_btn"):
            v = validate_query(exam_topic)
            if not v["valid"]:
                st.warning(f"⚠️ {v['error']}")
            else:
                chunks = search_chunks(
                    query=exam_topic,
                    index=st.session_state.index,
                    all_chunks=st.session_state.all_chunks,
                    selected_category=filter_category,
                    k=5
                )

                if not chunks:
                    st.warning(
                        "⚠️ No relevant content found for this topic. "
                        "Try a different topic or change the filter category."
                    )
                else:
                    try:
                        with st.spinner("Building your exam prep package..."):
                            result = generate_exam_prep(exam_topic, chunks, mode)
                        st.session_state.exam_result = result
                        st.markdown(result["content"])
                        st.caption(f"Based on {result['source_count']} source(s)")
                        record_topic_studied(exam_topic)
                    except RuntimeError as e:
                        st.error(get_friendly_error(e))
                    except Exception as e:
                        st.error(get_friendly_error(e))

        # ── Export exam prep ───────────────────────────────
        if st.session_state.exam_result:
            export_content = export_exam_prep(
                topic=st.session_state.exam_result["topic"],
                content=st.session_state.exam_result["content"]
            )
            st.download_button(
                label="⬇️ Download Exam Prep",
                data=export_content,
                file_name=f"exam_prep_{exam_topic[:20].replace(' ', '_')}.txt",
                mime="text/plain",
                key="download_exam_prep"
            )

    # ════════════════════════════════════════════════════════
    # TAB 3 — QUIZ MODE
    # ════════════════════════════════════════════════════════
    with tab3:
        st.subheader("🧪 Quiz Mode")
        st.markdown("Test your knowledge with AI-generated questions.")

        col1, col2, col3 = st.columns(3)
        with col1:
            quiz_topic = st.text_input(
                "Quiz topic:",
                placeholder="e.g. ER Diagrams",
                key="quiz_topic_input"
            )
        with col2:
            difficulty = st.selectbox(
                "Difficulty",
                ["Easy", "Medium", "Hard"],
                key="quiz_difficulty"
            )
        with col3:
            num_q = st.selectbox(
                "Number of questions",
                [3, 5, 10],
                key="quiz_num_q"
            )

        if st.button("🎯 Generate Quiz", key="generate_quiz_btn"):
            v = validate_quiz_topic(quiz_topic)
            if not v["valid"]:
                st.warning(f"⚠️ {v['error']}")
            else:
                with st.spinner("Generating quiz questions..."):
                    chunks = search_chunks(
                        query=quiz_topic,
                        index=st.session_state.index,
                        all_chunks=st.session_state.all_chunks,
                        selected_category=filter_category,
                        k=5
                    )

                if not chunks:
                    st.warning(
                        "⚠️ No content found for this topic. "
                        "Try a broader topic or change the filter category."
                    )
                else:
                    try:
                        raw_quiz = generate_quiz(
                            quiz_topic, chunks, difficulty, num_q
                        )
                        questions = parse_quiz(raw_quiz)

                        if questions:
                            st.session_state.quiz_questions = questions
                            st.session_state.quiz_topic = quiz_topic
                            st.session_state.quiz_results = []
                            st.session_state.quiz_submitted = False
                            st.session_state.weak_analysis = None
                            st.success(
                                f"✅ {len(questions)} questions generated! "
                                f"Scroll down to answer them."
                            )
                        else:
                            st.error(
                                "❌ Could not parse quiz questions. "
                                "Please try again or use a different topic."
                            )
                    except RuntimeError as e:
                        st.error(get_friendly_error(e))

        # ── Show quiz questions ────────────────────────────
        if st.session_state.quiz_questions and not st.session_state.quiz_submitted:
            st.markdown("---")
            st.markdown("### Answer the questions below:")

            user_answers = {}
            for i, q in enumerate(st.session_state.quiz_questions):
                st.markdown(f"**Q{i+1}. {q['question']}**")
                if q["options"]:
                    user_answers[i] = st.radio(
                        f"Select answer for Q{i+1}:",
                        q["options"],
                        key=f"quiz_ans_{i}",
                        label_visibility="collapsed"
                    )
                else:
                    user_answers[i] = st.text_input(
                        f"Your answer for Q{i+1}:",
                        key=f"quiz_text_{i}"
                    )
                st.markdown("---")

            if st.button("✅ Submit Quiz", key="submit_quiz_btn"):
                if not any(user_answers.values()):
                    st.warning("⚠️ Please answer at least one question before submitting.")
                else:
                    results = []
                    for i, q in enumerate(st.session_state.quiz_questions):
                        user_ans = user_answers.get(i, "")
                        correct = q["answer"]
                        is_correct = str(user_ans).lower().startswith(
                            correct.lower()
                        )
                        results.append({
                            "question": q["question"],
                            "user_answer": user_ans,
                            "correct_answer": correct,
                            "explanation": q["explanation"],
                            "is_correct": is_correct
                        })
                    st.session_state.quiz_results = results
                    st.session_state.quiz_submitted = True
                    st.rerun()

        # ── Show quiz results ──────────────────────────────
        if st.session_state.quiz_submitted and st.session_state.quiz_results:
            results = st.session_state.quiz_results
            score = sum(1 for r in results if r["is_correct"])
            total = len(results)
            percentage = int((score / total) * 100)
            level, color = get_performance_level(percentage)

            st.markdown("---")
            st.subheader("📊 Quiz Results")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", f"{score}/{total}")
            with col2:
                st.metric("Percentage", f"{percentage}%")
            with col3:
                st.metric("Performance", level)

            st.markdown("---")
            for i, r in enumerate(results):
                if r["is_correct"]:
                    st.success(f"✅ Q{i+1}: {r['question']}")
                else:
                    st.error(f"❌ Q{i+1}: {r['question']}")
                    st.write(f"Your answer: `{r['user_answer']}`")
                    st.write(f"Correct answer: `{r['correct_answer']}`")
                    st.write(f"💡 {r['explanation']}")
                st.markdown("---")

            # Detect weak areas
            if not st.session_state.weak_analysis:
                with st.spinner("Analyzing your performance..."):
                    weak = detect_weak_areas(results)
                st.session_state.weak_analysis = weak

                # Save to progress
                record_quiz_result(
                    topic=st.session_state.quiz_topic,
                    score=score,
                    total=total,
                    weak_areas=weak["weak_topics"]
                )

            weak = st.session_state.weak_analysis
            st.subheader("🔍 Weak Area Analysis")
            st.markdown(weak["recommendation"])

            # ── Export quiz results ────────────────────────
            export_content = export_quiz_results(
                topic=st.session_state.quiz_topic,
                results=results,
                score=score,
                total=total,
                percentage=percentage,
                weak_analysis=weak["recommendation"]
            )
            st.download_button(
                label="⬇️ Download Quiz Results",
                data=export_content,
                file_name=f"quiz_results_{st.session_state.quiz_topic[:20].replace(' ', '_')}.txt",
                mime="text/plain",
                key="download_quiz"
            )

            if st.button("🔄 Take Another Quiz", key="retry_quiz_btn"):
                st.session_state.quiz_questions = None
                st.session_state.quiz_results = []
                st.session_state.quiz_submitted = False
                st.session_state.weak_analysis = None
                st.rerun()

    # ════════════════════════════════════════════════════════
    # TAB 4 — STUDY PLAN
    # ════════════════════════════════════════════════════════
    with tab4:
        st.subheader("📅 Custom Study Plan")
        st.markdown("Generate a personalised study plan based on your uploaded content.")

        col1, col2 = st.columns(2)
        with col1:
            plan_subject = st.text_input(
                "Subject:",
                value=st.session_state.subject or "",
                placeholder="e.g. DBMS",
                key="plan_subject"
            )
        with col2:
            plan_days = st.selectbox(
                "Days until exam:",
                [3, 5, 7, 10, 14, 30],
                index=2,
                key="plan_days"
            )

        custom_topics = st.text_area(
            "Topics to cover (one per line, or leave blank to auto-detect):",
            placeholder="Normalization\nER Diagrams\nTransaction Management",
            key="plan_topics"
        )

        if st.button("📅 Generate Study Plan", key="study_plan_btn"):
            v = validate_study_plan(plan_subject, plan_days)
            if not v["valid"]:
                st.warning(f"⚠️ {v['error']}")
            else:
                topics = [t.strip() for t in custom_topics.split("\n") if t.strip()]
                chunks = st.session_state.all_chunks[:20]

                try:
                    with st.spinner("Creating your personalised study plan..."):
                        result = generate_study_plan(
                            subject=plan_subject,
                            chunks=chunks,
                            days=plan_days,
                            topics=topics if topics else None
                        )
                    st.session_state.study_result = result
                    st.markdown(result["plan"])
                    st.caption(
                        f"Plan covers {result['days']} days "
                        f"across {result['topics_count']} topic(s)"
                    )
                except RuntimeError as e:
                    st.error(get_friendly_error(e))
                except Exception as e:
                    st.error(get_friendly_error(e))

        # ── Export study plan ──────────────────────────────
        if st.session_state.study_result:
            export_content = export_study_plan(
                subject=st.session_state.study_result["subject"],
                days=st.session_state.study_result["days"],
                plan=st.session_state.study_result["plan"]
            )
            st.download_button(
                label="⬇️ Download Study Plan",
                data=export_content,
                file_name=f"study_plan_{plan_subject[:20].replace(' ', '_')}.txt",
                mime="text/plain",
                key="download_study_plan"
            )

    # ════════════════════════════════════════════════════════
    # TAB 5 — MY PROGRESS
    # ════════════════════════════════════════════════════════
    with tab5:
        st.subheader("📊 My Progress")
        stats = get_overall_stats()

        if stats["total_questions"] == 0:
            st.info("👆 Take a quiz to start tracking your progress!")
        else:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Questions", stats["total_questions"])
            with col2:
                st.metric("Correct Answers", stats["total_correct"])
            with col3:
                st.metric("Overall Score", f"{stats['overall_percentage']}%")
            with col4:
                level, _ = get_performance_level(stats["overall_percentage"])
                st.metric("Level", level)

            st.markdown("---")

            if stats["topics_studied"]:
                st.markdown("### 📚 Topics Studied")
                for topic in stats["topics_studied"]:
                    st.write(f"✅ {topic}")

            st.markdown("---")

            if stats["quiz_history"]:
                st.markdown("### 🧪 Quiz History")
                for i, quiz in enumerate(reversed(stats["quiz_history"]), 1):
                    level, _ = get_performance_level(quiz["percentage"])
                    with st.expander(
                        f"Quiz {i} — {quiz['topic']} — {quiz['percentage']}% {level}"
                    ):
                        st.write(f"Score: {quiz['score']}/{quiz['total']}")
                        st.write(f"Date: {quiz['date']}")
                        if quiz["weak_areas"]:
                            st.write("Weak areas:")
                            for area in quiz["weak_areas"]:
                                st.write(f"  - {area}")

            st.markdown("---")

            # ── Export progress ────────────────────────────
            export_content = export_progress(stats)
            st.download_button(
                label="⬇️ Download Progress Report",
                data=export_content,
                file_name="my_progress_report.txt",
                mime="text/plain",
                key="download_progress"
            )

            st.caption(f"Last active: {stats['last_active']}")

else:
    st.info("👆 Upload files and click **Process Files** to begin.")