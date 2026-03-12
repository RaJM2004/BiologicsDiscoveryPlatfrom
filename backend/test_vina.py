import subprocess
import os

vina_path = os.path.join(os.getcwd(), "bin", "vina.exe")
print(f"Testing binary at: {vina_path}")
print(f"Exists: {os.path.exists(vina_path)}")

try:
    result = subprocess.run([vina_path, "--version"], capture_output=True, text=True)
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
except Exception as e:
    print(f"Error: {e}")
