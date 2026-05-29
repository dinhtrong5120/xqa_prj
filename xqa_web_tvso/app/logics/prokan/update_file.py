import base64
import os
import secrets
import shutil
import subprocess
import os
import shutil
import zipfile
import tarfile


from typing import List
import streamlit as st

try:
    import py7zr
except ImportError:
    py7zr = None
try:
    import rarfile
except ImportError:
    rarfile = None

import pandas as pd
import streamlit as st

from xqa_web_tvso.app.logics.syo.db.funtion_database import offline_edit
from xqa_web_tvso.app.setting import BASE_DIR_FORM_OUT, BASE_DIR_DATAS, BASE_DIR_CADICS_TEMP, VALID_KEY_車両仕様表サンプル


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

def is_valid_excel(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ['.xlsx', '.xls'] and any(keyword.lower() in filename.lower() for keyword in VALID_KEY_車両仕様表サンプル)

def get_valid_excel_files(files: list) -> list:
    """
    Lấy danh sách file Excel hợp lệ ngoài archive.
    Args:
        files (list): Danh sách file upload từ người dùng.
    Returns:
        List các file excel hợp lệ ngoài archive.
    """
    return [f for f in files if is_valid_excel(f.name)]

def save_excel_files(excel_files: list, folder: str) -> list:
    """
    Lưu các file excel ngoài archive vào thư mục chỉ định.
    Args:
        excel_files (list): Danh sách file excel hợp lệ.
        folder (str): Đường dẫn thư mục lưu file.
    Returns:
        List đường dẫn file đã lưu.
    """
    saved_paths = []
    for f in excel_files:
        path = os.path.join(folder, f.name)
        with open(path, "wb") as out_f:
            out_f.write(f.getvalue())
        saved_paths.append(path)
    return saved_paths

def extract_and_get_excel_files(archive_files: list, folder: str) -> list:
    """
    Extract các file archive và lấy danh sách file excel hợp lệ sau extract.
    Args:
        archive_files (list): Danh sách file archive (.zip, .7z, ...)
        folder (str): Đường dẫn thư mục extract.
    Returns:
        List đường dẫn file excel hợp lệ sau extract.
    """
    extracted_excel = []
    for arc in archive_files:
        arc_path = os.path.join(folder, arc.name)
        with open(arc_path, "wb") as out_f:
            out_f.write(arc.getvalue())
        extract(arc_path, folder)
        os.remove(arc_path)
    # Tìm tất cả file excel hợp lệ sau extract
    for root, dirs, files_in_folder in os.walk(folder):
        for fname in files_in_folder:
            fp = os.path.join(root, fname)
            if is_valid_excel(fname):
                extracted_excel.append(fp)
            else:
                try:
                    os.remove(fp)
                except Exception as e:
                    print(f"Error deleting non-excel file {fp}: {e}")
    return extracted_excel

def check_excel_file_conflict(
    excel_files: list, extracted_excel_files: list
) -> tuple[list, str]:
    """
    Kiểm tra tổng số file excel hợp lệ (ngoài archive + trong archive),
    log lỗi rõ nguồn nếu có nhiều hơn 1 file.
    Args:
        excel_files (list): File excel ngoài archive.
        extracted_excel_files (list): File excel sau extract.
    Returns:
        Tuple (list file hợp lệ cuối cùng, lỗi nếu có)
    """
    all_valid = excel_files + extracted_excel_files
    errors = ""
    if len(all_valid) == 0:
        errors = (
            f"No valid Excel file uploaded! "
            f"Please upload one Excel file whose name contains one of: [{VALID_KEY_車両仕様表サンプル}]. "
            "You may upload the file directly or inside an archive."
        )
    elif len(all_valid) > 1:
        sources = []
        if excel_files:
            sources.append(f"{len(excel_files)} file(s) uploaded directly")
        if extracted_excel_files:
            sources.append(f"{len(extracted_excel_files)} file(s) extracted from archive")
        errors = (
            f"Multiple valid Excel files detected ({', '.join(sources)}). "
            f"Please upload only one Excel file whose name contains one of: [{VALID_KEY_車両仕様表サンプル}], "
            "either directly or inside an archive."
        )
    return all_valid, errors

def fast_clear_folder(folder_path):
    """
    Quickly delete all files and subfolders in folder_path by removing and recreating the folder.
    """
    try:
        # Remove the entire folder
        shutil.rmtree(folder_path)
        # Recreate the empty folder
        os.makedirs(folder_path, exist_ok=True)
    except Exception as e:
        print(f"Error clearing folder {folder_path}: {e}")

def process_uploaded_車両仕様表_Form_files(
    files: list, car_name: str
) -> tuple[list, str, int]:
    """
    Xử lý upload 車両仕様表_Form: kiểm tra model code, kiểm tra file excel hợp lệ,
    log lỗi rõ ràng.
    Args:
        files (list): Danh sách file upload từ người dùng.
        car_name (str): Mã xe/model code.
    Returns:
        Tuple (list file excel hợp lệ, lỗi, count_file_not_form)
    """
    if 'message_12' in st.session_state:
        del st.session_state['message_12']

    # folder = os.path.join(BASE_DIR_DATAS, car_name, "車両仕様表_Form")
    # Tạo các thư mục
    folder_save_file_upload = os.path.join(BASE_DIR_DATAS, car_name, "車両仕様表_Form")
    folder_excel = os.path.join(folder_save_file_upload, "excel_files")
    folder_archive = os.path.join(folder_save_file_upload, "archive_files")
    # folder_backup_error = os.path.join(folder_save_file_upload, "backup_error")
    os.makedirs(folder_excel, exist_ok=True)
    os.makedirs(folder_archive, exist_ok=True)
    # os.makedirs(folder_backup_error, exist_ok=True)
    errors = ""
    count_file_not_form = 0

    excel_files = get_valid_excel_files(files)
    archive_files = [f for f in files if os.path.splitext(f.name)[1].lower() in
                     ['.zip', '.7z', '.rar', '.tar', '.gz', '.bz2', '.tar.gz', '.tar.bz2']]
    saved_excel = save_excel_files(excel_files, folder_excel) if excel_files else []
    extracted_excel = extract_and_get_excel_files(archive_files, folder_archive) if archive_files else []

    all_valid, errors = check_excel_file_conflict(saved_excel, extracted_excel)

    # Nếu hợp lệ chỉ có 1 file, đổi tên chuẩn
    if len(all_valid) == 1:
        target = os.path.join(folder_save_file_upload, f"車両仕様表_{car_name}.xlsx")
        file_form_default = os.path.join(BASE_DIR_FORM_OUT, "Step2", "車両仕様表_Form.xlsx")
        src = all_valid[0]
 
        base_name = os.path.basename(src)
        if "車両仕様表_Form.xlsx".lower() == base_name.lower():
            if os.path.exists(file_form_default):
                os.remove(file_form_default)
            os.makedirs(os.path.dirname(file_form_default), exist_ok=True)            
            shutil.move(src, file_form_default)
            st.session_state.message_13 = f"Update complete file {base_name} to 車両仕様表_Form Default . "

        elif f"車両仕様表_{car_name}.xlsx".lower() == base_name.lower() and car_name and car_name.strip() != "":
            if os.path.exists(target):
                os.remove(target)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.move(src, target)
            st.session_state.message_13 = f"Update complete file {base_name} to 車両仕様表_Form for {car_name} "

        elif not car_name or car_name.strip() == "":
            err = "Check model code: Model Code is None"
            st.session_state.message_12 = err
            return [], err, 1
            

        else:
            str_error = (
                f"The file name is invalid: {base_name}. "
                f"Please upload either '車両仕様表_Form.xlsx' to update the default form, "
                f"or '車両仕様表_{car_name}.xlsx' to update the car-specific form."
            )
            
            errors += "\n" + str_error
            

        all_valid = [target]
    else:
        count_file_not_form = 1

    # Nếu lỗi: move toàn bộ file và folder sang backup_error
    for remove_dir in [folder_excel, folder_archive]:
        if os.path.exists(remove_dir):
            shutil.rmtree(remove_dir)
            
    st.session_state.message_11 = errors
    return all_valid, errors, count_file_not_form


def update_file_into_server_new(car_name, List_file, csrf_token):
    if csrf_token != get_csrf_token():
        st.error("Invalid CSRF token. This request is not allowed.")
        st.session_state.message_3 = "Invalid CSRF token. This request is not allowed."
    for file in List_file:
        # st.write('file: ', file.name)
        if (file.name in ['仕様表.zip', '仕様表.7z']) or (
                file.name.startswith('仕様表') and 'FORM' not in file.name.upper()):
            folder_save_file_upload = os.path.join(BASE_DIR_DATAS, "仕様表")
            # st.write('folder_save_file_upload: ',folder_save_file_upload)
            # if os.path.exists(folder_save_file_upload):
            #     shutil.rmtree(folder_save_file_upload)
            if not os.path.exists(folder_save_file_upload):
                os.makedirs(folder_save_file_upload)

            file_path = os.path.join(folder_save_file_upload, file.name)
            # st.write('file_path: ', file_path)
            with open(file_path, "wb") as f:
                f.write(file.getvalue())

            # ===================extract file .zip, .7z=======================
            if '仕様表' in file.name and (".zip" in file.name or ".7z" in file.name):
                extract(file_path, folder_save_file_upload)
                os.remove(file_path)
            st.session_state.message_10 = "仕様表 Updated"


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
                syo_files = [f for f in os.listdir(folder_save_file_upload) if f.endswith('.xlsx') and f.startswith('仕様表')]
                if len(syo_files) > 0:
                    destination_syo_folder = os.path.join(BASE_DIR_DATAS, "仕様表")
                    os.makedirs(destination_syo_folder, exist_ok=True)
                    for item in syo_files:
                        source_item_1 = os.path.join(folder_save_file_upload, item)
                        shutil.copy2(source_item_1, destination_syo_folder)
                st.session_state.message_10 = "プロ管 Updated"
                try:
                    del st.session_state['message_5']
                except:
                    pass
            elif car_name == "" or car_name.upper() not in file.name.upper() and file.name.upper() != "CADICS_ALL.CSV":

                st.error('No files have been uploaded for ファイルをインポート (仕様表, 関連表①，②，③，④)')
                st.session_state.message_10 = 'No files have been uploaded for ファイルをインポート (仕様表, 関連表①，②，③，④)'


def update_file_after_edit(code, pwt, plant, case, file_updates, csrf_token, name_user):
    flag = 0
    if csrf_token != get_csrf_token():
        st.session_state.message_3 = "Invalid CSRF token. This request is not allowed."
        return "Invalid CSRF token. This request is not allowed."
    for file_update in file_updates:
        if file_update.name == "CADICS_ALL.csv":
            flag = 1
            if code != "" and code != None:
                try:
                    new_data = pd.read_csv(file_update, header=None)
                except:
                    return "Encoding Error ! Please check file CADICS.csv !"
                folder_name = str(name_user).upper() + "_" + str(code).upper() + "_" + str(pwt).upper() + "_" + str(
                    plant).upper() + "_" + str(case).upper()
                folder_save_file_update = os.path.join(BASE_DIR_CADICS_TEMP, folder_name, "CADICS_ALL.csv")
                if not os.path.exists(folder_save_file_update):
                    return "FAIL: There is no cadic references"
                else:
                    old_data = pd.read_csv(folder_save_file_update, header=None)
                    st.write(folder_save_file_update)
                    st.write(new_data)
                    st.write(old_data)
                    offline_edit(str(code).upper(), plant, pwt, case, new_data, old_data)
                    return "Update Completed!!!"
            else:
                return "Project not exist!!!"
    if flag == 0:
        return ""


def extract(file_path, output_dir):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    ext = os.path.splitext(file_path)[1].lower()
    # Tên thư mục phụ (nếu có)
    subfolder = os.path.splitext(os.path.basename(file_path))[0]
    subfolder_path = os.path.join(output_dir, subfolder)

    # Giải nén như bình thường
    if ext == ".zip":
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
    elif ext in [".tar", ".gz", ".bz2", ".tar.gz", ".tar.bz2"]:
        with tarfile.open(file_path, 'r:*') as tar_ref:
            tar_ref.extractall(output_dir)
    elif ext == ".7z":
        if py7zr is None:
            raise ImportError("py7zr chưa được cài đặt. Hãy chạy: pip install py7zr")
        with py7zr.SevenZipFile(file_path, mode='r') as z:
            z.extractall(path=output_dir)
    elif ext == ".rar":
        if rarfile is None:
            raise ImportError("rarfile chưa được cài đặt. Hãy chạy: pip install rarfile")
        with rarfile.RarFile(file_path) as rf:
            rf.extractall(output_dir)
    else:
        raise ValueError("Định dạng file không được hỗ trợ.")

    # Nếu có subfolder trùng tên file nén, di chuyển hết ra ngoài rồi xóa subfolder
    if os.path.exists(subfolder_path) and os.path.isdir(subfolder_path):
        move_all_items(subfolder_path, output_dir)
        delete_folder(subfolder_path)


def move_all_items(source_dir, destination_dir):
    # Tạo thư mục đích nếu nó không tồn tại
    os.makedirs(destination_dir, exist_ok=True)

    # Lặp qua tất cả các mục trong thư mục nguồn
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        destination_item = os.path.join(destination_dir, item)

        # Di chuyển từng mục sang thư mục đích
        shutil.move(source_item, destination_item)


def delete_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f'Thư mục {folder_path} đã được xóa.')
    else:
        print(f'Thư mục {folder_path} không tồn tại.')


def move_all_items(source_dir, destination_dir):
    # Tạo thư mục đích nếu nó không tồn tại
    os.makedirs(destination_dir, exist_ok=True)

    # Lặp qua tất cả các mục trong thư mục nguồn
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        destination_item = os.path.join(destination_dir, item)

        # Di chuyển từng mục sang thư mục đích
        shutil.move(source_item, destination_item)


def delete_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f'Thư mục {folder_path} đã được xóa.')
    else:
        print(f'Thư mục {folder_path} không tồn tại.')
