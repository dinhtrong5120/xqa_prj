import pandas as pd
import unicodedata
import os
from .merge_row_cadics import merge_row_cadics
import warnings

warnings.filterwarnings("ignore")
from .check_zone import condition_zone_check
from .check_option import check_option
from .log_file_error import check_document
from xqa_web.app.logics.syo.db.funtion_database import update_new, get_header
from .read_data_view import frame_empty
from .check_option_new_v4 import check_option_new_v4
from .get_item_edit_1 import get_item
from xqa_web.app.logics.syo.db.function_database_new import querry_data_syo_hyo
from xqa_web.app.setting import BASE_DIR_DATAS, BASE_DIR_OUTPUTS, BASE_DIR_FORM_OUT


def create_cadics_new(case, market, powertrain, car, list_group):
    # working = os.path.dirname(__file__)
    folder_name = str(car).upper() + "_" + powertrain + "_" + market + "_" + case
    folder_data = os.path.join(BASE_DIR_DATAS, str(car).upper())
    folder_data = folder_data.replace("\\", "/")
    folder_out_check = os.path.join(BASE_DIR_OUTPUTS, folder_name)
    folder_out_check = folder_out_check.replace("\\", "/")

    if os.path.exists(folder_out_check) == False:
        os.mkdir(folder_out_check)

    file_spec, dic_group_karenhyo12, notice, group_pick = get_group_karenhyo12(folder_data, car, folder_out_check,
                                                                               list_group, market, case, powertrain)
    if notice == "Check market, case!":
        return "(Case, Power Train, Plant) does not exist in file 関連表① (Sheet パターン)", None, frame_empty(), None, None
    if len(dic_group_karenhyo12) == 0:
        return "Check input again!!!", None, frame_empty(), None, None
    # ===========================set link output=============================
    merge_end, unique_list_max, unique_list_submax = querry_data_syo_hyo(car)
    merge_end = merge_end.drop(columns=['group_key_map', 'default'])
    new_data = [merge_end.columns] + merge_end.values.tolist()  # Kết hợp tên cột với dữ liệu
    new_df = pd.DataFrame(new_data)
    new_df = new_df.replace('', None)
    # data_spec = pd.read_excel(file_spec, sheet_name="Sheet1", header=None)
    data_spec = new_df.copy()
    data_spec = data_spec.applymap(lambda x: normalize_japanese_text(x).lower() if isinstance(x, str) else x)
    # body_type = data_spec.iat[3, 4]
    # ========================Create File Output=============================
    adddress_config, frame_header, dict_grade, max_car, body_type = get_infor_car(data_spec)
    if str(body_type).lower().strip() not in ["sdn", "h/b", "suv", "minivan"]:
        return "Body_type not in [SDN, H/B, SUV, MiniVAN] !!!", None, frame_empty(), None, None
    my_dict_data = [{i: None for i in range(1, 180)}]
    dict_except_config = lot_except_config(data_spec)
    for group in dic_group_karenhyo12.keys():
        file_karenhyo_1 = dic_group_karenhyo12[group][0]
        file_karenhyo_2 = dic_group_karenhyo12[group][1]
        data_karenhyo1 = pd.read_excel(file_karenhyo_1, sheet_name="関連表", header=None)
        data_karenhyo1 = data_karenhyo1.map(lambda x: normalize_japanese_text(x).lower() if isinstance(x, str) else x)
        data_karenhyo1_list = data_karenhyo1.values
        max_column_karenhyo1 = len(data_karenhyo1.columns)

        data_karenhyo2 = pd.read_excel(file_karenhyo_2, sheet_name="関連表", header=None)
        data_karenhyo2 = data_karenhyo2.map(lambda x: normalize_japanese_text(x).lower() if isinstance(x, str) else x)
        dic_lot = get_lot(file_karenhyo_1, powertrain, market, case)  # contain
        flag_all, address_zone = condition_zone_check(data_karenhyo2, adddress_config)
        # common_option, dict_kep = check_option(data_karenhyo2, data_spec, max_car)
        list_infor = get_infor_fixed_group(data_karenhyo2)
        # ========================================================================
        for lot in dic_lot.keys():
            batan_no = dic_lot[lot]
            list_cadics = get_list_cadic(batan_no, data_karenhyo1, data_karenhyo1_list, max_column_karenhyo1)
            list_cadics_filter = filter_cadics(data_karenhyo2, list_cadics, address_zone, body_type)
            if len(list_cadics_filter) > 0:
                for cadics_no in list_cadics_filter:
                    list_dic_records = pick_car(data_karenhyo2, dict_except_config, cadics_no, adddress_config,
                                                group, lot, data_spec, list_infor, address_zone,
                                                dict_grade, max_car, flag_all)
                    my_dict_data = my_dict_data + list_dic_records

    frame_data = edit_dataframe(my_dict_data, frame_header, case, market, powertrain, car)
    # return frame_data
    # frame_data.to_csv("cadic_new.csv",index=None, header=None)
    # frame_data.to_excel(f"cadic_new_PARTxxx.xlsx", index=None, header=None)
    session, data, project_id, app_list = update_new(str(car).upper(), market, powertrain, case, frame_data, group_pick)
    return notice, session, data, project_id, app_list


