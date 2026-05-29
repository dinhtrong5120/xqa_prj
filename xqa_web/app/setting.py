import sys
import os
import streamlit as st
from streamlit_extras.grid import grid
from decouple import config
import warnings

warnings.filterwarnings("ignore")

# Đường dẫn gốc của dự án
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
BASE_DIR_STATICS = os.path.join(BASE_DIR, 'statics', 'css')
BASE_DIR_PAGES = os.path.join(BASE_DIR, 'pages')
BASE_DIR_LOGICS = os.path.join(BASE_DIR, 'logics')
BASE_DIR_DATAS = os.path.join(BASE_DIR, 'datas')
BASE_DIR_OUTPUTS = os.path.join(BASE_DIR, 'outputs')
BASE_DIR_HISTORY_FILE = os.path.join(BASE_DIR, 'logics', 'syo', 'db', 'your_file.txt')
BASE_DIR_CADICS_TEMP = os.path.join(BASE_DIR, 'cadic_temp')
BASE_DIR_FORM_OUT = os.path.join(BASE_DIR, 'form_out')

# Bảo mật
SECRET_KEY = 'your-secret-key'
DEBUG = True
ALLOWED_HOSTS = []

# Ứng dụng đã cài đặt
INSTALLED_APPS = [
    'syo',
    'syo',
    'syo',
    # Your apps
]

ROOT_URLCONF = 'my_project.urls'

user_pool_id = config('USER_POOL_ID')
app_client_id = config('APP_CLIENT_ID')
app_client_secret = config('APP_CLIENT_SECRET')

valid_email_domain = ['local.nmcorp.nissan.biz', 'mail.nissan.co.jp']
permission_default = 'admin'
project_default = 'ALL'

# Cơ sở dữ liệu
# Load environment variables
SECRET_KEY = config('DJANGO_SECRET_KEY', default='fallback-secret-key')
DEBUG = config('DEBUG', default=False, cast=bool)
DATABASE = {
    "NAME": config("DB_NAME"),
    "USER": config("DB_USER"),
    "PASSWORD": config("DB_PASSWORD"),
    "HOST": config("DB_HOST", default="localhost"),  # Default host
    "SYO": config("DB_NAME_SYO"),
}

# Mật khẩu
AUTH_PASSWORD_VALIDATORS = [
]

# Ngôn ngữ và múi giờ
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Load CSS from file
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


HORIZONTAL_RED = "./xqa_web/app/statics/image/icon_nissan.png"
ICON_RED = "./xqa_web/app/statics/image/c_red.png"
# st.logo(HORIZONTAL_RED, size="large", icon_image=ICON_RED)

# st.set_page_config(
#     page_title="My Streamlit App",
#     page_icon=":smiley:",
#     layout="wide"

# Define your valid keywords
VALID_KEY_車両仕様表サンプル = [
    "車両仕様表_Form", "車両仕様表_"
]
