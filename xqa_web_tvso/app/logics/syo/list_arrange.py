import ast


def check_list_sap_xep(text_file_path, new_list):
    """
    Bên Nhật yêu cầu danh sách hiển thị ra màn hình có thứ t giống với file của họ, file text tạo ra để lưu lại thứ tự

    Parameters:
        file_path (str): Path to the file containing the stored list (as a string representation).
        new_elements (list): List of new elements to add and prioritize in the result.

    Steps:
        1. Read the existing list from the file and convert it from string to Python list.
        2. Initialize a new list with all elements from 'new_elements'.
        3. For each element in the original list, if it does not exist in the new list,
           insert it into the appropriate position to maintain the relative order.
        4. Overwrite the file with the updated, merged, and sorted list.

    Example:
        If the file contains: ['b', 'c', 'd']
        And new_elements = ['a', 'c']
        The result written to the file will be: ['a', 'c', 'b', 'd']
    """
    with open(text_file_path, 'r') as file:
        data = file.read()

    # Convert string to list
    list_in_db = ast.literal_eval(data)
    sorted_list = []

    # Add all elements from new_elements to sorted_list
    for item in new_list:
        sorted_list.append(item)

    # Insert elements from the original list if not already present
    for item in list_in_db:
        if item not in sorted_list:
            # Tìm vị trí để chèn phần tử
            for i in range(len(sorted_list)):
                if (i == len(sorted_list) - 1) or (
                        sorted_list[i + 1] in list_in_db and list_in_db.index(sorted_list[i + 1]) > list_in_db.index(
                    item)):
                    sorted_list.insert(i + 1, item)
                    break

    # Overwrite the file with the updated list
    with open(text_file_path, 'w') as file:
        file.write(str(sorted_list))
