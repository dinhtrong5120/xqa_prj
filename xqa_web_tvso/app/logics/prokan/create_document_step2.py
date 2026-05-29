import numpy as np
import pandas as pd
import os
import shutil
import unicodedata
import warnings
from io import BytesIO
from openpyxl import load_workbook

warnings.filterwarnings("ignore")
from xqa_web_tvso.app.logics.prokan.create_wtc_request_list import create_file_request_list
from xqa_web_tvso.app.logics.prokan.create_wtc_spec_app import create_wtc_spec_app
from xqa_web_tvso.app.logics.prokan.create_car_request import create_car_request
from xqa_web_tvso.app.logics.prokan.create_experiment_part import create_experiment_part
from xqa_web_tvso.app.logics.prokan.create_manage_part import create_manage_part
from xqa_web_tvso.app.logics.syo.db.funtion_database import query_data
from xqa_web_tvso.app.logics.prokan.read_data_view import zip_folder
from xqa_web_tvso.app.logics.syo.db.function_database_new import querry_data_syo_hyo
from xqa_web_tvso.app.setting import BASE_DIR_DATAS, BASE_DIR_OUTPUTS, BASE_DIR_FORM_OUT


# dic_test={ "XQ2":[1,"【サンプル】XXQ2関連表1_B(車体音振).xlsx","【サンプル】XXQ2関連表2_B(車体音振).xlsx","【サンプル】XXQ2関連表3_B(車体音振) .xlsx","【サンプル】XXQ2関連表4_B(車体音振) .xlsx",4,"【サンプル】仕様表_L21C.xlsx"],"XQ4":[1,"【サンプル】XXQ4関連表1_B(車体音振).xlsx","【サンプル】XXQ4関連表2_B(車体音振).xlsx","【サンプル】XXQ4関連表3_B(車体音振).xlsx","【サンプル】XXQ4関連表4_B(車体音振).xlsx",4,"【サンプル】仕様表_L21C.xlsx"]}

