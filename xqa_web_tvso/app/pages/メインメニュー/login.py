import sys
import os
import jwt

from xqa_web_tvso.app.logics.syo.db.funtion_database import add_new_user, get_user_role
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import streamlit as st
import webbrowser

# from xqa_web_tvso.app.logics.syo.db.funtion_database import log_in_tvso
from xqa_web_tvso.app.setting import (
    app_client_id,
    app_client_secret,
    valid_email_domain,
    permission_default,
    project_default)
import auth
from logger import logger

def main():
    st.markdown(
        r"""
        <style>
        .stMainBlockContainer {
            padding-left: 25%;
            padding-right: 30%;
        }
        div.st-key-another_unique_key > div > button, div.st-key-confirm_sign_up > div > button, div.st-key-back_to_sign_in > div > button{
                background-color: rgb(255,255,255);
                color: rgb(85,150,210);
                border: None;
                text-decoration: underline;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    if 'show_sign_in' not in st.session_state:
        st.session_state.show_sign_in =  True
    
    if 'show_sign_up' not in st.session_state:
        st.session_state.show_sign_up =  False
    
    if 'ChallengeName' not in st.session_state:
        st.session_state.ChallengeName =  None

    if st.session_state.show_sign_in:
        st.session_state.session = None
        st.session_state.secret_hash = None
        st.session_state.email = None
        
        st.header("XQA集約業務1本化 Website ")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        # Sử dụng session state để lưu trạng thái của các nút
        if 'button_clicked' not in st.session_state:
            st.session_state.button_clicked = False

        if st.button("Login"):
            st.session_state.button_clicked = True
            # Check if the username and password are correct
            try:
                valid_email = auth.validate_email_address(email, valid_email_domain)
                if not valid_email:
                    raise Exception('Your email address is invalid!!!')
                
                response = auth.login(email, password, app_client_id, app_client_secret)
                set_auth(email, response)
            except Exception as e:
                st.error(f"ERROR: Login failed. Try again! {e}")

        # When button is clicked, update state
        if st.session_state.show_sign_in:
            if st.button("I don't have account", key="another_unique_key"):
                st.session_state.show_sign_in = False
                st.session_state.show_sign_up = True
                st.rerun()

    if st.session_state.show_sign_up:
        st.session_state.session = None
        st.header("Sign-Up")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Password Confirmation", type="password")

        if st.button("Submit"):
            if not email or not password or not confirm_password:
                st.warning("Please fill in all information.")
            elif password != confirm_password:
                st.error("Confirmation password does not match.")
            else:
                try:
                    valid_email = auth.validate_email_address(email, valid_email_domain)
                    if not valid_email:
                        raise Exception('Your email address is invalid!!!')

                    secret_hash = auth.get_secret_hash(email, app_client_id, app_client_secret)
                    username =  email.split('@')[0]
                    session = auth.sign_up(email, password, username, app_client_id, secret_hash)
                    
                    st.session_state.session = session
                    st.session_state.secret_hash = secret_hash
                    st.session_state.email = email
                    
                    st.session_state.show_sign_up = False
                    
                    st.rerun()  # Refresh to re-render layout
                except Exception as e:
                    st.error(f"{e}")

        if st.button("Confirm Sign-Up", key='confirm_sign_up'):
                st.session_state.show_sign_in = False
                st.session_state.show_sign_up = False
                st.rerun()

    if st.session_state.email:
        st.markdown(
            r"""
            <style>
            .stHorizontalBlock {
                width: 15rem;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.header("Confirm Email OTP Code")
        email = st.session_state.email if st.session_state.email else None
        st.success(f"Authentication successful! Please check your email and enter the confirmation code")
        confirmation_code = st.text_input("ConfirmationCode")
        try:
            if st.button("Confirm", key='confirm_btn'):
                secret_hash = auth.get_secret_hash(email, app_client_id, app_client_secret)
                if st.session_state.ChallengeName == "EMAIL_OTP":
                    challenge_response = {
                        "EMAIL_OTP_CODE": confirmation_code,
                        "USERNAME": email,
                        "SECRET_HASH": secret_hash
                    }
                    response = auth.response_to_auth_challenge(
                        app_client_id,
                        st.session_state.ChallengeName,
                        st.session_state.session,
                        challenge_response)

                    set_auth(email, response)
                else:  
                    response = auth.confirm_user_sign_up(
                        email,
                        app_client_id,
                        secret_hash,
                        confirmation_code)

                    username =  email.split('@')[0]
                    completed = add_new_user(username, permission_default, project_default)
            
                    if not completed:
                        raise Exception('Account authorization failed!!!')

                    st.session_state.session = None
                    st.session_state.secret_hash = None
                    st.session_state.email = None
                    st.session_state.show_sign_in = True
                    st.rerun()

        except Exception as e:
            st.session_state.show_sign_in = False
            st.error(f"{e}")

    if not st.session_state.email and not st.session_state.show_sign_in and not st.session_state.show_sign_up:
        st.session_state.session = None

        st.header("Resend Confirmation Sign-Up Code")
        email = st.text_input("Email", key='resend_code_email')
        if st.button("Resend", key="resend_code_btn"):
            try:
                valid_email = auth.validate_email_address(email, valid_email_domain)
                if not valid_email:
                    raise Exception('Your email address is invalid!!!')
                secret_hash = auth.get_secret_hash(email, app_client_id, app_client_secret)

                auth.resend_confirmation_code(
                    app_client_id,
                    secret_hash,
                    email)
                st.session_state.email = email
                st.session_state.secret_hash = secret_hash
                st.rerun()
            except Exception as e:
                st.error(f"{e}")

    if not st.session_state.show_sign_in:
        if st.button("Back to Sign-In page", key="back_to_sign_in"):
            st.session_state.session = None
            st.session_state.show_sign_in = True
            st.session_state.show_sign_up = False
            st.rerun()
                    
def set_auth(email, response):
    if 'ChallengeName' not in response:
        id_token = response['AuthenticationResult']['IdToken']
        payload = jwt.decode(id_token, options={"verify_signature": False})
        user = get_user_role(payload['name'])

        if user.permission is not None:
            st.session_state.position = user.permission
            st.session_state.name_user = user.username
            st.session_state.project_query = user.project
            st.session_state['is_logged_in'] = True
            st.session_state['next_page'] = '仕様表作成'
            # print("st.session_state['next_page']: ", st.session_state['next_page'])
            st.success("Login successful!")
            st.rerun()
        else:
            st.session_state.position = None
            st.error("Login failed. Please check your credentials.")
    else:
        session = response['Session']
        st.session_state.session = session
        st.session_state.ChallengeName = response['ChallengeName']
        st.session_state.show_sign_in =False
        st.session_state.email = email
        st.rerun()

# Hàm để chuyển hướng đến một URL
def open_url(url):
    webbrowser.open_new_tab(url)
