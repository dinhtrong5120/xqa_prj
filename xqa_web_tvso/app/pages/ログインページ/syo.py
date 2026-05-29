import sys
import os
import io

import pandas as pd
import numpy as np
from streamlit_modal import Modal
import streamlit_antd_components as sac

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from xqa_web_tvso.app.setting import *
from xqa_web_tvso.app.logics.syo.db.function_database_new import querry_data_syo_hyo, get_gray_blue, update_data_new, \
    update_and_querry_form_data, add_function_from_admin, update_syo, update_syo_form
from xqa_web_tvso.app.logics.syo.convert_data_syo import dataframe_convert
from xqa_web_tvso.app.logics.syo.update_file import get_csrf_token, update_file_into_server_new
from xqa_web_tvso.app.logics.syo.check_filed_information import check_key_spec_new, check_optioncode
from xqa_web_tvso.app.logics.syo.all_process_spec_not_protected import main_process_spec_not_protected
from xqa_web_tvso.app.logics.syo.create_syo_new_edit import create_syo


def main():
    csrf_token = get_csrf_token()
    local_css(os.path.join(BASE_DIR_STATICS, "styles.css"))
    # try :
    for item in ['data_cadics']:
        if item in st.session_state:
            st.session_state[item] = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)],
                                                  index=range(1, 101)).fillna("")
            try:
                st.session_state['data_pro'][item] = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)],
                                                                  index=range(1, 101)).fillna("")
            except:
                pass
    if 'message_1' in st.session_state:
        del st.session_state.message_1
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
    list_all_message = [f'message_{i + 1}' for i in range(12)]

    modal_view_syo = Modal(key="modal_syo_viewing", title="Viewing...")
    modal_load_file_syo = Modal(key="modal_loading", title="Loading...")
    modal_create_form = Modal(key="modal_create_form", title="仕様表_BLANK作成...")
    modal_create_syo = Modal(key="modal_create_syo", title="仕様表作成...")
    modal_save_syo = Modal(key="modal_save_syo", title="Saving...")
    col1, col2 = st.columns([24, 4.5])
    with col1:
        st.markdown(
            f'<h2 style="text-align: center;'
            f'background: linear-gradient(to right,  #000046, #1cb5e0);'
            f'border: 2px solid #D9D9D9; '
            f'color:azure;'
            f'border-radius: 10px;'
            f'padding: 10px">ステップ 1 : 仕様表作成</h2>',
            unsafe_allow_html=True)

    with col2:
        st.markdown(
            f'<p style="text-align: center;'
            f'background: linear-gradient(to right, #000046, #1cb5e0);'
            f'color:azure;'
            f'border-radius: 10px;'
            f'border: 2px solid #D9D9D9; '
            f'padding: 6px">{st.session_state.name_user}<br>{st.session_state.position}</p>',
            unsafe_allow_html=True)

    col3, col4 = st.columns([0.26, 0.74])
    if 'flg_check_fail' not in st.session_state:
        st.session_state.flg_check_fail = None

    for var_status in ["device_group", "device", 'data_for_create']:
        if var_status not in st.session_state:
            st.session_state[var_status] = []
    for var_name in ['formspec_view', 'data_syo_view', 'formspec', 'form', 'data_syo']:
        if var_name not in st.session_state:
            st.session_state[var_name] = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)],
                                                      index=range(1, 101)).fillna("")
    for var_status in ['button_disabled', 'view_syo_complete', 'load_syo_complete', 'create_form_complete',
                       'create_syo_complete', 'save_syo_complete']:
        if var_status not in st.session_state:
            st.session_state[var_status] = False

    with col3:
        with st.container(border=True, key="PROJ情報入力"):
            col_left_prj_grid = grid(1, 1, 1, 1, 1, vertical_align="top")
            col_left_prj_grid.subheader('PROJ情報入力')

            col_left_prj_grid.text_input("Model Code", key="code")

            col_left_prj_grid.markdown('ファイルをインポート :blue[(Spectlist, 仕様表, 仕様表フォーム)] ')
            files = col_left_prj_grid.file_uploader("", accept_multiple_files=True, label_visibility="collapsed")
            button_load_file = col_left_prj_grid.button("ファイル読み込む", use_container_width=True,
                                                        help='Upload input files to memory.')
            if button_load_file:
                st.session_state.view_syo_complete = False
                st.session_state.create_syo_complete = False
                st.session_state.create_form_complete = False
                st.session_state.save_syo_complete = False
                modal_load_file_syo.open()
        if modal_load_file_syo.is_open():
            with modal_load_file_syo.container():
                with st.spinner(text="In progress..."):
                    if len(files) > 0:
                        update_file_into_server_new(st.session_state.code, files, csrf_token)
                        update_syo()
                        update_syo_form(files)
                        if 'message_5' in st.session_state:
                            del st.session_state['message_5']
                        if st.session_state.code != '':
                            data_syo, unique_list_max, unique_list_submax = querry_data_syo_hyo(st.session_state.code)
                            st.session_state.data_syo = data_syo
                            st.session_state.device_group = unique_list_max
                            st.session_state.device = unique_list_submax

                            df_1, merged_df_4_optioncode, unique_list_max, unique_list_submax = update_and_querry_form_data()

                            form_df = pd.concat([df_1, merged_df_4_optioncode], axis=0).fillna('').drop(
                                columns=['device_name'])
                            st.session_state.form = form_df
                        else:
                            df_1, merged_df_4_optioncode, unique_list_max, unique_list_submax = update_and_querry_form_data()

                            form_df = pd.concat([df_1, merged_df_4_optioncode], axis=0).fillna('').drop(
                                columns=['device_name'])
                            st.session_state.form = form_df
                    else:
                        st.session_state.message_5 = "file has not been uploaded yet!!!"
                        if 'message_4' in st.session_state:
                            del st.session_state['message_4']
                        if 'message_10' in st.session_state:
                            del st.session_state['message_10']
                    st.session_state.load_syo_complete = True
                    modal_load_file_syo.close()

        with st.container(border=True, key="計算"):
            col_left_prj_grid_2 = grid(1, [0.2, 0.8], [0.2, 0.8], vertical_align="top")
            col_left_prj_grid_2.subheader('計算')

            # Tạo một container trong Streamlit
            with col_left_prj_grid_2.container():
                # Tạo nút với icon
                button_item = sac.ButtonsItem(icon=sac.BsIcon(name='1-circle-fill', size=20, color='black'))
                # Sử dụng sac.buttons với danh sách nút
                sac.buttons([button_item], align='center', variant='text', color='white')

            button_create_syohyo_form = col_left_prj_grid_2.button("仕様表フォーム作成", use_container_width=True,
                                                                   help='Get the equipment already in the database combined with the config from the speclist file.')
            if button_create_syohyo_form:
                st.session_state.view_syo_complete = False
                st.session_state.load_syo_complete = False
                st.session_state.create_syo_complete = False
                st.session_state.save_syo_complete = False

                modal_create_form.open()

            # Tạo một container trong Streamlit
            with col_left_prj_grid_2.container():
                # Tạo nút với icon
                button_item = sac.ButtonsItem(icon=sac.BsIcon(name='2-circle-fill', size=20, color='black'))
                # Sử dụng sac.buttons với danh sách nút
                sac.buttons([button_item], align='center', variant='text', color='white')
            button_create_syohyo = col_left_prj_grid_2.button("仕様表作成", use_container_width=True,
                                                              help='Create complete 仕様表 file.',
                                                              disabled=not ('flg_check_fail' in st.session_state))

            if button_create_syohyo:
                st.session_state.view_syo_complete = False
                st.session_state.load_syo_complete = False
                st.session_state.create_form_complete = False
                st.session_state.save_syo_complete = False
                modal_create_syo.open()

        if modal_create_syo.is_open():
            with modal_create_syo.container():
                with st.spinner(text="In progress..."):
                    if st.session_state.flg_check_fail is not None:
                        if st.session_state.formspec.shape[1] > 4:
                            # st.success(st.session_state.formspec_view)
                            check_option_code_result = check_optioncode(st.session_state.formspec_view)
                            if not check_option_code_result:
                                if st.session_state.code != '':
                                    form_syo = create_syo(st.session_state.formspec_view,
                                                          st.session_state.data_for_create)
                                    form_syo.replace({np.nan: ''}, inplace=True)

                                    result_querry_region_4_gray, result_querry_region_4_blue = get_gray_blue(
                                        st.session_state.code)
                                    df, df_1 = dataframe_convert(form_syo, st.session_state.code,
                                                                 result_querry_region_4_gray,
                                                                 result_querry_region_4_blue)
                                    update_data_new(st.session_state.code, df, df_1)
                                    st.session_state.message_7 = 'Completed'
                                    st.session_state.flg_check_fail = None
                                else:
                                    st.session_state.message_7 = 'Model code can not be left blank'
                                    st.warning("Model code can not be left blank")
                            else:
                                st.error('OptionCode empty')
                                st.session_state.message_7 = 'OptionCode empty'
                        else:
                            st.error('OptionCode empty')
                            st.session_state.message_7 = 'OptionCode empty'
                    else:
                        st.session_state.message_7 = 'Please create Form'
                        st.warning(st.session_state.message_7)
                        st.warning("Please create Form")
                    st.session_state.create_syo_complete = True
                    # modal_create_syo.close()
        if modal_create_form.is_open():
            with modal_create_form.container():
                with st.spinner(text="In progress..."):
                    if files is not None and files != []:
                        code = str(st.session_state.code).lower()
                        if code not in str(files[0].name).lower():
                            st.error("Model code or Spec incorrect_____1AA")
                            st.session_state.message_6 = "Model code or Spec incorrect_____1AA"
                            st.session_state.data_syo = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)],
                                                                     index=range(1, 101)).fillna("")

                        elif 'Spec_List' not in files[0].name:
                            print("files[0].name:", files[0].name)
                            st.error("Model code or Spec incorrect_____2")
                            st.session_state.message_6 = "Model code or Spec incorrect_____2"
                            st.session_state.data_syo = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)],
                                                                     index=range(1, 101)).fillna("")
                            
                        # if code not in str(files[0].name).lower() or 'Spec_List' not in files[0].name:
                        #     st.error("Model code or Spec incorrect_____1")
                        #     st.session_state.message_6 = "Model code or Spec incorrect_____1"
                        #     st.session_state.data_syo = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)],
                        #                                              index=range(1, 101)).fillna("")
                        elif code == '':
                            st.error('Model code is blank')
                            st.session_state.message_6 = 'Model code is blank'
                            st.session_state.data_syo = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)],
                                                                     index=range(1, 101)).fillna("")
                        else:
                            df_check_log, flg_check_fail = check_key_spec_new(files)
                            st.session_state.flg_check_fail = flg_check_fail
                            if flg_check_fail:
                                df_1, merged_df_4_optioncode, unique_list_max, unique_list_submax = update_and_querry_form_data()
                                merged_df_fail = pd.concat([df_1, merged_df_4_optioncode], axis=0)
                                st.session_state.formspec = merged_df_fail
                                st.session_state.device_group = unique_list_max
                                st.session_state.device = unique_list_submax
                                st.write(df_check_log)
                                st.warning("Form Speclist is incorrect")
                                st.session_state.message_6 = "Model code or Spec incorrect"
                            else:
                                df_end_region3, data_for_create = main_process_spec_not_protected(files[0],
                                                                                                  str(st.session_state.code).upper())
                                merger_end, unique_list_max, unique_list_submax = add_function_from_admin(
                                    df_end_region3, files)
                                merger_end = merger_end.reset_index(drop=True)
                                st.session_state.formspec = merger_end
                                # Để tránh trờng hợp khi ng dùng mở web rồi tạo syo rồi tải blank về mà không bấm view.
                                if 'auto' not in st.session_state.formspec_view:
                                    st.session_state.formspec_view = st.session_state.formspec
                                st.session_state.device_group = unique_list_max
                                st.session_state.device = unique_list_submax
                                st.session_state.data_for_create = data_for_create
                                st.session_state.message_6 = "Create Completed!!!"
                    else:
                        st.session_state.data_syo = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)],
                                                                 index=range(1, 101)).fillna("")
                        st.error('file has not been uploaded yet')
                        st.session_state.message_6 = "file has not been uploaded yet"
                    st.session_state.create_form_complete = True
                    modal_create_form.close()
        with st.container(border=True, key="データ表示"):
            col_left_prj_grid_3 = grid(1, 1, vertical_align="top")
            col_left_prj_grid_3.subheader('データ表示')
            button_view = col_left_prj_grid_3.button("表示", use_container_width=True,
                                                     help='View existing 仕様表 projects in the database')
            if button_view:
                # __________________________________
                st.session_state.load_syo_complete = False
                st.session_state.create_form_complete = False
                st.session_state.create_syo_complete = False
                st.session_state.save_syo_complete = False
                # __________________________________
                modal_view_syo.open()
        if modal_view_syo.is_open():
            with modal_view_syo.container():
                with st.spinner(text="In progress..."):
                    data_syo, unique_list_max, unique_list_submax = querry_data_syo_hyo(st.session_state.code)
                    st.session_state.data_syo = data_syo
                    st.session_state.device_group = unique_list_max
                    st.session_state.device = unique_list_submax

                    df_1, merged_df_4_optioncode, unique_list_max, unique_list_submax = update_and_querry_form_data()

                    form_df = pd.concat([df_1, merged_df_4_optioncode], axis=0).fillna('').drop(columns=['device_name'])
                    st.session_state.form = form_df
                    st.session_state.view_syo_complete = True
                    modal_view_syo.close()
        # ******************************************************
        if st.session_state.view_syo_complete:
            if 'message_1' in st.session_state:
                st.error(st.session_state.message_1)
            if 'Model code' in st.session_state.message_2:
                st.error(st.session_state.message_2)
            elif st.session_state.message_2 != '':
                st.success(st.session_state.message_2)
            # st.rerun()
        # ******************************************************
        if st.session_state.load_syo_complete:
            if 'message_10' in st.session_state:
                new_list = [msg for msg in list_all_message if msg != 'message_10']
                for item in new_list:
                    try:
                        del st.session_state[item]
                    except:
                        pass
                if 'Updated' in st.session_state.message_10:
                    st.success(st.session_state.message_10)
                else:
                    st.error(st.session_state.message_10)

            if 'message_3' in st.session_state:
                if 'Completed' in st.session_state.message_3:
                    st.success(st.session_state.message_3)
                elif st.session_state.message_3 != '':
                    st.error(st.session_state.message_3)
            if 'message_4' in st.session_state:
                if 'Update' in st.session_state.message_4:
                    if 'message_10' in st.session_state:
                        try:
                            st.success(st.session_state.message_10)
                            del st.session_state['message_4']
                            del st.session_state['message_2']
                        except:
                            pass
                    else:
                        st.success(st.session_state.message_4)
                elif st.session_state.message_4 != '':
                    st.error(st.session_state.message_4)

            if 'message_5' in st.session_state:
                if 'Updated' in st.session_state.message_5:
                    st.success(st.session_state.message_5)
                elif st.session_state.message_5 != '':
                    st.error(st.session_state.message_5)
        # ******************************************************
        if st.session_state.create_form_complete:
            if 'Completed!!!' in st.session_state.message_6:
                st.success(st.session_state.message_6)
                try:
                    del st.session_state['message_5']
                except:
                    pass
            else:
                st.error(st.session_state.message_6)
        # ******************************************************
        if st.session_state.create_syo_complete:
            if 'message_7' in st.session_state:
                if 'Completed' in st.session_state.message_7:
                    st.success(st.session_state.message_7)
                else:
                    st.error(st.session_state.message_7)
    with col4:
        col_right_prj_grid = grid([0.11, 0.2, 0.1, 0.1, 0.1, 0.15, 0.15], 1, vertical_align="top")
        col_right_prj_grid.markdown(
            f'<p style="text-align: center;'
            f'padding: 8px">出力を選択</p>',
            unsafe_allow_html=True)
        option_feedback_syo = ["仕様表", "FORM", "仕様表_BLANK"]

        if "selected_option_syo" not in st.session_state:
            st.session_state.selected_option_syo = option_feedback_syo[0]
        a_syo = st.session_state.selected_option_syo
        option = col_right_prj_grid.selectbox('output',
                                              option_feedback_syo,
                                              index=option_feedback_syo.index(st.session_state.selected_option_syo),
                                              placeholder="Select output...",
                                              label_visibility="collapsed",
                                              )
        st.session_state.selected_option_syo = option
        b_syo = st.session_state.selected_option_syo
        if a_syo != b_syo:
            st.rerun()
        col_right_prj_grid.write('')
        col_right_prj_grid.write('')
        col_right_prj_grid.write('')
        with col_right_prj_grid.container():
            if option == "仕様表":
                df = st.session_state.data_syo
            elif option == "FORM":
                if 'form' in st.session_state:
                    df = st.session_state.form
                else:
                    df = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)], index=range(1, 101)).fillna("")
            else:
                df = st.session_state.formspec_view
            num_columns = df.shape[1]
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                highlight_format_device_group = workbook.add_format(
                    {'bg_color': '#535353', 'font_color': '#FFFFFF'})
                highlight_format_device = workbook.add_format({'bg_color': '#245269', 'font_color': '#FFFFFF'})
                try:
                    for row_num, value in enumerate(df['auto'], start=1):
                        if str(value) is not None:
                            if str(value) in st.session_state.device_group:
                                for col_num in range(num_columns):
                                    worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num],
                                                    highlight_format_device_group)
                            if str(value) in st.session_state.device:
                                for col_num in range(num_columns):
                                    worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num],
                                                    highlight_format_device)

                except:
                    pass
            output.seek(0)

            if option == "仕様表":
                file_name = f"仕様表_{str(st.session_state.code).upper()}.xlsx"
            elif option == '仕様表_BLANK':
                file_name = "仕様表_BLANK.xlsx"
            else:
                file_name = "仕様表_FORM.xlsx"
            st.markdown('<span class="button-green"></span>', unsafe_allow_html=True)

            button_download_syo = st.download_button(label="ダウンロード", data=output, use_container_width=True,
                                                     icon=":material/cloud_download:",
                                                     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                                     key="button_download_syo",
                                                     file_name=file_name,
                                                     disabled=not (st.session_state.code != "" or option == 'FORM')
                                                     )

        with col_right_prj_grid.container():

            st.markdown('<span class="button-green"></span>', unsafe_allow_html=True)
            button_save_syo = st.button("保存", use_container_width=True, icon=":material/save:",
                                        disabled=not (option in ['仕様表'] and st.session_state.code != ""))
            if button_save_syo:
                st.session_state.view_syo_complete = False
                st.session_state.load_syo_complete = False
                st.session_state.create_form_complete = False
                st.session_state.create_syo_complete = False
                modal_save_syo.open()
        if modal_save_syo.is_open():
            with modal_save_syo.container():
                with st.spinner(text="In progress..."):
                    result_querry_region_4_gray, result_querry_region_4_blue = get_gray_blue(
                        st.session_state.code)
                    df, df_1 = dataframe_convert(st.session_state.data_syo_view, st.session_state.code,
                                                 result_querry_region_4_gray,
                                                 result_querry_region_4_blue)
                    update_data_new(st.session_state.code, df, df_1)
                    st.session_state.save_syo_complete = True
                    st.session_state.message_12 = 'Save Completed!!!'
                    modal_save_syo.close()

        if st.session_state.save_syo_complete:
            if 'message_12' in st.session_state:
                st.success(st.session_state.message_12)

        with col_right_prj_grid.container(border=True, key="view_inf_output"):

            if option == "仕様表":
                st.session_state.data_syo_view = st.data_editor(st.session_state.data_syo, height=625, width=10000,
                                                                disabled=['auto', 'gr', 'keyword',
                                                                          'CADICS ID', 'group_key_map', 'default'])
            elif option == "FORM":
                form_df_view = st.data_editor(st.session_state.form, height=625, width=10000,
                                              disabled=['auto', 'gr', 'keyword',
                                                        'CADICS ID', 'group_key_map', 'default'])
            else:
                st.session_state.formspec_view = st.data_editor(st.session_state.formspec, height=625, width=10000)