def create_doc(case, plant, powertrain, car):
    # ===========================load_infomation_input==========================
    folder_name = str(car).upper() + "_" + powertrain + "_" + plant + "_" + case
    folder_data = os.path.join(BASE_DIR_DATAS, str(car).upper())
    folder_data = folder_data.replace("\\", "/")
    folder_out = os.path.join(BASE_DIR_OUTPUTS, folder_name)
    folder_out = folder_out.replace("\\", "/")
    os.makedirs(folder_out, exist_ok=True)

    file_cadic = os.path.join(folder_out, "CADICS_ALL.csv")
    file_cadic = file_cadic.replace("\\", "/")
    data_return = query_data(str(car).upper(), plant, powertrain, case, "ALL", "ALL", is_cadics=True)
    # data_cadics_save = query_data(str(car).upper(), plant, powertrain, case, "ALL", "ALL", is_cadics=True)
    link_spec, dict_group_karenhyo3, dict_group_karenhyo4 = get_group_karenhyo34(folder_data, car)
    if data_return[0] == None:
        return "Data cadics not exist in database!"
    if len(dict_group_karenhyo3) == 0 and len(dict_group_karenhyo4) == 0:
        return "Lack of 関連表③, 関連表④"
    # ==========================Du lieu tong=====================================
    cadics_all = data_return[1]
    # cadics_all_save = data_cadics_save[1]
    buffer = BytesIO()
    cadics_all.to_csv(file_cadic, index=False, header=False, encoding='utf-8-sig')
    buffer.seek(0)
    cadics_all = cadics_all.map(lambda x: normalize_japanese_text(x) if isinstance(x, str) else x)
    my_dict_car_request = {"PFC": [], "VC": [], "PT1": [], "PT2": []}
    my_dict_request_list = {"PFC": [], "VC": []}
    my_dict_wtc_spec = {"PFC": {"t": [], "w": [], "c": []}, "VC": {"t": [], "w": [], "c": []}}
    my_dic_buhin = {"PFC": [], "VC": []}
    my_dic_buhin_list = {"PFC": [], "VC": []}
    # ==========================set link output==================================
    name_file_zip = folder_out + ".zip"
    # ===================process logic to write Output===========================
    merge_end, unique_list_max, unique_list_submax = querry_data_syo_hyo(car)
    merge_end = merge_end.drop(columns=['group_key_map', 'default'])
    new_data = [merge_end.columns] + merge_end.values.tolist()  # Kết hợp tên cột với dữ liệu
    new_df = pd.DataFrame(new_data)
    new_df = new_df.replace('', None)
    # data_spec = pd.read_excel(file_spec, sheet_name="Sheet1", header=None)
    data_spec = new_df.copy()
    # data_spec = pd.read_excel(link_spec, sheet_name="Sheet1",header=None)          # notice: sheet_name
    data_spec = data_spec.map(lambda x: normalize_japanese_text(x).lower() if isinstance(x, str) else x)
    frame_data_car, car_number, dict_config = get_car_infor(data_spec)
    # st.write(car_number)
    for group, link_kanrenhyo_3 in dict_group_karenhyo3.items():
        list_lot = get_lot_karen(link_kanrenhyo_3)
        for lot in list_lot:
            # ===================read input using pandas======================
            sheet_name = "関連表" + lot
            df = pd.read_excel(link_kanrenhyo_3, sheet_name=sheet_name, header=None)
            
            data_kanrenhyo_3 = df.map(lambda x: normalize_japanese_text(x) if isinstance(x, str) else x)
            data_cadics = filter_cadic3(lot, data_kanrenhyo_3, cadics_all, car_number)  # filter cadics base on lot group
            
            start_table3, end_table3 = find_table(data_kanrenhyo_3, powertrain)
            data_car_request = create_car_request(data_cadics, data_kanrenhyo_3, car_number, lot, start_table3, end_table3, group)
            
            my_dict_car_request[lot].extend(data_car_request)
            
            if lot in ["VC", "PFC"]:
                data_request_list, dict_type_block, list_config = create_file_request_list(data_cadics,
                                                                                           data_kanrenhyo_3, lot,
                                                                                           car_number, start_table3,
                                                                                           end_table3,group.lower())
                if len(data_request_list) > 0:
                    my_dict_request_list[lot].append(data_request_list)
                    data_wtc_spec_app_t, data_wtc_spec_app_w, data_wtc_spec_app_c = create_wtc_spec_app(data_cadics,
                                                                                                        lot,
                                                                                                        dict_type_block,
                                                                                                        list_config,
                                                                                                        dict_config)
                    my_dict_wtc_spec[lot]["t"] = my_dict_wtc_spec[lot]["t"] + data_wtc_spec_app_t
                    my_dict_wtc_spec[lot]["w"] = my_dict_wtc_spec[lot]["w"] + data_wtc_spec_app_w
                    my_dict_wtc_spec[lot]["c"] = my_dict_wtc_spec[lot]["c"] + data_wtc_spec_app_c

    for group, link_kanrenhyo_4 in dict_group_karenhyo4.items():
        list_lot = get_lot_karen(link_kanrenhyo_4)
        for lot in list_lot:
            # ===================read input using pandas======================
            sheet_name = "関連表" + lot
            df = pd.read_excel(link_kanrenhyo_4, sheet_name=sheet_name, header=None)
            data_kanrenhyo_4 = df.map(lambda x: normalize_japanese_text(x) if isinstance(x, str) else x)
            data_cadics = filter_cadic4(lot, data_kanrenhyo_4, cadics_all, car_number)  # filter cadics base on lot group
            
            if lot in ["VC", "PFC"]:
                list_dict_buhin = create_experiment_part(data_kanrenhyo_4, data_cadics, data_spec, lot)
                list_dict_buhin_list = create_manage_part(data_kanrenhyo_4, data_cadics, lot)
                my_dic_buhin[lot] = my_dic_buhin[lot] + list_dict_buhin
                my_dic_buhin_list[lot] = my_dic_buhin_list[lot] + list_dict_buhin_list
                
    write_excel(folder_out, my_dict_car_request, frame_data_car, my_dict_request_list, my_dict_wtc_spec, my_dic_buhin,
                my_dic_buhin_list)
    zip_folder(folder_out, name_file_zip)
    return "Completed!!!"


