import os
import pandas as pd
import re
import shutil
import openpyxl
import unicodedata
from xqa_web_tvso.app.logics.itest.patern_reduce import *
from xqa_web_tvso.app.setting import BASE_DIR_OUTPUTS, BASE_DIR_DATAS


def data_normalization(data):
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
        mở folder output taiso , tìm xem đã tồn tại output itest của những con base đang được chọ trên giao diện chưa :
        + ) tên output: 'itest_compare_base1' + '_compare_base2' +.....
        do đó trong tên file có "_compare_" = số lượng base được chọn VÀ tên các con base nằm trong tên folder output itest

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
    folder_name = "itest_compare_" + "_compare_".join(list_option_base)
    folder_output_itest_path = os.path.join(BASE_DIR_OUTPUTS, option_taiso, folder_name)
    os.makedirs(folder_output_itest_path)
    return folder_output_itest_path


def get_data_folder(option_taiso):
    car_name_taiso = option_taiso.split('_')[0]
    folder_data = os.path.join(BASE_DIR_DATAS, car_name_taiso)
    return folder_data


def create_output_log_and_kanren(option_taiso,folder_output_itest):
    """
        kiểm tra có file log chưa , nếu chưa có thì tạo
        kiểm tra folder "関連表③" có chưa , nếu chưa có thì tạo , nếu có rồi thì xóa và tạo folder "関連表③" mới
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
        Kiểm tra xem có file youbouhyo có cột "ファイル名" và cột "実験" nếu có thêm tên sheet vào list các sheet base để so sánh
        nếu không có thì ghi log là sheet... trong file base ... sai format
    """
    df_file = pd.read_excel(xls, sheet_name=sheet_name)

    column_file_name = "関連ファイル名"
    column_jikken= "実験"
    if len(df_file.columns) < 161 :
        new_row = {'file_name': youbouhyo_path , 'Sheet': sheet_name, '関連ファイル名' : "×", "実験": "×"}
        df_log.loc[len(df_log)] = new_row
    else:
        if data_normalization(df_file.iloc[17, 151]) == data_normalization(column_file_name):
            if data_normalization(df_file.iloc[17, 160]) == data_normalization(column_jikken):
                format_ok.append(sheet_name)
                new_row = {'file_name': youbouhyo_path , 'Sheet': sheet_name, '関連ファイル名' : "〇", "実験": "〇"}
                df_log.loc[len(df_log)] = new_row

        if data_normalization(df_file.iloc[17, 151]) != data_normalization(column_file_name):
            if data_normalization(df_file.iloc[17, 160]) == data_normalization(column_jikken):
                new_row = {'file_name': youbouhyo_path , 'Sheet': sheet_name, '関連ファイル名' : "×", "実験": "〇"}
                df_log.loc[len(df_log)] = new_row

        if data_normalization(df_file.iloc[17, 151]) == data_normalization(column_file_name):
            if data_normalization(df_file.iloc[17, 160]) != data_normalization(column_jikken):
                new_row = {'file_name': youbouhyo_path , 'Sheet': sheet_name, '関連ファイル名' : "〇", "実験": "×"}
                df_log.loc[len(df_log)] = new_row

        if data_normalization(df_file.iloc[17, 151]) != data_normalization(column_file_name):
            if data_normalization(df_file.iloc[17, 160]) != data_normalization(column_jikken):
                new_row = {'file_name': youbouhyo_path , 'Sheet': sheet_name, '関連ファイル名' : "×", "実験": "×"}
                df_log.loc[len(df_log)] = new_row
    return format_ok, df_log


def check_sheet_youbouhyo(df_log,list_option):
    """
        youbouhyo_path có đường dẫn mặc định "./learn_streamlit/app/outputs/base_car/Car配車要望表.xlsx
        check format từng file , từng sheet trong file .
        kết quả check được là 1 dic : có key là đường dẫn file , value là list các sheet đúng format
    """

    youbouhyo_name = "Car配車要望表.xlsx"
    # lấy được list path youbouhyo của các con xe trong list_option
    list_youbouhyo_path = [os.path.join(BASE_DIR_OUTPUTS, folder_name, youbouhyo_name) for folder_name in list_option]
    dic_filepath_sheetname = {}  # 1 dic

    for path in list_youbouhyo_path:
        if os.path.exists(path):
            xls = pd.ExcelFile(path)
            # df_inf_car = pd.read_excel (xls , skiprows=0 , nrows=18)
            list_format_ok = []
            for sheet_name in xls.sheet_names:  # check format từng sheet
                list_format_ok, df_log = check_format_youbouhyo(df_log,list_format_ok, path, xls, sheet_name)

            if list_format_ok == []:
                pass
            else:
                dic_filepath_sheetname[path] = list_format_ok
        else:
            pass
            # --------------------------Log
            # message = f"{path} không tồn tại \n"
            # write_log(link_folder_output, message)

    return dic_filepath_sheetname, df_log


