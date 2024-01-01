import subprocess
import os

# Get the directory of the current Python file
dir_path = os.path.dirname(os.path.realpath(__file__))

# Set the directory as the working directory
os.chdir(dir_path)

subprocess.Popen("python bot.py", shell=True)
subprocess.Popen("python log.py", shell=True)