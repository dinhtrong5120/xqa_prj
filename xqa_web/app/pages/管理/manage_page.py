import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))


import streamlit as st
from xqa_web.app.logics.syo.db.funtion_database import change_password, add_new_user, delete_user, get_all_user
from streamlit_extras.grid import grid

# st.set_page_config(
#     page_title="Account Management 🔑",
#     page_icon="",
# )
def main():
    st.markdown(
        r"""
        <style>
        .stMainBlockContainer {
        padding-left: 20%;
        padding-right: 30%;
        }
        </style>
        """, unsafe_allow_html=True
    )
    try:
        if st.session_state.name_user != None:
            st.title("# ACCOUNT MANAGEMENT! 🔑")
            st.header("CHANGE PASSWORD:")
            # username = st.text_input("Username")
            password_old = st.text_input("Old Password:", type="password")
            password_new1 = st.text_input("New Password:", type="password")
            password_new2 = st.text_input("Confirm Password:", type="password")
            if st.button("CHANGE PASSWORD"):
                # Check if the username and password are correct
                if password_new1 == password_new2:
                    notice = change_password(st.session_state.name_user, password_old, password_new1)
                    st.write(notice)
                else:
                    st.write("New password error")
    except:
        st.warning("Please login before running app!!!")

    try:
        if st.session_state.position != "staff":
            st.session_state.flagdf = 0
            st.header("CREATE OR DELETE ACCOUNT:")
            if st.session_state.position == "master":
                list_type = ["admin", "staff"]
            else:
                list_type = ['staff']

            local = grid(2, 2, vertical_align="top")
            local.selectbox("Type Account:", list_type, key="type_acc")
            if st.session_state.position == 'master':
                local.text_input("Project:", key="project")
            else:
                local.selectbox("Project:", [st.session_state.project_query], key="project")

            local.text_input("Username:", key="username_")
            local.text_input("Password:", type="password", key="password_new_")
            row_butt = st.columns(4)
            with row_butt[0]:
                if st.button("CREATE ACCOUNT", use_container_width=True):
                    notice = add_new_user(st.session_state.username_, st.session_state.password_new_,
                                          st.session_state.type_acc, st.session_state.project)
                    st.write(notice)

            with row_butt[1]:
                if st.button("View User", use_container_width=True):
                    frame_user = get_all_user(st.session_state.project_query)
                    # df.to_csv(r"C:\Users\KNT19862\Desktop\WORK\NO1_FINAL\xxxx.csv")
                    frame_user['Delete'] = False
                    frame_user.rename(columns={0: "id"})
                    st.session_state.frame_user = frame_user
                    # st.data_editor(st.session_state.xxx,num_rows="fix",disabled=["",'username', 'permission', 'project'], hide_index=True,key="yyy")

            frame_edited = st.data_editor(st.session_state.frame_user, num_rows="fix",
                                          disabled=["", 'username', 'permission', 'project'], hide_index=True, key="yyy", width=1000)
            if st.button("DELETE ACCOUNT"):
                with st.spinner(text="In progress..."):
                    df_delete = frame_edited.loc[frame_edited['Delete'] == True]
                    notice = delete_user(df_delete)
                    st.write(notice)
    except:
        # st.warning("Please login before running app!!!")
        print()

    #         notice=delete_user(st.session_state.username_,st.session_state.type_acc)
    #         st.write(notice)
    # st.session_state.df=df

    # with row_butt[2]:
    #     if st.button("DELETE ACCOUNT",use_container_width=True):
    #         notice=delete_user(st.session_state.username_,st.session_state.type_acc)
    #         st.write(notice)
    # try:
    #     xxx=st.data_editor(st.session_state.df,num_rows="fix",disabled=["",'username', 'permission', 'project'], hide_index=True)
    # except:
    #     None
# except:
#     st.write("xx")
