from xqa_web_tvso.app.setting import *
import pandas as pd
import numpy as np
import streamlit_antd_components as sac
from xqa_web_tvso.app.logics.itest.itest_btn_man import run_btn_inteligent_test, get_link_folder_output , get_data_folder
import os
import io
from xqa_web_tvso.app.logics.prokan.read_data_view import zip_folder
from xqa_web_tvso.app.logics.itest.itest_compare_youbouhyo_suse_ato import run_compare_youbouhyo_suse_ato
from xqa_web_tvso.app.logics.itest.edit_file import save_itest
from xqa_web_tvso.app.logics.itest.upload_itest import *

# from xqa_web_tvso.app.setting import BASE_DIR_OUTPUTS, BASE_DIR_DATAS
# st.set_page_config(
# page_title="My Streamlit App",
# page_icon=":smiley:",
# layout="wide"
# )
def get_list_out_put(folder_output_itest_path):
    list_output = []
    list_output.extend(os.listdir(folder_output_itest_path))
    return list_output


def main():
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
    col1, col2 = st.columns([24, 4.5])
    with col1:
        st.markdown(
            f'<h2 style="text-align: center;'
            f'background: linear-gradient(to right, #000046, #1cb5e0);'
            f'border: 2px solid #D9D9D9; '
            f'border-radius: 10px;'
            f'color:azure;'
            f'padding: 10px">ステップ３ : Family開発対応</h2>',
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
    with col3:
        with st.container(border=True, key="データアップデート"):
            col_left_prj_grid = grid(1, 1, 1, 1, 1, vertical_align="top")
            col_left_prj_grid.subheader('データアップデート')

            col_left_prj_grid.text_input("Model Code", key="code_itest")

            col_left_prj_grid.markdown('ファイルをインポート :blue[ ( AABB表, VC要件表 ) ] ')
            files = col_left_prj_grid.file_uploader("", accept_multiple_files=True, label_visibility="collapsed",
                                                    key='uploader_itest')
            # col_left_prj_grid.button('ファイル読み込む', use_container_width=True, help="ABCXYZZZ", icon=":material/upload:",label_visibility ="collapsed")
            button_upload_itest = col_left_prj_grid.button("ファイル読み込む", use_container_width=True)
            if button_upload_itest:
                if len(files) > 0:
                    update_file_itest(st.session_state.code_itest, files, csrf_token)
        with st.container(border=True, key="PROJ情報入力"):
            col_left_prj_grid_2 = grid(1, [0.2, 0.8],1, [0.2, 0.8],1, vertical_align="top")
            col_left_prj_grid_2.subheader('PROJ情報入力')
            # col_left_prj_grid_2.button('ベース', use_container_width=True)
            col_left_prj_grid_2.markdown(
                f'<p style="text-align: center;'
                # f'border: 2px solid #D9D9D9; '
                f'padding: 8px">ベース</p>',
                unsafe_allow_html=True)
            st.markdown(
                f"""
                <style>
                    .st-el {{
                        max-width: 400px !important;
                    }}
                </style>""",
                unsafe_allow_html=True,
            )

            # _________________________________________
            folder_car_base = []
            for folder_name in os.listdir(BASE_DIR_OUTPUTS):
                folder_path = os.path.join(BASE_DIR_OUTPUTS, folder_name)
                if os.path.isdir(folder_path):
                    folder_car_base.append(folder_name)
            # _________________________________________
            #-----------1 base
            options_car_base = col_left_prj_grid_2.selectbox('taiso',
                                                              folder_car_base,
                                                              index=None,
                                                              placeholder="Select 対象...",
                                                              label_visibility="collapsed",
                                                              key='itest'
                                                              )
            list_options_car_base = []
            if options_car_base is None :
                list_options_car_base = []
            else:
                list_options_car_base.append(options_car_base)
            #-----------2 base
            # list_options_car_base = col_left_prj_grid_2.multiselect(
            #     "Select ベース...",
            #     folder_car_base, label_visibility="collapsed", key='itest'
            # )
            #--------------------------------------------------------------------
            write_check_base = check_input_base(list_options_car_base)
            if write_check_base == "":
                # pass
                col_left_prj_grid_2.write("")
            else:
                col_left_prj_grid_2.error(write_check_base)
            col_left_prj_grid_2.markdown(
                f'<p style="text-align: center;'
                # f'border: 2px solid #D9D9D9; '
                f'padding: 8px">対象</p>',
                unsafe_allow_html=True)

            # _________________________________________
            folder_car_taiso = []
            for folder_name in os.listdir(BASE_DIR_OUTPUTS):
                folder_path = os.path.join(BASE_DIR_OUTPUTS, folder_name)
                if os.path.isdir(folder_path):
                    folder_car_taiso.append(folder_name)
            # _________________________________________

            options_car_taiso = col_left_prj_grid_2.selectbox('taiso',
                                                              folder_car_taiso,
                                                              index=None,
                                                              placeholder="Select 対象...",
                                                              label_visibility="collapsed",
                                                              )
            write_check_taiso = check_input_taiso(options_car_taiso)
            if write_check_taiso == "":
                col_left_prj_grid_2.write("")
            else:
                col_left_prj_grid_2.error(write_check_taiso)

        with st.container(border=True, key="計算"):
            col_left_prj_grid_3 = grid(1, [0.2, 0.8], [0.2, 0.8], vertical_align="top")
            col_left_prj_grid_3.subheader('計算')

            # Tạo một container trong Streamlit
            with col_left_prj_grid_3.container():
                button_item = sac.ButtonsItem(icon=sac.BsIcon(name='1-circle-fill', size=20, color='black'))
                sac.buttons([button_item], align='center', variant='text', color='white')

            if 'state_input' not in st.session_state:
                st.session_state.state_input = False

            if write_check_taiso != "" or write_check_base != "" or options_car_taiso is None or list_options_car_base == []:
                st.session_state.state_input = False
            else: 
                st.session_state.state_input = True

            btn_inteligent_test = col_left_prj_grid_3.button("車両要望表計算", use_container_width=True,disabled=not st.session_state.state_input)
            if btn_inteligent_test:
                with st.spinner(text="In progress..."):
                    if options_car_taiso is None or list_options_car_base == []:
                        vote('Select ベース and 対象 to run the program')
                    else:
                        if options_car_taiso in list_options_car_base:
                            vote('Do not re-select 対象 in ベース list.')
                        else:
                            message = run_btn_inteligent_test(list_options_car_base, options_car_taiso)
                            vote(message)

            with col_left_prj_grid_3.container():
                button_item = sac.ButtonsItem(icon=sac.BsIcon(name='2-circle-fill', size=20, color='black'))
                sac.buttons([button_item], align='center', variant='text', color='white')

            btn_inteligent_compare = col_left_prj_grid_3.button("配車要望表比較", use_container_width=True, disabled=not st.session_state.state_input)
            if btn_inteligent_compare:
                with st.spinner(text="In progress..."):
                    if options_car_taiso is None or list_options_car_base == []:
                        vote('Select ベース and 対象 to run the program')
                    else:
                        if options_car_taiso in list_options_car_base:
                            vote('Do not re-select 対象 in ベース list.')
                        else:
                            message = run_compare_youbouhyo_suse_ato(list_options_car_base, options_car_taiso)
                            vote(message)

        with st.container(border=True, key="データ表示"):
            col_left_prj_grid_4 = grid(1, 1, vertical_align="top")
            col_left_prj_grid_4.subheader('データ表示')
            button_view_itest = col_left_prj_grid_4.button("表示", use_container_width=True, help='VIEW',disabled=not st.session_state.state_input)
            # _____________________lấy các output trong folder output

            if "output_itest" not in st.session_state or options_car_taiso is None or list_options_car_base == []:
                st.session_state.output_itest = []

            if 'download_enabled' not in st.session_state or options_car_taiso is None or list_options_car_base == []:
                st.session_state.download_enabled = False

            if button_view_itest:
                with st.spinner(text="In progress..."):
                    view_list_output(list_options_car_base, options_car_taiso)

            # ________________________________________
    with col4:
        # with st.container(border=True,key="select_inf_output"):
        col_right_prj_grid = grid([0.11, 0.2, 0.1, 0.1, 0.1, 0.15, 0.15], [0.11, 0.2, 0.1, 0.1, 0.1, 0.15, 0.15], 1,
                                  vertical_align="top")
        # col_right_prj_grid.button('出力を選択', use_container_width=True, disabled=False)
        col_right_prj_grid.markdown(
            f'<p style="text-align: center;'
            # f'border: 2px solid #D9D9D9; '
            f'padding: 8px">出力を選択</p>',
            unsafe_allow_html=True)

        option_output = col_right_prj_grid.selectbox('output',
                                                     st.session_state.output_itest,
                                                     index=None,
                                                     placeholder="Select output...",
                                                     label_visibility="collapsed",
                                                     )
        # _____________________lấy các file tồn tại trong folder output

        if "file_output_itest" not in st.session_state or st.session_state.output_itest == []:
            st.session_state.file_output_itest = []
        
        view_list_file(list_options_car_base, options_car_taiso,option_output)
            # _________________________________________
        col_right_prj_grid.write('')
        col_right_prj_grid.write('')
        col_right_prj_grid.write('')
        col_right_prj_grid.write('')
        col_right_prj_grid.write('')

        col_right_prj_grid.markdown(
            f'<p style="text-align: center;'
            f'padding: 8px">ファイルを選択</p>',
            unsafe_allow_html=True)
        option_file = col_right_prj_grid.selectbox('file',
                                                   st.session_state.file_output_itest,
                                                   index=None,
                                                   placeholder="Select file...",
                                                   label_visibility="collapsed",
                                                   )
        # _____________________lấy các sheet có trong file

        if "sheet_output_itest" not in st.session_state or st.session_state.file_output_itest == [] or st.session_state.output_itest == []:
            st.session_state.sheet_output_itest = []
        view_list_sheet(list_options_car_base, options_car_taiso,option_output,option_file)
        # _________________________________________
        col_right_prj_grid.markdown(
            f'<p style="text-align: center;'
            f'padding: 8px">シート名</p>',
            unsafe_allow_html=True)
        option_sheet = col_right_prj_grid.selectbox('sheet',
                                                    st.session_state.sheet_output_itest,
                                                    index=None,
                                                    placeholder="Select sheet...",
                                                    label_visibility="collapsed",
                                                    )
        col_right_prj_grid.write('')

        with col_right_prj_grid.container():
            st.markdown('<div class="button-green"></span>', unsafe_allow_html=True)
            st.download_button(
                label="ダウンロード",
                data=get_data(write_check_taiso,write_check_base, list_options_car_base, options_car_taiso),
                file_name=get_file_name_zip(list_options_car_base, options_car_taiso),
                mime="application/zip",
                use_container_width=True,
                disabled=not st.session_state.download_enabled
            )
        if 'save_enabled' not in st.session_state:
            st.session_state.save_enabled = False

        if option_output is not None and option_file is not None and option_sheet is not None:
            st.session_state.save_enabled = True
        else: 
            st.session_state.save_enabled = False

        with col_right_prj_grid.container():
            st.markdown('<div class="button-green"></span>', unsafe_allow_html=True)
            button_save_itest = st.button("保存", use_container_width=True, icon=":material/save:",
                                          disabled=not st.session_state.save_enabled)
            
            if 'edit_df' not in st.session_state:
                st.session_state.edit_df = []
            if 'original_df' not in st.session_state:
                st.session_state.original_df = []

            if button_save_itest : 
                with st.spinner(text="In progress..."):
                    folder_output_itest_path = get_link_folder_output(list_options_car_base, options_car_taiso)
                    message = save_itest(folder_output_itest_path,option_output,option_file,option_sheet,st.session_state.edit_df,st.session_state.original_df)
                    vote(message)

        with col_right_prj_grid.container(border=True, key="view_inf_output"):
            # _____________________view df theo sheet đã chọn

            with st.spinner(text="In progress..."):
                view_data(list_options_car_base, options_car_taiso,option_output,option_file,option_sheet)

@st.dialog("Notification")
def vote(item):
    item = str(item)
    message_with_line_breaks = item.replace("\n", "<br>")
    st.markdown(message_with_line_breaks, unsafe_allow_html=True)

def check_input_taiso(taiso_car):
    if taiso_car is None:
        warning_input = ""
    else:
        # điều kiện 1 của taiso
        list_file_warnig=[]
        file_youbou_taiso_path = os.path.join(BASE_DIR_OUTPUTS,taiso_car,"Car配車要望表.xlsx")
        if os.path.exists(file_youbou_taiso_path):
            pass
        else:
            list_file_warnig.append("Car配車要望表.xlsx")

        # điều kiện 2 của taiso
        file_aabb = os.path.join(BASE_DIR_DATAS, "AABB表.xlsx")
        if os.path.exists(file_aabb):
            pass
        else:
            list_file_warnig.append("file AABB表.xlsx")

        # điều kiện 3 của taiso
        folder_data = get_data_folder(taiso_car)
        folder_vc = os.path.join(folder_data, "VC簡素化要件表")
        if os.path.exists(folder_vc):
            pass
        else:
            list_file_warnig.append("folder VC簡素化要件表")

        # điều kiện 4 của taiso
        if os.path.exists(folder_data):
            files_in_folder = os.listdir(folder_data)
            if any('関連表3' in file for file in files_in_folder):
                pass
            else:
                list_file_warnig.append("file 関連表3")
        else:
            list_file_warnig.append("file 関連表3")

        warning_input = ""
        if list_file_warnig !=[]:
            warning_input = f"MISSING FILE: \\\n "  + f"'{taiso_car}' : " + f"{list_file_warnig}"

    return warning_input

    
def check_input_base(list_base_car):
    if list_base_car == [] :
        warning_input = ""
    else: 
        # điều kiện của base
        warning_input_base = []
        for car in list_base_car:
            file_youbou_base_path = os.path.join(BASE_DIR_OUTPUTS,car,"Car配車要望表.xlsx")
            if os.path.exists(file_youbou_base_path):
                pass
            else:
                warning_input_base.append(f"'{car}' : [ Car配車要望表.xlsx ]")
                # warning_input_base = warning_input_base + f"'{car}' : [ Car配車要望表.xlsx ] \n "

        warning_input = ""
        if warning_input_base !=[]:
            warning_input = "MISSING FILE : "
            for wr in warning_input_base :
                warning_input = warning_input + " \n " + wr

    return warning_input

            
def get_data(write_check_taiso,write_check_base,list_options_car_base, options_car_taiso):
    if list_options_car_base == [] or options_car_taiso is None or write_check_taiso != "" or write_check_taiso !="":
        return 'abc'
    else:
        folder_output_itest = get_link_folder_output(list_options_car_base, options_car_taiso)
        if folder_output_itest == "":
            return 'abc'
        else:
            folder_output_itest = folder_output_itest.replace("\\", "/")
            if os.path.exists(folder_output_itest):
                zip_folder(folder_output_itest, folder_output_itest + '.zip')
                with open(folder_output_itest + ".zip", "rb") as fp:
                    zip_content = fp.read()
            return io.BytesIO(zip_content)


def get_file_name_zip(list_options_car_base, options_car_taiso):
    filename = ""
    if list_options_car_base == [] or options_car_taiso is None:
        pass
    else:
        folder_output_itest = get_link_folder_output(list_options_car_base, options_car_taiso)
        if folder_output_itest == "":
            pass
        else:
            name = os.path.basename(folder_output_itest)
            filename = options_car_taiso + name + ".zip"
            # print("filename: ",filename)
    return filename


def view_list_output(list_options_car_base, options_car_taiso):
    if options_car_taiso is None or list_options_car_base == []:
        vote('select 対象 and ベース to view output')
    else:
        if options_car_taiso in list_options_car_base:
            vote('Do not re-select 対象 in ベース list.')
        else:
            folder_output_itest_path = get_link_folder_output(list_options_car_base, options_car_taiso)
            if folder_output_itest_path == "":
                vote('Output does not exist')
            else:
                st.session_state.download_enabled = True
                list_output = get_list_out_put(folder_output_itest_path)
                if list_output == []:
                    # thông báo con xe chưa có output
                    st.session_state.output_itest = list_output
                    vote('No output')
                else:
                    st.session_state.output_itest = list_output


def view_list_file(list_options_car_base, options_car_taiso,option_output):
    list_file = []
    if option_output is None :
        pass
    else:
        folder_output_itest_path = get_link_folder_output(list_options_car_base, options_car_taiso)
        file_path_output_select = os.path.join(folder_output_itest_path, option_output)

        if os.path.isfile(file_path_output_select):
            list_file.append(option_output)
        elif os.path.isdir(file_path_output_select):
            list_file.extend(os.listdir(file_path_output_select))
        else:
            print('base_file_path khong phai duong dan')

    st.session_state.file_output_itest = list_file


def view_list_sheet(list_options_car_base, options_car_taiso,option_output,option_file):
    list_sheet = []
    file_select_path = ''
    if option_file is None or option_output is None :
        pass
    else:   
        folder_output_itest_path = get_link_folder_output(list_options_car_base, options_car_taiso)
        file_select_path = os.path.join(folder_output_itest_path, option_output)

        if os.path.isfile(file_select_path):
            pass
        else:
            file_select_path = os.path.join(folder_output_itest_path, option_output, option_file)

    # Kiểm tra xem tệp có tồn tại không
    if os.path.exists(file_select_path):
        list_sheet = pd.ExcelFile(file_select_path).sheet_names
    st.session_state.sheet_output_itest = list_sheet


def view_data(list_options_car_base, options_car_taiso,option_output,option_file,option_sheet):
    file_select_path = ""
    # df_output = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)], index=range(1, 101)).fillna("")
    if option_output is None or option_file is None or option_sheet is None:
        pass
    else:
        folder_output_itest_path = get_link_folder_output(list_options_car_base, options_car_taiso)
        file_select_path = os.path.join(folder_output_itest_path, option_output)

        if not os.path.isfile(file_select_path):
            file_select_path = os.path.join(folder_output_itest_path, option_output, option_file)

    # Kiểm tra xem tệp có tồn tại không
    if os.path.isfile(file_select_path):
        df_output = pd.read_excel(file_select_path, sheet_name=option_sheet).fillna("")
        st.session_state.original_df = df_output
    else:
        df_output = pd.DataFrame(columns=[f'Column_{i + 1}' for i in range(30)], index=range(1, 101)).fillna("")

    # _________________________________________

    if not df_output.empty:
        edited_df = st.data_editor(df_output, height=775, width=10000)
        st.session_state.edit_df = edited_df
    else:
        st.data_editor(df_output, height=775, width=10000)
