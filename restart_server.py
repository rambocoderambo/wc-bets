"""Restart the betting server without killing other Python processes.
Usage: python restart_server.py
"""
import subprocess, time, os, sys, signal

def find_pid_by_port(port=5000):
    """Find the PID of the process listening on a given port."""
    try:
        output = subprocess.check_output(
            f'netstat -ano | findstr ":{port} "',
            shell=True, text=True
        )
        for line in output.strip().split("\n"):
            if "LISTENING" in line or "ESTABLISHED" in line:
                parts = line.strip().split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        return int(pid)
        return None
    except subprocess.CalledProcessError:
        return None

def find_server_pids():
    """Find all Python processes that might be our server."""
    try:
        output = subprocess.check_output(
            'wmic process where "name=\'python.exe\'" get processid,commandline',
            shell=True, text=True
        )
        pids = []
        for line in output.strip().split("\n"):
            if "server.py" in line.lower():
                parts = line.strip().split()
                pid = parts[-1] if parts[-1].isdigit() else None
                if pid:
                    pids.append(int(pid))
        return pids
    except:
        return []

if __name__ == "__main__":
    # Method 1: Kill by port (port 5000)
    pid = find_pid_by_port(5000)
    if pid:
        print(f"Found process on port 5000: PID {pid}")
        subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
        print(f"Killed PID {pid}")
        time.sleep(2)
    else:
        # Method 2: Kill by matching server.py in command line
        pids = find_server_pids()
        if pids:
            for p in pids:
                print(f"Killing server process: PID {p}")
                subprocess.run(["taskkill", "/PID", str(p), "/F"], capture_output=True)
            time.sleep(2)
        else:
            print("No existing server process found on port 5000")

    # Start server
    subprocess.Popen(
        [sys.executable, "server.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    print("Server restarted on http://localhost:5000")
