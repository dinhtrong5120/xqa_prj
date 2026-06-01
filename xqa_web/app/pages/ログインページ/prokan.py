import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode, JsCode
# from setting import *
from xqa_web.app.setting import *
import streamlit_antd_components as sac
from xqa_web.app.logics.syo.db.function_database_new import update_syo
from xqa_web.app.logics.syo.db.funtion_database import query_data, update_edit
# from xqa_web.app.logics.syo.update_file import get_csrf_token, update_file_into_server_new, update_file_after_edit
from xqa_web.app.logics.prokan.read_data_view import check_file_out, read_output, write_cadic_temp
from xqa_web.app.logics.prokan.cadic_test import create_cadics_new
from xqa_web.app.logics.prokan.create_document_step2 import create_doc
from xqa_web.app.logics.prokan.classify_group import *
from xqa_web.app.logics.prokan.update_file import get_csrf_token, update_file_into_server_new, update_file_after_edit, process_uploaded_車両仕様表_Form_files
from xqa_web.app.logics.prokan.step3_create_output import fill_final_output, ensure_latest_form_in_output
from xqa_web.app.logics.prokan.step3_check_form import check_all_sheet_formats
from xqa_web.app.setting import BASE_DIR_DATAS, BASE_DIR_FORM_OUT
from streamlit_modal import Modal
from src.ux_ui.read_data_view import zip_folder

from io import BytesIO
import time
import numpy as np

def reset_data():
    if st.session_state.get('data_pro') is None:
        st.session_state['data_pro'] = {}