def filter_cadics(data_karenhyo, list_cadic, address_zone, body):
    list_cadic_return = []
    col_address_zone = []
    dict_address_body = {"sdn": 11, "h/b": 12, "suv": 13, "minivan": 14, "frame": 15}
    address_body = dict_address_body[body]

    for key in address_zone.keys():
        for item in address_zone[key]:
            if item[0] not in col_address_zone:
                col_address_zone.append(item[0])

    for cadic_no in list_cadic:
        address = data_karenhyo.loc[data_karenhyo[0] == cadic_no]
        col_pick = address.columns[address.eq("〇").any() | address.eq("○").any()]
        col_all_picked = [x for x in col_pick]
        col_zone_picked = list(set(col_all_picked).intersection(set(col_address_zone)))

        if len(col_zone_picked) != 0 and address_body in col_all_picked:
            list_cadic_return.append(cadic_no)

    return list_cadic_return


"""fuction:lot_except_config(data_spec):
-Description: get dic_except_config
-Input:data_spec (struct:dataframe)
-Output:dic_except_config (struct: {"DS":["config1","config2"],"DC":[],.....})
"""


def lot_except_config(data_spec):
    dic_except_config = {}
    list_lot = ["DS", "DC", "PFC", "VC", "PT1", "PT2"]
    for lot in list_lot:
        list_except = []
        lot = lot.lower()
        text_lot = lot + "-lot"
        address = data_spec.loc[data_spec[3] == text_lot]
        if address.empty:
            None
        else:
            col_pick = address.columns[address.eq("〇").any() | address.eq("○").any()]
            for index in col_pick:
                list_except.append(data_spec[index][0])
        dic_except_config[lot.upper()] = list_except
    return dic_except_config


"""fuction:get_lot(file_karenhyo_1,powertrain,market,case):
-Description: get all lot
-Input:file_karenhyo_1,powertrain,market,case
-Output:list_lot(struct:{key=lot:value=batan_no},Eg:{"DS":1,"DC":2...})
"""


def get_lot(file_karenhyo_1, powertrain, market, case):
    address_pwt = {"EV": 0, "e-Power": 10, "ICE": 20}
    address_maket_case = {"JPN_CASE1": 2, "US_CASE1.5": 3, "US_CASE2": 4, "PRC_CASE1.5": 5, "PRC_CASE2": 6,
                          "EUR_CASE1.5": 7, "EUR_CASE2": 8}
    list_lot_all = ["DS", "DC", "PFC", "VC", "PT1", "PT2"]
    dic_lot = {}
    df = pd.read_excel(file_karenhyo_1, sheet_name="パターン", header=None)
    data_batan = df.values
    market_case_in = market + "_" + case
    col_pwt = address_pwt[powertrain]
    try:
        row_maket_case = address_maket_case[market_case_in]
    except:
        return {}
    col_lot_start = col_pwt + 3
    for lot in list_lot_all:
        batan_value = data_batan[row_maket_case][col_lot_start]
        if batan_value != "-" and isinstance(batan_value, (int, str)) == True:
            dic_lot[lot] = batan_value
        col_lot_start = col_lot_start + 1
    return dic_lot


# ============================================================================================
"""fuction:get_infor_fixed_group(data_karenhyo):
-Description: get inforation of file karenhyo2 
-Input:file_karenhyo_1,powertrain,market,case
-Output:list_infor (struct: [col_zone,row_option,row_item])
"""


