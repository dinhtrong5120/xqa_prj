import pandas as pd
import streamlit
from sqlalchemy import ForeignKeyConstraint, Column, String, Integer, ForeignKey, create_engine, update, and_
from .region1 import *
from sqlalchemy import func
import numpy as np
from ..convert_data_syo import *
import mysql.connector
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, aliased
import streamlit as st
import decouple
from hashlib import sha256
import os
import shutil
from xqa_web.app.setting import *
from xqa_web.app.setting import BASE_DIR_DATAS
Base = declarative_base()

import logging
from datetime import datetime
import traceback

def setup_logger(log_file='log_syo.txt'):
    logger = logging.getLogger('syo_logger')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(fh)
    return logger

logger = setup_logger()

class CommentColumn(Base):
    __tablename__ = 'comment_column'

    comment_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    comment_name = Column(String(45), nullable=False, unique=True)


class Config(Base):
    __tablename__ = 'config'

    config_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    config_name = Column(String(45), nullable=False, unique=True)


class Device(Base):
    __tablename__ = 'device'

    device_name = Column(String(255), primary_key=True, nullable=False)
    device_group = Column(String(255), nullable=True)

    device_details = relationship("DeviceDetails", back_populates="device")
    project_devices = relationship("ProjectDevice", back_populates="device")


class DeviceDetails(Base):
    __tablename__ = 'device_details'

    device_details_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    device_name = Column(String(255), ForeignKey('device.device_name', ondelete='CASCADE', onupdate='CASCADE'),
                         nullable=False)
    device_details_name = Column(String(255), nullable=True, unique=True)
    group_detail = Column(String(255), nullable=True)
    option_detail = Column(String(500), nullable=True)
    auto_detail = Column(String(255), nullable=True)
    group_key_map = Column(String(255), nullable=False, default='default_key')
    default = Column(String(45))

    device = relationship("Device", back_populates="device_details")

    __table_args__ = (
        ForeignKeyConstraint(
            ['device_name'],
            ['device.device_name']
        ),
        {'sqlite_autoincrement': True}
    )


class InformationProject(Base):
    __tablename__ = 'information_project'

    parameter_name = Column(String(255), primary_key=True, nullable=False)
    group_infor = Column(String(255), nullable=True)
    keyword = Column(String(255), nullable=True)
    auto_infor = Column(String(255), nullable=True)


class Lot(Base):
    __tablename__ = 'lot'

    lot_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    lot_name = Column(String(45), nullable=False, unique=True)


class OptionCode(Base):
    __tablename__ = 'optioncode'

    config_id = Column(Integer, ForeignKey('config.config_id', ondelete='CASCADE', onupdate='CASCADE'),
                       primary_key=True, nullable=False)
    project_id = Column(Integer, ForeignKey('project.project_id', ondelete='CASCADE', onupdate='CASCADE'),
                        primary_key=True, nullable=False)
    optioncode_value = Column(String(45), nullable=True)


class Project(Base):
    __tablename__ = 'project'

    project_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    project_name = Column(String(45), nullable=False, unique=True)

    project_devices = relationship("ProjectDevice", back_populates="project")


class ProjectDevice(Base):
    __tablename__ = 'project_device'

    device_name = Column(String(255), ForeignKey('device.device_name', ondelete='CASCADE', onupdate='CASCADE'),
                         primary_key=True, nullable=False)
    project_id = Column(Integer, ForeignKey('project.project_id', ondelete='CASCADE', onupdate='CASCADE'),
                        primary_key=True, nullable=False)

    device = relationship("Device", back_populates="project_devices")
    project = relationship("Project", back_populates="project_devices")


class ProjectDeviceComment(Base):
    __tablename__ = 'project_device_comment'

    project_id = Column(Integer, ForeignKey('project.project_id', ondelete='CASCADE', onupdate='CASCADE'),
                        primary_key=True, nullable=False)
    device_details_id = Column(Integer,
                               ForeignKey('device_details.device_details_id', ondelete='CASCADE', onupdate='CASCADE'),
                               primary_key=True, nullable=False)
    comment_id = Column(Integer, ForeignKey('comment_column.comment_id', ondelete='CASCADE', onupdate='CASCADE'),
                        primary_key=True, nullable=False)
    comment_detail = Column(String(500), nullable=True)


class StatusConfigDeviceDetail(Base):
    __tablename__ = 'status_config_device_detail'

    device_details_id = Column(Integer,
                               ForeignKey('device_details.device_details_id', ondelete='CASCADE', onupdate='CASCADE'),
                               primary_key=True, nullable=False)
    config_id = Column(Integer, ForeignKey('config.config_id', ondelete='CASCADE', onupdate='CASCADE'),
                       primary_key=True, nullable=False)
    project_id = Column(Integer, ForeignKey('project.project_id', ondelete='CASCADE', onupdate='CASCADE'),
                        primary_key=True, nullable=False)
    status = Column(String(255), nullable=True)


