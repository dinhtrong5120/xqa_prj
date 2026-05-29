import os
import sys 
import json as js
import copy
from xqa_web_tvso.app.logics.itest.sub_function import *
from xqa_web_tvso.app.logics.itest.match_unmatch_function import *
# from xqa_web_tvso.app.logics.itest.vcMaster_handle import *
from xqa_web_tvso.app.setting import BASE_DIR_DATAS, BASE_DIR_OUTPUTS


def patern_reduce(options_car2, options_car1, link_folder_output, run_option):
    # #################################################SETUP INPUT################################################
    link_aabb = os.path.join(BASE_DIR_DATAS, 'AABB表.xlsx')
    list_name_base = []
    list_link_base = []
    for option_car in options_car1:
        name_base = option_car.split('_')[0]
        link_base = os.path.join(BASE_DIR_OUTPUTS, option_car, 'Car配車要望表.xlsx')
        list_link_base.append(link_base)
        list_name_base.append(name_base)

    link_taiso = os.path.join(BASE_DIR_OUTPUTS, options_car2, 'Car配車要望表.xlsx')
    parts = options_car2.split("_")
    powertrain = parts[1]
    name_taiso = options_car2.split('_')[0]
    link_folder_vc = os.path.join(BASE_DIR_DATAS, name_taiso, 'VC簡素化要件表')
    link_folder_kanren3_dont_change = os.path.join(BASE_DIR_DATAS, name_taiso)
    link_folder_kanren3_changed = os.path.join(link_folder_output, "関連表③")
    link_master_VC = os.path.join(BASE_DIR_DATAS, name_taiso, 'VC要件表_Master.xlsx')
    
    ########################################### INPUT CHECK #################################################
    err_txt = ""
    err_txt = check_input(link_folder_vc, link_master_VC, link_aabb)
    if err_txt.strip() != "": 
        return err_txt
    else:   
        ########################################### WORK FOR AABB FILE #################################################

        df_AABB = pd.read_excel(link_aabb, header=5, sheet_name="Family COCA LIST", engine='calamine')
        # key 1 is Row 8 off excel
        dict_part_AABB = convert_part_AABB(df_AABB)

        df_AABB = pd.read_excel(link_aabb, header=4, sheet_name="Family COCA LIST", engine='calamine')
        # key 2 is Row 9 off excel 
        dict_taiso_AABB = convert_vehInfo_AABB(df_AABB, name_taiso)
        list_row_all = []
        list_row_same = []
        list_row_not_same = []
        flag_match = False
        dict_reduce_day = dict()
        for base_cnt in range(len(list_name_base)):
            dict_base_AABB = convert_vehInfo_AABB(df_AABB, list_name_base[base_cnt])
            for app_taiso in dict_taiso_AABB:
                for app_base in dict_base_AABB:
                    flag_match = False
                    for key in dict_taiso_AABB[app_taiso].keys():
                        row_result_is_same = key - 1
                        list_row_all.append(row_result_is_same)
                        if (str(dict_taiso_AABB[app_taiso][key])).strip() == (str(dict_base_AABB[app_base][key])).strip():
                            list_row_same.append(row_result_is_same)
                            flag_match = True
                        else:
                            pass
                    if flag_match:
                        app_base = str(app_base)
                        dict_reduce_day = reduce_day(app_taiso, link_taiso, app_base, list_link_base[base_cnt],
                                                    dict_reduce_day)
                    else:
                        pass
                    
        
        # Run Changr Match/Unmatch and fill color in VC file 
        list_row_same = list(set(list_row_same)) 
        list_row_not_same = [item for item in list_row_all if item not in list_row_same]
        list_row_not_same = list(set(list_row_not_same))
        # dict_part_AABB : {0: {'commodity': 'nan', 'partname': 'nan', 'bodytype': 'BODY TYPE⇒'}, 1: {'commodity': 'MIRROR', 'partname': 'INSIDE MIRROR', 'bodytype': 'nan'}}
        if run_option == "vc_handle":
            vc_folder_name = os.path.basename(link_folder_vc)
            link_folder_output_VC_file = os.path.join(link_folder_output, vc_folder_name)
            print("Run copy folder")
            copy_folder(link_folder_vc, link_folder_output_VC_file)

            print("Run change VC file ")
            change_VC_file(list_row_same, list_row_not_same, dict_part_AABB, link_folder_output_VC_file, link_folder_output)
            return "OK"
        
        if run_option == "kanren3_handle":
            # Run Change kanren hyou 3
            print("Run Change kanren hyou 3")
            link_match_jikken_trigger = os.path.join(link_folder_output, "match_jikken_trigger.json")
            with open(link_match_jikken_trigger, 'r', encoding='utf-8') as file:
                dict_jikken_match = js.load(file)
            dict_reduce_day_final = copy.deepcopy(dict_reduce_day)
            for kanren3_filename in dict_reduce_day.keys():
                first_underscore = kanren3_filename.find('_')
                last_underscore = kanren3_filename.rfind('_')
                grp_name = kanren3_filename[first_underscore + 1:last_underscore]
                flg_reduce_day = False
                for key in dict_jikken_match:
                    if str(grp_name).upper() in key:
                        flg_reduce_day = True
                        for jikken in dict_reduce_day[kanren3_filename].keys():
                            arr_lot_jikken = str(jikken).split("*-*")
                            jikken_komoku = str(arr_lot_jikken[1])
                            if jikken_komoku in dict_jikken_match[key]:
                                pass
                            else:
                                del dict_reduce_day_final[kanren3_filename][jikken]
                    else:
                        pass
                    
                if flg_reduce_day: 
                    pass
                else:
                    del dict_reduce_day_final[kanren3_filename]   
                    
            change_kanren_file(dict_reduce_day_final, link_folder_kanren3_dont_change, link_folder_kanren3_changed, powertrain)
        return "OK"
