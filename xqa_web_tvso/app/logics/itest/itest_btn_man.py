import os
import pandas as pd
import re
import shutil
import openpyxl
import unicodedata
from xqa_web_tvso.app.logics.itest.patern_reduce import *
from xqa_web_tvso.app.setting import BASE_DIR_OUTPUTS, BASE_DIR_DATAS


def data_normalization(data):
    """ standardize data, avoid large and small letters and special characters"""
    data = str(data)
    normalized_text = ''
    data = re.sub(r'\s+', '', data)
    data = re.sub(r'[^\w\s\u3040-\u309F\u30A0-\u30FF]', '', data)
    
    for char in data:
        normalized_char = unicodedata.normalize('NFKC', char)
        normalized_text += normalized_char
    normalized_text = normalized_text.replace("\n", "")
    normalized_text = normalized_text.strip()
    return normalized_text


def write_log(folder_output_itest, df_log, sheet_log):
    log_path = os.path.join(folder_output_itest, 'log_itest.xlsx')
    
    with pd.ExcelWriter(log_path, engine='openpyxl', mode='a' ,if_sheet_exists= "replace") as writer:
        df_log.to_excel(writer, sheet_name= sheet_log, index= False, header= True)
        # df_log.to_excel(writer, sheet_name=sheet_log, index=False)


def get_link_folder_output(list_option_base, option_taiso):
    """
    open the taiso output folder, find out if the itest output of the bases currently selected on the interface exists:

    + ) output name: 'itest_compare_base1' + '_compare_base2' +.....
    so in the file name there is "_compare_" = the number of bases selected AND the names of the bases are in the itest output folder name

    """

    folder_car_taiso = os.path.join(BASE_DIR_OUTPUTS, option_taiso)
    for output in os.listdir(folder_car_taiso):
        output_path = os.path.join(folder_car_taiso, output)
        count_compare = output.count("_compare_")
        if 'itest_compare_' in output_path and all(options in output_path for options in list_option_base) and len(list_option_base) == count_compare and ".ZIP" not in output_path.upper():
            folder_output_itest_path = output_path
            break
        else:
            folder_output_itest_path = ""

    return folder_output_itest_path


def create_folder_output_itest(list_option_base, option_taiso):
    """ Create folder to save itest output """

    folder_name = "itest_compare_" + "_compare_".join(list_option_base)
    folder_output_itest_path = os.path.join(BASE_DIR_OUTPUTS, option_taiso, folder_name)
    os.makedirs(folder_output_itest_path)
    return folder_output_itest_path


def get_data_folder(option_taiso):
    """ Get data folder path """
    car_name_taiso = option_taiso.split('_')[0]
    folder_data = os.path.join(BASE_DIR_DATAS, car_name_taiso)
    return folder_data


def create_output_log_and_kanren(option_taiso,folder_output_itest):
    """
    check if there is a log file, if not, create it
    check if there is a folder "関連表③" or not, if not, create it, if there is, delete it and create a new folder "関連表③"
    """
    if os.path.exists(folder_output_itest) == False:
        print("bug")
    else:
        # --------------------------Log
        log_file_path = os.path.join(folder_output_itest, 'log_itest.xlsx')
        with pd.ExcelWriter(log_file_path) as writer:
            columns_check_youbou = ['file_name', 'Sheet', '関連ファイル名',"実験"]
            df1 = pd.DataFrame(columns=columns_check_youbou)
            df1.to_excel(writer, sheet_name='check_youbou', index=False)

            column_check_kanren=["file_name_check","jikken","sheet","log"]
            df2 = pd.DataFrame(columns = column_check_kanren )
            df2.to_excel(writer, sheet_name='check_up_kanren', index=False)

        compare_file = os.path.join(folder_output_itest, 'compare_配車要望表.xlsx')
        if os.path.exists(compare_file) == True:
             os.remove(compare_file)

        car_name_taiso = option_taiso.split('_')[0]
        delete_jikken_name = f"{car_name_taiso}_2番手_削減後_Car配車要望表.xlsx"
        delete_jikken_file = os.path.join(folder_output_itest, delete_jikken_name)
        if os.path.exists(delete_jikken_file) == True:
             os.remove(delete_jikken_file)

        folder_create = os.path.join(folder_output_itest, '関連表③')
        # folder_create=f"{folder_output_itest}/関連表③"
        folder_create = os.path.join(folder_output_itest, '関連表③')

        if os.path.exists(folder_create) == False:
            os.makedirs(folder_create, exist_ok=True)
        else:
            shutil.rmtree(folder_create)
            os.makedirs(folder_create, exist_ok=True)


