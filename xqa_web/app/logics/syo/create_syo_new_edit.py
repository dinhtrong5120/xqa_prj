import re
import pandas as pd
from .edit_syo_new import process_dataframe
from .check_filed_information import normalize_japanese_text


def create_syo(form_syo, data_for_create):
    """
    Generates a new SYO DataFrame by filling in configuration values based on a template and specification data.

    Args:
        form_syo (DataFrame): The SYO form template to be filled.
        data_for_create (tuple): A tuple containing:
            - data_spec (DataFrame): The specification data.
            - col_option (int): The column index for options in the spec.
            - col_start_config (int): The starting column index for configuration.
            - col_attribute (int): The column index for attributes.
            - col_option_code (int): The column index for option codes.
            - col_end_config (int): The ending column index for configuration.

    Returns:
        DataFrame: The completed SYO DataFrame after processing and filling all necessary values.

    Notes:
        - The function normalizes all string values in both `form_syo` and `data_spec`.
        - It creates a dictionary of option codes based on the "OptionCode" row in the form.
        - For each row in the form, it determines how to fill values based on the "keyword" and "CADICS ID" columns,
          using the `nhap` function and handling complex option patterns.
        - The function logs all local variables to 'create_syo_input.txt' for debugging.
        - After filling, it restores any dropped columns and applies additional post-processing to the DataFrame.
    """
    class_option = ''
    data_spec, col_option, col_start_config, col_attribute, col_option_code, col_end_config = data_for_create
    form_syo = form_syo.fillna("")
    data_spec = data_spec.fillna("")
    data_spec = data_spec.applymap(lambda x: normalize_japanese_text(x) if isinstance(x, str) else x)
    form_syo = form_syo.applymap(lambda x: normalize_japanese_text(x) if isinstance(x, str) else x)
    form_syo = form_syo.reset_index(drop=True)

    df_insert = form_syo[['group_key_map', 'default']]
    form_syo = form_syo.drop(columns=['group_key_map', 'default'])

    column_name = list(range(data_spec.shape[1]))
    data_spec.columns = column_name

    col_option = col_option - 1
    col_start_config = col_start_config  # in spec
    col_end_config = col_end_config  # in spec
    col_option_code = col_option_code - 1  # in spec
    col_attribute = col_attribute - 1  # in spec

    dict_option_code = {}
    # Determine the starting point
    index_start = form_syo[form_syo["auto"] == "X01_VISIBILITY"].index
    index_option_code = form_syo[form_syo["CADICS ID"] == "OptionCode"].index

    # Determine optioncode
    for index in range(4, len(form_syo.columns)):
        config = form_syo.columns[index]
        header = form_syo.columns[index]
        dict_option_code[config] = str(form_syo[header][int(index_option_code[0])])
    # EG: dict_option_code={'conf-001': 'SPTR6', 'conf-002': 'NAVI3,RRBY3,EQIPD', 'conf-003': 'CLAS2,EQIPC'}
    for index in range(int(index_start[0]), index_option_code[0]):
        keyword_col_C = form_syo["keyword"][index]
        keyword_col_C = keyword_col_C.replace('\n', "")
        if keyword_col_C == '':
            value_in_cadics_columns = form_syo["CADICS ID"][index].upper()
            value_in_auto_columns = form_syo["auto"][index].upper()
            if value_in_cadics_columns == '' and value_in_auto_columns != '':
                class_option = form_syo["auto"][index].upper()
        else:
            if keyword_col_C == 'ALL' or keyword_col_C == 'w,w/o':
                LIST_HIENTHI = ["w", "w/o"]
                if keyword_col_C == 'ALL':
                    LIST_HIENTHI = ["ALL", "-"]

                option = form_syo["CADICS ID"][index].upper()
                nhap(form_syo, data_spec, index, col_option, dict_option_code, col_start_config, col_end_config,
                     col_option_code, col_attribute, column_name, class_option, option, LIST_HIENTHI)
            elif '(ALL)' in keyword_col_C or '(w,w/o)' in keyword_col_C:
                LIST_HIENTHI = ["w", "w/o"]
                if '(ALL)' in keyword_col_C:
                    LIST_HIENTHI = ["ALL", "-"]
                option = keyword_col_C.replace("(ALL)", "")
                option = option.replace("(w,w/o)", "").upper()
                nhap(form_syo, data_spec, index, col_option, dict_option_code, col_start_config, col_end_config,
                     col_option_code, col_attribute, column_name, class_option, option, LIST_HIENTHI)
            else:
                parts = custom_split(keyword_col_C)
                for item in parts:
                    item = item.strip()
                    try:
                        result_yes = re.search(r'\(([^()]+)\)$', item).group(1)
                        result_yes_split = result_yes.split(",")
                        if len(result_yes_split) == 1:
                            LIST_HIENTHI = [result_yes_split[0], "-"]
                        else:
                            LIST_HIENTHI = [result_yes_split[0], result_yes_split[1]]
                        option = re.sub(r'\([^()]+\)$', '', item).strip().upper()

                        nhap(form_syo, data_spec, index, col_option, dict_option_code, col_start_config, col_end_config,
                             col_option_code, col_attribute, column_name, class_option, option, LIST_HIENTHI)

                    except:
                        LIST_HIENTHI = [item, "-"]
                        option = item.strip().upper()
                        nhap(form_syo, data_spec, index, col_option, dict_option_code, col_start_config,
                             col_end_config,
                             col_option_code, col_attribute, column_name, class_option, option, LIST_HIENTHI)
    df_combined = pd.concat([form_syo, df_insert], axis=1)
    df_2 = process_dataframe(df_combined)
    return df_2