def get_infor_fixed_group(data_karenhyo):
    max_col = len(data_karenhyo.columns)
    row_opt = data_karenhyo.iloc[1:2]
    row_item = data_karenhyo.iloc[2:3]
    row_class = data_karenhyo.iloc[3:4]
    col_zone_list = row_opt.columns[row_opt.eq("zone").any()]
    if len(col_zone_list):
        col_zone = col_zone_list[-1]
    else:
        col_zone = max_col
    return [col_zone, row_opt, row_item, row_class]


# =====================================================================================
"""fuction:get_list_cadic(batan_no,df,data_karenhyo,max_column_karenhyo):
-Description: get list_cadics 
-Input:batan_no,df,data_karenhyo,max_column_karenhyo
-Output:list_cadics(struct: ["MSTR-004-0000100","MSTR-004-0000200",...])
"""


def get_list_cadic(batan_no, df, data_karenhyo, max_column_karenhyo):
    column_batan = -1
    for index in range(11, max_column_karenhyo):
        if data_karenhyo[1][index] == batan_no:
            column_batan = index
            break

    if column_batan == -1:
        return []

    filtered_data = df.loc[
        df[0].notna() & df[0].apply(lambda x: isinstance(x, str)) & ((df[index] == "〇") | (df[index] == "○"))]
    cadic = filtered_data[0].tolist()
    return cadic


"""fuction:get_infor_car(df_spec):
-Description: get car's information 
-Input: df_spec
-Output: dic_col_config, frame_header, dict_grade,count,dict_optioncode
"""


def get_infor_car(df_spec):
    dict_grade = {}
    dict_optioncode = {}
    # working = os.path.dirname(__file__)
    # link_form_cadic = "./xqa_web/app/form_out/form_cadics.csv"
    link_form_cadic = os.path.join(BASE_DIR_FORM_OUT, 'form_cadics.csv')
    link_form_cadic = link_form_cadic.replace("\\", "/")
    frame_header = pd.read_csv(link_form_cadic, header=None)
    num_columns = len(frame_header.columns)
    column_names = [f'{i + 1}' for i in range(num_columns)]
    frame_header.columns = column_names
    dic_col_config = {}
    col_car_cadics = 130
    max_co = len(df_spec.columns)
    count = 0
    row_opcode = df_spec.loc[df_spec[3] == "optioncode"].index[0]

    row_grade = df_spec.loc[df_spec[3] == "grade"].index[0]
    row_zone = df_spec.loc[df_spec[3] == "zone"].index[0]
    row_engine = df_spec.loc[df_spec[3] == "engine"].index[0]
    row_axle = df_spec.loc[df_spec[3] == "axle"].index[0]
    row_handle = df_spec.loc[df_spec[3] == "handle"].index[0]
    row_trans = df_spec.loc[df_spec[3] == "trans"].index[0]
    row_body = df_spec.loc[df_spec[3] == "body"].index[0]
    body_type = df_spec[4][row_body]

    for index in range(4, max_co):
        config = df_spec[index][0]
        grade = df_spec[index][row_grade]
        zone = df_spec[index][row_zone]
        optioncode = df_spec[index][row_opcode]
        # ==============================================fix zone=============================================
        if zone == "usa":
            zone = "us"
        if zone == "canada":
            zone = "can"
        # ====================================================================================================
        # if config != None and isinstance(config, float) == False:
        if "conf" in str(config):
            count = count + 1
            if isinstance(optioncode, str):
                dict_optioncode[config] = optioncode
            else:
                dict_optioncode[config] = ""

            # ==================================lay cac cofig up_dow =============================================
            if zone not in dict_grade.keys():
                dic_col_config[zone] = {config: col_car_cadics}
                dict_grade[zone] = {config: grade}

            else:
                dict_grade[zone][config] = grade
                dic_col_config[zone][config] = col_car_cadics

            col_car_cadics = col_car_cadics + 1

    df_spec = df_spec.applymap(lambda x: x.upper() if isinstance(x, str) else x)
    frame_car = df_spec.iloc[[row_zone, row_engine, row_trans, row_axle, row_handle, 0], 4:(4 + count)]
    frame_car = frame_car.reset_index(drop=True)
    column_names = [f'{i}' for i in range(130, 130 + count)]
    frame_car.columns = column_names
    frame_header = pd.concat([frame_header, frame_car], axis=1)
    return dic_col_config, frame_header, dict_grade, count, body_type


"""fuction: pick_car(data_karenhyo,dict_except_config,cadic_no,adddress_config,group,lot,data_spec,infor_fix)
-Description: pick 1,*
"""


