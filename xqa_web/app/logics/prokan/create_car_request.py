import pandas as pd


def create_car_request(data_cadics, data_kanrenhyo, car_number, lot, start_table3, end_table3, group):
    dic_address={"DS":[54,58,59,66],"DC":[54,58,59,73],"PFC":[74,78,79,90],"VC":[91,95,96,106],"PT1":[91,95,96,116],"PT2":[91,95,96,126]}
    list_dict=[]
    try:
        kca_proj = data_cadics.iat[6,dic_address[lot][0]]
    except:
        return list_dict
    evaluation = data_cadics.iat[6,dic_address[lot][1]]
    id_mail = data_cadics.iat[6,dic_address[lot][2]]
    col_comment=dic_address[lot][3]
    file_name = data_kanrenhyo.iat[0,13]

    try:
        file_name=file_name[:file_name.index(")")+1]
    except:
        None
    
    for col in range(start_table3, end_table3):
        sum_time = data_kanrenhyo.iat[19,col]
        if sum_time > 0:
            cadic_pick=data_kanrenhyo.loc[(data_kanrenhyo[col]=="〇") | (data_kanrenhyo[col]=="○")]
            list_cadics=cadic_pick[0].tolist()
            data_frame=selected_car(data_cadics, list_cadics, car_number, col_comment)

            for row in range(len(data_frame)):
                dict_data={}
                dict_data[0]=file_name
                dict_data[1]=data_kanrenhyo.iat[1,col]
                dict_data[2]="初期確認"
                dict_data[3]=data_kanrenhyo.iat[2,col]
                dict_data[4]="2：トリム手配前"
                key_start=5
                for index in range(0,car_number):
                    value=str(data_frame.iat[row,index])
                    if "1" in value:
                        dict_data[key_start]=sum_time
                    if value=="*":
                        dict_data[key_start]="*"
                    key_start=key_start+1
                
                dict_data[136]=data_frame.iat[row,car_number]
                dict_data[150]=id_mail
                dict_data[151]=kca_proj+str(evaluation)
                dict_data[152]=id_mail
                dict_data[153]=kca_proj+str(evaluation)
                dict_data[154]="NML"
                dict_data[155]="NML"
                dict_data[156] = str(data_kanrenhyo.iat[26, col]).upper()
                if str(data_kanrenhyo.iat[6, col])=='nan':
                    dict_data[160] = ""
                else:
                    dict_data[160] = str(data_kanrenhyo.iat[6, col]).upper()
                dict_data[161] = group.lower()
                list_dict.append(dict_data)
    return list_dict


def selected_car(data_cadics,list_cadics,car_number,col_comment):
    data_frame=pd.DataFrame()
    for cadic in list_cadics:
        cadic=str(cadic)
        filtered_df = data_cadics[(data_cadics[1].str.startswith(cadic,na=False))]
        data_frame=pd.concat([data_frame, filtered_df], ignore_index=True)
    
    if len(data_frame)!=0:
        result=data_frame[[col_comment,*range(129,129+car_number)]]
        result.reset_index(drop=True)
        result=result.drop_duplicates()
        result = result.reset_index(drop=True)
        frame_pick_car=result[[*range(129,129+car_number)]]
        dict_pick_car=frame_pick_car.to_dict(orient='records')
        frame_pick_car_dup=frame_pick_car.drop_duplicates()
        dict_pick_car_dup=frame_pick_car_dup.to_dict(orient='records')

        for item in dict_pick_car_dup:
            string_comment=""
            for index in range(len(dict_pick_car)):
                if dict_pick_car[index]==item:
                    comment=result.iloc[index][col_comment]
                    if isinstance(comment,str)==True:
                        if len(string_comment)==0:
                            string_comment=comment
                        else:
                            string_comment=string_comment+", "+comment
            comment=filter_comment(string_comment)
            item[col_comment]=comment
        frame_pick_car_dup=pd.DataFrame(dict_pick_car_dup)
        return frame_pick_car_dup
    else:
        return data_frame


def filter_comment(string_comment):
    list_option=[]
    list_split=string_comment.split(",")
    for item in list_split:
        list_split2=item.split(":")
        if len(list_split2)>2:
            option=str(list_split2[0]).strip()
            if option not in list_option:
                list_option.append(option)
    
    comment=str(list_option)
    for sym in ["[",']',"'"]:
        comment=comment.replace(sym,"")
    return comment
    
