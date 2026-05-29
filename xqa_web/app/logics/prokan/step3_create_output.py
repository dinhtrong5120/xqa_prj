"""
File: create_output_step3.py

Mục đích:
    Xử lý mapping sheet giữa file yêu cầu xe và file form, điền thông tin xe và spec code vào file output cuối cùng.

Hàm chính:
    fill_final_output(path_folder_output, path_file_form_excel)

Input:
    path_folder_output (str): Đường dẫn thư mục output.
    path_file_form_excel (str): Đường dẫn file form excel.

Output:
    Ghi file '車両仕様表.xlsx' vào thư mục output với dữ liệu đã điền.
"""

import os
import shutil
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from xqa_web.app.logics.prokan.step3_error_log import (
# from step3_error_log import (
    collect_error_log,
    log_duplicate_spec_code,
    log_spec_code_not_in_car,
    log_spec_code_not_in_form,
    log_spec_code_format_error,
    log_invalid_spec_code_value,
    log_car_sheet_format_error,
    export_log_with_color_to_sheet
)

def ensure_latest_form_in_output(source_file, output_folder, filename_prefix="車両仕様表_Form"):
    """
    Đảm bảo luôn có file form mới nhất trong output_folder.
    Nếu source_file mới hơn hoặc chưa có trong output_folder, copy vào.
    Nếu source_file chính là file trong output_folder, không làm gì.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_file = os.path.join(output_folder, f"{filename_prefix}.xlsx")
    if os.path.abspath(source_file) == os.path.abspath(output_file):
        return False
    else:
        shutil.copy2(source_file, output_file)
        return True

def check_file_exists(file_path: str) -> None:
    """
    Kiểm tra file có tồn tại không. Nếu không raise FileNotFoundError.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File không tồn tại: {file_path}")
        

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

def copy_form_to_output(src: str, dst_folder: str, dst_name: str = "車両仕様表.xlsx") -> str:
    """
    Copy file form to output folder with new name, unless source and destination are the same.
    """
    dst_path = os.path.join(dst_folder, dst_name)
    # If source and destination are the same, do not copy
    if os.path.abspath(src) != os.path.abspath(dst_path):
        shutil.copy(src, dst_path)
    return dst_path

def read_car_info_from_sheet(
    file_path: str, sheet_name: str,
    col_start: int = 5, col_end: int = 134,
    row_start: int = 5, row_end: int = 17
) -> pd.DataFrame:
    """
    Đọc thông tin car từ sheet: các dòng row_start-row_end, các cột col_start-col_end.
    Chỉ lấy các cột có value ở dòng row_start.
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    # Lấy các cột có giá trị ở dòng row_start +1 (BODY)
    cols = [i for i in range(col_start, col_end+1) if not pd.isna(df.iloc[row_start+1, i])]
    info = df.iloc[row_start:row_end+1, cols]
    info.columns = cols
    info.reset_index(drop=True, inplace=True)
    return info

def read_spec_code_from_sheet(file_path: str, sheet_name: str, col: int = 10, start_row: int = 37) -> List[str]:
    """
    Lấy list spec code từ sheet file form: cột col, bắt đầu từ dòng start_row.
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    codes = df.iloc[start_row:, col].dropna().astype(str).map(str.strip)
    return codes[codes != ""].tolist()


