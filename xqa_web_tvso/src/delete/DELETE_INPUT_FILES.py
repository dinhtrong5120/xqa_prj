import os
import streamlit as st
from xqa_web_tvso.app.setting import BASE_DIR_DATAS

# 指定されたフォルダ内のファイルを取得する関数
def get_files_in_folder(folder_path):
    files = os.listdir(folder_path)
    return files


# ファイルを削除する関数
def delete_files(file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            st.success(f"ファイル {file_path} を削除しました。")
        else:
            st.error(f"ファイル {file_path} が見つかりませんでした。")

# Streamlitアプリケーションのセットアップ
def delete_input_file(selected_folder):
    with st.form('input_form_2'):
        #st.title("ファイル削除ページ")
        #st.caption('こちらのページはトライアル用に削除をしやすくするために用意しました。')

        #folder_list = [
            #folder
            #for folder in os.listdir(BASE_DIR_DATAS)
            #if not folder.startswith(".") and not "list_acc.json" in folder
        #]
        #selected_folder = st.selectbox("削除するフォルダを選択してください:", folder_list)

        # 選択されたフォルダのパスを作成
        try:
            folder_path = os.path.join(BASE_DIR_DATAS, selected_folder)

            # 選択されたフォルダ内のファイルを取得
            files = get_files_in_folder(folder_path)

            # ファイルを選択して削除
            files_to_delete = st.multiselect("削除するファイルを選択してください:", files)

            # 選択されたファイルのフルパスを作成
            
            file_paths = [os.path.join(folder_path, file) for file in files_to_delete]
        except:
            file_paths=[]
        if st.form_submit_button("選択されたファイルを削除"):
        # ファイルが選択された場合、削除ボタンを表示
            delete_files(file_paths)

# if __name__ == "__main__":
#     try:
#         if st.session_state.position!="staff":
#             try:
#                 main()
#             except:
#                 st.warning("Input is empty!")
#         else:
#             st.warning("Permission Deny!")
#     except:
#         st.warning("Please login before running app!!!")