def rename_sheet(folder_out):
    for item in os.listdir(folder_out):
        if not item.startswith('Car'):
            continue
        item_path = os.path.join(folder_out, item)
        wb = load_workbook(item_path)
        sheet_names = wb.sheetnames
        
        for old_name in sheet_names:
            new_name = old_name + "_車両"
            wb[old_name].title = new_name
        
        wb.save(item_path)


def reformat_data_car(
    frame_data_car: pd.DataFrame,
    idx_zone: int = 0,
    idx_equip: int = 9,
    idx_appno: int = 10,
    idx_numbers: int = 11
) -> pd.DataFrame:
    """
    Tạo một DataFrame mới dựa trên quy tắc hoán đổi dòng từ DataFrame đầu vào.

    Quy tắc hoán đổi:
        - Dòng idx_zone mới (mặc định 0) sẽ lấy giá trị của dòng idx_equip cũ (mặc định 9)
        - Dòng idx_equip mới (mặc định 9) sẽ lấy giá trị của dòng idx_appno cũ (mặc định 10)
        - Dòng idx_appno mới (mặc định 10) sẽ lấy giá trị của dòng idx_numbers cũ (mặc định 11)
        - Các dòng còn lại giữ nguyên giá trị như DataFrame gốc
        - Sau khi hoán đổi, dòng cuối cùng (idx_numbers) sẽ bị xóa khỏi DataFrame trả về

    Tham số:
        frame_data_car (pd.DataFrame): DataFrame đầu vào, không có tên dòng, chỉ số dòng xác định ý nghĩa.
        idx_zone (int):      Chỉ số dòng sẽ nhận giá trị dòng idx_equip (Zone). Mặc định là 0.
        idx_equip (int):     Chỉ số dòng sẽ nhận giá trị dòng idx_appno (Equip). Mặc định là 9.
        idx_appno (int):     Chỉ số dòng sẽ nhận giá trị dòng idx_numbers (APP№). Mặc định là 10.
        idx_numbers (int):   Chỉ số dòng chứa dãy số cuối cùng (APP№ thực sự). Mặc định là 11.

    Trả về:
        pd.DataFrame: DataFrame mới đã được hoán đổi dòng và xóa dòng cuối cùng.

    Raises:
        ValueError: Nếu DataFrame không đủ số dòng để thực hiện hoán đổi.
    """
    n_rows = frame_data_car.shape[0]
    if n_rows <= idx_numbers:
        raise ValueError(f"DataFrame phải có ít nhất {idx_numbers+1} dòng, hiện tại chỉ có {n_rows} dòng.")

    arr = frame_data_car.values.copy()
    arr[idx_zone] = frame_data_car.iloc[idx_equip].values
    arr[idx_equip] = frame_data_car.iloc[idx_appno].values
    arr[idx_appno] = frame_data_car.iloc[idx_numbers].values

    data_car_new = pd.DataFrame(arr[:-1], columns=frame_data_car.columns)
    return data_car_new


