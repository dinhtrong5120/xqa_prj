import pandas as pd
import unicodedata
import copy


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


def replace_standard(dict_need_to_replace):
    list_same_mean = [['w/o', 'without', '-'], ['w', 'with'], ['other', 'その他'], ['awd', '4wd'], ['fwd', '2wd']]
    new_dict_replaced = dict_need_to_replace.copy()

    for key, value_list in dict_need_to_replace.items():
        for i in range(len(value_list)):
            for sublist in list_same_mean:
                if value_list[i] in sublist:
                    new_dict_replaced[key][i] = sublist[0]
                    break
    return new_dict_replaced


def common_elements(dict_syo, dict_kanren):
    common_dict = {}
    for key, values2 in dict_kanren.items():
        if 'all' in values2 or 'All' in values2:
            common_values = dict_syo[key]
        else:
            list_item_in_karen = dict_syo[key].copy()
            list_item_in_syo = values2.copy()

            if "w" in list_item_in_syo:
                list_item_in_karen = [value for value in list_item_in_karen if value != "w/o"]
                list_item_in_syo.remove("w")
                list_item_in_syo.extend(list_item_in_karen)

            common_values = list(set(dict_syo[key]) & set(list_item_in_syo))

        common_dict[key] = common_values

    return common_dict


def create_dict_from_syo(list_option_from_karenhyo2, data_spec_, number_car):
    data_spec_.iloc[:, 3] = data_spec_.iloc[:, 3].str.strip()
    dict_syo = {}
    for option in list_option_from_karenhyo2:
        list_rows_found_option = data_spec_.index[data_spec_[3] == option]
        List_value = []
        if not list_rows_found_option.empty:
            List_value.append(data_spec_.iloc[list_rows_found_option[0], 4])
            for i in range(1, number_car):
                x = data_spec_.iloc[list_rows_found_option[0], 4 + i]
                if x not in List_value:
                    List_value.append(x)
            dict_syo[option] = List_value
        else:
            dict_syo[option] = []
    return dict_syo


