import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from streamlit_extras.grid import grid
from xqa_web_tvso.app.logics.syo.db.function_database_new import querry_to_show_project, delete_project_syo
from xqa_web_tvso.app.logics.syo.db.funtion_database import querry_to_show_project_prokan, delete_project__


# def main_cadic():
#     with st.form('input_form_1'):
#         # Row 1:
#         col_left_prj_grid = grid(1,2,2,2,vertical_align="top")
#         col_left_prj_grid.header("Project")
#         # Row 2:
#         code=col_left_prj_grid.text_input("Model Code")
#         pwt=col_left_prj_grid.selectbox("PowerTrain",['EV', 'e-Power', 'ICE'])
#         # Row 3
#         case= col_left_prj_grid.selectbox("Case",['CASE1', 'CASE1.5', 'CASE2'])
#         plant=col_left_prj_grid.selectbox("Plant",['JPN', 'US', 'EUR', 'PRC'])
#         # Row 4:
#         row_butt=st.columns(3)
#         if row_butt[1].form_submit_button("DELETE IN DB", use_container_width=True):
#             with st.spinner(text="In progress..."):
#                 notice=delete_project(code,plant,pwt,case)
#             st.write(notice)


# if __name__ == "__main__":
#     try:
#         if st.session_state.position!="staff":
#             main()
#         else:
#             st.warning("Permission Deny!")
#     except:
#         st.warning("Please login before running app!!!")
def delete_database():

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            '<h1 style="text-align: center;border: 2px solid #4CAF50; padding: 10px;">仕様表</h1>',
            unsafe_allow_html=True)
        st.subheader("")
        all_project = querry_to_show_project()
        st.session_state.data_frame1 = st.data_editor(all_project, key='editor1', height=500, width=1000)
        delete1_placeholder = st.empty()
        with delete1_placeholder.container():
            col1_empty, col1_delete, col1_empty2 = st.columns([4, 2, 4])
            with col1_delete:
                if st.button("DELETE", key='delete1'):
                    df_after_deleted = delete_project_syo(st.session_state.data_frame1)
                    st.rerun()

    with col2:
        st.markdown(
            '<h1 style="text-align: center;border: 2px solid #4CAF50; padding: 10px;">プロ管</h1>',
            unsafe_allow_html=True)
        st.subheader("")
        all_project = querry_to_show_project_prokan()
        st.session_state.data_frame2 = st.data_editor(all_project, key='editor2', height=500, width=1000)
        delete2_placeholder = st.empty()
        with delete2_placeholder.container():
            col2_empty, col2_delete, col2_empty2 = st.columns([4, 2, 4])
            with col2_delete:
                if st.button("DELETE", key='delete2'):
                    #st.write('delete test')
                    df_after_deleted = delete_project__(st.session_state.data_frame2)
                    st.rerun()
