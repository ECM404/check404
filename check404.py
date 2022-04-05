import subprocess
from subprocess import PIPE

process = subprocess.Popen("./a.out", stdin=PIPE, stdout=PIPE, encoding='utf-8')
process.stdin.write("5\n")
stdout, stderr = process.communicate()
print(stdout)
