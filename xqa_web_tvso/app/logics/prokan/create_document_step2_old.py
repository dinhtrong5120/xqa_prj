import pandas as pd
import os
import shutil
import unicodedata
import warnings
from io import BytesIO

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
    file_cadic = os.path.join(folder_out, "CADICS_ALL.csv")
    file_cadic = file_cadic.replace("\\", "/")
    data_return = query_data(str(car).upper(), plant, powertrain, case, "ALL", "ALL")
    link_spec, dict_group_karenhyo3, dict_group_karenhyo4 = get_group_karenhyo34(folder_data, car)
    if data_return[0] == None:
        return "Data cadics not exist in database!"
    if len(dict_group_karenhyo3) == 0 and len(dict_group_karenhyo4) == 0:
        return "Lack of 関連表③, 関連表④"
    # ==========================Du lieu tong=====================================
    cadics_all = data_return[1]

    #cadics_all.to_csv(file_cadic, index=None, header=None)
    buffer = BytesIO()
    cadics_all.to_csv(file_cadic, index=False, header=False, encoding='utf-8-sig')
    buffer.seek(0)
    cadics_all = cadics_all.map(lambda x: normalize_japanese_text(x).lower() if isinstance(x, str) else x)
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
            data_cadics = filter_cadic(lot, group, cadics_all, car_number)  # filter cadics base on lot group
            sheet_name = "関連表" + lot
            df = pd.read_excel(link_kanrenhyo_3, sheet_name=sheet_name, header=None)
            data_kanrenhyo_3 = df.map(lambda x: normalize_japanese_text(x).lower() if isinstance(x, str) else x)
            start_table3, end_table3 = find_table(data_kanrenhyo_3, powertrain)
            data_car_request = create_car_request(data_cadics, data_kanrenhyo_3, car_number, lot, start_table3,
                                                  end_table3)
            my_dict_car_request[lot].extend(data_car_request)
            if lot in ["VC", "PFC"]:
                data_request_list, dict_type_block, list_config = create_file_request_list(data_cadics,
                                                                                           data_kanrenhyo_3, lot,
                                                                                           car_number, start_table3,
                                                                                           end_table3)
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
            data_cadics = filter_cadic(lot, group, cadics_all, car_number)  # filter cadics base on lot group
            sheet_name = "関連表" + lot
            df = pd.read_excel(link_kanrenhyo_4, sheet_name=sheet_name, header=None)
            data_kanrenhyo_4 = df.applymap(lambda x: normalize_japanese_text(x).lower() if isinstance(x, str) else x)
            if lot in ["VC", "PFC"]:
                list_dict_buhin = create_experiment_part(data_kanrenhyo_4, data_cadics, data_spec, lot)
                list_dict_buhin_list = create_manage_part(data_kanrenhyo_4, data_cadics, lot)
                my_dic_buhin[lot] = my_dic_buhin[lot] + list_dict_buhin
                my_dic_buhin_list[lot] = my_dic_buhin_list[lot] + list_dict_buhin_list
    write_excel(folder_out, my_dict_car_request, frame_data_car, my_dict_request_list, my_dict_wtc_spec, my_dic_buhin,
                my_dic_buhin_list)
    zip_folder(folder_out, name_file_zip)
    return "Completed!!!"