def check_format_youbouhyo(df_log,format_ok, youbouhyo_path, xls, sheet_name):
    """
    Check if youbouhyo file has column "ファイル名" and column "実験" if yes add sheet name to list of base sheets for comparison
    if no then log sheet... in base file... wrong format
    """
    df_file = pd.read_excel(xls, sheet_name=sheet_name)

    column_file_name = "関連ファイル名"
    column_jikken= "実験"
    if len(df_file.columns) < 162 :
        new_row = {'file_name': youbouhyo_path , 'Sheet': sheet_name, '関連ファイル名' : "×", "実験": "×"}
        df_log.loc[len(df_log)] = new_row
    else:
        if data_normalization(df_file.iloc[17, 161]) == data_normalization(column_file_name):
            if data_normalization(df_file.iloc[17, 160]) == data_normalization(column_jikken):
                format_ok.append(sheet_name)
                new_row = {'file_name': youbouhyo_path , 'Sheet': sheet_name, '関連ファイル名' : "〇", "実験": "〇"}
                df_log.loc[len(df_log)] = new_row

        if data_normalization(df_file.iloc[17, 161]) != data_normalization(column_file_name):
            if data_normalization(df_file.iloc[17, 160]) == data_normalization(column_jikken):
                new_row = {'file_name': youbouhyo_path , 'Sheet': sheet_name, '関連ファイル名' : "×", "実験": "〇"}
                df_log.loc[len(df_log)] = new_row

        if data_normalization(df_file.iloc[17, 161]) == data_normalization(column_file_name):
            if data_normalization(df_file.iloc[17, 160]) != data_normalization(column_jikken):
                new_row = {'file_name': youbouhyo_path , 'Sheet': sheet_name, '関連ファイル名' : "〇", "実験": "×"}
                df_log.loc[len(df_log)] = new_row

        if data_normalization(df_file.iloc[17, 161]) != data_normalization(column_file_name):
            if data_normalization(df_file.iloc[17, 160]) != data_normalization(column_jikken):
                new_row = {'file_name': youbouhyo_path , 'Sheet': sheet_name, '関連ファイル名' : "×", "実験": "×"}
                df_log.loc[len(df_log)] = new_row
    return format_ok, df_log


def check_sheet_youbouhyo(df_log,list_option):
    """
    check the format of each file, each sheet in the file.
    The result is a dic: the key is the file path, the value is the list of sheets with the correct format
    """

    youbouhyo_name = "Car配車要望表.xlsx"
    # get the youbouhyo path list of the cars in list_option
    list_youbouhyo_path = [os.path.join(BASE_DIR_OUTPUTS, folder_name, youbouhyo_name) for folder_name in list_option]
    dic_filepath_sheetname = {}  # 1 dic

    for path in list_youbouhyo_path:
        if os.path.exists(path):
            xls = pd.ExcelFile(path)
            # df_inf_car = pd.read_excel (xls , skiprows=0 , nrows=18)
            list_format_ok = []
            for sheet_name in xls.sheet_names:  # check format of each sheet
                list_format_ok, df_log = check_format_youbouhyo(df_log,list_format_ok, path, xls, sheet_name)

            if list_format_ok == []:
                pass
            else:
                dic_filepath_sheetname[path] = list_format_ok
        else:
            pass

    return dic_filepath_sheetname, df_log


def get_base_compare(dic_sheet_base, dic_sheet_taiso):
    """
    get the list of base sheets that satisfy the comparison:
    taiso : sheets with correct format
    base : sheets with correct format and sheet name with name in the list of sheets taiso
    output of the function is 1 dic : key is the base file path, value is the list of base sheets that satisfy
    """
    dic_base_compare = {}
    set_sheet_taiso = set()
    # get list of satisfying sheets in base car
    for sheets in dic_sheet_taiso.values():
        set_sheet_taiso.update(sheets)

    for folder, sheets in dic_sheet_base.items():
        # Get the intersection between the sheets list in dic_sheet_base and dic_sheet_taiso
        common_sheets = list(set(sheets) & set_sheet_taiso)
        dic_base_compare[folder] = common_sheets

    return dic_base_compare