def extract_feature_matrix(
    list_dict,
    ls_spec_codes,
    key_col: int = 136,
    src_start: int = 5,
    src_end: int = 134,
    output_mark: str = "*",
    output_not_mark: str = "-",
    empty_values = ("", None, "-", np.nan)
) -> pd.DataFrame:
    """
    Tạo DataFrame học từ danh sách dict đầu vào và danh sách spec_codes đầu vào.
    """
    # Đưa list_dict về DataFrame để lọc nhanh
    df = pd.DataFrame(list_dict)
    # Chỉ lấy các cột trong khoảng src_start tới src_end và key_col
    cols = [key_col] + list(range(src_start, src_end+1))
    df = df.loc[:, [c for c in cols if c in df.columns]]
    # Chuẩn hóa key_col về string, lower, strip để so sánh
    df[key_col] = df[key_col].astype(str).map(str.strip).str.lower()
    # Tìm max key thực tế
    data_keys = [c for c in df.columns if c != key_col]
    if data_keys:
        max_key = max(data_keys)
    else:
        max_key = src_start - 1  # Không có dữ liệu

    rows = []
    for spec_code in ls_spec_codes:
        row = [spec_code, ""]
        # Chuẩn hóa spec_code để so sánh
        code_std = str(spec_code).strip().lower()
        # Lọc các dòng có key_col == code_std
        df_code = df[df[key_col] == code_std]
        for i in range(src_start, max_key + 1):
            if not df_code.empty:
                vals = df_code[i] if i in df_code.columns else pd.Series([], dtype=object)
                # Check tất cả đều empty_values hoặc NaN
                is_empty = vals.isna() | vals.isin(empty_values)
                if is_empty.all():
                    row.append(output_not_mark)
                else:
                    row.append(output_mark)
            else:
                row.append(output_not_mark)
        rows.append(row)
    columns = [0, 1] + list(range(2, max_key - src_start + 3))
    df_out = pd.DataFrame(rows, columns=columns)
    return df_out


def get_spec_codes_from_excel(file_path, sheet_name, col=10, start_row=37):
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    # Lấy cột 10 (index 9), từ dòng 37 (index 36) trở đi
    spec_codes = df.iloc[start_row:, col]
    # Loại bỏ NaN, strip, giữ lại giá trị không rỗng
    spec_codes = spec_codes.dropna().astype(str).map(str.strip)
    spec_codes = spec_codes[spec_codes != ""].unique()
    return list(spec_codes)