def custom_split(s):
    """
    Splits the input string into parts based on commas (','),
    but ignores commas that are inside parentheses.

    Args:
        s (str): The input string to split.

    Returns:
        list: A list of substrings after splitting.

    Example:
        custom_split("a,b,(c,d),e") returns ['a', 'b', '(c,d)', 'e']
    """
    parts = []
    in_parentheses = False
    current_part = ""
    for char in s:
        if char == "(":
            in_parentheses = True
        elif char == ")":
            in_parentheses = False
        if char == "," and not in_parentheses:
            parts.append(current_part)
            current_part = ""
        else:
            current_part += char
    parts.append(current_part)
    return parts


def nhap(form_syo, data_spec, index, col_option, dict_option_code, col_start_config, col_end_config,
         col_option_code, col_attribute, column_name, class_option, option, LIST_HIENTHI):
    """
    Fills in values into the `form_syo` DataFrame based on the provided options and configuration data.

    Args:
        form_syo (DataFrame): The form to be filled.
        data_spec (DataFrame): The specification data used for lookup.
        index (int): The row index in `form_syo` to fill.
        col_option (str): The column name in `data_spec` to match the option.
        dict_option_code (dict): Dictionary mapping config keys to option codes.
        col_start_config (int): The starting column index for configuration.
        col_end_config (int): The ending column index for configuration.
        col_option_code (str): The column name for option codes.
        col_attribute (str): The column name for attribute values.
        column_name (list): List of column names in `data_spec`.
        class_option (str): The class option to use if the option is not found.
        option (str): The option value to look up.
        LIST_HIENTHI (list): List of display replacement values.

    Returns:
        None: The function modifies `form_syo` in place.

    Notes:
        - Handles both the case when the option is found and not found in `data_spec`.
        - Applies replacement rules based on `LIST_HIENTHI`.
    """
    result = data_spec[data_spec[col_option] == option]
    if len(result) > 0:  # Case option is found
        result = result.reset_index(drop=True)
        list_data = option_in_A(result, dict_option_code, col_start_config, col_end_config,
                                col_option_code, col_attribute, 1)
        if LIST_HIENTHI != ["ALL", "-"]:
            replacement_value = LIST_HIENTHI[0]
            for i in range(len(list_data)):
                if list_data[i] != '-' and list_data[i] != '' and ':' not in list_data[i]:
                    list_data[i] = replacement_value
                else:
                    try:
                        if list_data[i] != '' and ':' not in list_data[i]:
                            list_data[i] = LIST_HIENTHI[1]
                        if ':' in list_data[i]:
                            list_data[i] = ''
                    except:
                        pass
    else:
        result = data_spec[data_spec[column_name[-1]] == class_option]  # 1 là cột class
        if LIST_HIENTHI == ["ALL", "-"]:
            LIST_HIENTHI = ["w", "w/o"]
        list_data = option_in_D(option, result, dict_option_code, col_start_config, col_end_config,
                                col_option_code, col_attribute, col_option, LIST_HIENTHI)
    col_start = 4

    for item in list_data:

        try:
            if form_syo.iat[index, col_start] == "" or form_syo.iat[index, col_start] == "-":
                form_syo.iat[index, col_start] = item
        except:
            form_syo[col_start] = ''
            form_syo.iat[index, col_start] = item
        finally:
            col_start = col_start + 1