def read_feature_matrix_from_car(
    file_path: str, sheet_name: str,
    key_col: int = 136, col_start: int = 5, col_end: int = 134,
    row_start: int = 19
) -> pd.DataFrame:
    """
    Đọc ma trận feature từ file car: từ dòng row_start tới hết, các cột key_col và col_start-col_end.
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    max_row = df.shape[0]
    feature_df = df.iloc[row_start:max_row, [key_col] + list(range(col_start, col_end+1))]
    feature_df = feature_df.dropna(subset=[key_col])
    return feature_df

def reformat_data_car(
    frame_data_car: pd.DataFrame,
    idx_zone: int = 0,
    idx_equip: int = 9,
    idx_appno: int = 10,
    idx_numbers: int = 11
) -> pd.DataFrame:
    """
    Hoán đổi dòng và xóa dòng cuối cùng theo quy tắc yêu cầu.
    """
    n_rows = frame_data_car.shape[0]
    if n_rows <= idx_numbers:
        raise ValueError(f"DataFrame phải có ít nhất {idx_numbers+1} dòng, hiện tại chỉ có {n_rows} dòng.")

    arr = frame_data_car.values.copy()
    arr[idx_zone] = frame_data_car.iloc[idx_equip].values
    arr[idx_equip] = frame_data_car.iloc[idx_appno].values
    arr[idx_appno] = frame_data_car.iloc[idx_numbers].values
    # Thay thế dòng cuối cùng bằng NaN hoặc giá trị phù hợp
    # Nếu mảng có dtype số, dùng np.nan
    arr[idx_numbers] = np.nan
    data_car_new = pd.DataFrame(arr[:-1], columns=frame_data_car.columns)
    return data_car_new

def explode_spec_codes(df, key_col):
    """
    Tách các dòng có nhiều spec code ở key_col thành nhiều dòng, mỗi dòng chỉ chứa một spec code.
    Phân tách bằng dấu phẩy ','.
    """
    df = df.copy()
    # Tạo một cột tạm, tách các spec code thành list
    df['_spec_list'] = df[key_col].astype(str).map(str.strip).str.lower().str.split(',')
    # Loại bỏ khoảng trắng thừa trong từng phần tử
    df['_spec_list'] = df['_spec_list'].apply(lambda lst: [x.strip() for x in lst if x.strip()])
    # Tách dòng
    df_exploded = df.explode('_spec_list')
    # Gán lại vào key_col
    df_exploded[key_col] = df_exploded['_spec_list']
    # Xóa cột tạm
    df_exploded = df_exploded.drop(columns=['_spec_list'])
    return df_exploded

def extract_feature_matrix(
    df_feature: pd.DataFrame,
    ls_spec_codes: List[str],
    key_col: int = 136,
    car_columns: List[int] = None,
    output_mark: str = "*",
    output_not_mark: str = "",
    empty_values = ("", None, "-", np.nan)
) -> pd.DataFrame:
    """
    Tạo DataFrame feature từ df_feature và ls_spec_codes.
    Mỗi dòng là một spec code, mỗi cột là một xe (theo car_columns).
    Nếu tại spec code, xe có value là số thì điền '*', ngược lại '-'.
    """
    # Chuẩn hóa key_col về string, lower, strip để so sánh
    df_feature = df_feature.copy()
    df_feature[key_col] = df_feature[key_col].astype(str).map(str.strip).str.lower()
    
    # TÁCH DÒNG THEO SPEC CODE
    df_feature = explode_spec_codes(df_feature, key_col)

    if car_columns is None:
        data_keys = [c for c in df_feature.columns if c != key_col]
    else:
        data_keys = [c for c in car_columns if c != key_col]
    
    # data_keys = [c for c in df_feature.columns if c != key_col]
    # max_key = max(data_keys) if data_keys else src_start - 1

    rows = []
    for spec_code in ls_spec_codes:
        code_std = str(spec_code).strip().lower()
        df_code = df_feature[df_feature[key_col] == code_std]
        row = []

        if not df_code.empty :
            for i in data_keys:
                if i in df_code.columns:
                    vals = df_code[i]
                    # Nếu có ít nhất một giá trị là số thì mark '*'
                    if vals.apply(lambda x: isinstance(x, (int, float)) and not pd.isna(x)).any():
                        row.append(output_mark)
                    else:
                        row.append(output_not_mark)
                else:
                    row.append(output_not_mark)
        else:
            row = row = [output_not_mark for i in data_keys]
        rows.append(row)

    columns = [f"Car_{i}" for i in data_keys]
    df_out = pd.DataFrame(rows, columns=columns)
    return df_out
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
        "Plant", "BODY", "ENGINE", "AXLE", "HANDLE", "GRADE", "TRANS", "YEAR", "INTAKE", "ZONE", "EQUIP", "Appl No"
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

def fill_final_output(
    path_folder_output: str,
    path_file_form_excel: str
) -> None:
    """
    Hàm chính điền thông tin vào file output cuối cùng và sinh log lỗi.
    """
    # 1. Kiểm tra file car, path_file_form_excel
    path_file_car = os.path.join(path_folder_output, "Car配車要望表.xlsx")
    check_file_exists(path_file_car)
    check_file_exists(path_file_form_excel)

    # 2. Lấy sheet
    sheet_car = get_excel_sheets(path_file_car)
    sheet_form = get_excel_sheets(path_file_form_excel)
    mapping_sheets = map_sheets(sheet_car, sheet_form)
    if not mapping_sheets:
        raise ValueError("Không có sheet trùng giữa hai file.")

    # 3. Copy file form thành output
    path_output = copy_form_to_output(path_file_form_excel, path_folder_output)

    # 4. Khởi tạo log lỗi
    df_log = collect_error_log()

    # 5. Ghi dữ liệu vào từng sheet
    with pd.ExcelWriter(path_output, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
        for sheet_car_name, sheet_form_name in mapping_sheets:
            # a. Đọc thông tin car
            frame_data_car = read_car_info_from_sheet(path_file_car, sheet_car_name)
            frame_data_car_new = reformat_data_car(frame_data_car)

            # b. Đọc feature matrix từ car
            df_feature = read_feature_matrix_from_car(path_file_car, sheet_car_name)

            # c. Lấy spec code từ form
            ls_spec_codes = read_spec_code_from_sheet(path_file_form_excel, sheet_form_name)
            # Lấy vị trí dòng spec code trong form
            df_form = pd.read_excel(path_file_form_excel, sheet_name=sheet_form_name, header=None)
            form_code_rows = list(range(37, 37 + len(ls_spec_codes)))

            # d. Lấy spec code từ car (dòng feature matrix)
            car_code_col = 136
            car_code_rows = list(range(df_feature.shape[0]))
            ls_car_codes = df_feature[car_code_col].astype(str).map(str.strip).tolist()

            # e. Kiểm tra lỗi và ghi log
            # 1. Duplicate Spec Code in Form
            logs = log_duplicate_spec_code(df_form, sheet_form_name, spec_col=10, start_row=37)
            df_log = pd.concat([df_log, pd.DataFrame(logs)], ignore_index=True)

            # 2. Spec Code in Form Not in Car
            logs = log_spec_code_not_in_car(ls_spec_codes, ls_car_codes, sheet_form_name, form_code_rows, spec_col=10)
            df_log = pd.concat([df_log, pd.DataFrame(logs)], ignore_index=True)

            # 3. Spec Code in Car Not in Form
            logs = log_spec_code_not_in_form(ls_car_codes, ls_spec_codes, sheet_car_name, car_code_rows, spec_col=car_code_col)
            df_log = pd.concat([df_log, pd.DataFrame(logs)], ignore_index=True)

            # 4. Spec Code Format Error (Form)
            # Giả sử ls_spec_codes là list các spec code lấy từ form
            form_code_rows = list(range(37, 37 + len(ls_spec_codes)))
            logs = log_spec_code_format_error(ls_spec_codes, sheet_form_name, form_code_rows, spec_col=10)
            df_log = pd.concat([df_log, pd.DataFrame(logs)], ignore_index=True)

            # 5. Kiểm tra giá trị spec code không hợp lệ trong feature matrix
            logs = log_invalid_spec_code_value(
                                                df_feature, 
                                                sheet_car_name, 
                                                allowed_values=("", None, "*", "-", np.nan), 
                                                from_type="Car", 
                                                key_col=136
                                            )
            df_log = pd.concat([df_log, pd.DataFrame(logs)], ignore_index=True)

            # 6. Car Sheet Format Error
            errors = check_format_car_sheet(path_file_car, sheet_car_name)
            logs = log_car_sheet_format_error(errors, sheet_car_name)
            df_log = pd.concat([df_log, pd.DataFrame(logs)], ignore_index=True)

            # Ghi thông tin car vào form
            frame_data_car_new.to_excel(writer, sheet_name=sheet_form_name, index=None, header=None, startcol=12, startrow=13)

            # Ghi feature matrix vào form
            frame_data_new_output = extract_feature_matrix(
                df_feature, ls_spec_codes,
                key_col=136, car_columns=list(frame_data_car_new.columns),
                output_mark="*", output_not_mark=""
            )
            frame_data_new_output.to_excel(writer, sheet_name=sheet_form_name, index=None, header=None, startcol=12, startrow=37)

    # 6. Xuất log lỗi ra file Excel (nếu cần)
    file_log_path = os.path.join(path_folder_output, "File Log.xlsx")
    sheet_log_name = "Error_create_車両仕様表"
    export_log_with_color_to_sheet(df_log, file_log_path, sheet_log_name)


# Example usage:
if __name__ == "__main__":
    # Example default paths (for testing)
    path_folder_output = r"xqa_web\app\test_demo_step3\data"
    path_file_form_excel = r"xqa_web\app\test_demo_step3\form\車両仕様表サンプル.xlsx"
    fill_final_output(path_folder_output, path_file_form_excel)