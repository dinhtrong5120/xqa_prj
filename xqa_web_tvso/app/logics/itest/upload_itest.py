import base64
import os
import secrets
import shutil
import subprocess

import streamlit as st
from xqa_web_tvso.app.setting import BASE_DIR_DATAS


@st.cache_resource
def get_csrf_token():
    return base64.b64encode(secrets.token_bytes(32)).decode("utf-8")


def update_file_itest(car_name, List_file, csrf_token):
    car_name = car_name.upper()
    if csrf_token != get_csrf_token():
        st.error("Invalid CSRF token. This request is not allowed.")
        st.session_state.message_3 = "Invalid CSRF token. This request is not allowed."

    if car_name == "":
        for file in List_file:
            if file.name == 'AABB表.xlsx':
                file_path = os.path.join(BASE_DIR_DATAS, file.name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                with open(file_path, "wb") as f:
                    f.write(file.getvalue())
                break
            try:
                vote('Check the uploaded file again')
            except:
                pass
    if car_name != "":
        folder_path = os.path.join(BASE_DIR_DATAS, car_name)
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)
        for file in List_file:
            if file.name == 'AABB表.xlsx':
                file_path = os.path.join(BASE_DIR_DATAS, file.name)
                if os.path.exists(file_path):
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    with open(file_path, "wb") as f:
                        f.write(file.getvalue())
                else:
                    with open(file_path, "wb") as f:
                        f.write(file.getvalue())
            if file.name == "VC要件表_Master.xlsx":
                file_path = os.path.join(folder_path, file.name)
                if os.path.exists(file_path):
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    with open(file_path, "wb") as f:
                        f.write(file.getvalue())
                else:
                    with open(file_path, "wb") as f:
                        f.write(file.getvalue())
            if file.name in ["VC簡素化要件表.zip", "VC簡素化要件表.7z"]:
                folder_vc_path = os.path.join(BASE_DIR_DATAS, car_name, 'VC簡素化要件表')
                file_path = os.path.join(BASE_DIR_DATAS, car_name, file.name)
                #if os.path.exists(folder_vc_path):
                    #shutil.rmtree(folder_vc_path)
                with open(file_path, "wb") as f:
                    f.write(file.getvalue())
                extract(file_path, folder_path)
                os.remove(file_path)
            if car_name in file.name and (".zip" in file.name or ".7z" in file.name):
                folder_temp_path = os.path.join(BASE_DIR_DATAS, 'temp')
                if os.path.exists(folder_temp_path):
                    shutil.rmtree(folder_temp_path)
                os.makedirs(folder_temp_path)
                file_path = os.path.join(folder_temp_path, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getvalue())
                extract(file_path, folder_temp_path)
                if car_name not in os.listdir(folder_temp_path):
                    files = os.listdir(folder_temp_path)
                    folder_temp_path_child = folder_temp_path
                else:
                    folder_temp_path_child = os.path.join(folder_temp_path, car_name)
                    files = os.listdir(folder_temp_path_child)
                for item_file in files:
                    if item_file == "VC要件表_Master.xlsx":
                        source_item = os.path.join(folder_temp_path_child, item_file)
                        destination_item = os.path.join(folder_path, item_file)
                        shutil.move(source_item, destination_item)
                    if item_file == 'AABB表.xlsx':
                        source_item = os.path.join(folder_temp_path_child, item_file)
                        destination_item = os.path.join(BASE_DIR_DATAS, item_file)
                        shutil.move(source_item, destination_item)
                    if item_file == 'VC簡素化要件表':
                        source_item = os.path.join(folder_temp_path_child, item_file)
                        destination_item = os.path.join(folder_path, item_file)
                        if os.path.exists(destination_item):
                            shutil.rmtree(destination_item)
                        # print('source_item: ',source_item)
                        # print('destination_item: ',destination_item)
                        shutil.move(source_item, destination_item)
                shutil.rmtree(folder_temp_path)
    vote('Update completed')
    # st.balloons()
    # rain(
    #     emoji="🎈",
    #     font_size=90,
    #     falling_speed=5,
    #     animation_length="infinite",
    # )

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
#         # move_all_items(folder, output_dir)
#         # delete_folder(folder)
#     if ".7z" in file_path:
#         subprocess.run([seven_zip_path, "x", file_path, f"-o{output_dir}", "-y"])
#         folder = file_path[:-3]  # Lấy đường dẫn mà không có phần mở rộng .7z
#         # if "仕様表" not in file_path:
#         # move_all_items(folder, output_dir)
#         # delete_folder(folder)


def extract(file_path, output_dir):
    # Tạo thư mục đích nếu nó chưa tồn tại
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Giải nén tệp .7z vào thư mục đích
    # subprocess.run(["7z","x",file_path,f"-o{output_dir}","-mcp=UTF-8"])
    # patoolib.extract_archive(file_path, outdir=output_dir)
    if ".zip" in file_path:
        subprocess.run(["unar","-f", file_path, "-o", output_dir])
        folder = file_path[0:len(file_path) - 4]
        # move_all_items(folder, output_dir)
        # delete_folder(folder)
    if ".7z" in file_path:
        subprocess.run(["7z", "x", file_path, f"-o{output_dir}", "-y"])
        folder = file_path[0:len(file_path) - 3]
        # move_all_items(folder, output_dir)
        # delete_folder(folder)


def delete_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f'Thư mục {folder_path} đã được xóa.')
    else:
        print(f'Thư mục {folder_path} không tồn tại.')


@st.dialog("Notification")
def vote(item):
    st.write(item)
