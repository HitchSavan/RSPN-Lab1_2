import socket
import math
import numpy as np
from mathutils import Matrix

address_to_server = ('localhost', 55555)

print("Type 'help' for commands")

while True:

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect(address_to_server)

    client.send(b'Connected')

    message = client.recv(1024)

    a = np.frombuffer(message, dtype=np.float64)
    k = 0
    matrix = Matrix.Translation((0, 0, 0))

    for i in range(4):
        for j in range(4):
            matrix[i][j] = a[k]
            k += 1

    msg = input("Input command: ").lower()

    if (msg in ["exit", "quit"]):
        break

    if (msg == "help"):
        print("\nTo move object input 'move [x] [y] [z]'")
        print("To move object to specific coordinates input 'move to [x] [y] [z]'")
        print("To rotate object input 'rotate [degree] [axis X/Y/Z]'")
        print("To rotate object from origin orientation input 'rotate to [degree] [axis X/Y/Z]'\n")
        continue

    data = msg.split()
    mode = data[0]

    if (mode == "move"):
        if (data[1] == "to"):
            for i in range(3):
                matrix[0 + i][3] = float(data[2 + i])
        else:
            translation = (float(data[1]), float(data[2]), float(data[3]))
            matrix @= Matrix.Translation(translation)
    
    if (mode == "rotate"):
        if (data[1] == "to"):
            rotation_angle = math.radians(float(data[2]))
            rotation_axis = data[3].upper()
            rotation_matrix = Matrix.Rotation(rotation_angle, 4, rotation_axis)
            for i in range(3):
                for j in range(3):
                    matrix[i][j] = rotation_matrix[i][j]
        else:
            rotation_angle = math.radians(float(data[1]))
            rotation_axis = data[2].upper()
            matrix @= Matrix.Rotation(rotation_angle, 4, rotation_axis)

    print(f'Modified matrix: \n{matrix}')

    a = []
    for i in matrix:
        for j in i:
            a.append(j)

    x = np.array(a)
    xb = x.tobytes()

    client.send(xb)

    data = client.recv(1024).decode()
    print(data)