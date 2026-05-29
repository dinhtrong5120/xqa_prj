"""Create by KD.Trong - KNT21617 17:00:00 - 07/12/2023"""
import pandas as pd
import unicodedata

"""
Name function: create_dict_from_syo
Create dictionaries from syo
input: list_option_from_karenhyo2(list): contains key ,ex: ['ivi display audio', 'hud']
        data_spec_ (dataframe): dataframe from file syo, 
output: dict_syo (dict):  Equipment in syo, ex: {'シート材質': ['Leather'], 'スポーツシート': ['-'], 'スライドシート': ['w']}
"""


def create_dict_from_syo(list_option_from_karenhyo2, data_spec_, number_car):
    data_spec_.iloc[:, 3] = data_spec_.iloc[:, 3].str.strip()
    # data_spec_.iloc[:, 3] = data_spec_.iloc[:, 3].str.strip()
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
            # print(f"Value '{option}' not found in data_spec_.")
            dict_syo[option] = []
    return dict_syo

"""
Name function: replace_standard
replace special characters
input: dict_need_to_replace(dict): Dictionary of equipment, list_same_mean(list): Equipment with the same mean
output: new_dict_replaced (dict):  New dictionary after being replaced
"""


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


"""
Name function: common_elements
Combine two dictionaries
input: dict_karen(dict): Dictionary of karenhyo2, dict_syo(dict): Dictionary of syo
output: common_dict (dict):  New dictionary after Combined
"""


def common_elements(dict_syo, dict_kanren):
    common_dict = {}
    # normalized_data = {}
    # for key, value in input_data.items():
    #     normalized_value = [normalize_japanese_text(item) for item in value]
    #     normalized_data[key] = normalized_value
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


def create_string(dict_from_karen2_standard, common_dict, dict_from_karen2, dict_from_syo_standard):
    for item1, item2, item3 in zip(common_dict, dict_from_karen2_standard, dict_from_syo_standard):
        if common_dict[item1] == dict_from_syo_standard[item3] or 'all' in dict_from_karen2_standard[item2]:
            dict_from_karen2.pop(item1)

    return dict_from_karen2


def check_option(df_karen2, data_spec, number_car):
    common_dict = {}
    flag_check_empty = False  # No region after 'zone'
    data_spec = data_spec.map(lambda x: normalize_japanese_text(x).lower() if isinstance(x, str) else x)
    df_karen2 = df_karen2.map(lambda x: normalize_japanese_text(x).lower() if isinstance(x, str) else x)
    # df_karen2 = df_karen2.map(lambda x: normalize_japanese_text(x) if isinstance(x, str) else x)
    list_zone_region_columns = df_karen2.columns[df_karen2.iloc[1].apply(lambda x: str(x)) == 'zone'].tolist()
    df_filter = df_karen2.iloc[1:3, max(list_zone_region_columns) + 1:] if len(
        list_zone_region_columns) > 0 else pd.DataFrame  # after last zone columns
    if df_filter.empty or df_filter.isna().all().all():
        flag_check_empty = True
        # print("DataFrame df_filter is empty.")
    else:
        flag_check_empty = False
        df_filter = df_filter.reset_index(drop=True)
    if flag_check_empty:
        return common_dict, 1
    else:
        list_option_from_karen2 = list(df_filter.iloc[0, :].drop_duplicates().dropna())
        list_options = df_filter.iloc[0, :].dropna().tolist()
        list_items = df_filter.iloc[1, :].tolist()
        dict_from_karen2 = {}

        for key, value in zip(list_options, list_items):
            if key not in dict_from_karen2:
                dict_from_karen2[key] = []

            if pd.notna(value) and value not in dict_from_karen2[key]:
                dict_from_karen2[key].append(value)
        dict_from_karen2_standard = replace_standard(dict_from_karen2)
        dict_from_syo = create_dict_from_syo(list_option_from_karen2, data_spec, number_car)
        dict_from_syo_standard = replace_standard(dict_from_syo)
        common_dict = common_elements(dict_from_syo_standard, dict_from_karen2_standard)
        dict_kep = create_string(dict_from_karen2_standard, common_dict, dict_from_karen2, dict_from_syo_standard)
        # print("dict_from_syo_standard: ", dict_from_syo_standard)
        # print("dict_from_karen2_standard: ", dict_from_karen2_standard)
        # print("common_dict:", common_dict)
        return common_dict, dict_kep