def pick_car(data_karenhyo, dict_except_config, cadic_no, adddress_config, group, lot, data_spec,
             infor_fix, address_zone, dict_grade, max_car, flag_all):
    col_zone, row_opt, row_item, row_class = infor_fix
    list_except_config = dict_except_config[lot]
    dic_address = {"DS": [55, 61, 67], "DC": [55, 68, 74], "PFC": [75, 81, 91], "VC": [92, 98, 107],
                   "PT1": [92, 108, 117], "PT2": [92, 118, 127]}
    col_group, col_evaluate, col_comment = dic_address[lot]
    list_dict = []
    dic_data = {}
    # find  cadic of location in column A
    address = data_karenhyo.loc[data_karenhyo[0] == cadic_no]
    # find column picked 〇
    col_pick = address.columns[address.eq("〇").any() | address.eq("○").any()]
    col_all_picked = [x for x in col_pick]
    col_opt_pick = [x for x in col_pick if (x > col_zone)]
    frame_option = data_karenhyo.loc[1:4, col_opt_pick]
    index_cadic = 0
    cadic_no_val = cadic_no.upper()
    string_comment = ''
    for zone in address_zone.keys():
        if len(address_zone[zone]) != 0:
            col_index_zone = [item[0] for item in address_zone[zone]]
            col_index_zone_picked = list(set(col_all_picked).intersection(set(col_index_zone)))
            if flag_all == True and len(address_zone[zone]) > 1:
                col_zone_all = col_index_zone[0]
                if col_zone_all in col_index_zone_picked:
                    col_index_zone_picked = [col_zone_all]
            for index in col_index_zone_picked:
                # ===========finde condition zone=========
                for item in address_zone[zone]:
                    if item[0] == index:
                        condition_zone = item[1]
                        break
                # =======================================================================================================
                adddress_config_zone, dict_grade_zone, dict_zone_conf_dk = get_config_zone(adddress_config, zone,
                                                                                           dict_grade,
                                                                                           list_except_config,
                                                                                           condition_zone)

                if len(col_opt_pick) == 0:
                    dic_data = case_no_option(condition_zone, cadic_no_val, adddress_config_zone, group,
                                              col_group, col_evaluate, col_comment, dict_grade_zone, list_except_config)
                    if len(dic_data) > 3:
                        list_dict.append(dic_data)
                        index_cadic = index_cadic + 1
                        cadic_no_val = cadic_no.upper() + "-d000" + str(index_cadic)
                else:
                    # ======================================================================================================
                    if cadic_no == "mstr-013-0140700" and lot == "VC":
                        None
                    dict_car, string_comment, dic_syo = check_option_new_v4(data_spec, frame_option, dict_zone_conf_dk,
                                                                            max_car)
                    pick_car_grade = grade_condition(dict_car, dict_grade_zone, zone)
                    dict_car_add_infor = get_item(data_spec, pick_car_grade, max_car)
                    list_dict_data, index_cadic = case_have_option(dict_car_add_infor, adddress_config_zone, group,
                                                                   col_group, col_evaluate, col_comment, cadic_no,
                                                                   index_cadic, lot)
                    list_dict = list_dict + list_dict_data
    # ================================================================================
    if len(list_dict) == 0:
        dic_data[2] = cadic_no.upper()
        dic_data[col_group] = group
        dic_data[col_evaluate] = "YES"
        dic_data[130 + max_car] = "要望仕様が存在しない"
        try:
            xxx = comment_nashi(col_opt_pick, row_opt, row_item, row_class, dic_syo)
            dic_data[131 + max_car] = xxx
        except:
            dic_data[131 + max_car] = ""  # + ', ' +comment_nashi(col_opt_pick, row_opt, row_item, row_class)
        return [dic_data]
    else:
        return list_dict


def grade_condition(dic_car, dict_grade_, zone):
    list_config_result = []
    for item in dic_car.keys():
        item_ = item.replace(zone, "")
        list_subitem = item_.split("_")
        condition = list_subitem[1]
        list_config_all = list_subitem[2:]
        list_config = []
        if condition == "最上級":
            value_max = max(dict_grade_.values(), key=lambda x: str(x))
            for config in list_config_all:
                if dict_grade_[config] == value_max:
                    list_config.append(config)

        if condition == "最下級":
            value_min = min(dict_grade_.values(), key=lambda x: str(x))
            for config in list_config_all:
                if dict_grade_[config] == value_min:
                    list_config.append(config)

        if condition == "不問":
            list_config = list_config_all

        if len(list_config) != 0:
            cmt = "グレード選択: " + condition
            # for sys in ["{","}","'",", グレード選択: 不問","[","]"]:
            #     cmt=cmt.replace(sys,"")
            list_config.append(dic_car[item])
            list_config.append(cmt)
            list_config_result.append(list_config)

    return list_config_result


