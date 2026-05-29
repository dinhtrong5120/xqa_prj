import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import PatternFill
import os
import re
import unicodedata
import json

def check_aabb_hyo_veh_app(df_AABB, veh_name):
        if veh_name in df_AABB.columns:
            return True
        else:
            return False

def check_input(link_folder_vc, link_master_VC, link_aabb, name_taiso, list_name_base):
    # check exist file 
    flg_check = False
    list_err = []
    
    if os.path.exists(link_folder_vc) :
        pass
    else:
        list_err.append("Input missing folder VC簡素化要件表")
    
    # if os.path.exists(link_master_VC):
    #     pass
    # else:
    #     list_err.append("Input missing file VC要件表_Master.xlsx")
    
    if os.path.exists(link_aabb):
        df_AABB = pd.read_excel(link_aabb, header=5, sheet_name=None, engine='calamine')
        for sheet_name, df in df_AABB.items():
            if sheet_name == "Family COCA LIST":
                flg_check = True
                try:
                    df_AABB_commodity = df["Commodity"]
                    df_AABB_partname = df["Part name"]
                    df_AABB_bodytype = df["BRAND⇒"]
                except:
                    flg_check = False
            else:
                pass
            
        df_AABB = pd.read_excel(link_aabb, header=4, sheet_name="Family COCA LIST", engine='calamine')
        df_AABB.fillna('', inplace=True)
        
        aabb_taiso_check = check_aabb_hyo_veh_app(df_AABB, name_taiso)
        if not aabb_taiso_check:
            list_err.append(f"Can't find app in row 6 or {name_taiso} in AABB表.xlsx")
            
        for name_base in list_name_base:
            aabb_base_check = check_aabb_hyo_veh_app(df_AABB, name_base)
            if not aabb_base_check:
                list_err.append(f"Can't find app in row 6 or {name_base} in AABB表.xlsx")
        
    else:
        list_err.append("Input missing file AABB表.xlsx")

    if flg_check:
        pass
    else:
        list_err.append("Format of AABB表.xlsx is wrong ! ")
    err_txt = ""
    if len(list_err)>0:
        err_txt = "Please check the input according to the messages below: "   
        for err in list_err:
            err_txt = f"{err_txt}\n{str(err).strip()}"
    return err_txt

############################################ COMMON FUNCTION ##################################################
def convert_part_AABB(df_AABB):
    # df_AABB_commodity = df_AABB["Commodity"]
    df_AABB_partname = df_AABB["Part name"]
    df_AABB_bodytype = df_AABB["BRAND⇒"]
            # Create AABB_part dict : (index : 1 -> max) 
            # {
            #     "index": {
            #         'commodity': ,
            #         'partname': ,
            #         'bodytype':
            #     }
            # }
    dict_part_AABB = {}
    for i in df_AABB_partname.index:
        dict_part_AABB[i] = dict()
        # dict_part_AABB[i]["commodity"] = str(df_AABB_commodity.loc[i]).strip()
        dict_part_AABB[i]["partname"] = str(df_AABB_partname.loc[i]).strip()
        dict_part_AABB[i]["bodytype"] = str(df_AABB_bodytype.loc[i]).strip()
    return dict_part_AABB

# def covert_vehInfo_AABB(df_AABB, veh_name). Use to get and covert data vehicle info from AABB to a Dict
def convert_vehInfo_AABB(df_AABB, veh_name):
    dict_AABB = {}
    for cl in df_AABB.columns:
        next_column_data = pd.Series()
        key = ""
        column_data = pd.Series()
        if veh_name in cl:
            col_index = df_AABB.columns.get_loc(cl)
            # get next column data contain buban name
            if col_index + 1 < len(df_AABB.columns):
                column_data = df_AABB.iloc[1:, col_index]
                next_column_data = df_AABB.iloc[:, col_index + 1]
                key = next_column_data.iloc[0]
            else:
                print("Cột 'A' là cột cuối cùng, không có cột tiếp theo.")
        column_data = column_data.to_dict()
        if key != "":
            dict_AABB[key]= dict()
            dict_AABB[key]= column_data

    return dict_AABB