def option_in_A(result, dict_option_code, col_start_config, col_end_config,
                col_option_code, col_attribute, flag):
    """
    Extracts configuration attributes and option codes from a DataFrame segment.

    Args:
        result (DataFrame): The filtered DataFrame to process.
        dict_option_code (dict): Dictionary mapping config keys to option codes.
        col_start_config (int): The starting column index for configuration.
        col_end_config (int): The ending column index for configuration.
        col_option_code (str): The column name for option codes.
        col_attribute (str): The column name for attribute values.
        flag (int): Determines the format of the return value.

    Returns:
        list or dict: If `flag` is 1, returns a list of configuration values and attributes.
                      If `flag` is 0, returns a dictionary mapping config keys to attributes.
        EG: list_data: list_data=['-', '-', '-', 'S1', '-', '-', '-', 'S1', '-', '-', '-', 'S1', '-', '-', '-', 'S1', '-',
        '-', '-', '-', 'HEAT3', 'S1: BATTERY HEATING']
        dict_config_value={'conf-001': 'BASIC', 'conf-002': 'BASIC', 'conf-003': 'BASIC', 'conf-004': 'BASIC', 'conf-005': 'BASIC',
        'conf-006': 'BASIC', 'conf-007': 'BASIC', 'conf-008': 'BASIC', 'conf-009': 'BASIC', 'conf-010': 'BASIC', 'conf-011': 'BASIC',
        'conf-012': 'BASIC', 'conf-013': 'BASIC', 'conf-014': 'BASIC', 'conf-015': 'BASIC', 'conf-016': 'BASIC', 'conf-017': 'BASIC',
        'conf-018': 'BASIC', 'conf-019': 'BASIC', 'conf-020': 'BASIC'}

    Notes:
        - Handles both option code and attribute extraction.
        - Converts attribute names to labels like S1, S2, etc., if `flag` is 1.
    """
    dict_config_value = {}
    list_option_code_all = []
    list_attribute = []
    index_config = 1
    for address_config in range(col_start_config, col_end_config):

        if index_config < 10:
            config = "conf-00" + str(index_config)
        if 9 < index_config < 100:
            config = "conf-0" + str(index_config)

        list_option_code = []
        index_attribute_o = result[result[address_config] == "Opt."].index
        attribute = "-"
        # =============================Get optioncode===================================
        if len(index_attribute_o) > 0:
            for index in range(len(index_attribute_o)):
                option_code = result[col_option_code][index_attribute_o[index]]
                if isinstance(option_code, str) and option_code != "":
                    list_option_code.append(option_code)
            # =============================== Case ==========================================

            syo_option_code = str(dict_option_code[config]).split(",")
            has_option = set(list_option_code).issubset(set(syo_option_code))
            if has_option:
                list_option_code_all = list_option_code_all + list_option_code
                attribute = result[col_attribute][index_attribute_o[0]]
                if attribute not in list_attribute:
                    list_attribute.append(attribute)

        if attribute == "-":
            index_attribute_d = result[result[address_config] == "D"].index

            if len(index_attribute_d) > 0:
                attribute = result[col_attribute][index_attribute_d[0]]
                if attribute not in list_attribute and attribute != "-":
                    list_attribute.append(attribute)
            else:
                index_attribute_s = result[result[address_config] == "S"].index
                if len(index_attribute_s) > 0:
                    attribute = result[col_attribute][index_attribute_s[0]]
                if attribute not in list_attribute and attribute != "-":
                    list_attribute.append(attribute)

        index_config = index_config + 1
        dict_config_value[config] = attribute

    # Convert Attribute to S, S2, S3 .....
    if flag == 1:
        for config, attribute in dict_config_value.items():
            if attribute != "-":
                index = list_attribute.index(attribute)
                dict_config_value[config] = "S" + str(index + 1)

        for index in range(len(list_attribute)):
            list_attribute[index] = "S" + str(index + 1) + ": " + str(list_attribute[index])

        list_option_code_all = list(dict.fromkeys(list_option_code_all))
        comment_option = str(list_option_code_all)
        for sys in ["[", "]", "'"]:
            comment_option = comment_option.replace(sys, "")
        list_attribute.insert(0, comment_option)
        # EG: list_attribute=['HEAT3', 'S1: BATTERY HEATING']
        values_list = list(dict_config_value.values())
        # EG: values_list=['-', '-', '-', 'S1', '-', '-', '-', 'S1', '-', '-', '-', 'S1', '-', '-', '-', 'S1', '-', '-', '-', '-']
        list_data = values_list + list_attribute
        return list_data
    else:
        return dict_config_value


