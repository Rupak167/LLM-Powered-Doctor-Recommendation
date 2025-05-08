import streamlit as st
import requests

st.set_page_config(page_title="Doctor Finder Assistant")

st.title("Doctor Finder Assistant")
st.write("I’ll help you find the right doctor. Please answer a few quick questions.")

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.symptom = ""
    st.session_state.location = ""
    st.session_state.specialization = ""
    st.session_state.finished = False
    st.session_state.submitted = False

# Display previously answered questions for context
if st.session_state.step >= 1:
    st.markdown(f"**Symptom:** {st.session_state.symptom}")

if st.session_state.step >= 2:
    st.markdown(f"**Location:** {st.session_state.location}")

if st.session_state.step >= 3:
    st.markdown(f"**Specialization:** {st.session_state.specialization}")

# Step-by-step input collection
if st.session_state.step == 0:
    symptom = st.text_input("What medical issue are you experiencing?", key="symptom_input")
    if symptom:
        st.session_state.symptom = symptom
        st.session_state.step += 1
        st.rerun()

elif st.session_state.step == 1:
    location = st.text_input("Where are you located?", key="location_input")
    if location:
        st.session_state.location = location
        st.session_state.step += 1
        st.rerun()

elif st.session_state.step == 2:
    specialization = st.text_input("Do you know the type of specialist you want to see?", key="specialization_input")
    if specialization != "":
        st.session_state.specialization = specialization
        st.session_state.finished = True
        st.session_state.step += 1
        st.rerun()

# Send request to backend after collecting all inputs
if st.session_state.finished and not st.session_state.submitted:
    with st.spinner("🔎 Searching for doctors..."):
        try:
            res = requests.post("http://localhost:8000/search/", json={
                "symptom": st.session_state.symptom,
                "location": st.session_state.location,
                "specialization": st.session_state.specialization
            })
            st.session_state.submitted = True

            if res.status_code == 200:
                data = res.json()
                st.success("✅ Doctors found based on your inputs.")

                st.markdown("### 💡 Doctor's Summary")
                st.write(data['llm_summary'])
            else:
                st.error("❌ Failed to fetch results from the backend.")
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")

# Show "Start Over" button only after submission
if st.session_state.submitted:
    if st.button("🔄 Start Over"):
        for key in ["step", "symptom", "location", "specialization", "finished", "submitted"]:
            st.session_state.pop(key, None)
        st.rerun()
