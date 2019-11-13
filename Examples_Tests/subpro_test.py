import subprocess
import os
import signal
if __name__ == "__main__":
    this_dir = os.path.dirname(__file__)
    gen_path = os.path.join(this_dir,os.path.join("pub_bridges","_rosout.py"))
    p = {}
    subprocess.Popen(["python",gen_path])
    K = subprocess.Popen(["python",gen_path]).pid
    pass