def convert_df_to_str(data):
        data_int = [int(item) if isinstance(item, float) else item for item in data]
        data_str = [str(item) if isinstance(item, int) else item for item in data_int]
        return data_str

# def convert_data_youbohyo(df_raw, sheet_name, app). Use to get and covert data vehicle info from Youbouhyo file to a Dict
def convert_data_youbohyo(df_raw, sheet_name, app):
    dict_all_data = dict()
    gr_column_name = None
    try:
        app = int(float(app))
        app = str(app)
    except Exception as e:
        print("convert app err: ", e)
        
    df = df_raw[sheet_name]
    df.fillna('-', inplace=True)
    header = df.iloc[17].values
    for name_header in header:
        if "関連ファイル名" in name_header:
            gr_column_name = name_header
            break
    if gr_column_name == None:
        return dict_all_data
    
    # cl_gr = np.where(header == "ファイル名")[0]
    cl_gr = np.where(header == gr_column_name)[0]
    cl_jikken = np.where(header == "実験")[0]

    list_gr_raw = (df.iloc[:, cl_gr].values)
    list_gr_raw = convert_df_to_str(list_gr_raw)
    
    list_jikken_raw = (df.iloc[:, cl_jikken].values)
    list_jikken_raw = convert_df_to_str(list_jikken_raw)
    
    header_app = df.iloc[3].values
    header_app = convert_df_to_str(header_app)
    try:
        cl_app = header_app.index(app)
    except:
        cl_app = 0
    list_data_app = (df.iloc[:, cl_app].values)
    list_data_app = convert_df_to_str(list_data_app)
    # From list_gr , list_data, list_jikken create dict_all 
    dict_all_data = dict()
    dict_all_data = {item[0]: dict() for item in list_gr_raw}
    for cnt in range(0, len(list_gr_raw)): 
        if list_gr_raw[cnt][0] == "-" or list_jikken_raw[cnt][0] == "-" or list_data_app[cnt][0]== "-":
            pass
        else:
            dict_all_data[list_gr_raw[cnt][0]][list_jikken_raw[cnt][0]] = list_data_app[cnt][0]
        
    return dict_all_data


def find_position(sheet, str_find, start_row, end_row, start_col, end_col, method):
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
    # Initialize a variable to store the position
    position = None

    if end_col is None:
        end_col = sheet.max_column
        
    # Iterate through the specified rows and columns in the sheet
    for row in sheet.iter_rows(min_row=start_row, max_row=end_row, min_col=start_col, max_col=end_col):
        for cell in row:
            if method == "same":
                if data_normalization(str(cell.value)) == data_normalization(str_find):  # Check if the cell contains the value
                    position = (cell.row, cell.column)  # Store the position (row, column)
                    break  # Exit the loop if found
            else:
                if data_normalization(str_find) in data_normalization(str(cell.value)):  # Check if the cell contains the value
                    position = (cell.row, cell.column)  # Store the position (row, column)
                    break  # Exit the loop if found
                
    if position:
        return position
    else:
        return None


def reduce_day(app_taiso, link_taiso, app_base, link_base, dict_reduce_day):
    # File car...
    df_full_taiso = pd.read_excel(link_taiso, sheet_name=None, engine='calamine')
    df_full_base = pd.read_excel(link_base, sheet_name=None, engine='calamine')
    for sheet_name in df_full_taiso:
        dict_all_taiso = convert_data_youbohyo(df_full_taiso, sheet_name, app_taiso)
        dict_all_base = convert_data_youbohyo(df_full_base, sheet_name, app_base)
        
        for item in dict_all_taiso:
            if not item in dict_reduce_day:
                dict_reduce_day[item] = dict()
            else:
                pass
            cnt = 0
            for key in dict_all_taiso[item].keys():
                if item in dict_all_base and key in dict_all_base[item]:
                    key_jikken = sheet_name + "*-*" + key
                    dict_reduce_day[item][key_jikken] = cnt
                    cnt += 1

    return dict_reduce_day 


