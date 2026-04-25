import streamlit as st
from orchestrator import run_pipeline

st.title("Cloud Provider Comparison Agent")

query = st.text_input("Enter query")

if st.button("Run"):
    if query:
        with st.spinner("Running..."):
            result = run_pipeline(query)

        st.success(f"Best Provider: {result['best_provider']}")
        st.info(f"Ranking: {result['ranking']}")

        st.subheader("Research")
        st.write(result["comparison"])

        st.subheader("Final Decision")
        st.write(result["final"])