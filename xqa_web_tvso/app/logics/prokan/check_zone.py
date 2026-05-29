def condition_zone(dict_zone, df_filter_):
    key_fumon = ""
    for key in dict_zone.keys():
        if key == "usa":
            key = "us"
        if key == "canada":
            key = "can"
        if len(key_fumon) == 0:
            key_fumon = key
        else:
            key_fumon = key_fumon + "_" + key
    Dict_return = {}
    flg_check_other, list_col_and_condition_other = create_list_col_condition('other|その他', df_filter_)
    flg_check_all, list_col_and_condition_all = create_list_col_condition('all', df_filter_)
    flg_check_fumon, list_col_and_condition_fumon = create_list_col_condition('不問|-|nan|ー', df_filter_)
    if flg_check_all:
        Dict_return.update({key: list_col_and_condition_all for key in dict_zone.keys()})
        for key_all in Dict_return.keys():
            if key_all == 'us':
                df_filter_1 = df_filter_.replace('rus', '', regex=True)
                flg_check_all_and_us, list_col_and_condition_all_add_us = create_list_col_condition(key_all,
                                                                                                    df_filter_1)
            else:
                flg_check_all_and_us, list_col_and_condition_all_add_us = create_list_col_condition(key_all,
                                                                                                    df_filter_)
            if flg_check_all_and_us:
                Dict_return_ref = Dict_return[key_all].copy()
                Dict_return_ref.extend(list_col_and_condition_all_add_us)
                Dict_return[key_all] = Dict_return_ref
            else:
                None
    elif flg_check_fumon:
        Dict_return.update({key_fumon: list_col_and_condition_fumon})
    else:
        list_key = list(dict_zone.keys())
        for item in list_key:
            if item == 'us':
                df_filter_1 = df_filter_.replace('rus', '', regex=True)
                flg_check_normal, list_col_and_condition_normal = create_list_col_condition(item,
                                                                                            df_filter_1)
            else:
                flg_check_normal, list_col_and_condition_normal = create_list_col_condition(item,
                                                                                            df_filter_)
            if flg_check_normal:
                Dict_return[item] = list_col_and_condition_normal
            else:
                None
            if len(list_col_and_condition_normal) == 0 and flg_check_other:
                Dict_return[item] = list_col_and_condition_other
            elif len(list_col_and_condition_normal) == 0 and not flg_check_other:
                Dict_return[item] = []
    return Dict_return, flg_check_all


def create_list_col_condition(keywords, df_filter_):
    list_col_found_keywords = df_filter_.columns[
        df_filter_.iloc[1].astype(str).str.lower().str.contains(keywords)].tolist()
    list_col_and_condition = [
        [i, df_filter_.loc[2, i]] if df_filter_.loc[2, i] in ["最下級", "最上級"] else [i, "不問"]
        for i in list_col_found_keywords
    ]
    return bool(list_col_found_keywords), list_col_and_condition


def combine_dict(dict_return):
    dict_result = {}
    elements_list = []
    for key, value in dict_return.items():
        elements_list.extend(value)

    unique_list = []
    for item in elements_list:
        if item not in unique_list:
            unique_list.append(item)

    for y in unique_list:
        found_keys = []
        for key, value in dict_return.items():
            if y in value:
                found_keys.append(key)

        key_combine = f"{'_'.join(found_keys)}"
        if key_combine not in dict_result.keys():
            dict_result[key_combine] = [y]
        else:
            if isinstance(y, list):
                dict_result[key_combine].append(y)
            else:
                dict_result[key_combine].append([y])
    return dict_result


def condition_zone_check(data_karenhyo2, dict_zone):
    data_karenhyo2 = data_karenhyo2.map(lambda x: x.lower() if isinstance(x, str) else x)
    data_test = data_karenhyo2.iloc[1:4, 11:]
    data_test = data_test.reset_index(drop=True)
    df_filter = data_test.copy().loc[:, data_test.loc[0] == 'zone']
    Dict_return, flag_check_all = condition_zone(dict_zone, df_filter)
    if flag_check_all:
        end_dict = Dict_return
    else:
        end_dict = combine_dict(Dict_return)
    return flag_check_all, end_dict
