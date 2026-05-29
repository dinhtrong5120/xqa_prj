import os
import streamlit as st
import shutil
from xqa_web_tvso.app.setting import BASE_DIR_OUTPUTS


# フォルダを削除する関数
def delete_folders(folder_paths):
    for folder_path in folder_paths:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            st.success(f"フォルダ {folder_path} を削除しました。")
        else:
            st.error(f"フォルダ {folder_path} が見つかりませんでした。")


# Streamlitアプリケーションのセットアップ
def delete_output():
    with st.form('input_form_4'):
        st.title("フォルダ削除ページ")
        st.caption('こちらのページはトライアル用に削除をしやすくするために用意しました。')

        # 削除するフォルダを選択
        folder_list = [
            folder
            for folder in os.listdir(BASE_DIR_OUTPUTS)
            if not folder.startswith(".") and not "list_acc.json" in folder
        ]
        st.write(folder_list)
        selected_folders = st.multiselect(
            "削除するフォルダを選択してください:", folder_list
        )

        # 選択されたフォルダのパスを作成
        folder_paths = [os.path.join(BASE_DIR_OUTPUTS, folder) for folder in selected_folders]

        # フォルダが選択された場合、削除ボタンを表示
        if st.form_submit_button("選択されたフォルダを削除"):
            delete_folders(folder_paths)


# if __name__ == "__main__":
#     try:
#         if st.session_state.position!="staff":
#             main()
#         else:
#             st.warning("Permission Deny!")
#     except:
#         st.warning("Please login before running app!!!")
