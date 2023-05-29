import bpy
import math
import socket
import threading
import select
import numpy as np
from mathutils import Matrix

# -----------------------------------------------------------------------------
# Настройки сокета

SERVER_ADDRESS = ('localhost', 55555)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(SERVER_ADDRESS)
server_socket.listen(20)

client_sockets = []

# -----------------------------------------------------------------------------
# Настройки куба

name = 'Cubert'

# Origin point transformation settings
mesh_offset = (0, 0, 0)
origin_offset = (0, 0, 0)

# -----------------------------------------------------------------------------
# Функции

def vert(x,y,z):
    """ Make a vertex """

    return (x + origin_offset[0], y + origin_offset[1], z + origin_offset[2])

def handle_client(client_socket, addr):
    while True:
        if select.select([client_socket], [], [], 0.1)[0]:

            message = client_socket.recv(1024)

            matrix = obj.matrix_world

            a = []
            for i in matrix:
                for j in i:
                    a.append(j)

            x = np.array(a)
            xb = x.tobytes()

            client_socket.send(xb)

            message = client_socket.recv(1024)
            client_socket.send(bytes('ok', encoding='UTF-8'))
            if message:

                a =  np.frombuffer(message, dtype=np.float64)
                k = 0

                for i in range(4):
                    for j in range(4):
                        matrix[i][j] = a[k]
                        k += 1
                
                print(obj.matrix_world)
                obj.matrix_world = matrix
                    
            else:
                print("Closing connection with %s" % str(addr))
                client_socket.close()
                client_sockets.remove(client_socket)
                break

def background_server():
    if select.select([server_socket], [], [], 0.1)[0]:
        client_socket, addr = server_socket.accept()
        print("Got a connection from %s" % str(addr))
        client_sockets.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()
    bpy.app.timers.register(background_server)

# -----------------------------------------------------------------------------
# Кубокод

verts = [vert(1.0, 1.0, -1.0),
         vert(1.0, -1.0, -1.0),
         vert(-1.0, -1.0, -1.0),
         vert(-1.0, 1.0, -1.0),
         vert(1.0, 1.0, 1.0),
         vert(1.0, -1.0, 1.0),
         vert(-1.0, -1.0, 1.0),
         vert(-1.0, 1.0, 1.0)]

faces = [(0, 1, 2, 3),
         (4, 7, 6, 5),
         (0, 4, 5, 1),
         (1, 5, 6, 2),
         (2, 6, 7, 3),
         (4, 0, 3, 7)]


# -----------------------------------------------------------------------------
# Добавляем объект в сцену

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

mesh = bpy.data.meshes.new(name)
mesh.from_pydata(verts, [], faces)

obj = bpy.data.objects.new(name, mesh)
bpy.context.scene.collection.objects.link(obj)

bpy.context.view_layer.objects.active = obj
obj.select_set(True)


# -----------------------------------------------------------------------------
# Перемещаем центральную точку

obj.location = [(i * -1) + mesh_offset[j] for j, i in enumerate(origin_offset)]


# -----------------------------------------------------------------------------
# Коннекшн

bpy.app.timers.register(background_server, first_interval=1.0)