def get_base_compare(dic_sheet_base, dic_sheet_taiso):
    """
        lấy danh sách các sheet base thỏa mãn sử dụng để so sánh :
        taiso : các sheet đúng format
        base  : các sheet đúng format và tên sheet có tên thuộc list sheet taiso
        output của function là 1 dic : key là đường dẫn file base , value là list các sheet base thỏa mãn
    """
    dic_base_compare = {}
    set_sheet_taiso = set()
    # lấy danh sách các sheet thỏa mãn trong base car
    for sheets in dic_sheet_taiso.values():
        set_sheet_taiso.update(sheets)

    for folder, sheets in dic_sheet_base.items():
        # Lấy giao giữa danh sách sheets trong dic_sheet_base và dic_sheet_taiso
        common_sheets = list(set(sheets) & set_sheet_taiso)
        dic_base_compare[folder] = common_sheets

    return dic_base_compare


def get_df_combine(flag ,dic_combine):
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
                    dic_dfs[sheet] = df  # Nếu sheet chưa có, khởi tạo
                else:
                    dic_dfs[sheet] = pd.concat([dic_dfs[sheet], df], ignore_index=True)  # Gộp DataFrame cung 1 lot
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
    file_json_trigger = os.path.join(link_folder_output, "match_jikken_trigger.json")
    merged_dic = {}
    df_taiso_combine = {}
    # Nếu lot trong taiso có tồn tại trong base
    for lot, df_taiso in dic_df_taiso.items():  # kiểm tra từng lot trong taiso
        if lot in dic_df_base:  # nếu lot tồn tại trong base
            df_base = dic_df_base[lot]  # lấy df trong sheet lot_base

            new_columns = {col: f"{col}_base" for col in df_base.columns}
            # print("new_columns: ",new_columns)
            df_base.rename(columns=new_columns,
                           inplace=True)  # sửa tên các cột trong df_base , thêm kí tự "_base" ở sau tên
            #--------------
        
            df_taiso.columns.values[151] = "file_name_check"
            df_taiso.columns.values[160] = "jikken"
            df_base.columns.values[151] = "file_name_check"
            df_base.columns.values[160] = "jikken"
            #--------------
            df_base['status_temp'] = 1  # thêm 1 cột check , điền "man_check" ở tất cả các hàng
            # Gộp df taiso và df base sau khi xử lí, theo chiều ngang (left_join : df_taiso bên trái)
            # giải thích left join : lấy toàn bộ các hàng của taiso
            # nếu giá trị trong 2 cột 'ファイル名','実験' của taiso = base thì các cột có kí tự "_base" và cột "check" có giá trị giống với df_base
            # Nếu giá trị trong 2 cột 'ファイル名','実験' của taiso != base thì các cột có kí tự "_base" và cột "check" có giá trị NaN
            merged_df = pd.merge(df_taiso, dic_df_base[lot], on=["file_name_check", "jikken"], how='left')
            merged_df = merged_df.fillna(0)
            merged_df = merged_df.loc[:, ~merged_df.columns.str.contains('_base')]
            merged_df = check_trigger(file_json_trigger, merged_df)
            merged_dic[lot] = merged_df

            merged_df['sheet'] = lot
            merged_df = merged_df.reset_index(drop=True)
            df_taiso_combine[lot] = merged_df
        else:
            pass

    file_output_youbou = os.path.join(link_folder_output, 'compare_配車要望表.xlsx')
    parts = link_folder_output.split('/')
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
        sheet.cell(row=19, column=162, value="status")
        for r_idx, row in df_list.iterrows():
            sheet.cell(row=r_idx + 20, column=162, value=row["status"])

    workbook.save(file_output_youbou)
    workbook.close()

    return df_taiso_combine


def compare_youbouhyo(dic_base_compare, dic_sheet_taiso, link_folder_output):
    """
        so sánh và điền 1 hoặc 0 vào file compare_配車要望表.xlsx
    """

    # gộp các df (cùng 1 lot) của các con xe base
    dic_df_base = get_df_combine("base" ,dic_base_compare)

    if dic_df_base == {}:
        pass
    else:
        # Lặp qua từng DataFrame trong dic_df_base
        for lot, df in dic_df_base.items():
            
            df.columns.values[151] = "file_name_check"
            df.columns.values[160] = "jikken"
    
            # xóa các hàng ở cột "実験" và cột "ファイル名" để trắng
            df = df[(df["jikken"].notna()) & (df["jikken"] != '') & (df["file_name_check"].notna()) & (df["file_name_check"] != '')]
            # xóa các hàng dupplicate
            df = df.drop_duplicates(subset=["jikken", "file_name_check"])
            dic_df_base[lot] = df

    # gộp các df (cùng 1 lot) của các xe taiso (1 xe)
    dic_df_taiso = get_df_combine("taiso", dic_sheet_taiso)
    # so sánh và điền 1 hoặc 0
    # start_time = time.time()
    dic_compare = compare_lot(dic_df_taiso, dic_df_base, link_folder_output)
    # end_time = time.time()
    # print(f"Function compare_lot took {end_time - start_time:.2f} seconds.")
    return dic_compare


