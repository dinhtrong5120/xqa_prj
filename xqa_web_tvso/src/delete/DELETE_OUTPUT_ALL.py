# import os
# import streamlit as st
# import shutil

# # Outputフォルダを空にする関数
# def empty_output_folder():
#     output_folder_path = "./output"
#     if os.path.exists(output_folder_path):
#         # Outputフォルダ内のすべてのファイルとフォルダを削除
#         for root, dirs, files in os.walk(output_folder_path, topdown=False):
#             for name in files:
#                 os.remove(os.path.join(root, name))
#             for name in dirs:
#                 shutil.rmtree(os.path.join(root, name))
#         st.success("Outputフォルダを空にしました。")
#     else:
#         st.warning("Outputフォルダが見つかりませんでした。")

# # Streamlitアプリケーションのセットアップ
# def main():
#     st.title("Outputフォルダの空にする")

#     # "Empty Output Folder"ボタンを押した場合、Outputフォルダを空にする
#     if st.button("Empty Output Folder"):
#         empty_output_folder()

# if __name__ == "__main__":
#     main()

import os
import streamlit as st
import shutil
from xqa_web_tvso.app.setting import BASE_DIR_OUTPUTS


# Outputフォルダを空にする関数
def empty_output_folder():
    # output_folder_path = "./xqa_web_tvso/app/outputs"
    if os.path.exists(BASE_DIR_OUTPUTS):
        # Outputフォルダ内のすべてのファイルとフォルダを再帰的に取得
        for root, dirs, files in os.walk(BASE_DIR_OUTPUTS, topdown=False):
            for name in files:
                # .gitkeep ファイル以外を削除
                if name != ".gitkeep":
                    os.remove(os.path.join(root, name))
            for name in dirs:
                # .gitkeep ファイル以外を削除
                if name != ".gitkeep":
                    shutil.rmtree(os.path.join(root, name))
        st.success("Outputフォルダを空にしました。")
    else:
        st.warning("Outputフォルダが見つかりませんでした。")


# Outputフォルダ内のファイルとフォルダの一覧を取得する関数
def list_files_and_folders(folder_path):
    items = []
    if os.path.exists(folder_path):
        for item in os.listdir(folder_path):
            # .gitkeep ファイルを除外
            if item != ".gitkeep":
                items.append(item)
    return items


# Streamlitアプリケーションのセットアップ
def delete_all_output():
    with st.form('input_form_5'):
        st.title("フォルダ全削除ページ")
        st.caption('こちらのページはトライアル用に削除をしやすくするために用意しました。')
        # Outputフォルダのパス
        # output_folder_path = "./xqa_web_tvso/app/outputs"

        # Outputフォルダ内のファイルとフォルダの一覧を取得
        items = list_files_and_folders(BASE_DIR_OUTPUTS)

        # 一覧を表示
        if items:
            st.write("Outputフォルダ内のファイルとフォルダ:")
            for item in items:
                st.write(item)
        else:
            st.write("Outputフォルダにはファイルやフォルダが存在しません。")

        # "Empty Output Folder"ボタンを押した場合、Outputフォルダを空にする
        if st.form_submit_button("Empty Output Folder"):
            empty_output_folder()


# if __name__ == "__main__":
#     try:
#         if st.session_state.position!="staff":
#             main()
#         else:
#             st.warning("Permission Deny!")
#     except:
#         st.warning("Please login before running app!!!")