def get_df_combine(flag ,dic_combine):
    """ If it is a taiso car:
    check the rows in the app columns
    If there is no cell with a number: set the "note" column to 0
    If there is at least 1 cell with a number: set the "note" column to 1

    Merge dfs of the same lot into 1 large df
    """    
    dic_dfs = {}
    if dic_combine == {}:
        pass
    else:
        for file_path, sheets in dic_combine.items():
            for sheet in sheets:
                df = pd.read_excel(file_path, sheet_name=sheet, header=18).fillna('')
                if flag == "taiso":
                    df['note'] = df.iloc[:, 5:135].apply(lambda row: 1 if row.apply(lambda x: isinstance(x, (int, float))).any() else 0, axis=1)
                else:
                    pass
                if sheet not in dic_dfs:
                    dic_dfs[sheet] = df  # If sheet does not exist, create it
                else:
                    dic_dfs[sheet] = pd.concat([dic_dfs[sheet], df], ignore_index=True)  # Merge DataFrame into 1 lot
    return dic_dfs


def check_trigger(file_json_trigger, df_lot):
    
    with open(file_json_trigger, 'r', encoding='utf-8') as file:
        data = json.load(file)
    records = []
    if data=={}:
        merged_df = df_lot
        merged_df = df_lot.drop(columns=['status_temp'])
        merged_df['status'] = 0
    else:
        for key, values in data.items():
            index_ = key.rfind('_')
            name_file = key[0:index_]
            for value in values:
                records.append({'ファイル名': str(name_file).lower(), '実験_json': value})

        df_json = pd.DataFrame(records)
        df_json["flag"] = "delete"
        df_json['jikken_df_youbohyo'] = df_json['実験_json'].apply(data_normalization)
        df_json['ファイル名_'] = df_json['ファイル名'].apply(data_normalization)
        df_json['jikken_df_youbohyo'] = df_json['jikken_df_youbohyo'].str.lower()

        # df_youbohyo = pd.read_excel(file_compare_path, sheet_name=name_ws, header=18)
        df_lot['jikken_df_youbohyo'] = df_lot['jikken'].apply(data_normalization)
        df_lot['ファイル名_'] = df_lot['ファイル名'].apply(data_normalization)

        df_lot['ファイル名_'] = df_lot['ファイル名_'].str.lower()
        df_lot['jikken_df_youbohyo'] = df_lot['jikken_df_youbohyo'].str.lower()

        merged_df = pd.merge(df_lot , df_json, on=["ファイル名_", "jikken_df_youbohyo"], how='left')
        columns_to_drop = ['jikken_df_youbohyo', 'ファイル名_', 'ファイル名_y', '実験_json']
        merged_df = merged_df.drop(columns=columns_to_drop)

        merged_df.reset_index(drop=True, inplace=True)
        # merged_df['status'] = np.where((merged_df['flag'] == 'delete') & (merged_df['status_temp'] == 1), 1, 0)
        merged_df['status'] = np.where((merged_df['flag'] == 'delete') & (merged_df['status_temp'] == 1) & (merged_df['note'] == 1), 1, 0)
        
        merged_df = merged_df.drop(columns=['status_temp','flag'])

    return (merged_df)