class StatusLotConfig(Base):
    __tablename__ = 'status_lot_config'

    project_id = Column(Integer, ForeignKey('project.project_id', ondelete='CASCADE', onupdate='CASCADE'),
                        primary_key=True, nullable=False)
    config_id = Column(Integer, ForeignKey('config.config_id', ondelete='CASCADE', onupdate='CASCADE'),
                       primary_key=True, nullable=False)
    lot_id = Column(Integer, ForeignKey('lot.lot_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                    nullable=False)
    status = Column(String(45), nullable=True)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=True)
    permission = Column(String(45), nullable=True)
    project = Column(String(255), nullable=False)


class ValueInf(Base):
    __tablename__ = 'value_inf'

    project_id = Column(Integer, ForeignKey('project.project_id', ondelete='CASCADE', onupdate='CASCADE'),
                        primary_key=True, nullable=False)
    config_id = Column(Integer, ForeignKey('config.config_id', ondelete='CASCADE', onupdate='CASCADE'),
                       primary_key=True, nullable=False)
    parameter_name = Column(String(255),
                            ForeignKey('information_project.parameter_name', ondelete='CASCADE', onupdate='CASCADE'),
                            primary_key=True, nullable=False)
    value = Column(String(45), nullable=True)


def connect_db():
    database_username = DATABASE['USER']
    database_url = DATABASE['HOST']

    database_password = DATABASE['PASSWORD']
    database_name = DATABASE['SYO']
    str_connect = "mysql+mysqlconnector://" + database_username + ":" + database_password + "@" + database_url + "/" + database_name
    engine = create_engine(str_connect)
    return engine


def log_in(username, password):
    password = sha256(password.encode('utf-8')).hexdigest()
    engine = connect_db()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    result = session.query(User.username, User.permission, User.project).filter_by(username=username,
                                                                                   password=password).first()
    if result is not None:
        session.close()
    else:
        session.close()
        result = (username, None, None)
    return result


def frame_empty():
    data_empty = pd.DataFrame([[""] * 30] * 20)
    column_names = [f'{i + 1}' for i in range(30)]
    data_empty = pd.DataFrame(data_empty, columns=column_names)
    data_empty = data_empty.fillna("")
    return data_empty


def querry_data_syo_hyo(project_name):
    project_name = project_name.upper()
    engine = connect_db()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    all_project = [name[0] for name in session.query(Project.project_name).all()]
    if project_name in all_project:
        result_querry_region1 = session.query(InformationProject).all()
        df_1 = region_1(result_querry_region1)

        querry_2 = session.query(ValueInf.parameter_name, Project.project_name, Config.config_name, ValueInf.value) \
            .join(Project, Project.project_id == ValueInf.project_id) \
            .join(Config, Config.config_id == ValueInf.config_id) \
            .filter(Project.project_name == project_name)
        result_querry_region2 = querry_2.all()
        df_2 = region_2(result_querry_region2)
        merged_df_1_2 = pd.merge(df_1, df_2, on='CADICS ID', how='inner')

        StatusDeviceDetailTB = session.query(
            StatusConfigDeviceDetail.project_id,
            Project.project_name,
            StatusConfigDeviceDetail.device_details_id,
            DeviceDetails.device_details_name,
            DeviceDetails.device_name,
            DeviceDetails.option_detail,
            DeviceDetails.group_detail,
            DeviceDetails.auto_detail,
            DeviceDetails.group_key_map,
            DeviceDetails.default
        ).join(Project, Project.project_id == StatusConfigDeviceDetail.project_id) \
            .join(DeviceDetails, DeviceDetails.device_details_id == StatusConfigDeviceDetail.device_details_id) \
            .group_by(
            StatusConfigDeviceDetail.device_details_id,
            StatusConfigDeviceDetail.project_id
        ).subquery()
        # result_querry_region_4 = session.query(
        #     Device.device_group,
        #     Device.device_name,
        #     DeviceDetails.auto_detail,
        #     DeviceDetails.group_detail,
        #     DeviceDetails.option_detail,
        #     DeviceDetails.device_details_name,
        #     DeviceDetails.group_key_map,
        #     DeviceDetails.default
        # ).outerjoin(DeviceDetails, Device.device_name == DeviceDetails.device_name).filter(Project.project_name == project_name).all()
        # index_df_1 = df_1.index.max()

        DeviceProject = session.query(
            ProjectDevice.project_id,
            Project.project_name,
            Device.device_name,
            Device.device_group
        ).join(Device, Device.device_name == ProjectDevice.device_name) \
            .join(Project, Project.project_id == ProjectDevice.project_id) \
            .subquery()

        result_querry_region_4 = session.query(
            DeviceProject.c.device_group,
            DeviceProject.c.device_name,
            StatusDeviceDetailTB.c.auto_detail,
            StatusDeviceDetailTB.c.group_detail,
            StatusDeviceDetailTB.c.option_detail,
            StatusDeviceDetailTB.c.device_details_name,
            StatusDeviceDetailTB.c.group_key_map,
            StatusDeviceDetailTB.c.default,
        ).outerjoin(
            StatusDeviceDetailTB,
            (StatusDeviceDetailTB.c.device_name == DeviceProject.c.device_name) &
            (StatusDeviceDetailTB.c.project_id == DeviceProject.c.project_id)
        ).filter(DeviceProject.c.project_name == project_name).all()
        index_df_1 = df_1.index.max()




        df_4, unique_list_max, unique_list_submax = region_4(result_querry_region_4, index_df_1)

        results_querry_region_7 = session.query(
            Project.project_name,
            Config.config_name,
            Lot.lot_name,
            OptionCode.optioncode_value,
            StatusLotConfig.status
        ).join(
            StatusLotConfig, Project.project_id == StatusLotConfig.project_id
        ).join(
            Config, Config.config_id == StatusLotConfig.config_id
        ).join(
            OptionCode,
            (OptionCode.config_id == StatusLotConfig.config_id) & (OptionCode.project_id == StatusLotConfig.project_id)
        ).join(
            Lot, Lot.lot_id == StatusLotConfig.lot_id
        ).filter(
            Project.project_name == project_name
        ).all()
        index_df_4 = df_4.index.max()
        df_7 = region_7(results_querry_region_7, index_df_4)
        querry_region_8 = session.query(
            Project.project_name,
            Config.config_name,
            DeviceDetails.device_name,
            DeviceDetails.device_details_name,
            DeviceDetails.group_detail,
            StatusConfigDeviceDetail.status
        ).join(DeviceDetails, StatusConfigDeviceDetail.device_details_id == DeviceDetails.device_details_id
               ).join(
            Project, StatusConfigDeviceDetail.project_id == Project.project_id
        ).join(
            Config, StatusConfigDeviceDetail.config_id == Config.config_id
        ).filter(
            Project.project_name == project_name
        )
        results_querry_region_8 = querry_region_8.all()
        df_8 = region_8(results_querry_region_8)
        # streamlit.write('DF_4: ',df_4)
        # streamlit.write('DF_8: ',df_8)
        merged_df_4_8 = pd.merge(df_4, df_8, on=['gr', 'CADICS ID', 'device_name'], how='left')
        # st.write('merged_df_4_8: ',merged_df_4_8)
        try:
            merged_df_4_8.set_index(df_4.index, inplace=True)
        except:
            merged_df_4_8.index = merged_df_4_8.index + 12
        merged_df_1_2_4_7_8 = pd.concat([merged_df_1_2, merged_df_4_8, df_7], axis=0)
        results_querry_region_6 = session.query(
            Project.project_name,
            DeviceDetails.device_details_name,
            DeviceDetails.device_name,
            DeviceDetails.group_detail,
            CommentColumn.comment_name,
            ProjectDeviceComment.comment_detail
        ).join(ProjectDeviceComment, Project.project_id == ProjectDeviceComment.project_id
               ).join(DeviceDetails, DeviceDetails.device_details_id == ProjectDeviceComment.device_details_id
                      ).join(CommentColumn, CommentColumn.comment_id == ProjectDeviceComment.comment_id
                             ).filter(Project.project_name == project_name).all()
        df_6 = region_6(results_querry_region_6)
        merged_df_1_2_4_6_7_8 = pd.merge(merged_df_1_2_4_7_8, df_6, on=['gr', 'CADICS ID', 'device_name'], how='left')
        merged_df_1_2_4_6_7_8 = merged_df_1_2_4_6_7_8.fillna("")
        merged_df_1_2_4_6_7_8 = merged_df_1_2_4_6_7_8.drop(columns=['device_name'])
        session.close()
        st.session_state.message_2 = f'{project_name}: Completed'
        return merged_df_1_2_4_6_7_8, unique_list_max, unique_list_submax
    else:
        session.close()
        st.error("Project (仕様表) not found in the database.")
        st.session_state.message_2 = "Model code (仕様表) not found in the database."
        df_1, merged_df_4_optioncode, unique_list_max, unique_list_submax = update_and_querry_form_data()
        merge_end = pd.concat([df_1, merged_df_4_optioncode], axis=0).fillna("")
        return merge_end, unique_list_max, unique_list_submax


def update_and_querry_form_data():

    engine = connect_db()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    result_querry_region1 = session.query(InformationProject).all()
    df_1 = region_1(result_querry_region1)
    result_querry_region_4 = session.query(
        Device.device_group,
        Device.device_name,
        DeviceDetails.auto_detail,
        DeviceDetails.group_detail,
        DeviceDetails.option_detail,
        DeviceDetails.device_details_name,
        DeviceDetails.group_key_map,
        DeviceDetails.default
    ).outerjoin(DeviceDetails, Device.device_name == DeviceDetails.device_name).all()
    index_df_1 = df_1.index.max()
    if pd.isna(index_df_1):
        index_df_1 = 11  # Thay thế NaN bằng 1
    df_4, unique_list_max, unique_list_submax = region_4(result_querry_region_4, index_df_1)
    result_querry_lot_name = session.query(Lot.lot_name).all()
    result_querry_lot_name_full = [('OptionCode',)] + result_querry_lot_name

    df_optioncode = pd.DataFrame(np.nan, index=range(len(result_querry_lot_name_full)),
                                 columns=['auto', 'gr', 'keyword', 'CADICS ID'])

    df_optioncode['CADICS ID'] = [t[0] for t in result_querry_lot_name_full]
    df_optioncode = df_optioncode.fillna("")
    merged_df_4_optioncode = pd.concat([df_4, df_optioncode], axis=0)
    session.close()
    return df_1, merged_df_4_optioncode, unique_list_max, unique_list_submax


def add_function_from_admin(df_end_region3, files):
    df_end_region3.rename(columns={df_end_region3.columns[0]: 'CADICS ID'}, inplace=True)
    df_end_region3.loc[df_end_region3['CADICS ID'] == 'SEAT/EQUIP', 'CADICS ID'] = 'SEAT'
    data_1, data_4_7, unique_list_max, unique_list_submax = update_and_querry_form_data()
    # st.write("data_1: ",data_1)
    # st.write("df_end_region3: ",df_end_region3)
    merge_1_spec = pd.merge(data_1, df_end_region3, on='CADICS ID', how='outer')

    merge_1_spec['order'] = merge_1_spec['CADICS ID'].apply(
        lambda x: df_end_region3['CADICS ID'].tolist().index(x) if x in df_end_region3[
            'CADICS ID'].tolist() else float('inf'))

    merge_1_spec = merge_1_spec.sort_values(by='order').drop(columns='order').reset_index(
        drop=True)
    # st.write('merge_1_spec: ', merge_1_spec)
    data_4_7.drop(columns=['device_name'], inplace=True)
    # st.write('data_4_7: ', data_4_7)

    merge_end = pd.concat([merge_1_spec, data_4_7], axis=0)
    merger_end = merge_end.fillna("")
    merger_end = merger_end.astype(str)
    conf_columns = ['auto', 'gr', 'keyword', 'CADICS ID'] + [f'conf-{str(i).zfill(3)}' for i in
                                                             range(1, merger_end.shape[1] - 5)] + ['group_key_map',
                                                                                                   'default']
    merger_end.columns = conf_columns

    return merger_end, unique_list_max, unique_list_submax


def update_data_new(project_name, df, df_1):
    logger.info(f"Start update_data_new for project: {project_name}")
    logger.debug(f"Input df shape: {df.shape}, columns: {df.columns.tolist()}")
    logger.debug(f"Input df_1 shape: {df_1.shape}, columns: {df_1.columns.tolist()}")

    df_ref = df.copy()
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df_1 = df_1.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    logger.debug("After strip: df head:\n%s", df.head())

    # *******************************************
    # Tạo một cột mới để đánh dấu các bản ghi trùng lặp
    df['duplicate_count'] = df.groupby(['CADICS ID', 'device_name']).cumcount()

    # Thêm hậu tố cho các bản ghi trùng lặp
    df['CADICS ID'] = df.apply(
        lambda x: f"{x['CADICS ID']}_{x['duplicate_count']}" if x['duplicate_count'] > 0 else x['CADICS ID'], axis=1)

    # Xóa cột duplicate_count
    df = df.drop(columns=['duplicate_count'])
    # *******************************************
    list_error = []
    project_name = str(project_name).upper()
    engine = connect_db()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    df.replace({np.nan: ''}, inplace=True)
    df.loc[df['CADICS ID'] == 'SEAT/EQUIP', 'CADICS ID'] = 'SEAT'
    df_1.replace({np.nan: ''}, inplace=True)

    logger.info("Checking if project exists: %s", project_name)
    existing_project_name = (session.query(Project).filter_by(project_name=project_name).first())
    if project_name != 'FORM':
        if existing_project_name is None:
            max_project_id = session.query(func.max(Project.project_id)).scalar()
            if max_project_id is None:
                max_project_id = 0
            try:
                new_project_name = Project(project_id=max_project_id + 1, project_name=project_name)
                session.add(new_project_name)
                session.commit()

            except mysql.connector.IntegrityError as e:
                list_error.append((project_name, e))
        else:
            project_name_ = str(project_name).upper()
            session.query(Project).filter(Project.project_name == project_name_).delete()
            session.commit()
            max_project_id = session.query(func.max(Project.project_id)).scalar()
            if max_project_id is None:
                max_project_id = 0
            try:
                new_project_name = Project(project_id=max_project_id + 1, project_name=project_name)
                session.add(new_project_name)
                session.commit()

            except mysql.connector.IntegrityError as e:
                list_error.append((project_name, e))

        # 5.---------------------------table device--------------------------
        # DEVICE table
        logger.info("Processing DEVICE table")

        list_existing_device_name = (session.query(Device.device_name, Device.device_group).all())
        device_table_df = device_table(df_ref)

        logger.debug(f"Device table from df_ref:\n{device_table_df}")

        list_device_table_df = list(device_table_df.itertuples(index=False, name=None))
        set_list_existing_device_name = set(list_existing_device_name)
        list_check_device = list(set([tup[0] for tup in set_list_existing_device_name]))
        list_only_in_list_device_table_df_insert = [item for item in list_device_table_df if
                                                    item not in set_list_existing_device_name and item[
                                                        0] not in list_check_device]

        list_only_in_list_device_table_df_update = [item for item in list_device_table_df if
                                                    item not in set_list_existing_device_name and item[
                                                        0] in list_check_device]
        
        logger.debug(f"Devices to insert: {list_only_in_list_device_table_df_insert}")
        logger.debug(f"Devices to update: {list_only_in_list_device_table_df_update}")

        if list_only_in_list_device_table_df_insert:
            device_table_df_add = pd.DataFrame(list_only_in_list_device_table_df_insert,
                                               columns=device_table_df.columns)
            for index, row in device_table_df_add.iterrows():
                try:
                    logger.info(f"Inserting device: {row['device_name']}, group: {row['device_group']}")
                    new_querry_device_table = Device(device_name=row['device_name'], device_group=row['device_group'])
                    session.add(new_querry_device_table)
                except mysql.connector.IntegrityError as e:
                    logger.error(f"Error mysql.connector.IntegrityError inserting device {row['device_name']}: {e}")
                    logger.error(traceback.format_exc())
                    list_error.append(("table device", row['device_name'], e))
                    session.rollback()
                except Exception as e:
                    logger.error(f"Error Exception inserting device {row['device_name']}: {e}")
                    logger.error(traceback.format_exc())
                    list_error.append(("table device", row['device_name'], e))
                    session.rollback()

        if list_only_in_list_device_table_df_update:
            device_table_df_add = pd.DataFrame(list_only_in_list_device_table_df_update,
                                               columns=device_table_df.columns)
            for index, row in device_table_df_add.iterrows():
                try:
                    logger.info(f"Updating device: {row['device_name']} group: {row['device_group']}")
                    existing_record = session.query(Device).filter_by(
                        device_name=row['device_name']
                    ).first()
                    if existing_record is not None:
                        stmt = (
                            update(Device).
                            where(Device.device_name == row['device_name']).
                            values(device_group=row['device_group'])
                        )
                        session.execute(stmt)
                except mysql.connector.IntegrityError as e:
                    print(e)
                    logger.error(f"Error mysql.connector.IntegrityError updating device {row['device_name']}: {e}")
                    logger.error(traceback.format_exc())
                    session.rollback()
                except Exception as e:
                    logger.error(f"Error Exception updating device {row['device_name']}: {e}")
                    logger.error(traceback.format_exc())
                    session.rollback()
        # 6.------------------------table device_detail--------------------------
        # DEVICE DETAILS table
        logger.info("Processing DEVICE_DETAILS table")

        list_existing_device_detail_name = (
            session.query(DeviceDetails.device_name, DeviceDetails.device_details_name,
                          DeviceDetails.group_detail, DeviceDetails.option_detail, DeviceDetails.auto_detail).all())

        list_existing_device_detail_name_upper = [
            (
                tup[0].strip().upper() if isinstance(tup[0], str) else tup[0],
                tup[1].strip().upper() if isinstance(tup[1], str) else tup[1],
                tup[2].strip().upper() if isinstance(tup[2], str) else tup[2]
            )
            for tup in list_existing_device_detail_name
        ]
        list_existing_device_detail_name = list_existing_device_detail_name_upper

        device_detail_table_df = device_detail_table(df)
        device_detail_table_df['device_name'] = device_detail_table_df['device_name'].apply(lambda x: x.strip().upper() if isinstance(x, str) else x)
        device_detail_table_df['device_details_name'] = device_detail_table_df['device_details_name'].apply(lambda x: x.strip().upper() if isinstance(x, str) else x)

        logger.debug(f"Device details table from df:\n{device_detail_table_df}")

        list_device_detail_table_df = list(device_detail_table_df.itertuples(index=False, name=None))
        logger.debug(f"Device details list_device_detail_table_df from df:\n{list_device_detail_table_df}")

        set_list_existing_device_detail_name = set(list_existing_device_detail_name)
        logger.debug(f"Device details set_list_existing_device_detail_name from df:\n{set_list_existing_device_detail_name}")

        list_check_device_detail = list(
            set([(tup[0], tup[1]) for tup in set_list_existing_device_detail_name]))
        logger.debug(f"Device details list_check_device_detail from df:\n{list_check_device_detail}")

        list_only_in_list_device_detail_table_df_insert = [item for item in list_device_detail_table_df if
                                                           item not in set_list_existing_device_detail_name and (
                                                               item[0], item[
                                                                   1]) not in list_check_device_detail]
        
        logger.debug(f"Device details list_only_in_list_device_detail_table_df_insert from df:\n{list_only_in_list_device_detail_table_df_insert}")


        list_only_in_list_device_detail_table_df_update = [item for item in list_device_detail_table_df if
                                                           item not in set_list_existing_device_detail_name and (
                                                               item[0], item[
                                                                   1]) in list_check_device_detail]
        
        logger.debug(f"Device details list_only_in_list_device_detail_table_df_update from df:\n{list_only_in_list_device_detail_table_df_update}")


        max_device_detail_id = session.query(func.max(DeviceDetails.device_details_id)).scalar()
        if max_device_detail_id is None:
            max_device_detail_id = 0

        list_error = []
        if list_only_in_list_device_detail_table_df_insert:
            device_detail_table_df_add = pd.DataFrame(list_only_in_list_device_detail_table_df_insert,
                                                      columns=device_detail_table_df.columns)
            for index, row in device_detail_table_df_add.iterrows():
                try:

                    logger.info(f"Inserting device detail: {row['device_details_name']} for device {row['device_name']}")
                    new_device_detail_id = max_device_detail_id + 1  # Tăng ID cho mỗi lần lặp

                    new_querry_device_detail_table = DeviceDetails(
                        device_details_id=new_device_detail_id,
                        device_name=row['device_name'],
                        device_details_name=row['device_details_name'],
                        group_detail=row['group_detail'],
                        option_detail=row['option_detail'],
                        auto_detail=row['auto_detail']
                    )
                    session.add(new_querry_device_detail_table)

                    max_device_detail_id = new_device_detail_id
                except Exception as e:
                    logger.error(f"Error inserting device detail {row['device_details_name']}: {e}")
                    logger.error(traceback.format_exc())
                    list_error.append(row['device_details_name'])
                    session.rollback()

        if list_only_in_list_device_detail_table_df_update:
            device_detail_table_df_update = pd.DataFrame(list_only_in_list_device_detail_table_df_update,
                                                         columns=device_detail_table_df.columns)
            for index, row in device_detail_table_df_update.iterrows():
                try:
                    logger.info(f"Updating device detail: {row['device_details_name']}")
                    existing_record = session.query(DeviceDetails).filter_by(
                        device_details_name=row['device_details_name']
                    ).first()
                    if existing_record is not None:
                        stmt = (
                            update(DeviceDetails).
                            where(DeviceDetails.device_details_name == row['device_details_name']).
                            values(
                                # device_name=row['device_name'],
                                auto_detail=row['auto_detail'])
                        )
                        session.execute(stmt)

                except Exception as e:
                    logger.error(f"Error updating device detail {row['device_details_name']}: {e}")
                    logger.error(traceback.format_exc())
                    session.rollback()
    elif project_name == 'FORM':

        logger.info(f"[FORM] Bắt đầu xử lý project FORM: {project_name}")

        # 5.---------------------------table device--------------------------
        list_existing_device_name = session.query(Device.device_name, Device.device_group).all()
        logger.debug(f"[FORM] Danh sách Device hiện tại trong DB: {list_existing_device_name}")

        device_table_df = device_table(df_ref).copy()
        logger.debug(f"[FORM] Device table lấy từ df_ref:\n{device_table_df}")

        # === FIX: normalize device_name để match DB collation CI ===
        device_table_df["device_name"] = device_table_df["device_name"].apply(norm_key)
        device_table_df["device_group"] = device_table_df["device_group"].apply(lambda x: x.strip() if isinstance(x, str) else x)

        device_table_df = device_table_df[device_table_df["device_name"] != ""].copy()
        device_table_df = device_table_df.drop_duplicates(subset=["device_name"], keep="last")

        # Map normalized_name -> raw_name_in_db (để delete/update chắc chắn đúng record)
        existing_norm_to_raw = {norm_key(n): n for (n, _) in list_existing_device_name if n}
        existing_norm_to_group = {norm_key(n): (g.strip() if isinstance(g, str) else g) for (n, g) in list_existing_device_name if n}
        existing_norm_set = set(existing_norm_to_raw.keys())

        upload_norm_to_group = {row["device_name"]: row["device_group"] for _, row in device_table_df.iterrows()}
        upload_norm_set = set(upload_norm_to_group.keys())

        # INSERT: name chưa có trong DB
        to_insert = [dn for dn in upload_norm_set if dn not in existing_norm_set]

        # UPDATE: name có rồi nhưng group khác
        to_update = [dn for dn in upload_norm_set if (dn in existing_norm_set and upload_norm_to_group[dn] != existing_norm_to_group.get(dn))]

        # DELETE: name có trong DB nhưng không có trong upload
        to_delete = [dn for dn in existing_norm_set if dn not in upload_norm_set]

        logger.debug(f"[FORM] Device cần INSERT (norm): {to_insert}")
        logger.debug(f"[FORM] Device cần UPDATE (norm): {to_update}")
        logger.debug(f"[FORM] Device cần DELETE (norm): {to_delete}")

        # --- INSERT ---
        for dn in to_insert:
            try:
                with session.begin_nested():
                    session.add(Device(device_name=dn, device_group=upload_norm_to_group[dn]))
                logger.info(f"[FORM] INSERT device: {dn}, group: {upload_norm_to_group[dn]}")
                existing_norm_to_raw[dn] = dn
                existing_norm_to_group[dn] = upload_norm_to_group[dn]
                existing_norm_set.add(dn)
            except IntegrityError as e:
                logger.error(f"[FORM] IntegrityError INSERT device {dn}: {e}")
                logger.error(traceback.format_exc())
            except Exception as e:
                logger.error(f"[FORM] Exception INSERT device {dn}: {e}")
                logger.error(traceback.format_exc())

        # --- UPDATE ---
        for dn in to_update:
            try:
                raw_name = existing_norm_to_raw.get(dn, dn)  # nếu không có map thì dùng dn
                with session.begin_nested():
                    stmt = (
                        update(Device)
                        .where(Device.device_name == raw_name)  # MySQL CI sẽ match đúng
                        .values(device_group=upload_norm_to_group[dn])
                    )
                    session.execute(stmt)
                logger.info(f"[FORM] UPDATE device: {dn}, group: {upload_norm_to_group[dn]}")
                existing_norm_to_group[dn] = upload_norm_to_group[dn]
            except Exception as e:
                logger.error(f"[FORM] Exception UPDATE device {dn}: {e}")
                logger.error(traceback.format_exc())

        # --- DELETE ---
        for dn in to_delete:
            try:
                raw_name = existing_norm_to_raw.get(dn)
                if not raw_name:
                    continue
                with session.begin_nested():
                    session.query(Device).filter(Device.device_name == raw_name).delete()
                logger.info(f"[FORM] DELETE device_name: {dn} (raw: {raw_name})")
            except Exception as e:
                logger.error(f"[FORM] Exception DELETE device {dn}: {e}")
                logger.error(traceback.format_exc())

        session.commit()
        logger.info("[FORM] Đã commit Device table")


        # 6.------------------------table device_detail--------------------------
        with session.no_autoflush:
            existing_dd = session.query(
                DeviceDetails.device_details_id,
                DeviceDetails.device_details_name,
                DeviceDetails.device_name,
                DeviceDetails.group_detail,
                DeviceDetails.option_detail,
                DeviceDetails.auto_detail,
                DeviceDetails.group_key_map,
                DeviceDetails.default
            ).all()

        # Map theo ddn_norm (vì DB unique theo device_details_name)
        existing_by_ddn = {}
        for (dd_id, ddn, dn, gd, od, ad, gkm, dft) in existing_dd:
            ddn_norm = norm_key(ddn)
            if ddn_norm:
                existing_by_ddn[ddn_norm] = {
                    "id": dd_id,
                    "device_name": norm_key(dn),
                    "group_detail": gd or "",
                    "option_detail": od or "",
                    "auto_detail": ad or "",
                    "group_key_map": gkm or "",
                    "default": dft or ""
                }

        logger.debug(f"[FORM] Existing DeviceDetails count (by ddn_norm): {len(existing_by_ddn)}")

        device_detail_table_df = device_detail_table(df).copy()
        device_detail_table_df["device_name"] = device_detail_table_df["device_name"].apply(norm_key)
        device_detail_table_df["device_details_name"] = device_detail_table_df["device_details_name"].apply(norm_key)

        # clean + dedupe theo ddn (đúng schema unique)
        device_detail_table_df = device_detail_table_df[device_detail_table_df["device_details_name"] != ""].copy()
        device_detail_table_df = device_detail_table_df.drop_duplicates(subset=["device_details_name"], keep="last")

        # Map upload theo ddn_norm
        upload_by_ddn = {}
        for _, row in device_detail_table_df.iterrows():
            ddn = row["device_details_name"]
            upload_by_ddn[ddn] = {
                "device_name": row["device_name"],
                "group_detail": (row.get("group_detail") or ""),
                "option_detail": (row.get("option_detail") or ""),
                "auto_detail": (row.get("auto_detail") or ""),
                "group_key_map": (row.get("group_key_map") or ""),
                "default": (row.get("default") or "")
            }

        upload_ddn_set = set(upload_by_ddn.keys())
        existing_ddn_set = set(existing_by_ddn.keys())

        to_delete_ddn = existing_ddn_set - upload_ddn_set
        to_insert_ddn = upload_ddn_set - existing_ddn_set
        to_maybe_update_ddn = upload_ddn_set & existing_ddn_set

        logger.debug(f"[FORM] DeviceDetails cần INSERT (ddn_norm): {len(to_insert_ddn)}")
        logger.debug(f"[FORM] DeviceDetails cần UPDATE (ddn_norm): {len(to_maybe_update_ddn)}")
        logger.debug(f"[FORM] DeviceDetails cần DELETE (ddn_norm): {len(to_delete_ddn)}")

        # DELETE theo id (an toàn nhất)
        for ddn in to_delete_ddn:
            try:
                dd_id = existing_by_ddn[ddn]["id"]
                with session.begin_nested():
                    session.query(DeviceDetails).filter(DeviceDetails.device_details_id == dd_id).delete()
                logger.info(f"[FORM] DELETE device_detail: ddn={ddn}, id={dd_id}")
            except Exception as e:
                logger.error(f"[FORM] Error DELETE device_detail ddn={ddn}: {e}")
                logger.error(traceback.format_exc())

        # INSERT (không set device_details_id, để autoincrement)
        for ddn in to_insert_ddn:
            v = upload_by_ddn[ddn]
            try:
                with session.begin_nested():
                    session.add(DeviceDetails(
                        device_name=v["device_name"],
                        device_details_name=ddn,
                        group_detail=v["group_detail"],
                        option_detail=v["option_detail"],
                        auto_detail=v["auto_detail"],
                        group_key_map=v["group_key_map"],
                        default=v["default"]
                    ))
                logger.info(f"[FORM] INSERT device_detail: {ddn} ({v['device_name']})")
            except IntegrityError as e:
                logger.error(f"[FORM] IntegrityError INSERT device_detail {ddn}: {e}")
                logger.error(traceback.format_exc())
            except Exception as e:
                logger.error(f"[FORM] Error INSERT device_detail {ddn}: {e}")
                logger.error(traceback.format_exc())

        # UPDATE (update cả device_name để tránh “đổi device_name rồi insert duplicate”)
        for ddn in to_maybe_update_ddn:
            old = existing_by_ddn[ddn]
            new = upload_by_ddn[ddn]

            need_update = (
                old["device_name"] != new["device_name"] or
                old["group_detail"] != new["group_detail"] or
                old["option_detail"] != new["option_detail"] or
                old["auto_detail"] != new["auto_detail"] or
                old["group_key_map"] != new["group_key_map"] or
                old["default"] != new["default"]
            )

            if not need_update:
                continue

            try:
                dd_id = old["id"]
                with session.begin_nested():
                    stmt = (
                        update(DeviceDetails)
                        .where(DeviceDetails.device_details_id == dd_id)
                        .values(
                            device_name=new["device_name"],
                            group_detail=new["group_detail"],
                            option_detail=new["option_detail"],
                            auto_detail=new["auto_detail"],
                            group_key_map=new["group_key_map"],
                            default=new["default"]
                        )
                    )
                    session.execute(stmt)
                logger.info(f"[FORM] UPDATE device_detail: ddn={ddn}, id={dd_id}")
            except Exception as e:
                logger.error(f"[FORM] Error UPDATE device_detail ddn={ddn}: {e}")
                logger.error(traceback.format_exc())

        session.commit()
        logger.info("[FORM] Đã commit DeviceDetails table")



        # 7.---------------------------table information_project------------------------------
        list_existing_information_project = (
            session.query(InformationProject.parameter_name, InformationProject.group_infor,
                          InformationProject.keyword, InformationProject.auto_infor).all())

        logger.debug(f"[FORM] Danh sách InformationProject hiện tại trong DB: {list_existing_information_project}")

        information_project_table_df = information_project_table(df)
        logger.debug(f"[FORM] InformationProject table lấy từ df:\n{information_project_table_df}")

        list_information_project_table_df = list(information_project_table_df.itertuples(index=False, name=None))
        set_list_existing_information_project = set(list_existing_information_project)
        list_check_information_project = list(set([tup[0] for tup in set_list_existing_information_project]))
        list_only_in_list_information_project_table_df_insert = [item for item in list_information_project_table_df if
                                                                 item not in set_list_existing_information_project and
                                                                 item[
                                                                     0] not in list_check_information_project]

        list_only_in_list_information_project_table_df_update = [item for item in list_information_project_table_df if
                                                                 item not in set_list_existing_information_project and
                                                                 item[
                                                                     0] in list_check_information_project]
        
        logger.debug(f"[FORM] InformationProject cần INSERT: {list_only_in_list_information_project_table_df_insert}")
        logger.debug(f"[FORM] InformationProject cần UPDATE: {list_only_in_list_information_project_table_df_update}")


        if list_only_in_list_information_project_table_df_insert:
            information_project_table_df_add = pd.DataFrame(list_only_in_list_information_project_table_df_insert,
                                                            columns=information_project_table_df.columns)
            for index, row in information_project_table_df_add.iterrows():
                try:
                    logger.info(f"[FORM] INSERT InformationProject: {row['CADICS ID']}")
                    new_querry_device_information_project_table = InformationProject(parameter_name=row['CADICS ID'],
                                                                                     group_infor=row['Gr'],
                                                                                     keyword=row['Keyword'],
                                                                                     auto_infor=row['auto'])
                    session.add(new_querry_device_information_project_table)
                except Exception as e:
                    logger.error(f"[FORM] Lỗi khi INSERT InformationProject {row['CADICS ID']}: {e}")
                    logger.error(traceback.format_exc())
                    list_error.append(row['CADICS ID'])

        if list_only_in_list_information_project_table_df_update:
            information_project_table_df_add = pd.DataFrame(list_only_in_list_information_project_table_df_update,
                                                            columns=information_project_table_df.columns)
            for index, row in information_project_table_df_add.iterrows():
                try:
                    logger.info(f"[FORM] UPDATE InformationProject: {row['CADICS ID']}")
                    existing_record = session.query(InformationProject).filter_by(
                        parameter_name=row['CADICS ID']
                    ).first()
                    if existing_record is not None:
                        stmt = (
                            update(InformationProject).
                            where(InformationProject.parameter_name == row['CADICS ID']).
                            values(group_infor=row['Gr'], keyword=row['Keyword'],
                                   auto_infor=row['auto_infor'])
                        )
                        session.execute(stmt)
                except Exception as e:
                    logger.error(f"[FORM] Lỗi khi UPDATE InformationProject {row['CADICS ID']}: {e}")
                    logger.error(traceback.format_exc())
                    list_error.append(row['CADICS ID'])
    session.commit()

    logger.info(f"Commit DB thành công cho project {project_name} - bắt đầu các bước bổ sung pipeline các bảng phụ")

    if df.shape[1] != 9:
        # 2.----------------------table config--------------------------------
        logger.info("BẮT ĐẦU xử lý bảng Config")
        list_existing_config_name = (session.query(Config.config_name).all())
        config_table_df = config_table(df)
        list_config_table_df = list(config_table_df.itertuples(index=False, name=None))

        set_list_existing_config_name = set(list_existing_config_name)
        only_in_list_config_table_df = [item for item in list_config_table_df if
                                        item not in set_list_existing_config_name]

        logger.debug(f"Config cần insert: {only_in_list_config_table_df}")

        config_table_df_final = pd.DataFrame(only_in_list_config_table_df, columns=['config_name'])
        max_config_id = session.query(func.max(Config.config_id)).scalar()
        for index, row in config_table_df_final.iterrows():
            try:
                logger.info(f"Insert Config: {row['config_name']}")
                if max_config_id is None:
                    max_config_id = 1
                elif index == 0 and max_config_id is not None:
                    max_config_id += 1
                new_config = Config(config_id=max_config_id + index, config_name=row['config_name'])
                session.add(new_config)
            except mysql.connector.IntegrityError as e:
                logger.error(f"Lỗi khi INSERT Config {row['config_name']}: {e}")
                logger.error(traceback.format_exc())
                list_error.append(("table config", row['config_name'], e))
                session.rollback()

            except Exception as e:
                logger.error(f"Lỗi khi INSERT Config {row['config_name']}: {e}")
                logger.error(traceback.format_exc())
                list_error.append(("table config", row['config_name'], e))
                session.rollback()

        # 3.---------------------table lot---------------------------------------
        logger.info("BẮT ĐẦU xử lý bảng Lot")
        list_existing_lot_name = (session.query(Lot.lot_name).all())
        lot_table_df = lot_table(df_1)
        list_lot_table_df = list(lot_table_df.itertuples(index=False, name=None))
        set_list_existing_lot_name = set(list_existing_lot_name)

        only_in_list_lot_table_df = [item for item in list_lot_table_df if item not in set_list_existing_lot_name]

        logger.debug(f"Lot cần insert: {only_in_list_lot_table_df}")

        if only_in_list_lot_table_df:
            max_lot_id = session.query(func.max(Lot.lot_id)).scalar()
            lot_table_df_final = pd.DataFrame(only_in_list_lot_table_df, columns=['lot_name'])
            for index, row in lot_table_df_final.iterrows():
                try:
                    logger.info(f"Insert Lot: {row['lot_name']}")
                    if max_lot_id is None:
                        max_lot_id = 1
                        new_lot = Lot(lot_id=max_lot_id + index, lot_name=row['lot_name'])
                    else:
                        new_lot = Lot(lot_id=max_lot_id + index + 1, lot_name=row['lot_name'])

                    session.add(new_lot)
                except mysql.connector.IntegrityError as e:
                    logger.error(f"Lỗi khi INSERT Lot {row['lot_name']}: {e}")
                    logger.error(traceback.format_exc())
                    list_error.append(("table lot", row['lot_name'], e))
                    session.rollback()

        # 4.-----------------------table comment_column--------------------------------------
        logger.info("BẮT ĐẦU xử lý bảng CommentColumn")
        list_existing_comment_name = (session.query(CommentColumn.comment_name).all())
        comment_column_table_df = comment_column_table(df)
        list_comment_table_df = list(comment_column_table_df.itertuples(index=False, name=None))
        set_list_existing_comment_name = set(list_existing_comment_name)

        only_in_list_comment_table_df = [item for item in list_comment_table_df if
                                         item not in set_list_existing_comment_name]
        
        logger.debug(f"CommentColumn cần insert: {only_in_list_comment_table_df}")
        
        if only_in_list_comment_table_df:
            max_comment_id = session.query(func.max(CommentColumn.comment_id)).scalar()
            comment_df = pd.DataFrame(only_in_list_comment_table_df, columns=['Comment'])
            for index, row in comment_df.iterrows():
                try:
                    logger.info(f"Insert CommentColumn: {row['Comment']}")
                    if max_comment_id is None:
                        max_comment_id = 1
                    elif index == 0 and max_comment_id is not None:
                        max_comment_id += 1
                    new_comment = CommentColumn(comment_id=max_comment_id + index, comment_name=row['Comment'])
                    session.add(new_comment)
                except mysql.connector.IntegrityError as e:
                    logger.error(f"Lỗi khi INSERT CommentColumn {row['Comment']}: {e}")
                    logger.error(traceback.format_exc())
                    list_error.append(("table comment_column", row['Comment'], e))
                    session.rollback()
                
                except Exception as e:
                    logger.error(f"Lỗi khi INSERT CommentColumn {row['Comment']}: {e}")
                    logger.error(traceback.format_exc())
                    list_error.append(("table comment_column", row['Comment'], e))
                    session.rollback()

        # 7.---------------------------table information_project------------------------------
        logger.info("BẮT ĐẦU xử lý bảng InformationProject")
        list_existing_information_project = (
            session.query(InformationProject.parameter_name, InformationProject.group_infor,
                          InformationProject.keyword, InformationProject.auto_infor).all())

        information_project_table_df = information_project_table(df)

        list_information_project_table_df = list(information_project_table_df.itertuples(index=False, name=None))
        set_list_existing_information_project = set(list_existing_information_project)
        list_check_information_project = list(set([tup[0] for tup in set_list_existing_information_project]))
        list_only_in_list_information_project_table_df_insert = [item for item in list_information_project_table_df if
                                                                 item not in set_list_existing_information_project and
                                                                 item[
                                                                     0] not in list_check_information_project]

        list_only_in_list_information_project_table_df_update = [item for item in list_information_project_table_df if
                                                                 item not in set_list_existing_information_project and
                                                                 item[
                                                                     0] in list_check_information_project]
        logger.debug(f"InformationProject cần insert: {list_only_in_list_information_project_table_df_insert}")
        logger.debug(f"InformationProject cần update: {list_only_in_list_information_project_table_df_update}")
        

        if list_only_in_list_information_project_table_df_insert:
            information_project_table_df_add = pd.DataFrame(list_only_in_list_information_project_table_df_insert,
                                                            columns=information_project_table_df.columns)
            for index, row in information_project_table_df_add.iterrows():
                try:
                    logger.info(f"Insert InformationProject: {row['CADICS ID']}")
                    new_querry_device_information_project_table = InformationProject(parameter_name=row['CADICS ID'],
                                                                                     group_infor=row['Gr'],
                                                                                     keyword=row['Keyword'],
                                                                                     auto_infor=row['auto'])
                    session.add(new_querry_device_information_project_table)
                except Exception as e:
                    logger.error(f"Lỗi khi INSERT InformationProject {row['CADICS ID']}: {e}")
                    logger.error(traceback.format_exc())
                    list_error.append(row['CADICS ID'])

        if list_only_in_list_information_project_table_df_update:
            information_project_table_df_add = pd.DataFrame(list_only_in_list_information_project_table_df_update,
                                                            columns=information_project_table_df.columns)
            for index, row in information_project_table_df_add.iterrows():
                try:
                    logger.info(f"Update InformationProject: {row['CADICS ID']}")
                    existing_record = session.query(InformationProject).filter_by(
                        parameter_name=row['CADICS ID']
                    ).first()
                    if existing_record is not None:
                        stmt = (
                            update(InformationProject).
                            where(InformationProject.parameter_name == row['CADICS ID']).
                            values(group_infor=row['Gr'], keyword=row['Keyword'],
                                   auto_infor=row['auto_infor'])
                        )
                        session.execute(stmt)
                except Exception as e:
                    logger.error(f"Lỗi khi UPDATE InformationProject {row['CADICS ID']}: {e}")
                    logger.error(traceback.format_exc())
                    list_error.append(row['CADICS ID'])

        # .---------------------------Querry 7 table under------------------------------
        logger.info("=== Start querying all reference tables for foreign key mapping (Config, Project, Lot, CommentColumn, DeviceDetails) ===")
        querry_config_in_DB = session.query(Config).all()
        config_data_after_querry = [(config.config_id, config.config_name) for config in querry_config_in_DB]
        config_table_df_querry = pd.DataFrame(config_data_after_querry, columns=['config_id', 'config_name'])
        logger.debug(f"Config in DB: {config_table_df_querry}")

        querry_project_in_DB = session.query(Project).all()
        project_data_after_querry = [(project.project_id, project.project_name) for project in querry_project_in_DB]
        project_table_df_querry = pd.DataFrame(project_data_after_querry, columns=['project_id', 'project_name'])
        logger.debug(f"Project in DB: {project_table_df_querry}")

        querry_lot_in_DB = session.query(Lot).all()
        lot_data_after_querry = [(lot.lot_id, lot.lot_name) for lot in querry_lot_in_DB]
        lot_table_df_querry = pd.DataFrame(lot_data_after_querry, columns=['lot_id', 'lot_name'])
        logger.debug(f"Lot in DB: {lot_table_df_querry}")

        querry_comment_column_in_DB = session.query(CommentColumn).all()
        comment_column_data_after_querry = [(comment.comment_id, comment.comment_name) for comment in
                                            querry_comment_column_in_DB]
        comment_column_table_df_querry = pd.DataFrame(comment_column_data_after_querry,
                                                      columns=['comment_id', 'comment_name'])
        
        logger.debug(f"CommentColumn in DB: {comment_column_table_df_querry}")

        querry_device_details_in_DB = session.query(DeviceDetails.device_details_id,
                                                    DeviceDetails.device_details_name, DeviceDetails.device_name).all()
        
        
        device_details_data_after_querry = [
            (device_details.device_details_id, device_details.device_details_name, device_details.device_name) for
            device_details in querry_device_details_in_DB]
        device_details_table_df_querry = pd.DataFrame(device_details_data_after_querry,
                                                      columns=['device_details_id', 'device_details_name',
                                                               'device_name'])
        
        logger.debug(f"DeviceDetails in DB: {device_details_table_df_querry}")
        # logger.debug(f"DeviceDetails in DB: {device_details_table_df_querry[device_details_table_df_querry['device_name'].strip().upper() == 'eDCA'.upper()]}")

        # 8.-------------------table optioncode--------------------------------------
        logger.info("=== Start processing OptionCode table ===")
        list_existing_optioncode = (
            session.query(OptionCode.optioncode_value, OptionCode.config_id, OptionCode.project_id).all())

        optioncode_table_df_temp = optioncode_table(df_1, project_name)
        logger.debug(f"OptionCode table (raw): {optioncode_table_df_temp}")

        optioncode_table_df_merge_config = pd.merge(optioncode_table_df_temp, config_table_df_querry, on='config_name',
                                                    how='left')
        optioncode_table_df = pd.merge(optioncode_table_df_merge_config, project_table_df_querry, on='project_name',
                                       how='left')

        optioncode_table_df.drop(columns=['config_name', 'project_name'], inplace=True)
        optioncode_table_df.fillna('null', inplace=True)

        list_OptionCode_table_df = list(optioncode_table_df.itertuples(index=False, name=None))
        set_list_existing_optioncode = set(list_existing_optioncode)
        list_only_in_list_optioncode_table_df = [item for item in list_OptionCode_table_df if
                                                 item not in set_list_existing_optioncode]
        
        logger.debug(f"OptionCode need insert/update: {list_only_in_list_optioncode_table_df}")

        if list_only_in_list_optioncode_table_df:
            optioncode_table_df_add = pd.DataFrame(list_only_in_list_optioncode_table_df,
                                                   columns=optioncode_table_df.columns)
            for index, row in optioncode_table_df_add.iterrows():
                try:
                    logger.info(f"Upsert OptionCode: config_id={row['config_id']}, project_id={row['project_id']}, value={row['optioncode_value']}")
            
                    existing_record = session.query(OptionCode).filter_by(
                        config_id=row['config_id'],
                        project_id=row['project_id']
                    ).first()
                    if existing_record is not None:
                        stmt = (
                            update(OptionCode).
                            where(
                                and_(
                                    OptionCode.config_id == row['config_id'],
                                    OptionCode.project_id == row['project_id']
                                )
                            ).
                            values(optioncode_value=row['optioncode_value'])
                        )
                        session.execute(stmt)
                        logger.info(f"Updated OptionCode: config_id={row['config_id']}, project_id={row['project_id']}")
            
                    else:
                        new_querry_optioncode_table = OptionCode(config_id=row['config_id'],
                                                                 project_id=row['project_id'],
                                                                 optioncode_value=row['optioncode_value'])
                        session.add(new_querry_optioncode_table)
                        logger.info(f"Inserted OptionCode: config_id={row['config_id']}, project_id={row['project_id']}")
                except Exception as e:
                    logger.error(f"Error upserting OptionCode config_id={row['config_id']}, project_id={row['project_id']}: {e}")
                    logger.error(traceback.format_exc())
                    list_error.append(row['CADICS ID'])
                    session.rollback()

        # 9.-------------------------table project_device-------------------------
        logger.info("=== Start processing ProjectDevice table ===")
        list_existing_project_device = (
            session.query(ProjectDevice.device_name, ProjectDevice.project_id).all())

        project_device = project_device_table(df_ref, project_name)
        project_device_table_df_temp = pd.merge(project_device, project_table_df_querry, on='project_name',
                                                how='left')
        project_device_table_df_temp.drop(columns=['project_name'], inplace=True)
        project_device_table_df_temp.fillna('null', inplace=True)

        list_project_device_table_df = list(project_device_table_df_temp.itertuples(index=False, name=None))
        set_list_existing_project_device = set(list_existing_project_device)

        list_only_in_list_project_device_table_df = [item for item in list_project_device_table_df if
                                                     item not in set_list_existing_project_device]
        
        logger.debug(f"ProjectDevice need insert: {list_only_in_list_project_device_table_df}")


        if list_only_in_list_project_device_table_df:
            project_device_table_df = pd.DataFrame(list_only_in_list_project_device_table_df,
                                                   columns=project_device_table_df_temp.columns)
            for index, row in project_device_table_df.iterrows():
                try:
                    logger.info(f"Insert ProjectDevice: device_name={row['device_name']}, project_id={row['project_id']}")
                    new_querry_project_device_table = ProjectDevice(device_name=row['device_name'],
                                                                    project_id=row['project_id'])
                    session.add(new_querry_project_device_table)
                except Exception as e:
                    print(e)
                    logger.error(f"Error inserting ProjectDevice device_name={row['device_name']}, project_id={row['project_id']}: {e}")
                    logger.error(traceback.format_exc())
                    session.rollback()

        # 10.--------------------------table value_inf------------------------------------
        logger.info("=== Start processing ValueInf table ===")
        list_existing_value_inf = (
            session.query(ValueInf.parameter_name, ValueInf.value, ValueInf.project_id, ValueInf.config_id).all())

        value_inf = value_inf_table(df.loc[:11, :])
        logger.debug(f"ValueInf table (raw): {value_inf}")

        value_inf_table_df_merge_prj = pd.merge(value_inf, project_table_df_querry, on='project_name',
                                                how='left')
        value_inf_table_df_temp = pd.merge(value_inf_table_df_merge_prj, config_table_df_querry, on='config_name',
                                           how='left')
        value_inf_table_df_temp.drop(columns=['project_name', 'config_name'], inplace=True)
        value_inf_table_df_temp.fillna('null', inplace=True)

        value_inf_table_df_temp['value'] = value_inf_table_df_temp['value'].apply(
            lambda x: str(x) if x is not None else '')

        list_value_inf_table_df = list(value_inf_table_df_temp.itertuples(index=False, name=None))
        set_list_existing_value_inf = set(list_existing_value_inf)
        list_check_value_inf = list(
            set([(tup[0], tup[2], tup[3]) for tup in set_list_existing_value_inf]))
        list_only_in_list_value_inf_table_df_insert = [item for item in list_value_inf_table_df if
                                                       item not in set_list_existing_value_inf and (
                                                           item[0], item[2], item[3]) not in list_check_value_inf]
        list_only_in_list_value_inf_table_df_update = [item for item in list_value_inf_table_df if
                                                       item not in set_list_existing_value_inf and (
                                                           item[0], item[2], item[3]) in list_check_value_inf]
        
        logger.debug(f"ValueInf need insert: {list_only_in_list_value_inf_table_df_insert}")
        logger.debug(f"ValueInf need update: {list_only_in_list_value_inf_table_df_update}")

        if list_only_in_list_value_inf_table_df_insert:

            value_inf_table_df = pd.DataFrame(list_only_in_list_value_inf_table_df_insert,
                                              columns=value_inf_table_df_temp.columns)
            for index, row in value_inf_table_df.iterrows():

                try:
                    logger.info(f"Insert ValueInf: param={row['parameter_name']}, config_id={row['config_id']}, project_id={row['project_id']}, value={row['value']}")

                    new_querry_value_inf_table = ValueInf(config_id=row['config_id'],
                                                          parameter_name=row['parameter_name'],
                                                          value=row['value'], project_id=row['project_id'])
                    session.add(new_querry_value_inf_table)
                    session.commit()
                except Exception as e:
                    print(e)
                    logger.error(f"Error inserting ValueInf param={row['parameter_name']}: {e}")
                    logger.error(traceback.format_exc())        
                    session.rollback()
        if list_only_in_list_value_inf_table_df_update:
            value_inf_table_df = pd.DataFrame(list_only_in_list_value_inf_table_df_update,
                                              columns=value_inf_table_df_temp.columns)
            for index, row in value_inf_table_df.iterrows():
                try:
                    logger.info(f"Update ValueInf: param={row['parameter_name']}, config_id={row['config_id']}, project_id={row['project_id']}, value={row['value']}")

                    stmt = (
                        update(ValueInf).
                        where(
                            and_(
                                ValueInf.parameter_name == row['parameter_name'],
                                ValueInf.config_id == row['config_id'],
                                ValueInf.project_id == row['project_id']
                            )
                        ).
                        values(comment_detail=row['comment_detail'])
                    )
                    session.execute(stmt)
                except Exception as e:
                    print(e)
                    logger.error(f"Error updating ValueInf param={row['parameter_name']}: {e}")
                    logger.error(traceback.format_exc())
                    session.rollback()

        # 11.---------------------------------table status_lot_config---------------------------
        logger.info("=== Start processing StatusLotConfig table ===")
        list_existing_status_lot_config = (
            session.query(StatusLotConfig.status, StatusLotConfig.project_id, StatusLotConfig.config_id,
                          StatusLotConfig.lot_id).all())

        status_lot_config = status_lot_config_table(df_1, project_name)
        logger.debug(f"StatusLotConfig table (raw): {status_lot_config}")

        status_lot_config_table_df_merge_prj = pd.merge(status_lot_config, project_table_df_querry, on='project_name',
                                                        how='left')
        status_lot_config_table_df_merge_config = pd.merge(status_lot_config_table_df_merge_prj, config_table_df_querry,
                                                           on='config_name',
                                                           how='left')
        status_lot_config_table_df_temp = pd.merge(status_lot_config_table_df_merge_config, lot_table_df_querry,
                                                   on='lot_name',
                                                   how='left')

        status_lot_config_table_df_temp.drop(columns=['project_name', 'config_name', 'lot_name'], inplace=True)
        status_lot_config_table_df_temp.fillna('null', inplace=True)

        list_status_lot_config_table_df = list(status_lot_config_table_df_temp.itertuples(index=False, name=None))
        set_list_existing_status_lot_config = set(list_existing_status_lot_config)
        list_only_in_list_status_lot_config_table_df = [item for item in list_status_lot_config_table_df if
                                                        item not in set_list_existing_status_lot_config]
        logger.debug(f"StatusLotConfig need insert/update: {list_only_in_list_status_lot_config_table_df}")

        if list_only_in_list_status_lot_config_table_df:
            status_lot_config_table_df = pd.DataFrame(list_only_in_list_status_lot_config_table_df,
                                                      columns=status_lot_config_table_df_temp.columns)
            for index, row in status_lot_config_table_df.iterrows():
                try:
                    logger.info(f"Upsert StatusLotConfig: config_id={row['config_id']}, project_id={row['project_id']}, lot_id={row['lot_id']}, status={row['status']}")

                    existing_record = session.query(StatusLotConfig).filter_by(
                        config_id=row['config_id'],
                        project_id=row['project_id'],
                        lot_id=row['lot_id']
                    ).first()
                    if existing_record is not None:
                        # Câu lệnh cập nhật ORM
                        stmt = (
                            update(StatusLotConfig).
                            where(
                                and_(
                                    StatusLotConfig.config_id == row['config_id'],
                                    StatusLotConfig.project_id == row['project_id'],
                                    StatusLotConfig.lot_id == row['lot_id']
                                )
                            ).
                            values(status=row['status'])
                        )
                        session.execute(stmt)
                        logger.info(f"Updated StatusLotConfig: config_id={row['config_id']}, project_id={row['project_id']}, lot_id={row['lot_id']}")
           
                    else:
                        new_querry_status_lot_config_table = StatusLotConfig(config_id=row['config_id'],
                                                                             lot_id=row['lot_id'],
                                                                             status=row['status'],
                                                                             project_id=row['project_id'])
                        session.add(new_querry_status_lot_config_table)
                        logger.info(f"Inserted StatusLotConfig: config_id={row['config_id']}, project_id={row['project_id']}, lot_id={row['lot_id']}")

                except Exception as e:
                    print(e)
                    logger.error(f"Error upserting StatusLotConfig config_id={row['config_id']}, project_id={row['project_id']}, lot_id={row['lot_id']}: {e}")
                    logger.error(traceback.format_exc())
                    session.rollback()

        # 12.---------------------------------table project_device_comment--------------------
        logger.info("=== Start processing ProjectDeviceComment table ===")
        list_existing_project_device_comment = (
            session.query(ProjectDeviceComment.comment_detail, ProjectDeviceComment.project_id,
                          ProjectDeviceComment.comment_id, ProjectDeviceComment.device_details_id).all())
        #st.write('list_existing_project_device_comment: ', list_existing_project_device_comment)
        project_device_comment = project_device_comment_table(df.loc[11:, ], project_name)
        if not project_device_comment.empty:
            project_device_comment_table_df_merge_prj = pd.merge(project_device_comment, project_table_df_querry,
                                                                 on='project_name',
                                                                 how='left')
            project_device_comment_table_df_merge_cmt = pd.merge(project_device_comment_table_df_merge_prj,
                                                                 comment_column_table_df_querry, on='comment_name',
                                                                 how='left')
            project_device_comment_table_df_temp = pd.merge(project_device_comment_table_df_merge_cmt,
                                                            device_details_table_df_querry,
                                                            on=['device_details_name', 'device_name'],
                                                            how='left')
            project_device_comment_table_df_temp.drop(columns=['project_name', 'comment_name', 'device_details_name'],
                                                      inplace=True)

            project_device_comment_table_df_temp.fillna('null', inplace=True)

            list_project_device_comment_table_df = list(
                project_device_comment_table_df_temp.itertuples(index=False, name=None))
            set_list_existing_project_device_comment = set(list_existing_project_device_comment)
            list_check_project_device_comment = list(
                set([(tup[1], tup[2], tup[3]) for tup in set_list_existing_project_device_comment]))
            # st.write("list_check_project_device_comment: ", list_check_project_device_comment)
            list_only_in_list_project_device_comment_table_df_insert = [item for item in
                                                                        list_project_device_comment_table_df if
                                                                        item not in set_list_existing_project_device_comment and (
                                                                            item[1], item[2],
                                                                            item[
                                                                                3]) not in list_check_project_device_comment]
            list_only_in_list_project_device_comment_table_df_update = [item for item in
                                                                        list_project_device_comment_table_df if
                                                                        item not in set_list_existing_project_device_comment and (
                                                                            item[1], item[2],
                                                                            item[
                                                                                3]) in list_check_project_device_comment]
            
            logger.debug(f"ProjectDeviceComment need insert: {list_only_in_list_project_device_comment_table_df_insert}")
            logger.debug(f"ProjectDeviceComment need update: {list_only_in_list_project_device_comment_table_df_update}")

            if list_only_in_list_project_device_comment_table_df_update:
                project_device_comment_table_df = pd.DataFrame(list_only_in_list_project_device_comment_table_df_update,
                                                               columns=project_device_comment_table_df_temp.columns)
                for index, row in project_device_comment_table_df.iterrows():
                    try:
                        logger.info(f"Update ProjectDeviceComment: project_id={row['project_id']}, comment_id={row['comment_id']}, device_details_id={row['device_details_id']}")

                        stmt = (
                            update(ProjectDeviceComment).
                            where(
                                and_(
                                    ProjectDeviceComment.comment_id == row['comment_id'],
                                    ProjectDeviceComment.project_id == row['project_id'],
                                    ProjectDeviceComment.device_details_id == row['device_details_id']
                                )
                            ).
                            values(comment_detail=row['comment_detail'])
                        )
                        session.execute(stmt)
                    except Exception as e:
                        print(e)
                        logger.error(f"Error updating ProjectDeviceComment: project_id={row['project_id']}, comment_id={row['comment_id']}, device_details_id={row['device_details_id']}: {e}")
                        logger.error(traceback.format_exc())
                        session.rollback()

            if list_only_in_list_project_device_comment_table_df_insert:
                project_device_comment_table_df = pd.DataFrame(list_only_in_list_project_device_comment_table_df_insert,
                                                               columns=project_device_comment_table_df_temp.columns)
                for index, row in project_device_comment_table_df.iterrows():
                    try:
                        logger.info(f"Insert ProjectDeviceComment: project_id={row['project_id']}, comment_id={row['comment_id']}, device_details_id={row['device_details_id']}")

                        new_querry_project_device_comment_table_table = ProjectDeviceComment(
                            device_details_id=row['device_details_id'], comment_id=row['comment_id'],
                            comment_detail=row['comment_detail'], project_id=row['project_id'])
                        session.add(new_querry_project_device_comment_table_table)
                    #         session.commit()
                    except Exception as e:
                        logger.error(f"Error inserting ProjectDeviceComment: project_id={row['project_id']}, comment_id={row['comment_id']}, device_details_id={row['device_details_id']}: {e}")
                        logger.error(traceback.format_exc())
                        session.rollback()
        # 13.-------------------------table status_config_device_detail------------------------------
        # st.write('ok')
        try:
            logger.info("=== Start processing StatusConfigDeviceDetail table ===")
            list_existing_status_config_device_detail = (
                session.query(StatusConfigDeviceDetail.status, StatusConfigDeviceDetail.project_id,
                            StatusConfigDeviceDetail.config_id, StatusConfigDeviceDetail.device_details_id).all())
            

            logger.debug(f"Existing StatusConfigDeviceDetail: {list_existing_status_config_device_detail}")
            # st.write('ok1')
            status_config_device_detail = status_config_device_detail_table(df.loc[12:, ], project_name)
            logger.debug(f"Raw status_config_device_detail_table: {status_config_device_detail}")

            status_config_device_detail_table_df_merge_prj = pd.merge(status_config_device_detail, project_table_df_querry,
                                                                    on='project_name',
                                                                    how='left')
            status_config_device_detail_table_df_merge_config = pd.merge(status_config_device_detail_table_df_merge_prj,
                                                                        config_table_df_querry,
                                                                        on='config_name',
                                                                        how='left')
            status_config_device_detail_table_df_temp = pd.merge(status_config_device_detail_table_df_merge_config,
                                                                device_details_table_df_querry,
                                                                on=['device_details_name', 'device_name'],
                                                                how='left')
            status_config_device_detail_table_df_temp.drop(columns=['project_name', 'config_name', 'device_details_name'],
                                                        inplace=True)
            status_config_device_detail_table_df_temp.fillna('null', inplace=True)
            status_config_device_detail_table_df_temp['status'] = status_config_device_detail_table_df_temp['status'].apply(
                lambda x: str(x) if x is not None else '')
            list_status_config_device_detail_table_df = list(
                status_config_device_detail_table_df_temp.itertuples(index=False, name=None))
            set_list_existing_status_config_device_detail = set(list_existing_status_config_device_detail)
            list_check_status_config_device_detail = list(
                set([(tup[1], tup[2], tup[3]) for tup in set_list_existing_status_config_device_detail]))
            list_only_in_list_status_config_device_detail_table_df_insert = [item for item in
                                                                            list_status_config_device_detail_table_df
                                                                            if
                                                                            item not in set_list_existing_status_config_device_detail and (
                                                                                item[1], item[2], item[
                                                                                    3]) not in list_check_status_config_device_detail]
            list_only_in_list_status_config_device_detail_table_df_update = [item for item in
                                                                            list_status_config_device_detail_table_df
                                                                            if
                                                                            item not in set_list_existing_status_config_device_detail and (
                                                                                item[1], item[2], item[
                                                                                    3]) in list_check_status_config_device_detail]
            
            logger.debug(f"StatusConfigDeviceDetail need insert: {list_only_in_list_status_config_device_detail_table_df_insert}")
            logger.debug(f"StatusConfigDeviceDetail need update: {list_only_in_list_status_config_device_detail_table_df_update}")

            st.write(list_only_in_list_status_config_device_detail_table_df_insert)

            if list_only_in_list_status_config_device_detail_table_df_insert:
                status_config_device_detail_table_df = pd.DataFrame(
                    list_only_in_list_status_config_device_detail_table_df_insert,
                    columns=status_config_device_detail_table_df_temp.columns)
                logger.info(f"Inserting {len(status_config_device_detail_table_df)} StatusConfigDeviceDetail records")
                st.write(status_config_device_detail_table_df)
                for index, row in status_config_device_detail_table_df.iterrows():
                    try:
                        logger.info(
                            f"Insert StatusConfigDeviceDetail: device_details_id={row['device_details_id']}, "
                            f"config_id={row['config_id']}, project_id={row['project_id']}, status={row['status']}")
                        new_querry_status_config_device_detail_table = StatusConfigDeviceDetail(
                            device_details_id=row['device_details_id'], config_id=row['config_id'],
                            status=row['status'], project_id=row['project_id'])
                        session.add(new_querry_status_config_device_detail_table)
                    except Exception as e:
                        logger.error(
                            f"Error inserting StatusConfigDeviceDetail device_details_id={row['device_details_id']}, "
                            f"config_id={row['config_id']}, project_id={row['project_id']}: {e}")
                        logger.error(traceback.format_exc())
                        session.rollback()

            if list_only_in_list_status_config_device_detail_table_df_update:
                status_config_device_detail_table_df = pd.DataFrame(
                    list_only_in_list_status_config_device_detail_table_df_update,
                    columns=status_config_device_detail_table_df_temp.columns)
                logger.info(f"Updating {len(status_config_device_detail_table_df)} StatusConfigDeviceDetail records")
                for index, row in status_config_device_detail_table_df.iterrows():
                    try:
                        logger.info(
                            f"Update StatusConfigDeviceDetail: device_details_id={row['device_details_id']}, "
                            f"config_id={row['config_id']}, project_id={row['project_id']}, status={row['status']}")
                        stmt = (
                            update(StatusConfigDeviceDetail).
                            where(
                                and_(
                                    StatusConfigDeviceDetail.config_id == row['config_id'],
                                    StatusConfigDeviceDetail.project_id == row['project_id'],
                                    StatusConfigDeviceDetail.device_details_id == row['device_details_id']
                                )
                            ).
                            values(status=row['status'])
                        )
                        session.execute(stmt)
                    except Exception as e:
                        logger.error(
                            f"Error updating StatusConfigDeviceDetail device_details_id={row['device_details_id']}, "
                            f"config_id={row['config_id']}, project_id={row['project_id']}: {e}")
                        logger.error(traceback.format_exc())
                        session.rollback()

            session.commit()
            session.close()
            logger.info("Commit StatusConfigDeviceDetail thành công")

        except Exception as e:
            logger.error(f"Exception in StatusConfigDeviceDetail: {e}")
            logger.error(traceback.format_exc())
            session.rollback()


def delete_project_syo(df_):
    df_delete = df_.loc[df_['Delete'] == True]
    engine = connect_db()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    for index, row in df_delete.iterrows():
        project_name_ = row['project_name']
        project_name_ = str(project_name_).upper()
        session.query(Project).filter(Project.project_name == project_name_).delete()
    session.commit()
    session.close()
    st.success("Delete Completed")
    return df_.loc[df_['Delete'] == False]


def get_gray_blue(project_name):
    project_name = project_name.upper()
    engine = connect_db()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    all_project = [name[0] for name in session.query(Project.project_name).all()]
    max_project_id = session.query(func.max(Project.project_id)).scalar()
    if project_name not in all_project:
        if max_project_id is None:
            max_project_id = 0
        new_project = Project(project_id=max_project_id + 1, project_name=project_name)
        session.add(new_project)
        session.commit()
    result_querry_region_4_gray = set(session.query(Device.device_group).all())
    result_querry_region_4_blue = set(session.query(Device.device_name).all())
    session.close()
    return result_querry_region_4_gray, result_querry_region_4_blue


def querry_to_show_project():
    engine = connect_db()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    df_project = session.query(Project.project_name).all()
    all_project = [name[0] for name in session.query(Project.project_name).all()]
    session.close()
    df = pd.DataFrame(df_project, columns=['project_name'])
    df['Delete'] = False
    return df


def update_syo():
    folder_data = os.path.join(BASE_DIR_DATAS, '仕様表')
    folder_data = folder_data.replace("\\", "/")
    st.session_state.message_4 = ''
    # st.write('folder_data: ', folder_data)
    if os.path.exists(folder_data):
        syo_files = [f for f in os.listdir(folder_data) if f.endswith('.xlsx')]
        # streamlit.write('syo_files: ',syo_files)
        if syo_files is not None and len(syo_files) > 0:
            for file_update in syo_files:
                code = file_update.split('.')[0]
                if "仕様表_" == code[0:4]:
                    code = code.replace("仕様表_", "")
                    file_path = os.path.join(folder_data, file_update)
                    df, df_1 = dataframe_convert(file_path, code, [], [])
                    if not isinstance(df, pd.DataFrame):
                        if df_1:
                            st.error(df + str(df_1))
                            st.session_state.message_4 += "\n" + "\n" + df + str(df_1)
                        else:
                            st.error(df)
                            st.session_state.message_4 = df
                        continue
                    update_data_new(code, df, df_1)
                    if df.shape[1] != 7:
                        data_syo_hyo, unique_list_max, unique_list_submax = querry_data_syo_hyo(code)
                        data_syo_hyo = data_syo_hyo.fillna("")
                        st.session_state.message_4 = 'Updated'
                    else:
                        df_1, merged_df_4_optioncode, unique_list_max, unique_list_submax = update_and_querry_form_data()
                        form_df = pd.concat([df_1, merged_df_4_optioncode], axis=0)
                        st.success('Updated!')
                        st.session_state.message_4 = 'Updated'
                else:
                    st.error('Upload file name is incorrect')
                    st.session_state.message_4 = 'Upload file name is incorrect'
        else:
            del st.session_state['message_4']
        shutil.rmtree(folder_data)
    else:
        #st.write("link khong ton tai")
        pass


def update_syo_form(files_updates):
    if len(files_updates) > 0:
        for file_update in files_updates:
            if file_update.name == "仕様表_FORM.xlsx":
                code = file_update.name.split('.')[0]
                code = code.replace("仕様表_", "")
                df, df_1 = dataframe_convert(file_update, code, [], [])
                if not isinstance(df, pd.DataFrame):
                    if df_1:
                        st.error(df + str(df_1))
                    else:
                        st.error(df)
                    continue
                update_data_new(code, df, df_1)
                st.success('Updated!')
                st.session_state.message_5 = "Updated!!!"
    elif len(files_updates) == 0:
        print()