############################################ CHANGE KANREN HYOU 3 ##################################################
def change_number_day(namefile, powertrain, list_jikken_komoku, workbook, link_folder_kanren3_changed):
    flg_change = False
    for jikken in list_jikken_komoku:
        arr_lot_jikken = str(jikken).split("*-*")
        lot = str(arr_lot_jikken[0])
        sheet_name = "関連表" + lot
        jikken_komoku = str(arr_lot_jikken[1])
        sheet = workbook[sheet_name]
        position_powertrain = find_position(sheet, powertrain, 1, 1, 1, None, "contain")
        if position_powertrain:
            # powertrain_row = position_powertrain[0]
            powertrain_cl = position_powertrain[1]
            # position_jikken_title = find_position(sheet, "初期確認実験項目", 1, None, powertrain_cl-1, powertrain_cl, "contain")
            # position_day_sum = find_position(sheet, "車両必要日数（日台）", 1, None, powertrain_cl-1, powertrain_cl, "same")
            position_powertrain_next = find_position(sheet, "原単位表", 1, 1, powertrain_cl+1, None, "contain")
            start_row_jikken = 7
            end_row_jikken = 7
            start_cl_jikken = position_powertrain[1]
            if position_powertrain_next:
                end_cl_jikken = position_powertrain_next[1]
            else:
                end_cl_jikken = None
            position_jikken = find_position(sheet, jikken_komoku, start_row_jikken, end_row_jikken, start_cl_jikken, end_cl_jikken, "same")
        else:
            position_jikken = find_position(sheet, jikken_komoku, 7, 7, 5, None, "same")
       
        if position_jikken: 
            sheet.cell(row= 20, column= position_jikken[1]).value = "0"
            blueFill = PatternFill(start_color='00FFFF',
                        end_color='00FFFF',
                        fill_type='solid')
            sheet.cell(row= 20, column= position_jikken[1]).fill = blueFill
            flg_change = True

    if flg_change:
        link_save = os.path.join(link_folder_kanren3_changed, namefile)
        workbook.save(link_save)
        return "Change"
    else:
        return "Don't find jikken komomu"


def change_kanren_file(dict_reduce_day, link_folder_kanren3_dont_change, link_folder_kanren3_changed, powertrain):
    # dict_file_name = dict()
    # for file_name in os.listdir(link_kanren_folder):
    #     if os.path.isfile(os.path.join(link_kanren_folder, file_name)):
    #         # Using regular expression to find the substring
    #         matches = re.findall(r'_(.*?)_', file_name)
    #         dict_file_name[matches[0]] = file_name
    try: 
        for file in dict_reduce_day:
            # Pre name file before using
            namefile = str(file).strip().upper()
            namefile = namefile.replace("関連表1", "関連表3")
            namefile = namefile.replace(".XLSX", ".xlsx")
            if "NAN" in namefile:
                namefile = namefile.replace("NAN", "")
                
            if ".xlsx" in namefile:
                if len(dict_reduce_day[file]) != 0:
                    link_file_kanren_old = os.path.join(link_folder_kanren3_dont_change, namefile)
                    link_file_kanren_new = os.path.join(link_folder_kanren3_changed, namefile)
                    if os.path.exists(link_file_kanren_new):
                        workbook = openpyxl.load_workbook(link_file_kanren_new)
                        change_number_day(namefile, powertrain, dict_reduce_day[file], workbook, link_folder_kanren3_changed)
                    elif os.path.exists(link_file_kanren_old):
                        workbook = openpyxl.load_workbook(link_file_kanren_old)
                        change_number_day(namefile, powertrain, dict_reduce_day[file], workbook, link_folder_kanren3_changed)
                    else:
                        pass
                    workbook = None
                else:
                    pass
            else :
                pass
        return "OK"
    except:
        return "NG"