def comment_nashi(col_opt_pick, row_opt, row_item, row_class, dic_opt_syo):
    dict_syo_ref = dic_opt_syo.copy()
    dic_opt = {}
    dict_karen = {}
    for index in col_opt_pick:
        opt = row_opt[index][1]
        opt = str(opt)
        opt = opt.strip()
        opt_item = row_item[index][2]
        opt_item = str(opt_item)
        opt_item = opt_item.strip()
        condition = row_class[index][3]
        if opt not in dict_karen.keys():
            dict_karen[opt] = []
        if opt_item == "all":
            dict_karen[opt] = ["all"]
        if opt_item == "w" or opt_item == "with":
            value = dict_syo_ref[opt]
            try:
                value.remove("w/o")
            except:
                None
            try:
                value.remove("-")
            except:
                None
            dict_karen[opt].extend(value)

    # print('dict_karen: ',dict_karen)
    # print('dic_opt_syo: ',dic_opt_syo)
    for opt in dic_opt_syo.keys():
        if len(dic_opt_syo[opt]) > 0 and dict_karen[opt] == ['all']:
            del dict_karen[opt]
        try:
            if len(dic_opt_syo[opt]) == 1 and all(item in dict_karen[opt] for item in dic_opt_syo[opt]) == True:
                del dict_karen[opt]
        except:
            None

    for index in col_opt_pick:
        opt = row_opt[index][1]
        opt = str(opt)
        opt = opt.strip()
        opt_item = row_item[index][2]
        opt_item = str(opt_item)
        opt_item = opt_item.strip()
        condition = row_class[index][3]
        if opt in dict_karen.keys():
            if isinstance(condition, str) == False:
                condition = "不問"
            condition = condition.strip()
            if opt not in dic_opt.keys():
                dic_opt[opt] = []
            if condition not in ["最下級", "最上級"]:
                condition = "不問"

            if condition != "不問":
                string_comment = "(" + opt_item + ", グレード選択:" + condition + ")"
            else:
                string_comment = opt_item

            dic_opt[opt].append(string_comment)

    string_comment = str(dic_opt)
    for sym in ["{", "}", "[", "]", "'"]:
        string_comment = string_comment.replace(sym, "")

    return string_comment.upper()


def get_config_zone(adddress_config, zone, dict_grade, list_except_config, condition_zone):
    dict_config = {}
    dict_grade_ = {}
    list_zone = zone.split("_")
    for item in list_zone:
        dict_config.update(adddress_config[item])
        dict_grade_.update(dict_grade[item])

    list_config_all = dict_config.keys()
    list_config_all = list(list_config_all)
    if len(list_except_config) == 0:
        list_config = list_config_all
    else:
        list_config = list(set(list_config_all).intersection(set(list_except_config)))

    dict_zone_conf_dk = {zone + "_" + condition_zone: list_config}
    return dict_config, dict_grade_, dict_zone_conf_dk


# def grade_conditon(dict_grade_):


def get_config_condition(condition_zone, dict_grade_):
    list_config = []
    if condition_zone == "最上級":
        value_max = max(dict_grade_.values(), key=lambda x: str(x))
        for config in dict_grade_.keys():
            if dict_grade_[config] == value_max:
                list_config.append(config)

    if condition_zone == "最下級":
        value_min = min(dict_grade_.values(), key=lambda x: str(x))
        for config in dict_grade_.keys():
            if dict_grade_[config] == value_min:
                list_config.append(config)

    if condition_zone == "不問":
        for config in dict_grade_.keys():
            list_config.append(config)

    return list_config


def case_no_option(condition, cadic_no_val, address_config_zone, group,
                   col_group, col_evaluate, col_comment, dict_grade_zone, list_except_config):
    dic_data = {}
    flag_ = 0
    flag_2 = 0
    list_config_all = get_config_condition(condition, dict_grade_zone)
    if len(list_except_config) == 0:
        list_config = list_config_all
    else:
        list_config = list(set(list_config_all).intersection(set(list_except_config)))

    list_config = sorted(list_config)
    for config in list_config:
        if flag_ == 0:
            dic_data[2] = cadic_no_val
            dic_data[col_group] = group
            dic_data[col_evaluate] = "YES"
            dic_data[address_config_zone[config]] = "1"
            if condition != "不問":
                dic_data[col_comment] = "グレード選択: " + condition
            flag_2 = 1
        if flag_ == 1:
            dic_data[address_config_zone[config]] = "*"
        if flag_2 == 1:
            flag_ = 1
    return dic_data