def compare_lot(dic_df_taiso, dic_df_base, link_folder_output):
    """
    Compare with 4 conditions:
    1. "note" column has flag 1: that is, in the row at the app column position, there is at least 1 numeric value
    2. file name, jikken item is not empty
    3. in the taiso car exists jikken item and corresponding file name in the base
    4. jikken item and this file name are in the trigger file
    Satisfy 4 conditions: that row will have status 1

    """
    file_json_trigger = os.path.join(link_folder_output, "match_jikken_trigger.json")
    merged_dic = {}
    df_taiso_combine = {}
    # If lot in taiso exists in base
    for lot, df_taiso in dic_df_taiso.items():  # check each lot in taiso
        if lot in dic_df_base:  # if lot exists in base
            df_base = dic_df_base[lot]  # get df in sheet lot_base

            new_columns = {col: f"{col}_base" for col in df_base.columns}
            # print("new_columns: ",new_columns)
            df_base.rename(columns=new_columns,
                           inplace=True)  # edit column names in df_base , add "_base" character after name
            #--------------
        
            df_taiso.columns.values[161] = "file_name_check"
            df_taiso.columns.values[160] = "jikken"
            df_base.columns.values[161] = "file_name_check"
            df_base.columns.values[160] = "jikken"
            #--------------
            df_base['status_temp'] = 1  # add 1 column check , fill 1 in all rows
            # Merge df taiso and df base after processing, horizontally (left_join : df_taiso on the left)
            # explanation left join : get all rows of taiso
            # if the value in 2 columns 'ファイル名','実験' of taiso = base then the columns with the character "_base" and the column "check" have the same value as df_base
            # If the value in 2 columns 'ファイル名','実験' of taiso != base then the columns with the character "_base" and the column "check" have the value NaN
            merged_df = pd.merge(df_taiso, dic_df_base[lot], on=["file_name_check", "jikken"], how='left')
            merged_df = merged_df.fillna(0)
            merged_df = merged_df.loc[:, ~merged_df.columns.str.contains('_base')]
            merged_df = check_trigger(file_json_trigger, merged_df)
            merged_dic[lot] = merged_df

            merged_df['sheet'] = lot
            merged_df = merged_df.reset_index(drop=True)
            df_taiso_combine[lot] = merged_df

    file_output_youbou = os.path.join(link_folder_output, 'compare_配車要望表.xlsx')
    parts = link_folder_output.split('\\') if '\\' in link_folder_output else link_folder_output.split('/')
    option_taiso = parts[-2]
    folder_car_taiso=os.path.join(BASE_DIR_OUTPUTS, option_taiso)
    youbou_file = os.path.join(folder_car_taiso, "Car配車要望表.xlsx")
    shutil.copy(youbou_file, file_output_youbou)
    workbook = openpyxl.load_workbook(file_output_youbou)

    sheets_to_keep = merged_dic.keys()
    sheets_to_remove = [sheet for sheet in workbook.sheetnames if sheet not in sheets_to_keep]
    for sheet in sheets_to_remove:
        std = workbook[sheet]
        workbook.remove(std)

    for lot, df_list in merged_dic.items():
        sheet = workbook[lot]
        sheet.cell(row=19, column=163, value="status")
        for r_idx, row in df_list.iterrows():
            sheet.cell(row=r_idx + 20, column=163, value=row["status"])

    workbook.save(file_output_youbou)
    workbook.close()

    return df_taiso_combine


def compare_youbouhyo(dic_base_compare, dic_sheet_taiso, link_folder_output):
    """
    compare and fill in 1 or 0 in the file compare_配車要望表.xlsx
    """

    # merge df (same lot) of base cars
    dic_df_base = get_df_combine("base" ,dic_base_compare)

    if dic_df_base == {}:
        pass
    else:
        # Loop through each DataFrame in dic_df_base
        for lot, df in dic_df_base.items():
            
            df.columns.values[161] = "file_name_check"
            df.columns.values[160] = "jikken"
    
            # delete rows in column "実験" and column "ファイル名" to leave blank
            df = df[(df["jikken"].notna()) & (df["jikken"] != '') & (df["file_name_check"].notna()) & (df["file_name_check"] != '')]
            # delete duplicate rows
            df = df.drop_duplicates(subset=["jikken", "file_name_check"])
            dic_df_base[lot] = df

    # merge df (same lot) of taiso cars (1 car)
    dic_df_taiso = get_df_combine("taiso", dic_sheet_taiso)
    # compare and fill in 1 or 0
    # start_time = time.time()
    dic_compare = compare_lot(dic_df_taiso, dic_df_base, link_folder_output)
    # end_time = time.time()
    # print(f"Function compare_lot took {end_time - start_time:.2f} seconds.")
    return dic_compare