def check_format_kanren(file_search, sheet_kanren, power_train):
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
        # -----------------------------lấy vị trí power_train để tìm 実験 (start_power_train,end_power_train )-----------------------------------
        power_train_upper = power_train.upper()
        # kiểm tra xem sheet có power_train không : nếu không thì tìm jiken từ đầu đến cột cuối cùng có dữ liệu , nếu có chỉ tìm trong khu vực powertrain
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
        # kiểm tra xem format sheet có đúngkhông
        check_2 = df.iloc[27, 1] == "Performance Targets"  # Hàng 29, cột B (chỉ số 28)
        check_3 = df.iloc[27, 3] == "Vehicle Targets"  # Hàng 29, cột D (chỉ số 28)
        check_4 = df.iloc[27, 6] == "Component Targets"  # Hàng 29, cột G (chỉ số 28)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~GHI LOG ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        message1=""
        message2=""
        message3=""
        message4=""
        if check_1==False:
            message1 = f"không tìm thấy 【初期確認実験項目\n(業界毎に変更・追加の上入力ください)】ở hàng 7 sheet {name_sheet} file {file_search} ."

        if check_2==False:
            message2 = f"không tìm thấy 【Performance Targets】ở hàng 29 cột B sheet {name_sheet} file {file_search} . "

        if check_3==False:
            message3 = f"không tìm thấy 【Vehicle Targets】ở hàng 29 cột D sheet {name_sheet} file {file_search} . "

        if check_4==False:
            message4 = f"không tìm thấy 【Component Targets】ở hàng 29 cột G sheet {name_sheet} file {file_search} ."

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        if check_1 == True and check_2 == True and check_3 == True and check_4 == True:
            check_format_kanren = True
        else:
            check_format_kanren = False

    return check_format_kanren, start_power_train, end_power_train, name_sheet,message1,message2,message3,message4


def update_1_kanren(workbook, file_kanren, sheet, list_jikken, start_power_train, end_power_train, name_sheet,
                    ):
    
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
            sheet.cell(row=29, column=found_column, value=1)  # Điền 1 vào ô ở hàng 29 của cột tìm thấy
        else:
            message_jikken = message_jikken + f"Mục {jikken} không tìm thấy trong sheet {name_sheet} file {file_kanren} ."
    workbook.save(file_kanren)
    return message_jikken


def up_kanren(df_log_kanren,list_df_update, folder_data, link_folder_output, option_taiso):
    parts = option_taiso.split("_")
    power_train = parts[1]
    list_file_name = [f for f in os.listdir(folder_data) if f.endswith('.xlsx') or f.endswith('.XLSX')]
    dict_file_name = {item.lower(): item for item in list_file_name}

    for df_file in list_df_update:
        df_file.reset_index(drop=True, inplace=True)
        file_name_update = df_file.iloc[0, 151]
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
    column_check_kanren=["file_name_check","sheet","log"]
    df_log_kanren = pd.DataFrame(columns=column_check_kanren)

    if df_taiso_combine != {}:
        df_update = pd.concat(df_taiso_combine.values(), ignore_index=True)

        df_update = df_update[~(
                (df_update['jikken'].isnull() | (df_update['jikken'] == '')) |
                (df_update['file_name_check'].isnull() | (df_update['file_name_check'] == '')) | (df_update['status'] != 1)
        )]
        df_update = df_update.drop_duplicates(subset=["jikken", "file_name_check", 'sheet'])
        # tách df thành 1 list df_mini , mỗi df_mini là 1 "ファイル名"
        list_df_update = [group for _, group in df_update.groupby('file_name_check')]
        df_log_kanren= up_kanren(df_log_kanren,list_df_update, folder_data, link_folder_output, option_taiso)
        write_log(link_folder_output, df_log_kanren, 'check_up_kanren')
    else:
        pass


def compare_base_taiso(list_option_base, option_taiso, link_folder_output):
    columns_sheet_check_youbou = ['file_name', 'Sheet', '関連ファイル名',"実験"]
    df_log = pd.DataFrame(columns=columns_sheet_check_youbou)
    # lấy danh sách đường dẫn file youbouhyo của các con base và các sheet của file youbouhyo,đã check đúng format
    # dic_sheet_base là 1 dic : có key là đường dẫn file , value là list các sheet đúng format
    dic_sheet_base,df_log = check_sheet_youbouhyo(df_log,list_option_base)
    # lấy danh sách sheet trong file youbouhyo của sheet taiso ,đã check đúng format
    # dic_sheet_base là 1 dic : có key là đường dẫn file , value là list các sheet đúng format
    option_taiso_check = [option_taiso]
    dic_sheet_taiso,df_log = check_sheet_youbouhyo(df_log,option_taiso_check)
    
    # Lấy danh sách các sheet base dùng để so sánh
    # dic_base_compare :  Giữ lại các item trong dic_sheet_base MÀ lot đó cũng tồn tại trong dic_sheet_taiso
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
        # so sánh youbouhyo
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
    else:
        pass
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
