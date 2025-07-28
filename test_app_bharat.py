import streamlit as st
from groq import Groq

# ----------------- INIT ------------------
st.set_page_config(page_title="Interview & Practice App", layout="wide")
debug_mode = True

groq_key = "xxxxxxxx"
client = Groq(api_key=groq_key)  # Replace with your actual Groq API key

# ----------------- PROMPT HANDLERS ------------------

def get_test_questions(subject, level):
    try:
        prompt = (
            f"Generate 5 {level} level multiple-choice questions (MCQs) for the subject: {subject}.\n"
            "Each question must follow this format exactly:\n"
            "Q1. [Question text]\n"
            "A. Option A\n"
            "B. Option B\n"
            "C. Option C\n"
            "D. Option D\n"
            "Answer: [A/B/C/D]\n"
            "Explanation: [1-line explanation]\n\n"
            "Repeat for all 10 questions in the same format. Do not add code or comments."
        )
        if debug_mode:
            st.write(f"[DEBUG] Test Prompt: {prompt}")

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        questions = []
        blocks = content.strip().split("\n\n")

        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) >= 7:
                q = {
                    "question": lines[0].split("Question:")[-1].strip(),
                    "options": [
                        lines[1].split("A.")[1].strip(),
                        lines[2].split("B.")[1].strip(),
                        lines[3].split("C.")[1].strip(),
                        lines[4].split("D.")[1].strip()
                    ],
                    "answer": lines[5].split("Answer:")[-1].strip(),
                    "explanation": lines[6].split("Explanation:")[-1].strip()
                }
                questions.append(q)
        return questions[:10]
    except Exception as e:
        st.error(f"[ERROR] Test question generation failed: {e}")
        return []

def get_interview_questions(subject, level):
    try:
        prompt = f"Generate 10 {level} level interview questions on the topic: {subject}."
        if debug_mode:
            st.write(f"[DEBUG] Interview Prompt: {prompt}")

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip().split("\n")
    except Exception as e:
        st.error(f"[ERROR] Interview question generation failed: {e}")
        return []

# def get_coding_questions(subject, level):
#     try:
#         prompt = (
#              f"Generate 5 {level} level coding questions for the subject: {subject}.\n"
#             "List each question in the following format:\n"
#             "1. [Question 1]\n"
#             "2. [Question 2]\n"
#             "...up to 10.\n"
#             "Avoid sample answers or code. Only include the problem statement."
#         )
#         if debug_mode:
#             st.write(f"[DEBUG] Coding Prompt: {prompt}")

#         response = client.chat.completions.create(
#             model="llama3-70b-8192",
#             messages=[{"role": "user", "content": prompt}]
#         )
#         return response.choices[0].message.content.strip().split("\n")
#     except Exception as e:
#         st.error(f"[ERROR] Coding question generation failed: {e}")
#         return []
def get_coding_questions(subject, level):
    try:
        prompt = (
            f"Generate 5 {level} level coding questions for the subject: {subject}.\n"
            "List each question in the following format:\n"
            "1. [Question 1]\n"
            "2. [Question 2]\n"
            "...up to 10.\n"
            "Avoid sample answers or code. Only include the problem statement."
        )

        if debug_mode:
            st.write(f"[DEBUG] Coding Prompt:\n{prompt}")

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )

        raw_output = response.choices[0].message.content.strip()
        questions = [q.strip()[3:].strip() for q in raw_output.split("\n") if q.strip().startswith(tuple(str(i) for i in range(1, 11)))]

        return questions[:10]
    except Exception as e:
        st.error(f"[ERROR] Coding question generation failed: {e}")
        return []




# ----------------- MAIN APP ------------------

st.title("💡 Interview & Practice App")

option = st.sidebar.radio("Choose Mode", ["📝 Test", "💬 Interview", "💻 Coding Practice"])

# Common inputs
subject = st.sidebar.text_input("Enter Subject (e.g., Python, SQL, History)", key="subject_input")
level = st.sidebar.selectbox("Select Level", ["Easy", "Medium", "Hard"], key="level_input")