def write_excel(folder_out, my_dict_car_request, frame_data_car, 
                my_dict_request_list, my_dict_wtc_spec, my_dic_buhin,
                my_dic_buhin_list):
    src_form = os.path.join(BASE_DIR_FORM_OUT, "Step2")
    src_form = src_form.replace("\\", "/")
    shutil.copytree(src_form, folder_out, dirs_exist_ok=True)
    link_file_car_request = folder_out + "/Car配車要望表.xlsx"
    link_file_request_list = folder_out + "/WTC要望集約兼チェックリスト.xlsx"
    link_file_wtc_spec = folder_out + "/WTC仕様用途一覧表.xlsx"
    link_buhin = folder_out + "/実験部品.xlsx"
    link_buhin_list = folder_out + "/特性管理部品リスト.xlsx"
    form_car_request = [{i: None for i in range(0, 162)}]

    dict_address = {'関連表1_b(操安台上)_xq2.xlsx': 6, '関連表1_b(車体音振_車両音振)_xq4x.xlsx': 7,
                    '関連表1_a(内外装耐環境)_xr2.xlsx': 8,
                    '関連表1_a(コントロール)_xr2.xlsx': 11, '関連表1_l(車体信頼性)_xr2_.xlsx': 14,
                    '関連表1_z(シャシー)_xr2.xlsx': 16,
                    '関連表1_m(衝突)_xtf.xlsx': 17, '関連表1_a(シート)_xr3.xlsx': 21, '関連表1_(シート)_xl4.xlsx': 22,
                    '関連表1_m(シートベルト)_xr6.xlsx': 24, '関連表1_m(乗員判別)_xr6.xlsx': 27,
                    '関連表1_i(gaオーディオ音質)_xm6.xlsx': 28,
                    '関連表1_i(gaオーディオアンテナ)_xm6.xlsx': 29, '関連表1_k(電池システムx)_xp6.xlsx': 32}
    
    with pd.ExcelWriter(link_file_car_request, engine='openpyxl', mode="a", if_sheet_exists="overlay") as writer:
        for lot in my_dict_car_request.keys():
            data_update = {
                '145': [
                    'CANハーネス',
                    'w、w/o、(空白:どちらでも可)'
                ]
            }
            df_update = pd.DataFrame(data_update)
            
            if len(my_dict_car_request[lot]) > 0:
                list_dict = form_car_request + my_dict_car_request[lot]
                frame_data = pd.DataFrame(list_dict)
                frame_data = frame_data.drop(0)
                frame_data_car.to_excel(writer, sheet_name=lot, index=None, header=None, startcol=5, startrow=5)
                frame_data.to_excel(writer, sheet_name=lot, index=None, header=None, startcol=0, startrow=19)
                
                df_update.to_excel(
                    writer,
                    sheet_name=lot,
                    startrow=17,
                    startcol=145,
                    header=False,
                    index=False
                )
    
    with pd.ExcelWriter(link_file_request_list, engine='openpyxl', mode="a", if_sheet_exists="overlay") as writer:
        for lot in my_dict_request_list.keys():
            end_row = 34
            for item in my_dict_request_list[lot]:
                KCA_id = str(item[0])
                file_name = KCA_id[:KCA_id.find(".xlsx") + 5]
                try:
                    row = dict_address[item[10]]
                except:
                    row = end_row
                    end_row = end_row + 1
                del item[10]
                frame_data = pd.DataFrame([item])
                frame_data.to_excel(writer, sheet_name=lot, index=None, header=None, startcol=3, startrow=row)
    form_wtc_spec = [{i: None for i in range(0, 89)}]

    with pd.ExcelWriter(link_file_wtc_spec, engine='openpyxl', mode="a", if_sheet_exists="overlay") as writer:
        for lot in my_dict_wtc_spec.keys():
            if len(my_dict_wtc_spec[lot]["t"]) > 0:
                list_dict_t = form_wtc_spec + my_dict_wtc_spec[lot]["t"]
                frame_t = pd.DataFrame(list_dict_t)
                frame_t = frame_t.drop(0)
                frame_t.to_excel(writer, sheet_name=lot, index=None, header=None, startcol=6, startrow=46)
            if len(my_dict_wtc_spec[lot]["w"]) > 0:
                list_dict_w = form_wtc_spec + my_dict_wtc_spec[lot]["w"]
                frame_w = pd.DataFrame(list_dict_w)
                frame_w = frame_w.drop(0)
                frame_w.to_excel(writer, sheet_name=lot, index=None, header=None, startcol=6, startrow=121)
            if len(my_dict_wtc_spec[lot]["c"]) > 0:
                list_dict_c = form_wtc_spec + my_dict_wtc_spec[lot]["c"]
                frame_c = pd.DataFrame(list_dict_c)
                frame_c = frame_c.drop(0)
                frame_c.to_excel(writer, sheet_name=lot, index=None, header=None, startcol=6, startrow=196)
    form_buhin = [{i: None for i in range(0, 22)}]

    with pd.ExcelWriter(link_buhin, engine='openpyxl', mode="a", if_sheet_exists="overlay") as writer:
        for lot in my_dic_buhin.keys():
            if len(my_dic_buhin[lot]) > 0:
                list_dict = form_buhin + my_dic_buhin[lot]
                frame_data = pd.DataFrame(list_dict)
                frame_data = frame_data.drop(0)
                frame_data.to_excel(writer, sheet_name=lot, index=None, header=None, startcol=2, startrow=7)
    
    with pd.ExcelWriter(link_buhin_list, engine='openpyxl', mode="a", if_sheet_exists="overlay") as writer:
        for lot in my_dic_buhin_list.keys():
            if len(my_dic_buhin_list[lot]) > 0:
                frame_data = pd.DataFrame(my_dic_buhin_list[lot])
                frame_data.to_excel(writer, sheet_name=lot, index=None, header=None, startcol=2, startrow=30)
    
    rename_sheet(folder_out)

