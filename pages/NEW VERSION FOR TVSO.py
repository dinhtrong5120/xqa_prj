import streamlit as st
# RESET SESSION_STATE ĐẦU FILE
if "NEW VERSION ❤" in st.session_state:
# if st.session_state["6 NEW VERSION ❤"]:
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    
    Base = None
    engine = None
    Session = None
    session = None

if "NEW VERSION FOR TVSO" not in st.session_state:
    st.session_state["NEW VERSION FOR TVSO"] = True


exec(open(r"./xqa_web_tvso/app/streamlit_app.py", encoding='utf-8').read())