def write_excel(folder_out, my_dict_car_request, frame_data_car, my_dict_request_list, my_dict_wtc_spec, my_dic_buhin,
                my_dic_buhin_list):
    # working = os.path.dirname(__file__)
    src_form = os.path.join(BASE_DIR_FORM_OUT, "Step2")
    src_form = src_form.replace("\\", "/")
    shutil.copytree(src_form, folder_out, dirs_exist_ok=True)
    link_file_car_request = folder_out + "/Car配車要望表.xlsx"
    link_file_request_list = folder_out + "/WTC要望集約兼チェックリスト.xlsx"
    link_file_wtc_spec = folder_out + "/WTC仕様用途一覧表.xlsx"
    link_buhin = folder_out + "/実験部品.xlsx"
    link_buhin_list = folder_out + "/特性管理部品リスト.xlsx"
    form_car_request = [{i: None for i in range(0, 161)}]
    with pd.ExcelWriter(link_file_car_request, engine='openpyxl', mode="a", if_sheet_exists="overlay") as writer:
        for lot in my_dict_car_request.keys():
            if len(my_dict_car_request[lot]) > 0:
                list_dict = form_car_request + my_dict_car_request[lot]
                frame_data = pd.DataFrame(list_dict)
                frame_data = frame_data.drop(0)
                frame_data_car.to_excel(writer, sheet_name=lot, index=None, header=None, startcol=5, startrow=5)
                frame_data.to_excel(writer, sheet_name=lot, index=None, header=None, startcol=0, startrow=19)
    dict_address = {'関連表1_b(操安台上)_xq2.xlsx': 6, '関連表1_b(車体音振_車両音振)_xq4x.xlsx': 7,
                    '関連表1_a(内外装耐環境)_xr2.xlsx': 8,
                    '関連表1_a(コントロール)_xr2.xlsx': 11, '関連表1_l(車体信頼性)_xr2_.xlsx': 14,
                    '関連表1_z(シャシー)_xr2.xlsx': 16,
                    '関連表1_m(衝突)_xtf.xlsx': 17, '関連表1_a(シート)_xr3.xlsx': 21, '関連表1_(シート)_xl4.xlsx': 22,
                    '関連表1_m(シートベルト)_xr6.xlsx': 24, '関連表1_m(乗員判別)_xr6.xlsx': 27,
                    '関連表1_i(gaオーディオ音質)_xm6.xlsx': 28,
                    '関連表1_i(gaオーディオアンテナ)_xm6.xlsx': 29, '関連表1_k(電池システムx)_xp6.xlsx': 32}
    with pd.ExcelWriter(link_file_request_list, engine='openpyxl', mode="a", if_sheet_exists="overlay") as writer:
        for lot in my_dict_request_list.keys():
            end_row = 34
            for item in my_dict_request_list[lot]:
                KCA_id = str(item[0])
                file_name = KCA_id[:KCA_id.find(".xlsx") + 5]
                try:
                    row = dict_address[file_name]
                except:
                    row = end_row
                    end_row = end_row + 1
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


def find_table(frame_karen3, powertrain):
    max_col = len(frame_karen3.columns)
    address = frame_karen3.loc[1:1, :]
    col_start = address.columns[address.eq("実験識別").any()]
    if len(col_start) == 0:
        return 0, 0
    if len(col_start) == 1:
        return col_start[0] + 1, max_col
    else:
        for index in range(len(col_start)):
            powertrain_check = str(frame_karen3.iat[0, col_start[index]]).lower()
            if powertrain_check.find(powertrain.lower()) != -1 and index < len(col_start) - 1:
                return col_start[index] + 1, col_start[index + 1] - 1
            if powertrain_check.find(powertrain.lower()) != -1 and index == len(col_start) - 1:
                return col_start[index] + 1, max_col
        return col_start[0] + 1, col_start[1] - 1


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
        normalized_text = normalized_text.replace("\n", "")
        normalized_text = normalized_text.strip()
        return normalized_text
    else:
        return input_text


def filter_cadic(lot, group, df, car_number):
    dic_address = {"DS": [54, 60], "DC": [54, 67], "PFC": [74, 80], "VC": [91, 97], "PT1": [91, 107], "PT2": [91, 117]}
    # dic_address = {
    #         "DS": [61, 67],
    #         "DC": [61, 74],
    #         "PFC": [81, 87],
    #         "VC": [98, 104],
    #         "PT1": [98, 114],
    #         "PT2": [98, 124]
    #     }
    
    col_group = dic_address[lot][0]
    col_evaluate = dic_address[lot][1]
    df.columns = range(len(df.columns))
    group = normalize_japanese_text(group).lower()
    head = df.iloc[0:6]
    try:
        data_ = df.loc[
            (df[col_evaluate] == "yes") & (df[col_group] == group) & (df[129 + car_number] != "要望仕様が存在しない")]
    except:
        data_ = df.loc[(df[col_evaluate] == "yes") & (df[col_group] == group)]
    result = pd.concat([head, data_], axis=0)
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
