# 📘 Subject Guide AI Agent

An AI-powered comprehensive academic assistant that helps students understand subjects, solve exam questions, generate study plans, and track learning progress using Retrieval-Augmented Generation (RAG) with multi-LLM support.

---

## 🚀 Features

### 💬 Ask Question
- Intent-based routing — automatically detects topic explanation, question solving, learning path, or cross-reference
- Exam Mode and Quick Answer Mode for different response styles
- Source citations and chunk preview
- Download answers as text files

### 📝 Exam Preparation
- Generates complete exam prep packages with key concepts, definitions, expected questions, revision points, and common mistakes
- Tailored to uploaded study material

### 🧪 Quiz Mode
- AI-generated MCQ questions from uploaded content
- Three difficulty levels: Easy, Medium, Hard
- Instant score card with detailed feedback on wrong answers
- Automatic weak area analysis and revision recommendations
- Download quiz results as text files

### 📅 Study Plan Generator
- Day-wise personalised study schedule
- Daily targets and recommended resources from uploaded files
- Weekly milestones and exam day tips
- Tailored to Indian university exam patterns
- Download study plan as text file

### 📊 Progress Tracker
- Tracks total questions attempted, correct answers, and overall score
- Topics studied across sessions
- Full quiz history with weak areas highlighted
- Download progress report as text file

### 🔒 Input Validation & Error Handling
- File size and format validation (PDF, DOCX, PPTX up to 10MB)
- Query validation for empty, too short, or too long inputs
- Friendly error messages for all API failures
- Multi-LLM fallback: Gemini primary, OpenAI GPT-4o-mini backup

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| LLM Primary | Google Gemini 2.5 Flash |
| LLM Fallback | OpenAI GPT-4o-mini |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector Store | FAISS |
| Text Splitting | LangChain Text Splitters |
| Document Parsing | PyPDF2, python-docx, python-pptx |
| Language | Python 3.11 |

---

## 📦 Project Structure
Subject_Guide_Ai_Agent/
│
├── app.py                        # Main Streamlit application
├── requirements.txt              # Python dependencies
├── .env                          # API keys (not pushed to GitHub)
├── .gitignore
│
├── src/
│   ├── file_loader.py            # PDF, DOCX, PPTX text extraction
│   ├── text_chunker.py           # LangChain recursive text splitting
│   ├── vector_store.py           # FAISS index creation
│   ├── retriever.py              # Semantic search + keyword reranking
│   ├── llm_handler.py            # Legacy answer generator (Week 1-2)
│   ├── question_utils.py         # Question type detection
│   ├── gemini_client.py          # Multi-LLM client with fallback
│   ├── intent_router.py          # Query intent detection and routing
│   ├── topic_engine.py           # Topic explanation tool
│   ├── question_solver.py        # Question solving tool
│   ├── learning_path.py          # Learning progression tool
│   ├── cross_ref.py              # Cross-document reference tool
│   ├── exam_workflow.py          # Exam preparation package generator
│   ├── quiz_engine.py            # Quiz generation and parsing
│   ├── weak_area_detector.py     # Weak area analysis from quiz results
│   ├── study_plan_generator.py   # Personalised study plan generator
│   ├── progress_tracker.py       # Session-based progress tracking
│   ├── validator.py              # Input validation and error messages
│   └── exporter.py               # Export answers, plans, results as text
│
└── README.md
---

## ▶️ How to Run

```bash
# Clone the repository
git clone https://github.com/Finey10/Subject_Guide_Ai_Agent.git
cd Subject_Guide_Ai_Agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py --server.fileWatcherType poll
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here

> OpenAI key is optional — only used as fallback when Gemini quota is exhausted.

For Streamlit Cloud deployment, add these under:
App Settings → Secrets

---

## 🧠 How It Works
Upload Files → Extract Text → Chunk → FAISS Index
↓
User Query → Validate → Intent Router → Topic / Solver / Learning / CrossRef
↓
Gemini 2.5 Flash (primary)
↓ (if quota exhausted)
OpenAI GPT-4o-mini (fallback)
↓
Structured Academic Answer + Export Option

---

## 🎯 Use Cases

- Students preparing for university exams (DBMS, DSA, OS, CN)
- Lab record writing assistance
- Understanding concepts from multiple uploaded sources
- Self-study with structured Theory → Practice → Assessment flow
- Cross-referencing answers from textbooks, notes, and question papers
- Generating personalised study plans for Indian university syllabi

---

## 📋 Requirements
streamlit
faiss-cpu
google-genai
python-docx
python-pptx
PyPDF2
python-dotenv
sentence-transformers==2.7.0
langchain-text-splitters
numpy
openai

---

## 🚀 Deployment

Live demo: [Your Streamlit Cloud URL here]

Deployed on Streamlit Cloud with API keys configured in Streamlit Secrets.

---
