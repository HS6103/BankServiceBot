import subprocess
import os
import re
import ast
import argparse

def run_scripts_concurrently(scripts, msg):
    """
    Run multiple Python scripts concurrently.
    
    :param scripts: List of script paths to run.
    """
    processes = []
    outputLIST = []
    for script in scripts:
        try:
            #print(f"Starting script: {script}")
            process = subprocess.Popen(["python", script, "--msg", msg], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            processes.append((script, process))
        except FileNotFoundError:
            pass
            #print(f"Script not found: {script}")

    # Wait for all scripts to complete
    for script, process in processes:
        stdout, stderr = process.communicate()
        #print(f"Finished script: {script}")
        if process.returncode == 0:
            outputLIST.append(ast.literal_eval(stdout.decode()))
            #print(f"Output:\n{stdout.decode()}")
        else:
            pass
            #print(f"Error:\n{stderr.decode()}")
    return outputLIST

def get_relevant_doc(outputLIST):
    
    # 使用 max() 函數尋找分數最大的條目，並返回對應的字串
    max_entry = max(outputLIST, key=lambda x: x[1])
    max_score = max_entry[1]
    
    if max_score < 5:
        max_string = ''
    else:
        # 返回對應的字串
        max_string = re.sub(r"^[a-z_]+>>\n", "", max_entry[0]).strip("\n")
        
    
    return max_string

def main():
    
    # 使用 argparse 解析參數
    parser = argparse.ArgumentParser(description="Run toaster_(intent) with a message")
    parser.add_argument("--msg", type=str, help="Message to process", required=True)
    args = parser.parse_args()

    scripts_to_run = [
        os.path.join('toaster','toaster_line.py'),
        os.path.join('toaster','toaster_small_corp.py'),
    ]
    outputLIST = run_scripts_concurrently(scripts_to_run, args.msg)
    print(get_relevant_doc(outputLIST))

main()