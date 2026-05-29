# import streamlit as st
# import streamlit_antd_components as sac
# import importlib
#
# st.set_page_config(
#     page_title="My Streamlit App",
#     page_icon=":smiley:",
#     layout="wide"
# )
# # Tạo menu trong sidebar
# with st.sidebar:
#     selected_item = sac.menu(
#         [
#             sac.MenuItem('ログインページ', icon='1-circle-fill', children=[
#                 sac.MenuItem('ログインページ', icon='box-arrow-in-right'),
#             ]),
#             sac.MenuItem('メインメニュー', icon='2-circle-fill', children=[
#                 sac.MenuItem('仕様表作成', icon='emoji-angry'),
#                 sac.MenuItem('プロ管集約業務', icon='emoji-heart-eyes'),
#                 sac.MenuItem('Family開発対応', icon='emoji-dizzy'),
#             ]),
#             sac.MenuItem('管理', icon='3-circle-fill', children=[
#                 sac.MenuItem('アカウント管理', icon='person-fill-gear'),
#                 sac.MenuItem('データ削除', icon='trash3'),
#             ]),
#         ],
#         open_all=True,
#     )
#
# # Bản đồ tên hiển thị tới đường dẫn module
# menu_mapping = {
#     "ログインページ": "pages.メインメニュー.login",
#     "仕様表作成": "pages.ログインページ.syo",
#     "プロ管集約業務": "pages.ログインページ.prokan",
#     "Family開発対応": "pages.ログインページ.itest",
#     "アカウント管理": "pages.管理.manage_page",
#     "データ削除": "pages.管理.delete_data",
# }
#
# # Điều hướng tới module tương ứng
# if selected_item:
#     module_path = menu_mapping[selected_item]
#     # try:
#     module = importlib.import_module(module_path)
#     if hasattr(module, 'main'):
#         module.main()
#     else:
#         st.error(f"Module '{module_path}' không có hàm 'main()'.")
#     # except ModuleNotFoundError:
#     #     st.error(f"Không tìm thấy module '{module_path}'.")
# import streamlit as st
# import streamlit_antd_components as sac
# import importlib
#
# st.set_page_config(
#     page_title="My Streamlit App",
#     page_icon=":smiley:",
#     layout="wide"
# )
#
# # Kiểm tra trạng thái đăng nhập
# if 'is_logged_in' not in st.session_state:
#     st.session_state['is_logged_in'] = False
#
# # Tạo menu trong sidebar
# with st.sidebar:
#     selected_item = sac.menu(
#         [
#             sac.MenuItem('ログインページ', children=[
#                 sac.MenuItem('ログインページ', icon='box-arrow-in-right'),
#             ]),
#             sac.MenuItem('メインメニュー', children=[
#                 sac.MenuItem('仕様表作成', icon='1-circle-fill'),
#                 sac.MenuItem('プロ管集約業務', icon='2-circle-fill'),
#                 sac.MenuItem('Family開発対応', icon='3-circle-fill'),
#             ]),
#             sac.MenuItem('管理', children=[
#                 sac.MenuItem('アカウント管理', icon='person-fill-gear'),
#                 sac.MenuItem('データ削除', icon='trash3'),
#             ]),
#         ],
#         variant='filled',
#         color='blue', open_all=True,
#     )
# st.markdown(
#     """
#     <style>
#         section[data-testid="stSidebar"] {
#             width: 300px !important; # Set the width to your desired value
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )
# # Bản đồ tên hiển thị tới đường dẫn module
# menu_mapping = {
#     "ログインページ": "pages.メインメニュー.login",
#     "仕様表作成": "pages.ログインページ.syo",
#     "プロ管集約業務": "pages.ログインページ.prokan",
#     "Family開発対応": "pages.ログインページ.itest",
#     "アカウント管理": "pages.管理.manage_page",
#     "データ削除": "pages.管理.delete_data",
# }
#
# # Kiểm tra chuyển hướng sau khi đăng nhập
# if st.session_state['is_logged_in'] and 'next_page' in st.session_state:
#     selected_item = st.session_state['next_page']
#     del st.session_state['next_page']
#     # st.rerun()
#
# # Điều hướng tới module tương ứng
# if selected_item:
#     module_path = menu_mapping[selected_item]
#     # try:
#     module = importlib.import_module(module_path)
#     if hasattr(module, 'main'):
#         module.main()
#     else:
#         st.error(f"Module '{module_path}' không có hàm 'main()'.")
#     # except ModuleNotFoundError:
#     #     st.error(f"Không tìm thấy module '{module_path}'.")
import streamlit as st
import streamlit_antd_components as sac
import importlib

