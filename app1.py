import streamlit as st
import ollama
import json
import os

# File to store candidate responses
DATA_FILE = "candidates_data.json"

# Function to generate questions
def generate_questions(tech_stack):
    prompt = f"""
    You are an intelligent Hiring Assistant for 'TalentScout'. 
    Generate 3-5 relevant technical questions for a candidate skilled in: {tech_stack}.

    **STRICT FORMAT:**  
    Provide output ONLY in valid JSON format:
    {{
        "questions": [
            {{"question": "Question 1"}},
            {{"question": "Question 2"}},
            {{"question": "Question 3"}}
        ]
    }}
    """

    response = ollama.chat(model="llama3.2:1b", messages=[{"role": "user", "content": prompt}])

    full_response = response.get("message", {}).get("content", "").strip()

    try:
        parsed_response = json.loads(full_response)
        return [q["question"] if isinstance(q, dict) and "question" in q else str(q) for q in parsed_response.get("questions", [])]
    except json.JSONDecodeError:
        return ["Error: Failed to parse response."]

# Function to store candidate details locally
def save_candidate_data():
    data = {
        "name": st.session_state.name,
        "email": st.session_state.email,
        "phone": st.session_state.phone,
        "experience": st.session_state.experience,
        "position": st.session_state.position,
        "location": st.session_state.location,
        "tech_stack": st.session_state.tech_stack,
        "answers": st.session_state.answers
    }

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    existing_data.append(data)

    with open(DATA_FILE, "w") as file:
        json.dump(existing_data, file, indent=4)

    st.success("✅ Form Submitted Successfully! Data Saved.")

# Function to handle chatbot response
def chatbot_response(user_input):
    fallback_responses = [
        "I'm not sure I understand. Could you rephrase?",
        "Hmm, that doesn't seem related to hiring. Could you clarify?",
        "I can help with hiring questions. Can you ask something related to job applications?",
    ]

    if "exit" in user_input.lower():
        return "Thank you for using TalentScout! Have a great day! 😊"

    st.session_state.chat_history.append({"role": "user", "content": user_input})

    response = ollama.chat(model="llama3.2:1b", messages=st.session_state.chat_history)
    bot_reply = response.get("message", {}).get("content", "").strip()

    if not bot_reply or "error" in bot_reply.lower():
        bot_reply = fallback_responses.pop(0)  # Provide fallback response

    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
    return bot_reply

# Main Streamlit UI
def main():
    st.title("TalentScout - Intelligent Hiring Assistant")
    st.write("Welcome! Please enter your details to proceed with the initial screening.")

    # Initialize session state
    if "questions_generated" not in st.session_state:
        st.session_state.questions_generated = []

    if "answers" not in st.session_state:
        st.session_state.answers = {}

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Collect Candidate Details
    st.session_state.name = st.text_input("Full Name")
    st.session_state.email = st.text_input("Email")
    st.session_state.phone = st.text_input("Phone Number")
    st.session_state.experience = st.number_input("Years of Experience", min_value=0, step=1)
    st.session_state.position = st.text_input("Desired Position")
    st.session_state.location = st.text_input("Preferred Location")
    st.session_state.tech_stack = st.text_area("Tech Stack (comma-separated, e.g., Python, Django, MySQL)")

    # Generate Questions Button
    if st.button("Generate Technical Questions"):
        if st.session_state.tech_stack.strip():
            st.session_state.questions_generated = generate_questions(st.session_state.tech_stack)
            st.session_state.answers = {q: "" for q in st.session_state.questions_generated}  # Reset answers
            st.rerun()
        else:
            st.error("❌ Please enter your tech stack to generate questions.")

    # Display Questions and Answer Fields
    if st.session_state.questions_generated:
        st.write("### 📌 Technical Questions")
        for idx, question in enumerate(st.session_state.questions_generated, 1):
            st.session_state.answers[question] = st.text_area(f"{idx}. {question}", st.session_state.answers.get(question, ""))

    # Submit Form Button
    if st.button("Submit Form"):
        if all([st.session_state.name, st.session_state.email, st.session_state.phone, st.session_state.position]):
            save_candidate_data()
        else:
            st.error("❌ Please fill in all required fields before submitting.")

    # Conversational Chatbot Section
    st.write("---")
    st.write("### 💬 Chat with TalentScout")

    user_input = st.text_input("Ask anything about the hiring process:")

    if st.button("Send"):
        if user_input.strip():
            bot_reply = chatbot_response(user_input)
            st.write(f"🤖 TalentScout: {bot_reply}")

    # Display Chat History
    for chat in st.session_state.chat_history:
        role = "🧑‍💼 You: " if chat["role"] == "user" else "🤖 TalentScout: "
        st.write(f"{role} {chat['content']}")

if __name__ == "__main__":
    main()