def case_have_option(list_all_config, address_config_zone,
                     group, col_group, col_evaluate,
                     col_comment, cadic_no, index_cadic, lot):
    list_dict = []
    for item in list_all_config:
        dic_data = {}
        list_config = item[:len(item) - 2]
        list_cmt = item[len(item) - 2:]
        cmt = str(list_cmt)
        for sys in ["{", "}", "'", ", グレード選択: 不問", "[", "]", 'グレード選択: 不問']:
            cmt = cmt.replace(sys, "")
        if index_cadic == 0:
            dic_data[2] = cadic_no.upper()
        else:
            dic_data[2] = cadic_no.upper() + "-d000" + str(index_cadic)
        index_cadic = index_cadic + 1
        dic_data[col_group] = group
        dic_data[col_evaluate] = "YES"
        flag = 0
        for config in list_config:
            if flag == 0:
                dic_data[address_config_zone[config]] = "1"
                flag = 1
            else:
                dic_data[address_config_zone[config]] = "*"
        dic_data[col_comment] = cmt
        list_dict.append(dic_data)
    return list_dict, index_cadic


"""write_excel(my_dic_data,file_name,frame_header):
-Description: get config suiable for required config
-Input: my_dic_data,file_name,frame_header
-Output: write data in file csv
"""


def edit_dataframe(my_dic_data, frame_header, develop_case, market, powertrain, project_name):
    frame = pd.DataFrame(my_dic_data)
    frame = frame.drop(0)
    num_columns = len(frame.columns)
    column_names = [f'{i + 1}' for i in range(num_columns)]
    frame.columns = column_names
    df_sorted = frame.sort_values(by="2")

    result = pd.concat([frame_header, df_sorted], axis=0)
    result = result.reset_index(drop=True)
    result = pd.DataFrame(result.values, columns=None)
    data_new = merge_row_cadics(result)
    # data_new.to_csv("data.csv")
    return data_new


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


def get_group_karenhyo12(folder_data, car, folder_out, list_group, market, case, powertrain):
    dic_group_karenhyo12 = {}
    group_pick = []
    file_name_spec = "仕様表_" + str(car).upper() + ".xlsx"
    link_file_spec = os.path.join(folder_data, file_name_spec)
    link_file_spec = link_file_spec.replace("\\", "/")
    if os.path.exists(folder_data) == False:
        return None, dic_group_karenhyo12, "Data is empty!", []

    notice = check_document(folder_data, link_file_spec, folder_out, market, case, list_group, powertrain)
    # notice=""
    if notice == 'Error':
        return None, dic_group_karenhyo12, "Check market, case!", []

    if os.path.exists(link_file_spec) == False:
        link_file_spec = None
    # =============================================================================================
    list_file = []
    karen_files = [f for f in os.listdir(folder_data) if f.endswith('.xlsx')]
    if "ALL" not in list_group:
        for item in list_group:
            list_filename_contain_group = [file_name for file_name in karen_files if item in file_name]
            list_file.extend(list_filename_contain_group)
    else:
        list_filename_contain_group = [file_name for file_name in karen_files]
        list_file.extend(list_filename_contain_group)
    # =============================================================================================
    for file_name in list_file:
        if file_name.find("関連表1") == 0:
            file_karenhyo2 = file_name.replace("関連表1", "関連表2")
            link_file_karenhyo2 = os.path.join(folder_data, file_karenhyo2)
            link_file_karenhyo2 = link_file_karenhyo2.replace('\\', '/')
            if os.path.exists(link_file_karenhyo2):
                link_file_karenhyo1 = os.path.join(folder_data, file_name)
                link_file_karenhyo1 = link_file_karenhyo1.replace('\\', '/')
                dic_group_karenhyo12[file_name] = [link_file_karenhyo1, link_file_karenhyo2]
                group_pick.append(file_name)
    group_pick = tuple(group_pick)
    return link_file_spec, dic_group_karenhyo12, notice, group_pick

# ================================TEST============================================================

# create_cadics_new(case="CASE1", market="JPN", powertrain="EV", car="WZ1J", list_group=["ALL"])