# Cấu hình ứng dụng
st.set_page_config(
    page_title="My Streamlit App",
    page_icon=":smiley:",
    layout="wide"
)
# Kiểm tra trạng thái đăng nhập
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False
# Tạo menu trong sidebar
with st.sidebar:
    selected_item = sac.menu(
        [
            sac.MenuItem('ログインページ', children=[
                sac.MenuItem('ログインページ', icon='box-arrow-in-right'),
            ]),
            sac.MenuItem('メインメニュー', children=[
                sac.MenuItem('仕様表作成', icon='1-circle-fill'),
                sac.MenuItem('プロ管集約業務', icon='2-circle-fill'),
                sac.MenuItem('Family開発対応', icon='3-circle-fill'),
            ]),
            sac.MenuItem('管理', children=[
                sac.MenuItem('アカウント管理', icon='person-fill-gear'),
                sac.MenuItem('データ削除', icon='trash3'),
            ]),
        ],
        variant='filled',
        color='blue',
        open_all=True,
    )
# Cập nhật trạng thái vào session_state
# Đồng bộ trạng thái `next_page` với `selected_item`
if st.session_state['is_logged_in'] and 'next_page' in st.session_state:
    if selected_item == 'ログインページ':
        selected_item = st.session_state['next_page']  # Cập nhật trạng thái từ next_page
    else:
        if selected_item != st.session_state['next_page']:
            st.session_state['next_page'] = selected_item
            # list_all_message = [f'message_{i + 1}' for i in range(12)]
            # for item in list_all_message:
            #     try:
            #         del st.session_state[item]
            #     except:
            #         pass
            for var_status in ['view_syo_complete', 'load_syo_complete', 'create_form_complete',
                               'create_syo_complete', 'save_syo_complete', 'load_prokan_complete',
                               'create_cadics_complete', 'create_output_complete',
                               'view_prokan_complete', 'save_prokan_complete']:
                st.session_state[var_status] = False
        else:
            selected_item = st.session_state['next_page']
    # del st.session_state['next_page']  # Xóa next_page sau khi xử lý
# Bản đồ tên hiển thị tới đường dẫn module
menu_mapping = {
    # "ログインページ": "pages.メインメニュー.login",
    "ログインページ": "xqa_web_tvso.app.pages.メインメニュー.login",
    "仕様表作成": "xqa_web_tvso.app.pages.ログインページ.syo",
    "プロ管集約業務": "xqa_web_tvso.app.pages.ログインページ.prokan",
    "Family開発対応": "xqa_web_tvso.app.pages.ログインページ.itest",
    "アカウント管理": "xqa_web_tvso.app.pages.管理.manage_page",
    "データ削除": "xqa_web_tvso.app.pages.管理.delete_data",
}
# Điều hướng tới module tương ứng
if selected_item:
    module_path = menu_mapping[selected_item]
    module = importlib.import_module(module_path)
    # Kiểm tra xem name_user có tồn tại trong session_state không
    if not st.session_state['is_logged_in'] and selected_item != 'ログインページ':
        st.error("Please login before running app!!!")
    else:
        if hasattr(module, 'main'):
            module.main()
        else:
            st.error(f"Module '{module_path}' không có hàm 'main()'.")
    # if hasattr(module, 'main'):
    #     module.main()
    # else:
    #     st.error(f"Module '{module_path}' không có hàm 'main()'.")
