import serial
port_name = 'COM7'
port = serial.Serial(port_name, 115200, timeout=None)
while True:
    data = port.readline().decode('utf-8').strip()
    print(data)