def check_option_new_v4(data_spec, df_input, dict_input, number_car):
    data_spec = data_spec.map(lambda x: normalize_japanese_text(x).lower() if isinstance(x, str) else x)
    df_input = df_input.map(lambda x: normalize_japanese_text(x).lower() if isinstance(x, str) else x)
    df_input.iloc[2] = df_input.iloc[2].fillna('不問')
    df_input.iloc[2] = df_input.iloc[2].replace(to_replace=['ー', '-'], value='不問', regex=True)
    # return df_input
    list_option_from_karen2 = list(df_input.iloc[0, :].drop_duplicates().dropna())
    dict_from_syo = create_dict_from_syo(list_option_from_karen2, data_spec, number_car)
    
    zone = list(dict_input.keys())[0]
    for item in ['_最上級', '_不問', '_最下級']:
        zone = zone.replace(item, '')
    # return zone
    condition_base = list(dict_input.keys())[0].split('_')[-1]
    result_dict_up = {}
    result_dict_down = {}
    dict_items_from_filtered_df_up = {}
    dict_items_from_filtered_df_down = {}
    if condition_base in ['最上級', '不問']:
        filtered_df_up = df_input.loc[:, df_input.iloc[2].isin(['最上級', '不問'])]
        list_option_from_filtered_df_up = list(filtered_df_up.iloc[0, :])  # ['axle', 'axle', 'サンルーフ', 'サンルーフ']
        list_condition = filtered_df_up.iloc[2, :].tolist() # ['不問', '不問', '不問', '不問']
        list_condition.append(str(condition_base)) # ['不問', '不問', '不問', '不問', '不問']
        if '最上級' in list_condition:
            condition = '最上級'
        else:
            condition = '不問'
        if len(set(list_option_from_filtered_df_up)) < len(list_option_from_karen2):
            # Nếu các option sau khi lọc up mà nhỏ hơn số options ban đầu thì loại.
            result_dict_up = {}
        else:
            list_items_up = filtered_df_up.iloc[1, :].tolist()  # ['2wd', '4wd', 'w', 'w/o']
            dict_items_from_filtered_df_up = {}

            for key_sub, value in zip(list_option_from_filtered_df_up, list_items_up):
                if key_sub not in dict_items_from_filtered_df_up:
                    dict_items_from_filtered_df_up[key_sub] = []

                if pd.notna(value) and value not in dict_items_from_filtered_df_up[key_sub]:
                    dict_items_from_filtered_df_up[key_sub].append(value)
            # dict_items_from_filtered_df_up = {'axle': ['2wd', '4wd'], 'サンルーフ': ['w', 'w/o']}

            # Lọc file spec chỉ còn các options cần quan tâm.
            filtered_df_spec_in_case_up = data_spec[data_spec.iloc[:, 3].isin(list_option_from_filtered_df_up)]
            # Đặt tên cột cho df
            filtered_df_spec_in_case_up.columns = data_spec.iloc[0]
            # result_dict_up = {}
            # Duyệt qua từng values ví dụ ['conf-001', 'conf-002', 'conf-003']
            for list_name_conf in dict_input.values():
                # Duyệt qua từng cột trong đó: ví dụ 'conf-001':
                for column in list_name_conf:
                    sub_dict = dict(zip(filtered_df_spec_in_case_up['cadics id'],
                                        filtered_df_spec_in_case_up[column].apply(lambda x: [x])))
                    # sub_dict = {'axle': ['awd'], 'サンルーフ': ['w/o']}
                    if len(sub_dict) != len(dict_items_from_filtered_df_up):
                        sub_dict = {}
                        dict_items_from_filtered_df_up = {}
                    sub_dict_replace_standard = copy.deepcopy(sub_dict)
                    sub_dict_replace_standard = replace_standard(
                        sub_dict_replace_standard)  # {'axle': ['awd'], 'サンルーフ': ['w/o']}
                    dict_items_from_filtered_df_up_replace_standard = replace_standard(
                        dict_items_from_filtered_df_up)  # {'axle': ['fwd', 'awd'], 'サンルーフ': ['w', 'w/o']}
                    common_dict = common_elements(sub_dict_replace_standard, dict_items_from_filtered_df_up_replace_standard)
                    flag_check_dict_up = False
                    if common_dict == sub_dict_replace_standard:
                        flag_check_dict_up = True

                    for key_sub in result_dict_up.keys():
                        # Tìm vị trí chữ 'c' cuối cùng trong key
                        last_c_index = key_sub.rfind('c')
                        # Chỉ lấy cột cuối ví dụ chuỗi 'US_最上級_conf-001_conf-002' thì lấy 'conf-002'
                        last_column_in_pair = key_sub[last_c_index:]
                        # Nếu cột giống nhau và nằm trong cùng zone key thì thêm vào key
                        if (filtered_df_spec_in_case_up[column] == filtered_df_spec_in_case_up[
                            last_column_in_pair]).all() and last_column_in_pair in list_name_conf and condition in key_sub and column not in key_sub:
                            # Nối các conf nếu chúng có các option giống hệt nhau
                            key_merge = key_sub + "_" + column
                            # Sau khi nối xong thì thay key cũ bằng key mới.
                            result_dict_up[key_merge] = result_dict_up.pop(key_sub)
                            flag_check_dict_up = False
                            break
                    if flag_check_dict_up:
                        result_dict_up[zone + "_" +condition + "_" + column] = sub_dict
    if condition_base in ['最下級', '不問']:
        # Lấy những option trong karen sau đó xóa trùng lặp
        filtered_df_down = df_input.loc[:, df_input.iloc[2].isin(['最下級', '不問'])]
        # list_option_from_filtered_df_down = list(filtered_df_down.iloc[0, :].drop_duplicates().dropna())
        list_option_from_filtered_df_down = list(filtered_df_down.iloc[0, :])  # ['axle', 'axle', 'サンルーフ', 'サンルーフ']
        list_condition = filtered_df_down.iloc[2, :].tolist()  # ['不問', '不問', '不問', '不問']
        list_condition.append(str(condition_base))  # ['不問', '不問', '不問', '不問', '不問']
        if '最下級' in list_condition:
            condition = '最下級'
        else:
            condition = '不問'
        # return set(list_option_from_filtered_df_down)
        if len(set(list_option_from_filtered_df_down)) < len(list_option_from_karen2):
            # Nếu các option sau khi lọc down mà nhỏ hơn số options ban đầu thì loại.
            result_dict_down = {}
        else:
            list_items_down = filtered_df_down.iloc[1, :].tolist()  # ['2wd', '4wd', 'w', 'w/o']
            dict_items_from_filtered_df_down = {}

            for key_sub, value in zip(list_option_from_filtered_df_down, list_items_down):
                if key_sub not in dict_items_from_filtered_df_down:
                    dict_items_from_filtered_df_down[key_sub] = []

                if pd.notna(value) and value not in dict_items_from_filtered_df_down[key_sub]:
                    dict_items_from_filtered_df_down[key_sub].append(value)
            # dict_items_from_filtered_df_down = {'axle': ['2wd', '4wd'], 'サンルーフ': ['w', 'w/o']}

            # Lọc file spec chỉ còn các options cần quan tâm.
            filtered_df_spec_in_case_down = data_spec[data_spec.iloc[:, 3].isin(list_option_from_filtered_df_down)]
            # Đặt tên cột cho df
            filtered_df_spec_in_case_down.columns = data_spec.iloc[0]
            # Duyệt qua từng values ví dụ ['conf-001', 'conf-002', 'conf-003']
            for list_name_conf in dict_input.values():
                # Duyệt qua từng cột trong đó: ví dụ 'conf-001':
                for column in list_name_conf:
                    sub_dict = dict(zip(filtered_df_spec_in_case_down['cadics id'],
                                        filtered_df_spec_in_case_down[column].apply(lambda x: [x])))
                    # sub_dict = {'axle': ['awd'], 'サンルーフ': ['w/o']}
                    if len(sub_dict) != len(dict_items_from_filtered_df_down):
                        sub_dict = {}
                        dict_items_from_filtered_df_down = {}
                    sub_dict_replace_standard = copy.deepcopy(sub_dict)
                    sub_dict_replace_standard = replace_standard(
                        sub_dict_replace_standard)  # {'axle': ['awd'], 'サンルーフ': ['w/o']}
                    dict_items_from_filtered_df_down_replace_standard = replace_standard(
                        dict_items_from_filtered_df_down)  # {'axle': ['fwd', 'awd'], 'サンルーフ': ['w', 'w/o']}
                    common_dict = common_elements(sub_dict_replace_standard,
                                                  dict_items_from_filtered_df_down_replace_standard)
                    flag_check_dict_down = False
                    if common_dict == sub_dict_replace_standard:
                        flag_check_dict_down = True

                    for key_sub in result_dict_down.keys():
                        # Tìm vị trí chữ 'c' cuối cùng trong key
                        last_c_index = key_sub.rfind('c')
                        # Chỉ lấy cột cuối ví dụ chuỗi 'US_最下級_conf-001_conf-002' thì lấy 'conf-002'
                        last_column_in_pair = key_sub[last_c_index:]
                        # Nếu cột giống nhau và nằm trong cùng zone key thì thêm vào key
                        if (filtered_df_spec_in_case_down[column] == filtered_df_spec_in_case_down[
                            last_column_in_pair]).all() and last_column_in_pair in list_name_conf and condition in key_sub and column not in key_sub:
                            # Nối các conf nếu chúng có các option giống hệt nhau
                            key_merge = key_sub + "_" + column
                            # Sau khi nối xong thì thay key cũ bằng key mới.
                            result_dict_down[key_merge] = result_dict_down.pop(key_sub)
                            flag_check_dict_down = False
                            break
                    if flag_check_dict_down:
                        result_dict_down[zone + "_" +condition + "_" + column] = sub_dict
            # print("result_dict_down :", result_dict_down)
    if not any({**result_dict_up, **result_dict_down}.values()):
        string_comment = str({**dict_items_from_filtered_df_up, **dict_items_from_filtered_df_down})
        for sym in ["{", "}", "[", "]", "'"]:
            string_comment = string_comment.replace(sym, "")
        return {}, string_comment.upper(), dict_from_syo
    return {**result_dict_up, **result_dict_down}, '', dict_from_syo


# if __name__ == '__main__':
#     link_karen2 = r"C:\Users\KNT21617\Downloads\New folder (5)\NO1_FINAL_4\data\WZ1J\関連表2_I(HF-VR-ETC)_XM6.xlsx"
#     link_spec = r"C:\Users\KNT21617\Downloads\New folder (5)\NO1_FINAL_4\data\WZ1J\仕様表_WZ1J.xlsx"
#     data_spec = pd.read_excel(link_spec, header=None, sheet_name="Sheet1")
#     df_karen2 = pd.read_excel(link_karen2, sheet_name="関連表", header=None)
#     df_input = df_karen2.iloc[1:4, [24, 37]]
#     print(df_input)
#     dict_input_1 = {'us_can_不問': ['conf-001', 'conf-002', 'conf-003', 'conf-004', 'conf-005', 'conf-006']}

#     dict_input = {'us_不問': ['conf-003']}
#     time1 = time.time()
#     dict_output, string_comment = check_option_new_v4(data_spec, df_input, dict_input_1,6)
#     print("dict_output: ", dict_output)
#     # print("dict_output: ", dict_output)
#     time2 = time.time()
#     print('Runtime: ', time2 - time1)