def option_in_D(attribute, result, dict_option_code, col_start_config, col_end_config,
                col_option_code, col_attribute, col_option, LIST_HIENTHI):
    """
    Processes attributes and fills configuration values based on complex attribute patterns.

    Args:
        attribute (str): The attribute string to process (may contain '+' or '✚').
        result (DataFrame): The filtered DataFrame to process.
        dict_option_code (dict): Dictionary mapping config keys to option codes.
        col_start_config (int): The starting column index for configuration.
        col_end_config (int): The ending column index for configuration.
        col_option_code (str): The column name for option codes.
        col_attribute (str): The column name for attribute values.
        col_option (str): The column name for options.
        LIST_HIENTHI (list): List of display replacement values.

    Returns:
        list: List of configuration values based on the attribute and options.
        EG: ['w/o', 'w/o', 'w/o', 'w/o', 'w/o', 'w/o', 'w/o', 'w/o', 'w/o', 'w/o', 'w/o', 'w/o', 'w/o', 'w/o', 'w/o', 'w/o', 'w/o', 'w/o', 'w/o', 'w/o']

    Notes:
        - Supports processing of multiple attributes joined by '+' or '✚'.
        - Applies display replacement rules based on `LIST_HIENTHI`.

    """
    list_vip = []
    if '✚' in attribute or '+' in attribute:
        list_attribute = re.split(r"[✚+]", attribute)
        # EG: list_attribute=['HEAT3', 'S1: BATTERY HEATING']
        dict_check = {}
        dict_check_1 = {}
        for item in list_attribute:
            filter_attribute = result[result[col_attribute].str.contains(item, regex=False, na=False)]
            if len(filter_attribute) > 0:

                list_option = filter_attribute[col_option].dropna().unique()
                #eg: list_option=['TAILGATE/TRUNK OPENING']
                for option in list_option:
                    sub_result = result[result[col_option] == option]
                    sub_result = sub_result.reset_index(drop=True)

                    dict_config_value = option_in_A(sub_result, dict_option_code, col_start_config, col_end_config,
                                                    col_option_code, col_attribute, 0)
                    for config, value in dict_config_value.items():
                        if config not in dict_check.keys():
                            dict_check[config] = value
                        else:
                            dict_check[config] = dict_check[config] + "+" + value
                for config_1, value_1 in dict_check.items():
                    if item in value_1:
                        if item not in list_vip:
                            list_vip.append(item)
                        if len(list_vip) == 1:
                            dict_check_1[config_1] = item
                        elif len(list_vip) > 1:
                            dict_check_1[config_1] += ('✚' + item)
                    else:
                        dict_check_1[config_1] = '-'

            else:
                list_data = [LIST_HIENTHI[1]] * (col_end_config - col_start_config)
                return list_data
        # EG: dict_check_1={'conf-001': '-', 'conf-002': '-', 'conf-003': 'POWER OPEN/CLOSE ✚ HANDS FREE',
        # 'conf-004': 'POWER OPEN/CLOSE ✚ HANDS FREE', 'conf-005': '-', 'conf-006': '-',
        # 'conf-007': 'POWER OPEN/CLOSE ✚ HANDS FREE', 'conf-008': 'POWER OPEN/CLOSE ✚ HANDS FREE',
        # 'conf-009': '-', 'conf-010': '-', 'conf-011': 'POWER OPEN/CLOSE ✚ HANDS FREE',
        # 'conf-012': 'POWER OPEN/CLOSE ✚ HANDS FREE', 'conf-013': '-', 'conf-014': '-',
        # 'conf-015': 'POWER OPEN/CLOSE ✚ HANDS FREE', 'conf-016': 'POWER OPEN/CLOSE ✚ HANDS FREE',
        # 'conf-017': '-', 'conf-018': 'POWER OPEN/CLOSE ✚ HANDS FREE', 'conf-019': 'POWER OPEN/CLOSE ✚ HANDS FREE',
        # 'conf-020': 'POWER OPEN/CLOSE ✚ HANDS FREE'}
        list_data = list(dict_check_1.values())
        if LIST_HIENTHI == ['w', 'w/o']:
            for i in range(len(list_data)):
                if list_data[i] != '-' and list_data[i] != '' and ':' not in list_data[i]:
                    list_data[i] = LIST_HIENTHI[0]
                if list_data[i] == '-':
                    list_data[i] = LIST_HIENTHI[1]
                if ':' in list_data[i]:
                    list_data[i] = ''
        return list_data

    else:
        filter_attribute = result[result[col_attribute].str.contains(attribute, regex=False, na=False)]
        if len(filter_attribute) > 0:
            dict_check = {}
            list_option = filter_attribute[col_option].dropna().unique()

            for option in list_option:
                sub_result = result[result[col_option] == option]
                sub_result = sub_result.reset_index(drop=True)

                dict_config_value = option_in_A(sub_result, dict_option_code, col_start_config, col_end_config,
                                                col_option_code, col_attribute, 0)

                for config, value in dict_config_value.items():
                    if config not in dict_check.keys():
                        dict_check[config] = value
                    else:
                        dict_check[config] = dict_check[config] + " + " + value

            for config, value in dict_check.items():
                if attribute in value:
                    dict_check[config] = LIST_HIENTHI[0]
                else:
                    dict_check[config] = LIST_HIENTHI[1]

            list_data = list(dict_check.values())

        else:
            list_data = [LIST_HIENTHI[1]] * (col_end_config - col_start_config)
        return list_data
