import streamlit as st
# RESET SESSION_STATE ĐẦU FILE

if "NEW VERSION FOR TVSO" in st.session_state:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    Base = None
    engine = None
    Session = None
    session = None
    # st.session_state["7 NEW VERSION FOR TVSO"] = False

if "NEW VERSION ❤" not in st.session_state:
    st.session_state["NEW VERSION ❤"] = True
exec(open(r"./xqa_web/app/streamlit_app.py", encoding='utf-8').read())