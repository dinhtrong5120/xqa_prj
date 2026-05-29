import os
from xqa_web.app.setting import BASE_DIR_DATAS


def get_name_group(code):
    link_folder = os.path.join(BASE_DIR_DATAS, str(code).upper())
    if not os.path.exists(link_folder):
        return [], 'Project code not exist!'
    karen_files = [f for f in os.listdir(link_folder) if f.endswith('.xlsx')]
    chars_to_remove = ["(", ")", " ", "_"]
    list_group = []
    for file_name in karen_files:
        list_positions = []
        for i in range(len(file_name)):
            if file_name[i] == "_":
                list_positions.append(i)
        if len(list_positions) == 2:
            group = file_name[(max(list_positions) + 1):-5]
            for char in chars_to_remove:
                group = group.replace(char, "")
            list_group.append(group) if group not in list_group else None
    return list_group, 'Completed !'


def get_file_group(list_group, link_folder):
    list_file = []
    if not os.path.exists(link_folder):
        return []
    karen_files = [f for f in os.listdir(link_folder) if f.endswith('.xlsx')]
    for item in list_group:
        list_filename_contain_group = [file_name for file_name in karen_files if item in file_name and "関連表1"]
        list_file.extend(list_filename_contain_group)
    return list_file

# list_group_output = get_name_group(r"C:\Users\KNT21617\Downloads\OneDrive_1_1-30-2024\トライアル①②\New folder")
# print(list_group_output)
# end_list = get_file_group(['XR4', 'XXQ2'])
# print(end_list)