def main():
    reset_data()
    csrf_token = get_csrf_token()
    local_css(os.path.join(BASE_DIR_STATICS, "styles.css"))
    st.markdown(
        r"""
        <style>
        .stMainBlockContainer {
            padding-left: 1rem;
            padding-right: 2rem;
        }
        </style>
        """, unsafe_allow_html=True
    )
    for item in ['data_syo']:
        if item in st.session_state:
            st.session_state[item] = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)], index=range(1, 101)).fillna("")
    modal_view_prokan = Modal(key="modal_prokan_viewing", title="Viewing...")
    modal_load_file_prokan = Modal(key="modal_loading", title="Viewing...")
    modal_create_cadics = Modal(key="modal_create_cadics", title="Create cadics...")
    modal_create_output = Modal(key="modal_create_output", title="Create output...")
    modal_save_prokan = Modal(key="modal_save_prokan", title="Saving...")
    for var_status in ['load_prokan_complete', 'create_cadics_complete', 'create_output_complete',
                       'view_prokan_complete', 'save_prokan_complete']:
        if var_status not in st.session_state:
            st.session_state[var_status] = False
    if 'selected_option_sheet' in st.session_state and "plant2_prokan" not in st.session_state:
        st.session_state["plant2_prokan"] = st.session_state.selected_option_sheet
    # if "plant2_prokan" not in st.session_state:
    #     st.session_state["plant2_prokan"] = "ALL"
    #     print('49')
    else:
        pass
    col1, col2 = st.columns([24, 4.5])
    with col1:
        st.markdown(
            f'<h2 style="text-align: center;'
            f'background: linear-gradient(to right,  #000046, #1cb5e0);'
            f'border: 2px solid #D9D9D9; '
            f'color:azure;'
            f'border-radius: 10px;'
            f'padding: 10px">ステップ 2 : プロ管集約業務</h2>',
            unsafe_allow_html=True)

    with col2:
        st.markdown(
            f'<p style="text-align: center;'
            f'background: linear-gradient(to right,  #000046, #1cb5e0);'
            f'color:azure;'
            f'border-radius: 10px;'
            f'border: 2px solid #D9D9D9; '
            f'padding: 6px">{st.session_state.name_user}<br>{st.session_state.position}</p>',
            unsafe_allow_html=True)
    if "data_cadics" not in st.session_state:
        st.session_state.data_cadics = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)],
                                                    index=range(1, 101)).fillna("")

        set_data_prokan("data_cadics", pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)],
                                                    index=range(1, 101)).fillna(""))
    if "code_prokan" not in st.session_state:
        st.session_state.code_prokan = ""

    if "list_sheet" not in st.session_state:
        st.session_state.list_sheet = []
    col1_1, col2_1 = st.columns([0.26, 0.74])
    with col1_1:
        if "plant2_prokan" not in st.session_state:
            st.session_state.plant2_prokan = "ALL"
        else:
            pass
        with st.container(border=True, key="PROJ情報入力"):
            col_left_prj_grid_1 = grid(1, 2, 2, 1, 1, 1, vertical_align="top")
            col_left_prj_grid_1.subheader('PROJ情報入力')
            col_left_prj_grid_1.text_input("Model Code", key="code_prokan")
            col_left_prj_grid_1.selectbox("Case", ['CASE1', 'CASE1.5', 'CASE2'], key="case_prokan")
            col_left_prj_grid_1.selectbox("PowerTrain", ['EV', 'e-Power', 'ICE'], key="pwt_prokan")
            col_left_prj_grid_1.selectbox("Plant", ['JPN', 'US', 'EUR', 'PRC'], key="plant_prokan")
            try:
                list_group, notice = get_name_group(st.session_state.code_prokan)
                list_group = ["ALL"] + list_group
            except:
                list_group = ["ALL"]
            col_left_prj_grid_1.multiselect("Dev :red[(＊CADICS作成時に入力するだけです。)]", list_group,
                                            default=["ALL"],
                                            key="dev_prokan")
            if st.session_state.position == "admin" or st.session_state.position == "master":
                col_left_prj_grid_1.markdown('ファイルをインポート :blue[( 仕様表, 関連表①，②，③，④) ] ')
                files = col_left_prj_grid_1.file_uploader("", accept_multiple_files=True, label_visibility="collapsed")
                button_upload_file = st.button('ファイル読み込む', use_container_width=True, icon=":material/upload:")
                if button_upload_file:
                    # __________________________________
                    st.session_state.save_prokan_complete = False
                    st.session_state.view_prokan_complete = False
                    st.session_state.create_cadics_complete = False
                    st.session_state.create_output_complete = False
                    # __________________________________
                    modal_load_file_prokan.open()
                if modal_load_file_prokan.is_open():
                    with modal_load_file_prokan.container():
                        with st.spinner(text="In progress..."):
                            if len(files) > 0:
                                
                                valid_excel_paths , str_error, count_file_not_form = process_uploaded_車両仕様表_Form_files(files, st.session_state.code_prokan)
                                
                                if str_error == "":
                                     # Set flag if a valid form file was uploaded and saved
                                    st.session_state.form_uploaded_車両仕様表_Form_files = True

                                if str_error != "Check model code: Model Code is None" and count_file_not_form != 0 :
                                    update_file_into_server_new(st.session_state.code_prokan, files, csrf_token)
                                    notice = update_file_after_edit(st.session_state.code_prokan,
                                                                    st.session_state.pwt_prokan,
                                                                    st.session_state.plant_prokan,
                                                                    st.session_state.case_prokan, files, csrf_token,
                                                                    st.session_state.name_user)
                                    st.session_state.message_3 = notice
                                    update_syo()
                            else:
                                st.session_state.message_5 = "file has not been uploaded yet!!!"
                                if 'message_4' in st.session_state:
                                    del st.session_state['message_4']
                                if 'message_10' in st.session_state:
                                    del st.session_state['message_10']
                                if 'message_3' in st.session_state:
                                    del st.session_state['message_3']
                                if 'message_11' in st.session_state:
                                    del st.session_state['message_11']
                                if 'message_12' in st.session_state:
                                    del st.session_state['message_12']
                            st.session_state.load_prokan_complete = True
                            modal_load_file_prokan.close()
        if st.session_state.position == "admin" or st.session_state.position == "master":
            with st.container(border=True, key="計算_prokan"):
                col_left_prj_grid_2 = grid(1, [0.2, 0.8], [0.2, 0.8] , [0.2, 0.8], vertical_align="top")
                col_left_prj_grid_2.subheader('計算')

                # Tạo một container trong Streamlit
                with col_left_prj_grid_2.container():
                    # Tạo nút với icon
                    button_item = sac.ButtonsItem(icon=sac.BsIcon(name='1-circle-fill', size=20, color='black'))
                    # Sử dụng sac.buttons với danh sách nút
                    sac.buttons([button_item], align='center', variant='text', color='white')

                button_create_cadic = col_left_prj_grid_2.button("CADICS作成", use_container_width=True)

                # Tạo một container trong Streamlit
                with col_left_prj_grid_2.container():
                    # Tạo nút với icon
                    button_item = sac.ButtonsItem(icon=sac.BsIcon(name='2-circle-fill', size=20, color='black'))
                    # Sử dụng sac.buttons với danh sách nút
                    sac.buttons([button_item], align='center', variant='text', color='white')

                button_create_output = col_left_prj_grid_2.button("配車・部品要望作成", use_container_width=True)     
                # Tạo một container trong Streamlit
                with col_left_prj_grid_2.container():
                    # Tạo nút với icon
                    button_item = sac.ButtonsItem(icon=sac.BsIcon(name='3-circle-fill', size=20, color='black'))
                    # Sử dụng sac.buttons với danh sách nút
                    sac.buttons([button_item], align='center', variant='text', color='white')

                button_車両仕様表_excel = col_left_prj_grid_2.button("車両仕様表 作成", use_container_width=True)

            if button_車両仕様表_excel:
                # st.session_state.form_uploaded_車両仕様表_Form_files
                # Always use the saved form file path for the current car
                car_name = st.session_state.code_prokan
                folder_output = get_data_prokan("folder_output")
                if not folder_output:
                    list_file, folder_output, name_zip = check_file_out(st.session_state.code_prokan,
                                                                            st.session_state.pwt_prokan,
                                                                            st.session_state.plant_prokan,
                                                                            st.session_state.case_prokan)
                    set_state(list_file, folder_output, name_zip)
                file_form = os.path.join(BASE_DIR_DATAS, car_name, "車両仕様表_Form", f"車両仕様表_{car_name}.xlsx")
                file_form_default = os.path.join(BASE_DIR_FORM_OUT, "Step2", "車両仕様表_Form.xlsx")
                file_car = os.path.join(folder_output, "Car配車要望表.xlsx")
                filename_prefix = f"車両仕様表_{car_name}"
                # filename_prefix_default = f"車両仕様表_Form"

                if not os.path.exists(file_car):
                    st.warning("Please complete Step 2 (配車・部品要望作成) before creating 車両仕様表.xlsx.")
                else:
                    if not "form_uploaded_車両仕様表_Form_files" in st.session_state:
                        # Check if the form file exists
                        if not os.path.exists(file_form):
                            ensure_latest_form_in_output(file_form_default, folder_output, filename_prefix = filename_prefix)
                            file_form = os.path.join(folder_output, f"{filename_prefix}.xlsx")
                            st.warning(
                                f"Form file for this car ({car_name}) does not exist yet! The system will use the default form file for this car."
                            )
                        else:
                            ensure_latest_form_in_output(file_form, folder_output, filename_prefix = filename_prefix)
                            st.info(
                                "No new 車両仕様表_Form file was uploaded in this session. The system will use the previous form file for this car."
                            )
                    else:
                        if not os.path.exists(file_form):
                            ensure_latest_form_in_output(file_form_default, file_form, filename_prefix = filename_prefix)

                        ensure_latest_form_in_output(file_form, folder_output, filename_prefix = filename_prefix)
                              
                    # ---- Tích hợp check_all_sheet_formats ở đây ----
                    try:
                        check_all_sheet_formats(folder_output, file_form)
                    except ValueError as e:
                        st.error(f"Excel form format error: {e}")
                        return  # Dừng xử lý nếu file không hợp lệ
                    # -----------------------------------------
                    # try:
                    with st.spinner("Creating 車両仕様表 ..."):
                        fill_final_output(folder_output, file_form)
                    st.success("車両仕様表 was created successfully!")
                    set_data_prokan("車両仕様表", os.path.join(folder_output, "車両仕様表.xlsx"))
                    
                    if os.path.exists(f"{folder_output}.zip"):
                        os.remove(f"{folder_output}.zip")
                    zip_folder(folder_output, f"{folder_output}.zip")
                        
                    # except Exception as e:
                    #     st.error(f"Error while creating file: {e}")
                
                

            if button_create_output:
                st.session_state.load_prokan_complete = False
                st.session_state.view_prokan_complete = False
                st.session_state.create_cadics_complete = False
                st.session_state.save_prokan_complete = False
                modal_create_output.open()
            if modal_create_output.is_open():
                with modal_create_output.container():
                    with st.spinner(text="In progress..."):
                        notice = create_doc(st.session_state.case_prokan, st.session_state.plant_prokan,
                                            st.session_state.pwt_prokan,
                                            st.session_state.code_prokan)
                        list_file, folder_output, name_zip = check_file_out(st.session_state.code_prokan,
                                                                            st.session_state.pwt_prokan,
                                                                            st.session_state.plant_prokan,
                                                                            st.session_state.case_prokan)
                        set_state(list_file, folder_output, name_zip)
                        set_data("running", 0)
                        st.write("notice: ", notice)
                        st.session_state.message_9 = notice
                        st.session_state.create_output_complete = True
                        # modal_create_output.close()
            if button_create_cadic:
                st.session_state.load_prokan_complete = False
                st.session_state.view_prokan_complete = False
                st.session_state.save_prokan_complete = False
                st.session_state.create_output_complete = False
                modal_create_cadics.open()
            if modal_create_cadics.is_open():
                with modal_create_cadics.container():
                    with st.spinner(text="In progress..."):
                        print('ok')
                        notice, session, data, project_id, app_list = create_cadics_new(st.session_state.case_prokan,
                                                                                        st.session_state.plant_prokan,
                                                                                        st.session_state.pwt_prokan,
                                                                                        st.session_state.code_prokan,
                                                                                        # 'AAAA',
                                                                                        st.session_state.dev_prokan)
                        set_data("data_cadics", data)
                        set_state_db(session, project_id, app_list)
                        list_file, folder_output, name_zip = check_file_out(st.session_state.code_prokan,
                                                                            st.session_state.pwt_prokan,
                                                                            st.session_state.plant_prokan,
                                                                            st.session_state.case_prokan)
                        set_state(list_file, folder_output, name_zip)
                        set_data("running", 0)
                        st.write("notice: ", notice)
                        st.session_state.message_8 = notice

                        if st.session_state.plant2_prokan in ["ALL", "DS", "DC", "PFC", "VC", "PT1", "PT2"]:
                            session, data, project_id, app_list = query_data(str(st.session_state.code_prokan).upper(),
                                                                             st.session_state.plant_prokan,
                                                                             st.session_state.pwt_prokan,
                                                                             st.session_state.case_prokan,
                                                                             st.session_state.dev_prokan,
                                                                             # 'ALL')
                                                                             st.session_state.plant2_prokan)
                            st.session_state.data_cadics = data
                            set_data("data_cadics", data)
                            set_state_db(session, project_id, app_list)
                        list_file, folder_output, name_zip = check_file_out(st.session_state.code_prokan,
                                                                            st.session_state.pwt_prokan,
                                                                            st.session_state.plant_prokan,
                                                                            st.session_state.case_prokan)
                        set_state(list_file, folder_output, name_zip)
                        st.session_state.create_cadics_complete = True
        with st.container(border=True, key="データ表示_prokan"):
            col_left_prj_grid_3 = grid(1, 1, vertical_align="top")
            col_left_prj_grid_3.subheader('データ表示')
            button_view_prokan = col_left_prj_grid_3.button("表示", use_container_width=True, help='View existing プロ管 projects in the database')
            if button_view_prokan:
                # __________________________________
                st.session_state.load_prokan_complete = False
                st.session_state.create_cadics_complete = False
                st.session_state.create_output_complete = False
                st.session_state.save_prokan_complete = False
                # __________________________________
                # modal_view_prokan.open()
                with st.spinner(text="In progress..."):
                    if st.session_state.plant2_prokan in ["ALL", "DS", "DC", "PFC", "VC", "PT1", "PT2"]:
                        session, data, project_id, app_list = query_data(str(st.session_state.code_prokan).upper(),
                                                                         st.session_state.plant_prokan,
                                                                         st.session_state.pwt_prokan,
                                                                         st.session_state.case_prokan,
                                                                         st.session_state.dev_prokan,
                                                                         # 'ALL')
                                                                         st.session_state.plant2_prokan)
                        
                        st.session_state.data_cadics = data
                        set_data("data_cadics", data)
                        set_state_db(session, project_id, app_list)
                    list_file, folder_output, name_zip = check_file_out(st.session_state.code_prokan,
                                                                        st.session_state.pwt_prokan,
                                                                        st.session_state.plant_prokan,
                                                                        st.session_state.case_prokan)
                    set_state(list_file, folder_output, name_zip)
                st.session_state.view_prokan_complete = True
        # if modal_view_prokan.is_open():
        #     with modal_view_prokan.container():
            # modal_view_prokan.close()

        if st.session_state.view_prokan_complete:
            # ******************************************************
            if st.session_state.view_prokan_complete:
                if 'message_1' in st.session_state:
                    if 'Completed' in st.session_state.message_1:
                        st.success(st.session_state.message_1)
                    else:
                        st.error(st.session_state.message_1)
        if st.session_state.load_prokan_complete:
                        
            if st.session_state.code_prokan != "" and 'message_12' in st.session_state:
                del st.session_state['message_12']

            if 'message_3' in st.session_state:
                if 'Completed' in st.session_state.message_3:
                    st.success(st.session_state.message_3)
                elif st.session_state.message_3 != "":
                    st.error(st.session_state.message_3)
                try:
                    del st.session_state['message_5']
                except:
                    pass
            if 'message_5' in st.session_state:
                st.error(st.session_state.message_5)
                try:
                    del st.session_state['message_1']
                except:
                    pass
            if 'message_10' in st.session_state:
                if 'Updated' in st.session_state.message_10:
                    st.success(st.session_state.message_10)
                else:
                    # st.error(st.session_state.message_10)
                    st.warning(st.session_state.message_10)
            if 'message_11' in st.session_state :
                if st.session_state.message_11 != "":
                    if 'message_13' in st.session_state:
                        del st.session_state['message_13']
                        
                    st.error(st.session_state.message_11)


            if 'message_12' in st.session_state:
                if st.session_state.message_12 != "":
                    if 'message_13' in st.session_state:
                        del st.session_state['message_13']
                    st.error(st.session_state.message_12)

            if 'message_13' in st.session_state:
                if st.session_state.message_13 != "":
                    if 'message_11' in st.session_state :
                        del st.session_state['message_11']
                    if 'message_12' in st.session_state :
                        del st.session_state['message_12']
                    st.success(st.session_state.message_13)
            
        if st.session_state.create_cadics_complete:
            if 'message_8' in st.session_state:
                if st.session_state.message_8 == "Completed!":
                    st.success(st.session_state.message_8)
                elif 'Completed!, ' in st.session_state.message_8:
                    st.warning(st.session_state.message_8)
                else:
                    st.error(st.session_state.message_8)
                try:
                    del st.session_state['message_1']
                    del st.session_state['message_2']
                except:
                    pass
        if st.session_state.create_output_complete:
            if 'message_9' in st.session_state:
                if st.session_state.message_9 == "Completed!!!":
                    st.success(st.session_state.message_9)
                else:
                    st.error(st.session_state.message_9)
                for item in ['message_1', 'message_2', 'message_8']:
                    if item in st.session_state:
                        del st.session_state[item]
    with col2_1:
        col_right_prj_grid_1 = grid([0.11, 0.2, 0.1, 0.1, 0.1, 0.15, 0.15, 0.15], 1, vertical_align="top")
        col_right_prj_grid_1.markdown(
            f'<p style="text-align: center;'
            f'padding: 8px">出力を選択</p>',
            unsafe_allow_html=True)
        option_feedback_prokan = ["CADICS項目", "Car配車要望表", "WTC仕様用途一覧表",
                                    "WTC要望集約兼チェックリスト",
                                    "実験部品", "特性管理部品リスト", "車両仕様表", 
                                    "車両仕様表_Form", "File Log"
                                ]
        if "selected_option_prokan" not in st.session_state:
            st.session_state.selected_option_prokan = option_feedback_prokan[0]
        a_prokan = st.session_state.selected_option_prokan
        option_view_prokan = col_right_prj_grid_1.selectbox('option_view_prokan',
                                                            option_feedback_prokan,
                                                            index=option_feedback_prokan.index(st.session_state.selected_option_prokan),
                                                            key="plant1_prokan",
                                                            label_visibility="collapsed")
        st.session_state.selected_option_prokan = option_view_prokan
        b_prokan = st.session_state.selected_option_prokan

        col_right_prj_grid_1.markdown(
            f'<p style="text-align: center;'
            f'padding: 8px">Sheet名</p>',
            unsafe_allow_html=True)
        if option_view_prokan == "CADICS項目":
            st.session_state.list_sheet = ["ALL", "DS", "DC", "PFC", "VC", "PT1", "PT2"]
            set_data_prokan("link", "cadics")
        elif option_view_prokan == "車両仕様表":
            st.session_state.list_sheet = ["PFC", "VC", "PT1", "PT2"]
            if get_data_prokan("車両仕様表"):
                set_data_prokan("link", get_data_prokan("車両仕様表"))
                set_data_prokan("name", "車両仕様表.xlsx")
            else:
                list_file, folder_output, name_zip = check_file_out(st.session_state.code_prokan,
                                                                            st.session_state.pwt_prokan,
                                                                            st.session_state.plant_prokan,
                                                                            st.session_state.case_prokan)
                set_data_prokan("車両仕様表", os.path.join(folder_output, "車両仕様表.xlsx"))
                # set_data_prokan("link", get_data_prokan("車両仕様表"))
                set_data_prokan("name", "車両仕様表.xlsx")
        elif option_view_prokan == "車両仕様表_Form":
            # Xác định đường dẫn file form theo Model Code
            if st.session_state.code_prokan and st.session_state.code_prokan.strip():
                car_name = st.session_state.code_prokan
                file_form = os.path.join(BASE_DIR_DATAS, car_name, "車両仕様表_Form", f"車両仕様表_{car_name}.xlsx")
                if not os.path.exists(file_form):
                    st.warning(f"Form file {file_form} for {st.session_state.code_prokan} not found. The default form file will be displayed.")
                    file_form = "xqa_web/app/form_out/Step2/車両仕様表_Form.xlsx"
            else:
                file_form = "xqa_web/app/form_out/Step2/車両仕様表_Form.xlsx"
            
            # Kiểm tra file tồn tại, nếu không tồn tại thì cảnh báo và trả về bảng rỗng
            if not os.path.exists(file_form):
                st.warning(f"Không tìm thấy file form: {file_form}")
                st.session_state.list_sheet = []
                data = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)], index=range(1, 101)).fillna("")
            
            else:
                st.session_state.list_sheet = ["PFC", "VC", "PT1", "PT2"]
                set_data_prokan("link", file_form)
                set_data_prokan("name", "車両仕様表_Form.xlsx")
        elif option_view_prokan == "Car配車要望表":
            st.session_state.list_sheet = ["PFC", "VC", "PT1", "PT2"]
            set_data_prokan("link", get_data_prokan("Car配車要望表"))
            set_data_prokan("name", "Car配車要望表.xlsx")
        elif option_view_prokan == "File Log":
            st.session_state.list_sheet = ["COUNT", "関連表①", "関連表②", "関連表③", "関連表④", "Error_create_車両仕様表"]
            set_data_prokan("link", get_data_prokan("File Log"))
            set_data_prokan("name", "File Log.xlsx")
        elif option_view_prokan == "WTC仕様用途一覧表":
            st.session_state.list_sheet = ["PFC", "VC"]
            set_data_prokan("link", get_data_prokan("WTC仕様用途一覧表"))
            set_data_prokan("name", "WTC仕様用途一覧表.xlsx")
        elif option_view_prokan == 'WTC要望集約兼チェックリスト':
            st.session_state.list_sheet = ["PFC", "VC"]
            set_data_prokan("link", get_data_prokan("WTC要望集約兼チェックリスト"))
            set_data_prokan("name", "WTC要望集約兼チェックリスト.xlsx")
        elif option_view_prokan == "実験部品":
            st.session_state.list_sheet = ["PFC", "VC"]
            set_data_prokan("link", get_data_prokan("実験部品"))
            set_data_prokan("name", "実験部品.xlsx")
        elif option_view_prokan == "特性管理部品リスト":
            st.session_state.list_sheet = ["PFC", "VC"]
            set_data_prokan("link", get_data_prokan("特性管理部品リスト"))
            set_data_prokan("name", "特性管理部品リスト.xlsx")
        if 'plant2_prokan' not in st.session_state:
            if option_view_prokan == "CADICS項目":
                st.session_state.plant2_prokan = "ALL"
            else:
                st.session_state.plant2_prokan = "PFC"
        if 'plan_before' not in st.session_state:
            st.session_state.plan_before = st.session_state.plant2_prokan

        if "selected_option_sheet" not in st.session_state:
            st.session_state.selected_option_sheet = st.session_state.list_sheet[0]
        selected_sheet = col_right_prj_grid_1.selectbox('', st.session_state.list_sheet,
                                       key="plant2_prokan",
                                       # index=st.session_state.list_sheet.index(st.session_state.selected_option_sheet),
                                       label_visibility="collapsed")
        st.session_state.selected_option_sheet = selected_sheet
        col_right_prj_grid_1.write('')
        with col_right_prj_grid_1.container():
            st.markdown('<span class="button-green"></span>', unsafe_allow_html=True)
            if get_data_prokan("link") is not None and get_data_prokan("link") not in ["cadics", 'FORM', '仕様表']:
                with open(get_data_prokan("link"), "rb") as fp:
                    st.download_button(
                        label="ダウンロード",
                        icon=":material/cloud_download:",
                        data=fp,
                        file_name=get_data_prokan("name"),
                        mime="text/plain",
                        use_container_width=True,
                        key="button_download_prokan"
                    )
            elif get_data_prokan("link") == "cadics" and len(get_data_prokan("data_cadics").columns) > 31:
                buffer = BytesIO()
                get_data_prokan("data_cadics").to_csv(buffer, index=False, header=False, encoding='utf-8-sig')
                buffer.seek(0)
                bool = st.download_button(
                    label="ダウンロード",
                    icon=":material/cloud_download:",
                    data=buffer,
                    file_name="CADICS_ALL.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="button_download_prokan"
                )
                if bool and st.session_state.position in ["admin", "master"]:
                    write_cadic_temp(st.session_state.name_user, st.session_state.position, st.session_state.code_prokan, st.session_state.pwt_prokan,
                     st.session_state.plant_prokan, st.session_state.case_prokan, get_data_prokan("data_cadics"))
                    bool = False

        with col_right_prj_grid_1.container():
            st.markdown('<span class="button-green"></span>', unsafe_allow_html=True)
            button_save_prokan = st.button("保存", use_container_width=True, icon=":material/save:",
                                           disabled=(
                                                   option_view_prokan not in ["CADICS項目", "車両仕様表"] or st.session_state.position not in [
                                               "admin", "master"]))
        with col_right_prj_grid_1.container():
            # st.markdown('<span class="button-green"></span>', unsafe_allow_html=True)
            # button_save_prokan_1 = st.button("保存1", use_container_width=True, icon=":material/save:",
            #                                disabled=(
            #                                        option_view_prokan != "CADIC 項目" or st.session_state.position not in [
            #                                    "admin", "master"]))
            try:
                st.markdown('<span class="button-green"></span>', unsafe_allow_html=True)
                with open(get_data_prokan("folder_output") + ".zip", "rb") as fp:
                    st.download_button(
                        label="Download All",
                        icon=":material/cloud_download:",
                        data=fp,
                        file_name=get_data_prokan("name_zip"),
                        mime="application/zip",
                        use_container_width=True
                    )
            except:
                None

    with col_right_prj_grid_1.container(border=True, key="dataframe_prokan"):
        sheet_name = st.session_state.plant2_prokan
        if option_view_prokan == "CADICS項目":
            if st.session_state.plan_before != st.session_state.plant2_prokan:
                st.session_state.plan_before = st.session_state.plant2_prokan
                with st.spinner(text="In progress..."):
                    session, data, project_id, app_list = query_data(str(st.session_state.code_prokan).upper(),
                                                                     st.session_state.plant_prokan,
                                                                     st.session_state.pwt_prokan,
                                                                     st.session_state.case_prokan,
                                                                     st.session_state.dev_prokan,
                                                                     st.session_state.plant2_prokan)
                    st.session_state.data_cadics = data
                    set_data("data_cadics", data)
                    list_file, folder_output, name_zip = check_file_out(st.session_state.code_prokan,
                                                                        st.session_state.pwt_prokan,
                                                                        st.session_state.plant_prokan,
                                                                        st.session_state.case_prokan)
                    set_state(list_file, folder_output, name_zip)
                    set_state_db(session, project_id, app_list)

            data = st.session_state.data_cadics
            if len(st.session_state.code_prokan) > 0 and len(data.columns) > 60:
                lot_indexes = [60, 67, 80, 97, 107, 117]
                
                for lot in lot_indexes:
                    if data.iloc[5, lot] == "Evaluate or not":
                        new_val = str(data.iloc[2, lot]) + "_" + str(data.iloc[5, lot])
                        data.iloc[5, lot] = new_val

            grid_response_data = show_aggrid_table(data, num_col_freeze=2, row_freeze=5, editable=True)
        elif option_view_prokan == "車両仕様表":
            data = read_output(get_data_prokan("車両仕様表"), sheet_name)
            cols = list(data.columns)
            cols[0], cols[10] = cols[10], cols[0]
            data = data[cols]
            grid_response_data = show_aggrid_table(data, num_col_freeze=2, row_freeze=7)
        elif option_view_prokan == "車両仕様表_Form":
            # Kiểm tra file tồn tại và sheet_name hợp lệ
            if not os.path.exists(file_form):
                st.warning(f"Không tìm thấy file form: {file_form}")
                data = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)], index=range(1, 101)).fillna("")
            else:
                data = read_output(file_form, sheet_name)
            grid_response_data = show_aggrid_table(data, num_col_freeze=10, row_freeze=7)
        elif option_view_prokan == "Car配車要望表":
            sheet_name = f"{sheet_name}_車両"
            data = read_output(get_data_prokan("Car配車要望表"), sheet_name)
            grid_response_data = show_aggrid_table(data, num_col_freeze=4, row_freeze=18)
        elif option_view_prokan == "WTC仕様用途一覧表":
            data = read_output(get_data_prokan("WTC仕様用途一覧表"), sheet_name)
            grid_response_data = show_aggrid_table(data, num_col_freeze=2, row_freeze=36)
        elif option_view_prokan == "WTC要望集約兼チェックリスト":
            data = read_output(get_data_prokan("WTC要望集約兼チェックリスト"), sheet_name)
            grid_response_data = show_aggrid_table(data, num_col_freeze=3, row_freeze=4)
        elif option_view_prokan == "実験部品":
            data = read_output(get_data_prokan("実験部品"), sheet_name)
            grid_response_data = show_aggrid_table(data, num_col_freeze=3, row_freeze=4)
        elif option_view_prokan == "特性管理部品リスト":
            data = read_output(get_data_prokan("特性管理部品リスト"), sheet_name)
            grid_response_data = show_aggrid_table(data, num_col_freeze=3, row_freeze=26)
        elif option_view_prokan == "File Log":
            data = read_output(get_data_prokan("File Log"), sheet_name)
            st.dataframe(data, height=775, width=10000)
        else:
            empty_df = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)], index=range(1, 101)).fillna("")
            st.data_editor(empty_df, height=775, width=10000)
            
    if button_save_prokan:
        st.session_state.load_prokan_complete = False
        st.session_state.view_prokan_complete = False
        st.session_state.create_cadics_complete = False
        st.session_state.create_output_complete = False
        modal_save_prokan.open()

    if modal_save_prokan.is_open():
        with modal_save_prokan.container():
            with st.spinner(text="In progress..."):
                time1 = time.time()
                data_fame_after_edit = pd.DataFrame(grid_response_data)

                if option_view_prokan == "CADICS項目":
                    update_edit(data_fame_after_edit, get_data_prokan("session"), get_data_prokan("data_cadics"),
                                get_data_prokan("project_id"), get_data_prokan("app_list"))
                    set_data_prokan("data_cadics", data_fame_after_edit)
                    st.session_state.save_prokan_complete = True

                time2 = time.time()
                if (time2 - time1) < 5:
                    time.sleep(5 - (time2 - time1))
                modal_save_prokan.close()

    if st.session_state.save_prokan_complete:
        for item in ['message_1', 'message_2', 'message_9']:
            if item in st.session_state:
                del st.session_state[item]
        if 'message_11' in st.session_state:
            if st.session_state.message_11 == 'Save Completed!!!':
                col1_1.success(st.session_state.message_11)
            else:
                col1_1.error(st.session_state.message_11)

    if a_prokan != b_prokan:
        st.rerun()