def check_format_kanren(file_search, sheet_kanren, power_train):
    """
    1. Find the location of power_train in the kanren file
    If found, the jikken entry is searched only in the power_train area
    If not found, search for the jikken entry in the entire sheet
    2. Check if row 7 is the row containing the jikken entry = check_1
    3. Is row 29 column B == "Performance Targets" ? = check_2
    2. Is row 29 column D == "Vehicle Targets" ? = check_3
    2. Is row 29 column G == "Component Targets" ? = check_4
    """
    start_power_train = 0
    end_power_train = 0
    check_format_kanren = False

    # Tìm sheet có tên chứa "sheet_kanren"
    df = pd.DataFrame()
    xls = pd.ExcelFile(file_search)
    for name_sheet in xls.sheet_names:
        if sheet_kanren in name_sheet:
            df = pd.read_excel(file_search, sheet_name=name_sheet, engine='calamine')
            break

    if df.empty:
        pass
    else:
        check_1 = False
        check_2 = False
        check_3 = False
        check_4 = False
        # -----------------------------get power_train position to find 実験 (start_power_train,end_power_train )-----------------------------------
        power_train_upper = power_train.upper()
        # check if sheet has power_train : if not then search for jiken from the beginning to the last column with data , if yes then only search in powertrain area
        if power_train_upper in df.columns.str.upper().tolist():
            column_index = df.columns.str.upper().tolist().index(power_train_upper)
            matching_columns_zone = df.columns[df.iloc[0].apply(lambda x: str(x).lower()) == '配車使用欄'].tolist()
            matching_columns_zone = [df.columns.get_loc(col) for col in matching_columns_zone]
            start_power_train = column_index - 1
            if start_power_train in matching_columns_zone:
                index = matching_columns_zone.index(start_power_train)
                if index + 1 < len(matching_columns_zone):
                    end_power_train = matching_columns_zone[index + 1]
                else:
                    end_power_train_col = df.columns[df.notna().any()].tolist()[-1]
                    end_power_train = df.columns.get_loc(end_power_train_col)

                data_row_7 = df.iloc[5, start_power_train]
                row_7_check = "初期確認実験項目\n(業界毎に変更・追加の上入力ください)"
                data_row_7 = data_normalization(data_row_7)
                row_7_check = data_normalization(row_7_check)
                check_1 = data_row_7 == row_7_check
            else:
                end_power_train_col = df.columns[df.notna().any()].tolist()[-1]
                end_power_train = df.columns.get_loc(end_power_train_col)

                data_row_7 = df.iloc[5, start_power_train]
                row_7_check = "初期確認実験項目\n(業界毎に変更・追加の上入力ください)"
                data_row_7 = data_normalization(data_row_7)
                row_7_check = data_normalization(row_7_check)
                check_1 = data_row_7 == row_7_check

        else:
            matching_columns_zone = df.columns[df.iloc[0].apply(lambda x: str(x).lower()) == '配車使用欄'].tolist()
            matching_columns_zone = [df.columns.get_loc(col) for col in matching_columns_zone]
            start_power_train = matching_columns_zone[0]
            end_power_train_col = df.columns[df.notna().any()].tolist()[-1]
            end_power_train = df.columns.get_loc(end_power_train_col)

            data_row_7 = df.iloc[5, start_power_train]
            row_7_check = "初期確認実験項目\n(業界毎に変更・追加の上入力ください)"
            data_row_7 = data_normalization(data_row_7)
            row_7_check = data_normalization(row_7_check)
            check_1 = data_row_7 == row_7_check
        # ---------------------------------------------------------------
        # check if the format sheet is correct
        check_2 = df.iloc[27, 1] == "Performance Targets"  # Row 29, column B (index 28)
        check_3 = df.iloc[27, 3] == "Vehicle Targets"  # Row 29, column D (index 28)
        check_4 = df.iloc[27, 6] == "Component Targets"  # Row 29, column G (index 28)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~GHI LOG ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        message1=""
        message2=""
        message3=""
        message4=""
        if check_1==False:
            message1 = f"can't find 【初期確認実験項目\n(業界毎に変更・追加の上入力ください)】in row 7 sheet {name_sheet} file {file_search} ."

        if check_2==False:
            message2 = f"【Performance Targets】could not be found in row 29 column B sheet {name_sheet} file {file_search} . "

        if check_3==False:
            message3 = f"【Vehicle Targets】could not be found in row 29 column D sheet {name_sheet} file {file_search} . "

        if check_4==False:
            message4 = f"【Component Targets】could not be found in row 29 column G sheet {name_sheet} file {file_search} ."

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        if check_1 == True and check_2 == True and check_3 == True and check_4 == True:
            check_format_kanren = True
        else:
            check_format_kanren = False

    return check_format_kanren, start_power_train, end_power_train, name_sheet,message1,message2,message3,message4