def find_table(frame_karen3, powertrain):
    powertrains = ["ICE", "e-POWER", "EV"]
    res_dict = {}
    
    for p in powertrains:
        row = frame_karen3.iloc[0]
        cols = row[row == p].index.tolist()
        cols[0] += 1
        res_dict[p] = cols
    
    res_dict["ICE"].append(res_dict["e-POWER"][0] - 2)
    res_dict["e-POWER"].append(res_dict["EV"][0] - 2)
    res_dict["EV"].append(len(frame_karen3.columns))
    
    return res_dict[powertrain]


def get_lot_karen(link_kanrenhyo):
    excel_file = pd.ExcelFile(link_kanrenhyo)
    sheet_name3 = excel_file.sheet_names
    list_check = ['関連表PFC', '関連表VC', '関連表PT1', '関連表PT2']
    list_sheet = list(set(sheet_name3).intersection(set(list_check)))
    list_lot = []
    for item in list_sheet:
        lot = item[3:]
        list_lot.append(lot)
    return list_lot


def get_car_infor(data_spect):
    list_dict_car_infor = []
    count_car = 0
    dict_config = {}
    row_grade = data_spect.loc[data_spect[3] == "grade"].index[0]
    row_zone = data_spect.loc[data_spect[3] == "zone"].index[0]
    row_engine = data_spect.loc[data_spect[3] == "engine"].index[0]
    row_axle = data_spect.loc[data_spect[3] == "axle"].index[0]
    row_handle = data_spect.loc[data_spect[3] == "handle"].index[0]
    row_trans = data_spect.loc[data_spect[3] == "trans"].index[0]
    row_body = data_spect.loc[data_spect[3] == "body"].index[0]
    row_year = data_spect.loc[data_spect[3] == "year"].index[0]
    row_intake = data_spect.loc[data_spect[3] == "intake"].index[0]
    row_seat = data_spect.loc[data_spect[3] == "seat"].index[0]
    row_number = data_spect.loc[data_spect[3] == "number"].index[0]
    for index in range(4, len(data_spect.columns)):
        dict = {}
        config = data_spect[index][0]
        if "conf" in str(config):
            dict_config[config] = {}
            count_car = count_car + 1
            dict[0] = ""
            dict_config[config]["body"] = dict[1] = str(data_spect[index][row_body]).upper()  # body
            dict_config[config]["engine"] = dict[2] = str(data_spect[index][row_engine]).upper()  # engin
            dict_config[config]["axle"] = dict[3] = str(data_spect[index][row_axle]).upper()  # axle
            dict_config[config]["handle"] = dict[4] = str(data_spect[index][row_handle]).upper()  # handle
            dict[5] = str(data_spect[index][row_grade]).upper()  # grade
            dict_config[config]["trans"] = dict[6] = str(data_spect[index][row_trans]).upper()  # trans
            dict[7] = str(data_spect[index][row_year]).upper()  # year
            dict[8] = str(data_spect[index][row_intake]).upper()  # intake
            dict_config[config]["zone"] = dict[9] = str(data_spect[index][row_zone]).upper()  # zone
            dict[10] = str(data_spect[index][row_seat]).upper()  # equip==seat
            dict[11] = str(data_spect[index][row_number]).upper()  # App No== Number

            list_dict_car_infor.append(dict)
    frame = pd.DataFrame(list_dict_car_infor).T
    return frame, count_car, dict_config


def normalize_japanese_text(input_text):
    normalized_text = ''
    if isinstance(input_text, str):
        for char in input_text:
            normalized_char = unicodedata.normalize('NFKC', char)
            normalized_text += normalized_char
        # normalized_text = normalized_text.replace("\n", "")
        normalized_text = normalized_text.strip()
        return normalized_text
    else:
        return input_text


def filter_cadic3(lot, data_kanrenhyo_3, df, car_number):
    dic_address = {"DS": 67, "DC": 74, "PFC": 87, "VC": 104, "PT1": 114, "PT2": 124}

    col_evaluate = dic_address[lot]
    df.columns = range(len(df.columns))
    head = df.iloc[0:6]
    try:
        data_ = df.loc[(df[col_evaluate] == "YES") & (df[129 + car_number] != "要望仕様が存在しない")]
    except:
        data_ = df.loc[df[col_evaluate] == "YES"]
        
    list_cadic = data_kanrenhyo_3.iloc[30:, 0].tolist()
    mask = data_.iloc[:, 1].apply(lambda x: str(x) in list_cadic)
    filtered_df = data_[mask]
    
    result = pd.concat([head, filtered_df], axis=0)
    result = result.reset_index(drop=True)

    return result