def get_excel_sheets(file_path):
    try:
        # Nếu file tồn tại, trả về danh sách sheet
        xls = pd.ExcelFile(file_path)
        return xls.sheet_names
    except Exception as e:
        # Nếu file lỗi hoặc không phải excel, trả về list rỗng
        return []

def show_aggrid_table(data, num_col_freeze, row_freeze, editable=False):
    headers = data.columns.astype(str).to_list()
    pinned_rows = data.iloc[row_freeze:row_freeze + 1].to_dict('records')

    # Javascript code to process pin columns.
    js_pin_cols = JsCode('''
    function onColumnPinned(event) {
        console.log("onColumnPinned triggered:", event);
        let newCols = [];

        setTimeout(() => {
            const gridApi = event.api;
            const changedColId = event.column.getColId();
            const pinnedSide = event.pinned; // 'left', 'right', or null

            const match = changedColId.match(/(\\d+)/);
            if (!match) return;

            const targetIndex = parseInt(match[1]);
                    
            let isStart = (window.isStart === false) ? false : true;
            if (isStart) {
                const allColumns = gridApi.getAllGridColumns();
                newCols = allColumns.map((col, index) => {
                    const item = {
                        colId: col.getColId(),
                        pinned: null
                    };
                    return item;
                });
            }
            else {
                newCols = window.columnStates;
                newCols.forEach(state => {
                    console.log(`Cột ${state.colId} được ghim ${state.pinned}`);
                });
            }
                        
            if (pinnedSide === 'left') {
                for (let i in newCols) {
                    if (i < targetIndex) {
                        newCols[i].pinned = 'left';
                    }  
                }
            } else if (pinnedSide === 'right') {
                for (let i in newCols) {
                    if (i >= targetIndex - 1) {
                        newCols[i].pinned = 'right';
                    }
                }
            } else if (pinnedSide === null) {
                for (let i in newCols) {
                    if (i > 1) {
                        newCols[i].pinned = null;
                    }
                    
                }
            }

            if (newCols.length > 0) {
                gridApi.applyColumnState({
                    state: newCols,
                });
                window.columnStates = newCols;
                window.isStart = false;
            }
        }, 100);
    };
    ''')

    # Javascript code to add full-screen button
    grid_ready_js = JsCode('''
    function(params) {
        console.log("Grid is ready");
        
        // Function toggle full screen
        function toggleFullScreen(element) {
            if (!document.fullscreenElement) {
                if (element.requestFullscreen) {
                    element.requestFullscreen();
                } else if (element.webkitRequestFullscreen) {
                    element.webkitRequestFullscreen();
                } else if (element.msRequestFullscreen) {
                    element.msRequestFullscreen();
                }
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                } else if (document.msExitFullscreen) {
                    document.msExitFullscreen();
                }
            }
        }

        // Add button full screen
        function addFullScreenButton() {
            const gridWrappers = document.querySelectorAll('.ag-root-wrapper');
            gridWrappers.forEach(wrapper => {
                if (!wrapper.querySelector('.fullscreen-btn')) {
                    const button = document.createElement('button');
                    button.innerHTML = '⛶';
                    button.className = 'fullscreen-btn';
                    button.style.cssText = `
                        position: absolute;
                        top: 5px;
                        right: 5px;
                        z-index: 1000;
                        background: rgba(255, 255, 255, 0.9);
                        border: 1px solid #ccc;
                        border-radius: 4px;
                        padding: 5px 10px;
                        cursor: pointer;
                        font-size: 16px;
                    `;
                    
                    button.onclick = function() {
                        toggleFullScreen(wrapper);
                    };
                    
                    wrapper.style.position = 'relative';
                    wrapper.appendChild(button);
                }
            });
        }
        
        // Add button when grid is ready
        setTimeout(addFullScreenButton, 500);
    }
    ''')

    # CSS for full-screen button
    st.markdown("""
    <style>
        .ag-theme-alpine {
            width: 100% !important;
            max-width: 100% !important;
        }
        .ag-root-wrapper {
            width: 100% !important;
            max-width: 100% !important;
            position: relative !important;
        }
        [data-testid="stAgGrid"] {
            width: 100% !important;
        }
        
        /* Fullscreen styles */
        .ag-root-wrapper:-webkit-full-screen {
            width: 100vw !important;
            height: 100vh !important;
            background: white;
        }
        .ag-root-wrapper:-moz-full-screen {
            width: 100vw !important;
            height: 100vh !important;
            background: white;
        }
        .ag-root-wrapper:fullscreen {
            width: 100vw !important;
            height: 100vh !important;
            background: white;
        }
    </style>
    """, unsafe_allow_html=True)

    # Create grid option builder
    gb = GridOptionsBuilder.from_dataframe(data, enableRowGroup=True, enableValue=True, enablePivot=True)
    gb.configure_default_column(
        minWidth=100,
        resizable=True,
        editable=editable, 
        filter=True
    )

    # Default pinned columns
    if len(headers) >= num_col_freeze:
        for i in range(num_col_freeze):
            gb.configure_column(headers[i], pinned='left')
    
    gb.configure_grid_options(
        onColumnPinned=js_pin_cols,
        onGridReady=grid_ready_js,
        suppressColumnVirtualisation=True,
    )

    gb.configure_grid_options(pinnedTopRowData=pinned_rows)
    gb.configure_selection('multiple')
    gb.configure_grid_options(enableRangeSelection=True)
    
    custom_css = {
        ".ag-cell": {
            "text-align": "left",
            "justify-content": "center",
            "box-shadow": "inset 0 0 0 0.5px #888 !important",
            "white-space": "normal !important",
            "word-break": "break-word !important"
        },
        ".ag-row-even .ag-cell": {"background-color": "#e3f2fd !important"},
        ".ag-row-odd .ag-cell": {"background-color": "#ffffff !important"},
    }

    grid_options = gb.build()

    grid_response = AgGrid(
        data,
        gridOptions=grid_options,
        theme='balham',
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.SELECTION_CHANGED if editable else 'NO_UPDATE',
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        height=700,
        width='100%',
        editable=editable,
        custom_css=custom_css,
        reload_data=True
    )

    return grid_response['data']


def set_state(list_file, folder_output, name_zip):
    set_data("folder_output", folder_output)
    set_data("name_zip", name_zip)
    list_link = ["Car配車要望表", "WTC仕様用途一覧表", "WTC要望集約兼チェックリスト", 
                 "実験部品", "特性管理部品リスト", "車両仕様表",
                 "File Log"]
    for index in range(len(list_link)):
        set_data(list_link[index], list_file[index]) 
    set_data("flag_view", 1)


def set_state_db(session, project_id, app_list):
    set_data("session", session)
    set_data("project_id", project_id)
    set_data("app_list", app_list)


def set_data(key: str, value):
    st.session_state['data_pro'][key] = value


def set_data_prokan(key: str, value):
    st.session_state['data_pro'][key] = value


def get_data_prokan(key):
    return st.session_state['data_pro'].get(key)
