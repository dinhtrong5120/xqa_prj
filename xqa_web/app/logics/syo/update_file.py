import base64
import os
import secrets
import shutil
import subprocess
import sys

import pandas as pd
import streamlit as st

import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from .db.funtion_database import offline_edit
from xqa_web.app.setting import BASE_DIR_DATAS, BASE_DIR_CADICS_TEMP


@st.cache_resource
def get_csrf_token():
    return base64.b64encode(secrets.token_bytes(32)).decode("utf-8")


def update_file_into_server(car_name, List_file, csrf_token):
    if csrf_token != get_csrf_token():
        st.error("Invalid CSRF token. This request is not allowed.")
        st.session_state.message_3 = "Invalid CSRF token. This request is not allowed."
        return
    if car_name != "":
        car_name = str(car_name).upper()
        folder_save_file_upload = os.path.join(BASE_DIR_DATAS, car_name)
        if not os.path.exists(folder_save_file_upload):
            os.makedirs(folder_save_file_upload)
        for file in List_file:
            file_path = os.path.join(folder_save_file_upload, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getvalue())

            # ===================extract file .zip, .7z=======================
            if car_name in file.name and (".zip" in file.name or ".7z" in file.name):
                extract(file_path, folder_save_file_upload)

        if len(List_file) != 0:
            st.write("Update File Completed!!!")


def update_file_into_server_new(car_name, List_file, csrf_token):
    if csrf_token != get_csrf_token():
        st.error("Invalid CSRF token. This request is not allowed.")
        st.session_state.message_3 = "Invalid CSRF token. This request is not allowed."
    for file in List_file:
        if (file.name in ['仕様表.zip', '仕様表.7z']) or (
                file.name.startswith('仕様表') and 'FORM' not in file.name.upper()):
            folder_save_file_upload = os.path.join(BASE_DIR_DATAS, "仕様表")
            if not os.path.exists(folder_save_file_upload):
                os.makedirs(folder_save_file_upload)

            file_path = os.path.join(folder_save_file_upload, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getvalue())

            # ===================extract file .zip, .7z=======================
            if '仕様表' in file.name and (".zip" in file.name or ".7z" in file.name):
                extract(file_path, folder_save_file_upload)
                os.remove(file_path)
            st.session_state.message_10 = "仕様表 Updated"
        elif file.name.startswith('関連表') and file.name.endswith('.xlsx') and car_name != "":
            car_name = str(car_name).upper()
            folder_save_file_upload = os.path.join(BASE_DIR_DATAS, car_name)
            if not os.path.exists(folder_save_file_upload):
                os.makedirs(folder_save_file_upload)
            source_item_1 = os.path.join(folder_save_file_upload, file.name)
            with open(source_item_1, "wb") as f:
                f.write(file.getvalue())
            st.success("Update 関連表 Completed!!!")
        else:
            if car_name != "" and car_name.upper() in file.name.upper():
                car_name = str(car_name).upper()
                folder_save_file_upload = os.path.join(BASE_DIR_DATAS, car_name)
                if not os.path.exists(folder_save_file_upload):
                    os.makedirs(folder_save_file_upload)
                file_path = os.path.join(folder_save_file_upload, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getvalue())

                # ===================extract file .zip, .7z=======================
                if car_name in file.name and (".zip" in file.name or ".7z" in file.name):
                    extract(file_path, folder_save_file_upload)
                    os.remove(file_path)
                syo_files = [f for f in os.listdir(folder_save_file_upload) if
                             f.endswith('.xlsx') and f.startswith('仕様表')]
                if len(syo_files) > 0:
                    destination_syo_folder = os.path.join(BASE_DIR_DATAS, "仕様表")
                    os.makedirs(destination_syo_folder, exist_ok=True)
                    for item in syo_files:
                        source_item_1 = os.path.join(folder_save_file_upload, item)
                        shutil.copy2(source_item_1, destination_syo_folder)
                st.session_state.message_10 = "プロ管 Updated"
            elif car_name == "" or car_name.upper() not in file.name.upper():
                if file.name != "仕様表_FORM.xlsx":
                    st.session_state.message_10 = 'Check model code or file name'

