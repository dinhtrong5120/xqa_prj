import os
import shutil
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple

def check_file_exists(file_path: str) -> None:
    """
    Kiểm tra file có tồn tại không. Nếu không raise FileNotFoundError.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File không tồn tại: {file_path}")
        

def check_format_car_sheet(file_path: str, sheet_name: str) -> list:
    """
    Trả về list các lỗi format của sheet car.
    """
    errors = []
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    except Exception as e:
        errors.append(f"Lỗi đọc sheet: {e}")
        return errors

    expected_values = [
        "Plant", "BODY", "ENGINE", "AXLE", "HANDLE", 
        "GRADE", "TRANS", "YEAR", "INTAKE", "ZONE", 
        "EQUIP", "Appl No"
    ]
    actual_values = [str(df.iloc[i, 4]).strip() for i in range(5, 17)]
    if actual_values != expected_values:
        errors.append(
            f"Cột 4 dòng 5~16 không đúng định dạng. Expected: {expected_values}, Actual: {actual_values}"
        )

    val_opt = str(df.iloc[17, 136]).strip()
    if val_opt != "オプション指定欄":
        errors.append(
            f"Cột 136 dòng 17 phải là 'オプション指定欄', hiện tại: {val_opt}"
        )

    val_abs = str(df.iloc[18, 136]).strip()
    if val_abs != "絶対に必要な仕様":
        errors.append(
            f"Cột 136 dòng 18 phải là '絶対に必要な仕様', hiện tại: {val_abs}"
        )
    return errors

def check_format_form_sheet(file_path: str, sheet_name: str) -> list:
    """
    Trả về list các lỗi format của sheet form.
    """
    errors = []
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    except Exception as e:
        errors.append(f"Lỗi đọc sheet: {e}")
        return errors

    expected_zone = [
        "Zone", "Body", "Engine", "Axle", "Handle", "Grade", "Trans", "Year", "Intake", "Equip", "APP№"
    ]
    actual_zone = [str(df.iloc[i, 7]).strip() for i in range(13, 24)]
    if actual_zone != expected_zone:
        errors.append(
            f"Cột 7 dòng 13~23 không đúng định dạng. Expected: {expected_zone}, Actual: {actual_zone}"
        )

    val_spec_code = str(df.iloc[35, 10]).replace('\n', ' ').strip().lower()
    if "spec code" not in val_spec_code:
        errors.append(
            f"Cột 10 dòng 35 phải chứa 'Spec Code', hiện tại: {df.iloc[35, 10]}"
        )

    val_opt_mark = str(df.iloc[35, 11]).strip()
    if val_opt_mark != 'オプションを取る場合は"*"':
        errors.append(
            f"Cột 11 dòng 35 phải là 'オプションを取る場合は\"*\"', hiện tại: {val_opt_mark}"
        )

    expected_row36 = ["Pair", "Exclusion", "CLAS2", "*", "*"]
    actual_row36 = [str(df.iloc[36, i]).strip() for i in range(8, 13)]
    if actual_row36 != expected_row36:
        errors.append(
            f"Dòng 36 cột 8~12 không đúng định dạng. Expected: {expected_row36}, Actual: {actual_row36}"
        )
    return errors


def get_excel_sheets(file_path: str) -> List[str]:
    """
    Lấy danh sách tên sheet của một file excel.
    """
    return pd.ExcelFile(file_path).sheet_names

def map_sheets(sheet_car: List[str], sheet_form: List[str]) -> List[Tuple[str, str]]:
    """
    Mapping tên sheet trùng nhau theo quy tắc:
        - Nếu sheet trong car là 'PFC_車両', sheet form là 'PFC' thì coi là trùng.
        - Các sheet khác trùng tên trực tiếp.
    Trả về list tuple (sheet_car, sheet_form).
    """
    mapping = []
    for s_car in sheet_car:
        s_form = None
        if s_car.endswith("車両"):
            base = s_car.replace("_車両", "")
            for s in sheet_form:
                if s == base:
                    s_form = s
                    break
        if not s_form and s_car in sheet_form:
            s_form = s_car
        if s_form:
            mapping.append((s_car, s_form))
    return mapping

def check_all_sheet_formats(path_folder_output, path_file_form_excel):

    # 1. Kiểm tra file car, path_file_form_excel
    path_file_car = os.path.join(path_folder_output, "Car配車要望表.xlsx")
    check_file_exists(path_file_car)
    check_file_exists(path_file_form_excel)

    # Lấy sheet
    sheet_car = get_excel_sheets(path_file_car)
    sheet_form = get_excel_sheets(path_file_form_excel)
    mapping_sheets = map_sheets(sheet_car, sheet_form)

    all_errors = []
    for sheet_car, sheet_form in mapping_sheets:
        car_errors = check_format_car_sheet(path_file_car, sheet_car)
        form_errors = check_format_form_sheet(path_file_form_excel, sheet_form)

        if car_errors:
            all_errors.append(f"[Car][{sheet_car}]:\n" + "\n".join(f"  - {err}" for err in car_errors))
        if form_errors:
            all_errors.append(f"[Form][{sheet_form}]:\n" + "\n".join(f"  - {err}" for err in form_errors))

    if all_errors:
        error_report = "\n\n".join(all_errors)
        raise ValueError(f"Phát hiện lỗi định dạng ở các sheet sau:\n\n{error_report}")

# Example usage:
if __name__ == "__main__":
    # Example default paths (for testing)
    # case 1: FileNotFoundError: File không tồn tại: xqa_web_tvso\app\test_demo_step3\data1\Car配車要望表.xlsx
    # path_folder_output = r"xqa_web_tvso\app\test_demo_step3\data1"
    # path_file_form_excel = r"xqa_web_tvso\app\test_demo_step3\form\車両仕様表サンプル.xlsx"
    # check_all_sheet_formats(path_folder_output, path_file_form_excel)

    # # case 2: FileNotFoundError: File không tồn tại: xqa_web_tvso\app\test_demo_step3\form\sample.xlsx
    # path_folder_output = r"xqa_web_tvso\app\test_demo_step3\data"
    # path_file_form_excel = r"xqa_web_tvso\app\test_demo_step3\form\sample.xlsx"
    # check_all_sheet_formats(path_folder_output, path_file_form_excel)

    # case 3: tesst cacs case sai format
    path_folder_output = r"xqa_web_tvso\app\test_demo_step3_v2\data"
    path_file_form_excel = r"xqa_web_tvso\app\test_demo_step3_v2\form\車両仕様表サンプル.xlsx"
    check_all_sheet_formats(path_folder_output, path_file_form_excel)