def update_1_kanren(workbook, file_kanren, sheet, list_jikken, start_power_train, end_power_train, name_sheet,
                    ):
    """ Update 1 in row 29 at the column position where jikken item is found"""
    message_jikken=''
    row_7 = sheet[7]
    # list_jikken = [data_normalization(item) for item in list_jikken]
    for jikken in list_jikken:
        end_power_train = int(end_power_train)
        found_column = None
        jikken = data_normalization(jikken).lower()
        for col in range(start_power_train - 1, int(end_power_train)):
            if jikken == data_normalization(row_7[col - 1].value).lower():
                found_column = col
                break
        if found_column:
            sheet.cell(row=29, column=found_column, value=1)  # Enter 1 in the cell in row 29 of the found column
        else:
            message_jikken = message_jikken + f"The item {jikken} was not found in sheet {name_sheet} file {file_kanren} ."
    workbook.save(file_kanren)
    return message_jikken


def up_kanren(df_log_kanren,list_df_update, folder_data, link_folder_output, option_taiso):
    """
    1. get list of files with extension ".xlsx" or ".XLSX"
    2. dict_file_name has key is file name in list_file_name, but converted to lowercase, value is original file name unchanged.
    3. find file and enter 1 in karen found
    """
    parts = option_taiso.split("_")
    power_train = parts[1]
    list_file_name = [f for f in os.listdir(folder_data) if f.endswith('.xlsx') or f.endswith('.XLSX')]
    dict_file_name = {item.lower(): item for item in list_file_name}

    for df_file in list_df_update:
        df_file.reset_index(drop=True, inplace=True)
        file_name_update = df_file.iloc[0, 161]
        file_name_update = file_name_update.replace("関連表1", "関連表3")
        if ".xlsx" in file_name_update:
            index = file_name_update.index(".xlsx")
            file_name_update = file_name_update[:index + 5]

        sheet_update = df_file['sheet'].unique()

        # if os.path.exists(file_search):
        if file_name_update.lower() in dict_file_name.keys():
            file_search = os.path.join(folder_data, dict_file_name[file_name_update.lower()])
            destination_file = os.path.join(link_folder_output, "関連表③", dict_file_name[file_name_update.lower()])
            shutil.copy(file_search, destination_file)
            workbook = openpyxl.load_workbook(destination_file)

            for sheet_kanren in sheet_update:
                format_sheet_kanren, start_power_train, end_power_train, name_sheet ,message1,message2,message3,message4= check_format_kanren(file_search,
                                                                                                          sheet_kanren,
                                                                                                          power_train)

                if format_sheet_kanren == True:
                    sheet = workbook[name_sheet]
                    list_jikken = df_file.loc[df_file['sheet'] == sheet_kanren, 'jikken'].tolist()
                    message_jikken = update_1_kanren(workbook, destination_file, sheet, list_jikken, start_power_train, end_power_train, name_sheet)
                else:
                    continue

                new_row = {'file_name_check': destination_file , 'sheet': name_sheet, 'log' : message1 + "\n" + message2 + "\n" + message3 + "\n" + message4 + "\n" + message_jikken+ "\n" }
                df_log_kanren.loc[len(df_log_kanren)] = new_row
            workbook.close()
        else:
            pass
            new_row = {'file_name_check': file_name_update , 'sheet': name_sheet, '' : f"không tìm thấy file  trong folder data \n"}
            df_log_kanren.loc[len(df_log_kanren)] = new_row
    return df_log_kanren
    

