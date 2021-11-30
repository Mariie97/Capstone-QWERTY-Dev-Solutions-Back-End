import sys

print("Cristo: ", sys.path)
sys.path.insert(0, '/var/www/PaRapido_backend/Capstone-QWERTY-Dev-Solutions-Back-End')
print('Manuel: ', sys.path)

activate_this = '/home/ubuntu/venv/bin/activate_this.py'
with open(activate_this) as file:
    exec(file.read(), dict(__file__=activate_this))

from app import app as application