def update_file_after_edit(code, pwt, plant, case, file_updates, csrf_token, name_user):
    all_variables = dir()
    with open('update_file_after_edit_input.txt', 'w' , encoding='utf-8') as f:
        for item in all_variables:
            f.write(str(item) + "=" + str(eval(item)) + '\n')
    flag = 0
    if csrf_token != get_csrf_token():
        st.session_state.message_3 = "Invalid CSRF token. This request is not allowed."
        return "Invalid CSRF token. This request is not allowed."
    for file_update in file_updates:
        if file_update.name == "CADICS_ALL.csv":
            flag = 1
            if code != "" and code != None:
                new_data = pd.read_csv(file_update, header=None)
                folder_name = str(name_user).upper() + "_" + str(code).upper() + "_" + str(pwt).upper() + "_" + str(
                    plant).upper() + "_" + str(case).upper()
                folder_save_file_update = os.path.join(BASE_DIR_CADICS_TEMP, folder_name, "CADICS_ALL.csv")
                if not os.path.exists(folder_save_file_update):
                    return "FAIL: There is no cadic references"
                else:
                    old_data = pd.read_csv(folder_save_file_update, header=None)
                    offline_edit(str(code).upper(), plant, pwt, case, new_data, old_data)
                    return "Update Completed!!!"
            else:
                return "Project not exist!!!"
    if flag == 0:
        return ""


# def extract(file_path, output_dir):
#     # Tạo thư mục đích nếu nó chưa tồn tại
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#     seven_zip_path = shutil.which("7z")
#
#     # Nếu không tìm thấy 7z trong PATH, sử dụng đường dẫn mặc định
#     if seven_zip_path is None:
#         seven_zip_path = "C:\\Program Files\\7-Zip\\7z.exe"  # Thay thế bằng đường dẫn đầy đủ đến 7z.exe nếu cần
#
#     if not os.path.exists(seven_zip_path):
#         raise FileNotFoundError(
#             f"The command '{seven_zip_path}' was not found. Please install it or add it to your PATH.")
#
#     if ".zip" in file_path:
#         subprocess.run([seven_zip_path, "x", file_path, f"-o{output_dir}", "-y"])
#         folder = file_path[:-4]  # Lấy đường dẫn mà không có phần mở rộng .zip
#         # if "仕様表" not in file_path:
#         move_all_items(folder, output_dir)
#         delete_folder(folder)
#     if ".7z" in file_path:
#         subprocess.run([seven_zip_path, "x", file_path, f"-o{output_dir}", "-y"])
#         folder = file_path[:-3]  # Lấy đường dẫn mà không có phần mở rộng .7z
#         # if "仕様表" not in file_path:
#         move_all_items(folder, output_dir)
#         delete_folder(folder)


def extract(file_path, output_dir):
    all_variables = dir()
    with open('extract_input.txt', 'w' , encoding='utf-8') as f:
        for item in all_variables:
            f.write(str(item) + "=" + str(eval(item)) + '\n')
    # Tạo thư mục đích nếu nó chưa tồn tại
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Giải nén tệp .7z vào thư mục đích
    if ".zip" in file_path:
        subprocess.run(["unar", file_path, "-o", output_dir])
        folder = file_path[0:len(file_path) - 4]
        move_all_items(folder, output_dir)
        delete_folder(folder)
    if ".7z" in file_path:
        subprocess.run(["7z", "x", file_path, f"-o{output_dir}"])
        folder = file_path[0:len(file_path) - 3]
        move_all_items(folder, output_dir)
        delete_folder(folder)


def move_all_items(source_dir, destination_dir):
    all_variables = dir()
    with open('move_all_items_input.txt', 'w' , encoding='utf-8') as f:
        for item in all_variables:
            f.write(str(item) + "=" + str(eval(item)) + '\n')
    # Tạo thư mục đích nếu nó không tồn tại
    os.makedirs(destination_dir, exist_ok=True)

    # Lặp qua tất cả các mục trong thư mục nguồn
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        destination_item = os.path.join(destination_dir, item)

        # Di chuyển từng mục sang thư mục đích
        shutil.move(source_item, destination_item)


def delete_folder(folder_path):
    all_variables = dir()
    with open('delete_folder_input.txt', 'w' , encoding='utf-8') as f:
        for item in all_variables:
            f.write(str(item) + "=" + str(eval(item)) + '\n')
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
