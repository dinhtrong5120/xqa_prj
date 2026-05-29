import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from xqa_web_tvso.src.delete.DELETE_DATABASE import delete_database
from xqa_web_tvso.src.delete.DELETE_INPUT_FILES import delete_input_file
from xqa_web_tvso.src.delete.DELETE_INPUT_FOLDERS import delete_input_folder
from xqa_web_tvso.src.delete.DELETE_OUTPUT_FOLDERS import delete_output
from xqa_web_tvso.src.delete.DELETE_OUTPUT_ALL import delete_all_output
import streamlit as st
import pandas as pd
from xqa_web_tvso.app.setting import *
from streamlit_extras.grid import grid



# st.set_page_config(
#     page_title="My Streamlit App",
#     page_icon=":smiley:",
#     layout="wide"
# )
def main():
    # try :
    for item in ['data_syo', 'data_cadics']:
        if item in st.session_state:
            st.session_state[item] = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)], index=range(1, 101)).fillna("")
            try:
                st.session_state['data_pro'][item] = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)], index=range(1, 101)).fillna("")
            except:
                pass
    # st.write(st.session_state)
    if 'position' in st.session_state:
        if st.session_state.position == "admin" or st.session_state.position == "master":
            delete_database()
            st.write("")
            st.write("")
            st.write("")

            st.markdown(
                '<h1 style="text-align: center;border: 2px solid #4CAF50; padding: 10px;">INPUT</h1>',
                unsafe_allow_html=True)
            st.subheader("")
            st.write("")
            col1, col2 = st.columns(2)
            with col1:

                delete_input_folder()
                st.write("")
                st.write("")
                st.write("")
                st.write("")
                st.write("")
            # delete_output(
            with col2:
                try:
                    st.title("ファイル削除ページ")
                    st.caption('こちらのページはトライアル用に削除をしやすくするために用意しました。')

                    folder_list = [
                        folder
                        for folder in os.listdir(BASE_DIR_DATAS)
                        if not folder.startswith(".") and not "list_acc.json" in folder
                    ]
                    selected_folder = st.selectbox("削除するフォルダを選択してください:", folder_list)
                    delete_input_file(selected_folder)
                    st.write("")
                    st.write("")
                    st.write("")
                    st.write("")
                    st.write("")
                except:
                    st.warning("Input is empty3!")
            st.markdown(
                '<h1 style="text-align: center;border: 2px solid #4CAF50; padding: 10px;">OUTPUT</h1>',
                unsafe_allow_html=True)
            st.write("")
            col3, col4 = st.columns(2)
            with col3:
                delete_output()
            with col4:
                delete_all_output()

        else:
            st.warning("Permission Deny!")
    else:
        st.warning("Please login before running app!!!")
    # except:
    #     st.warning("Please login before running app!!!")
