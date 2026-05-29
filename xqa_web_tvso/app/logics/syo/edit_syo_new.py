import pandas as pd
import numpy as np

def process_dataframe(df_):
    df_['default'] = df_['default'].fillna('')
    # Lọc các hàng hợp lệ
    valid_df = df_[~df_['group_key_map'].isin([None, '', 'default_key', np.nan])]
    if not valid_df.empty:
        # Lấy danh sách các cột bắt đầu bằng 'conf-'
        conf_cols = [col for col in df_.columns if str(col).startswith('conf-')]

        # Tạo hàm để chỉnh sửa các giá trị 'conf-'
        def update_conf_values(group):
            for col in conf_cols:
                unique_values = group[col].unique()
                # Lấy giá trị đầu tiên không phải là '-'
                valid_value = next((val for val in unique_values if val not in ['-', 'w/o']), None)
                if valid_value:
                    group[col] = valid_value
            return group

        # Tạo một dataframe tạm thời để lưu kết quả
        result_df = pd.DataFrame(columns=df_.columns)
        # Áp dụng hàm trên từng group và lưu vào dataframe tạm thời
        for name, group in valid_df.groupby('group_key_map'):
            updated_group = update_conf_values(group.copy())  # Copy để tránh thay đổi original dataframe
            result_df = pd.concat([result_df, updated_group])

        # Ghép các hàng không hợp lệ vào dataframe kết quả
        final_df = pd.concat([result_df, df_[df_['group_key_map'].isin([None, '', 'default_key', np.nan])]])
        final_df = final_df.sort_index()

        def update_conf_values(row):
            if row['default'] not in [None, np.nan, '']:
                for col in final_df.columns:
                    if str(col).startswith('conf-'):
                        if str(row['default']).upper() == 'XQA':
                            final_df.at[row.name, col] = ''
                        else:
                            final_df.at[row.name, col] = row['default']

        # Áp dụng hàm update_conf_values cho từng hàng
        final_df.apply(update_conf_values, axis=1)
        return final_df
    else:
        def update_conf_values(row):
            if row['default'] not in [None, np.nan, '', np.NaN]:
                for col in df_.columns:
                    if str(col).startswith('conf-'):
                        df_.at[row.name, col] = row['default']

        # Áp dụng hàm update_conf_values cho từng hàng
        df_.apply(update_conf_values, axis=1)
        return df_