def filter_cadic4(lot, data_framekaren, df, car_number):
    dic_address = {"DS": [54, 60], "DC": [54, 67], "PFC": [74, 80], "VC": [91, 97], "PT1": [91, 107], "PT2": [91, 117]}
    # dic_address = {
    #         "DS": [61, 67],
    #         "DC": [61, 74],
    #         "PFC": [81, 87],
    #         "VC": [98, 104],
    #         "PT1": [98, 114],
    #         "PT2": [98, 124]
    #     }
    col_evaluate = dic_address[lot][1]
    df.columns = range(len(df.columns))
    head = df.iloc[0:6]
    try:
        data_ = df.loc[(df[col_evaluate] == "YES") & (df[129 + car_number] != "要望仕様が存在しない")]
    except:
        data_ = df.loc[df[col_evaluate] == "YES"]

    list_cadic=data_framekaren.iloc[19:,0].tolist()
    tmp_list_cadic = [str(x).lower() for x in list_cadic]
    mask = data_.iloc[:, 1].apply(lambda x: any(val in str(x).lower() for val in tmp_list_cadic))
    filtered_df = data_[mask]
    result = pd.concat([head, filtered_df], axis=0)
    result = result.reset_index(drop=True)

    return result

def get_lot(link_kanrenhyo_3, link_kanrenhyo_4):
    excel_file = pd.ExcelFile(link_kanrenhyo_3)
    sheet_name3 = excel_file.sheet_names
    excel_file = pd.ExcelFile(link_kanrenhyo_4)
    sheet_name4 = excel_file.sheet_names
    list_inter = list(set(sheet_name3).intersection(set(sheet_name4)))
    list_check = ['関連表PFC', '関連表VC', '関連表PT1', '関連表PT2']
    list_sheet = list(set(list_inter).intersection(set(list_check)))
    list_lot = []
    for item in list_sheet:
        lot = item[3:]
        list_lot.append(lot)
    return list_lot


def get_group_karenhyo34(folder_data, car):
    dic_group_karenhyo3 = {}
    dic_group_karenhyo4 = {}
    if os.path.exists(folder_data) == False:
        return None, dic_group_karenhyo3, dic_group_karenhyo4
    files = [f for f in os.listdir(folder_data) if os.path.isfile(os.path.join(folder_data, f))]
    file_name_spec = "仕様表_" + str(car).upper() + ".xlsx"
    link_file_spec = os.path.join(folder_data, file_name_spec)
    link_file_spec = link_file_spec.replace("\\", "/")
    if os.path.exists(link_file_spec) == False:
        link_file_spec = None

    for file_name in files:
        if file_name.find("関連表3") == 0:
            group = file_name.replace("関連表3", "関連表1")
            link_file_karenhyo = os.path.join(folder_data, file_name)
            link_file_karenhyo = link_file_karenhyo.replace('\\', '/')
            dic_group_karenhyo3[group] = link_file_karenhyo

        if file_name.find("関連表4") == 0:
            group = file_name.replace("関連表4", "関連表1")
            link_file_karenhyo = os.path.join(folder_data, file_name)
            link_file_karenhyo = link_file_karenhyo.replace('\\', '/')
            dic_group_karenhyo4[group] = link_file_karenhyo
    dic_group_karenhyo3 = dict(sorted(dic_group_karenhyo3.items()))
    dic_group_karenhyo4 = dict(sorted(dic_group_karenhyo4.items()))

    return link_file_spec, dic_group_karenhyo3, dic_group_karenhyo4
# ====================================TEST========================================


# a=create_doc("CASE1.5","US","EV","WZ1J")
