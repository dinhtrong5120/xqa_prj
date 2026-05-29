
def create_wtc_spec_app(data_cadics,lot,dict_type_block,list_config,dict_config):
    dict_address_block={
        'body bench durability    case 1': 33, 
        'body bench durability    case 2': 34, 
        'seat mtg durability': 35, 
        'hook strength, durability, trailer hitch mtg': 36, 
        'fr/rr bottoming strength': 37, 
        'assist grip mtg strength': 38, 
        'wiper  mtg durability': 39, 
        'windshield glass strength': 40, 
        'inner rope hook mtg strength': 41, 
        'roof rail mtg strength': 42, 
        'body strength, durability, safety (rv)': 43, 
        'body strength, durability, safety (frame vehicle)': 44, 
        'a/t cont performance / strength / durability': 45, 
        'm/t cont performance / strength / durability': 46, 
        'pkb cont performance / strength / durability': 47, 
        'abc pedal  strength/ durability': 48, 'roof crash': 49, 'belt anchor strength': 50, 
        'child anchor strength': 51, 'sidedoor strength': 52, 'body nvh': 53, 'body stiffness': 54, 
        'hood stiffness / strength,hood open/close durability': 55, 'backdoor open / close durability/stiffness/strength/performance': 56, 
        'trunk stiffness / strength / durability performance': 57, 
        'sunroof performance / durability': 58, 'door open / close durabirity ,door strength/stiffness': 59, 
        'wdw reg performance / durability': 60, 'roof paintseal study': 61, 'front wiper durability': 63, 'trim durability environment sed / coupe': 64, 
        'trim durability environment h/b': 65, 'suv / pickup   wgn / others': 66, 'inst impact': 67, 'interior head impact': 68, 'fuel tank performance 2wd': 69, 
        'fuel tank performance 4wd': 70, 'fuel tank durability all': 71, 'fuel tank durability frame': 72, 
        'lpg container assembly portion test': 73, 'plastic tank fire resistance': 74, '35 mile occupant protect performance': 75, 
        'cargo room impact - seat': 76, 'side impact performance': 77, 'belt dynamic': 78, 'strg impact': 79, 
        'assist airbag performance': 80, 'curtain airbag performance': 81, 
        'seat anchor dynamic': 82, 'cargo room inpact-seat': 83, 'rear seat comfort': 84, 
        'body anti. corrosion performance': 85, 'glass antenna tuning': 86, 'sound quality': 87, 'b / d harness durability': 88}
    
    dic_address={"DPFC": [54, 58, 59, 66], "DS": [54, 58, 59, 73], "DC": [54, 58, 59, 80], "PFC": [81, 85, 86, 97], 
                 "VC": [98, 102, 103, 113], "PT1": [98, 102, 103, 123], "PT2": [98, 102, 103, 133]}

    dict_data_all={"t":[],"w":[],"c":[]}
    try:
        kca_proj = data_cadics.iat[6,dic_address[lot][0]]
    except:
        return [],[],[]
    evaluation = data_cadics.iat[6,dic_address[lot][1]]
    id_mail = data_cadics.iat[6,dic_address[lot][2]]
    for type_ in dict_type_block.keys():
        if len(dict_type_block[type_])>0:
            for config in list_config:
                config = config.lower()
                dict_data={0:dict_config[config]["zone"],1:dict_config[config]["body"],2:dict_config[config]["axle"],
                           3:dict_config[config]["handle"],4:dict_config[config]["engine"],5:dict_config[config]["trans"],
                           23:kca_proj,24:evaluation,26:id_mail,27:kca_proj,28:evaluation,30:id_mail}
                for occupancy in dict_type_block[type_].keys():
                    dict_data_ref=dict_data.copy()
                    for block in dict_type_block[type_][occupancy]:
                        try:
                            dict_data_ref[dict_address_block[block]]="〇"
                        except:
                            None
                    dict_data_all[type_].append(dict_data_ref)

    return dict_data_all["t"],dict_data_all["w"],dict_data_all["c"]