def update_folder_kanren(df_taiso_combine, folder_data, link_folder_output, option_taiso):
    """
    1. Merge the df lot taiso that needs to be updated 1 into kanren into 1 df
    2. Delete rows in the column 'jikken', 'file_name_check' that are empty or null, nan and rows with Status other than 1
    3. Divide into small dfs, with each df being a kannren file that needs to be updated
    """
    column_check_kanren=["file_name_check","sheet","log"]
    df_log_kanren = pd.DataFrame(columns=column_check_kanren)

    if df_taiso_combine != {}:
        df_update = pd.concat(df_taiso_combine.values(), ignore_index=True)

        df_update = df_update[~(
                (df_update['jikken'].isnull() | (df_update['jikken'] == '')) |
                (df_update['file_name_check'].isnull() | (df_update['file_name_check'] == '')) | (df_update['status'] != 1)
        )]
        df_update = df_update.drop_duplicates(subset=["jikken", "file_name_check", 'sheet'])
        # split df into 1 list df_mini , each df_mini is 1 "ファイル名"
        list_df_update = [group for _, group in df_update.groupby('file_name_check')]
        df_log_kanren= up_kanren(df_log_kanren,list_df_update, folder_data, link_folder_output, option_taiso)
        write_log(link_folder_output, df_log_kanren, 'check_up_kanren')
    else:
        pass


def compare_base_taiso(list_option_base, option_taiso, link_folder_output):
    columns_sheet_check_youbou = ['file_name', 'Sheet', '関連ファイル名',"実験"]
    df_log = pd.DataFrame(columns=columns_sheet_check_youbou)
    # get the list of youbouhyo file paths of the bases and sheets of the youbouhyo file, checked for correct format
    # dic_sheet_base is a dic: the key is the file path, the value is the list of sheets in the correct format
    dic_sheet_base,df_log = check_sheet_youbouhyo(df_log,list_option_base)
    # get list of sheets in youbouhyo file of sheet taiso, checked correct format
    # dic_sheet_base is a dic: key is file path, value is list of sheets in correct format
    option_taiso_check = [option_taiso]
    dic_sheet_taiso,df_log = check_sheet_youbouhyo(df_log,option_taiso_check)
        
    # Get the list of base sheets to compare
    # dic_base_compare : Keep items in dic_sheet_base WHICH lot also exists in dic_sheet_taiso
    dic_base_compare = get_base_compare(dic_sheet_base, dic_sheet_taiso)
    write_log(link_folder_output, df_log, 'check_youbou')

    message = ""
    if dic_sheet_taiso != {} and dic_base_compare == {}:
        message = "Please check ベース file format again"
    elif dic_sheet_taiso == {} and dic_base_compare != {}:
        message = "Please check 対象 file format again"
    elif dic_sheet_taiso == {} and dic_base_compare == {}:
        message = "Please check ベース file and 対象 file format again"
    else:
        pass

    df_taiso_combine = {}
    if message == "":
        df_taiso_combine = compare_youbouhyo(dic_base_compare, dic_sheet_taiso, link_folder_output)
    else:
        pass
    
    return df_taiso_combine, message


def run_btn_inteligent_test(list_option_base, option_taiso):
    link_folder_output = get_link_folder_output(list_option_base, option_taiso)
    if link_folder_output == "":
        link_folder_output = create_folder_output_itest(list_option_base, option_taiso)

    folder_data = get_data_folder(option_taiso)
    create_output_log_and_kanren(option_taiso,link_folder_output)
    
    print("==========================================patern_reduce: vc_handle=========================================")
    err_text = patern_reduce(option_taiso, list_option_base, link_folder_output, "vc_handle")
    if err_text == "OK":
        # dic_taiso_combine là 1 dic : key : lot , value : df
        file_json_trigger = os.path.join(link_folder_output, "match_jikken_trigger.json")
        message = ''
        if os.path.exists(file_json_trigger) == False :
            message = 'match_jikken_trigger.json not found'
        else:
            dic_taiso_output_flag, message= compare_base_taiso(list_option_base, option_taiso, link_folder_output)
            if message == "":
                update_folder_kanren(dic_taiso_output_flag, folder_data, link_folder_output, option_taiso)
                message = 'Completed'
            else:
                pass
        print("==========================================patern_reduce: kanren3_handle=========================================")
        patern_reduce(option_taiso, list_option_base, link_folder_output, "kanren3_handle")
        return message
    else:
        message = err_text
        return message