# ---------- TEST MODE ----------
if option == "📝 Test":
    if st.button("Start Test"):
        st.session_state.test_questions = get_test_questions(subject, level)
        st.session_state.test_started = True
        for i in range(10):
            st.session_state[f"answer_{i}"] = None  # reset answers

    if st.session_state.get("test_started", False):
        questions = st.session_state.get("test_questions", [])
        if not questions:
            st.warning("No test questions returned. Please try a different subject or level.")
        else:
            st.subheader("Test Questions")
            for idx, q in enumerate(questions):
                st.write(f"**Q{idx+1}: {q['question']}**")
                st.session_state[f"answer_{idx}"] = st.radio(
                    "Select an option",
                    q["options"],
                    key=f"radio_{idx}"
                )

            if st.button("Submit Test"):
                correct = 0
                for idx, q in enumerate(questions):
                    selected = st.session_state.get(f"radio_{idx}")
                    correct_option = {
                        "A": q["options"][0],
                        "B": q["options"][1],
                        "C": q["options"][2],
                        "D": q["options"][3]
                    }.get(q["answer"].upper(), "")
                    if selected == correct_option:
                        correct += 1
                score_percent = (correct / len(questions)) * 100
                st.success(f"✅ Score: {score_percent:.2f}%")

                st.subheader("📘 Review Answers")
                for idx, q in enumerate(questions):
                    selected = st.session_state.get(f"radio_{idx}")
                    st.markdown(f"**Q{idx+1}: {q['question']}**")
                    st.write(f"- Your Answer: `{selected}`")
                    st.write(f"- Correct Answer: `{q['answer']}` → {q['options'][ord(q['answer'].upper()) - 65]}")
                    st.write(f"- Explanation: {q['explanation']}")
                    st.markdown("---")

# ---------- INTERVIEW MODE ----------
elif option == "💬 Interview":
    if st.button("Generate Interview Questions"):
        st.session_state.interview_questions = get_interview_questions(subject, level)

    if "interview_questions" in st.session_state:
        st.subheader("📋 Interview Questions")
        for q in st.session_state.interview_questions:
            st.write(f"- {q}")

# ---------- CODING MODE ----------
# elif option == "💻 Coding Practice":
#     if st.button("Generate Coding Questions"):
#         st.session_state.coding_questions = get_coding_questions(subject, level)

#     if "coding_questions" in st.session_state:
#         st.subheader("💻 Coding Questions")
#         for idx, q in enumerate(st.session_state.coding_questions):
#             st.markdown(f"**Q{idx+1}:** {q}")

# ---------- CODING MODE ----------
elif option == "💻 Coding Practice":
    if st.button("Generate Coding Questions"):
        # Get questions with expected answers (modify LLM prompt to include answers)
        st.session_state.coding_questions = get_coding_questions(subject, level)
        st.session_state.coding_started = True
        for i in range(10):
            st.session_state[f"user_code_{i}"] = ""

    if st.session_state.get("coding_started", False):
        questions = st.session_state.get("coding_questions", [])
        if not questions:
            st.warning("No coding questions found.")
        else:
            st.subheader("💻 Coding Questions")
            for idx, q in enumerate(questions):
                st.markdown(f"**Q{idx+1}:** {q}")
                st.session_state[f"user_code_{idx}"] = st.text_area(
                    f"Your Code for Q{idx+1}",
                    value=st.session_state.get(f"user_code_{idx}", ""),
                    key=f"code_area_{idx}",
                    height=150
                )

            if st.button("Submit Code"):
                correct = 0
                st.subheader("📘 Your Coding Answers")

                for idx, q in enumerate(questions):
                    user_code = st.session_state.get(f"user_code_{idx}", "")
                    st.markdown(f"**Q{idx+1}:** {q}")
                    st.code(user_code, language="python")

                    # 🔴 You can add real code evaluation here
                    # For now, treat non-empty submission as correct (simulate)
                    if user_code.strip():
                        st.success("✅ Answer Submitted.")
                        correct += 1
                    else:
                        st.warning("⚠️ No code entered.")

                score = (correct / len(questions)) * 100
                st.markdown(f"### ✅ Your Score: **{score:.2f}%**")
