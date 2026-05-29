import pandas as pd


def create_file_request_list(data_cadics, data_kanrenhyo,lot,car_number,start_table3,end_table3,name_file):
    dict_type_block={
        "t": [], 
        "w": [], 
        "c": []
    }
    place = []
    dic_address={"DPFC": [54, 58, 59, 66], "DS": [54, 58, 59, 73], "DC": [54, 58, 59, 80], "PFC": [81, 85, 86, 97], 
                 "VC": [98, 102, 103, 113], "PT1": [98, 102, 103, 123], "PT2": [98, 102, 103, 133]}
    try:
        kca_proj = data_cadics.iat[6, dic_address[lot][0]]
    except:
        return {}, dict_type_block, []
    
    evaluation = data_cadics.iat[6, dic_address[lot][1]]

    for col in range(start_table3, end_table3):
        sum_time = data_kanrenhyo.iat[24, col]
        block_full = data_kanrenhyo.iat[25, col]
        type_= data_kanrenhyo.iat[20, col]

        if not sum_time:
            continue

        type_ = str(type_).lower()
        if sum_time > 0 and type_ in dict_type_block.keys() and isinstance(block_full, str) == True:
            cadic_pick = data_kanrenhyo.loc[(data_kanrenhyo[col]=="〇") | (data_kanrenhyo[col]=="○")]
            list_cadics = cadic_pick[0].tolist()
            if len(list_cadics) > 0:
                for cadic in list_cadics:
                    filtered_df = data_cadics[(data_cadics[1].str.startswith(cadic, na=False))]
                    if len(filtered_df) > 0:
                        place_=data_kanrenhyo.iat[26,col]
                        dict_type_block[type_].append(block_full)
                        place.append(place_)

    place=list(set(place))
    dict_type_block["t"]=list(set(dict_type_block["t"]))
    dict_type_block["w"]=list(set(dict_type_block["w"]))
    dict_type_block["c"]=list(set(dict_type_block["c"]))

    dict_occupancy=find_occupancy(dict_type_block)
    list_config=[]
    row = data_cadics.iloc[0]
    cols = row[row == "Market"].index.tolist()
    start_index = cols[0] + 1
    for col in range(start_index, start_index + car_number):
        filtered_df = data_cadics.loc[data_cadics[col].astype(str).str.contains("1", na=False)]
        if len(filtered_df) > 0:
            list_config.append(data_cadics.iat[5,col])

    config_full=str(list_config)
    place_full=str(place).upper()
    for sym in ["'","[","]"]:
        config_full=config_full.replace(sym,"")
        place_full=place_full.replace(sym,"")

    car_t = len(list_config)*len(dict_occupancy["t"])
    car_w = len(list_config)*len(dict_occupancy["w"])
    car_c = len(list_config)*len(dict_occupancy["c"])

    if (car_t + car_w + car_c) == 0:
        return {}, dict_type_block, []
    else:
        dic_return={0:str(kca_proj).upper()+str(evaluation).upper(),1:"",2:"",3:car_t,4:car_w,5:car_c,6:"NML",7:place_full,8:"",9:config_full,10:name_file}
        return dic_return, dict_occupancy, list_config

def find_occupancy(dict_type_block):
    dict_return={}
    tmp_list = ["1","2","3","4","5","6","7","8"]

    for type_ in dict_type_block.keys():
        dic_sub={}
        for number in tmp_list:
            for item in dict_type_block[type_]:
                location=str(item).find(number)
                if location!=-1 and location!=len(str(item))-1:
                    while item[location] in tmp_list and location < len(item)-2:               #notice -1-2
                        location=location+1
                    block=item[location:]
                    if number not in dic_sub.keys():
                        dic_sub[number]=[block]
                    elif block not in dic_sub[number] :
                        dic_sub[number].append(block)
               
        dict_return[type_]=dic_sub

    return dict_return
