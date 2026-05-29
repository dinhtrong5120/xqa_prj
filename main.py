import subprocess
import os
 
if __name__ == '__main__':
    base_dir = os.getcwd()
    path_file = os.path.join(base_dir, 'NEW VERSION ❤.py')
    subprocess.run(["streamlit", "run", path_file])
