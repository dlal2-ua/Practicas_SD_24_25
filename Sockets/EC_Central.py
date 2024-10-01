import socket

# Leer mapa de la ciudad y taxis
def leer_mapa(fichero_mapa):
    mapa = {}
    with open(fichero_mapa, 'r') as f:
        for linea in f:
            partes = linea.strip().split()
            mapa[partes[0]] = (int(partes[1]), int(partes[2]))
    return mapa

def leer_taxis(fichero_taxis):
    taxis = []
    with open(fichero_taxis, 'r') as f:
        for linea in f:
            partes = linea.strip().split()
            taxis.append({'id': partes[0], 'x': int(partes[1]), 'y': int(partes[2]), 'estado': partes[3]})
    return taxis

# Asignar taxi al cliente
def asignar_taxi(destino, taxis):
    taxi_libre = next((taxi for taxi in taxis if taxi['estado'] == 'LIBRE'), None)
    if taxi_libre:
        taxi_libre['estado'] = 'OCUPADO'
        return taxi_libre['id'], taxi_libre
    return None, None

# Inicializar el servidor
def iniciar_servidor():
    mapa = leer_mapa('mapa.txt')
    taxis = leer_taxis('taxis.txt')
    
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('localhost', 5000))
    servidor.listen(5)
    
    print("Servidor CENTRAL esperando solicitudes...")
    while True:
        cliente_socket, direccion = servidor.accept()
        destino = cliente_socket.recv(1024).decode('utf-8')
        print(f"Solicitud de servicio para destino: {destino}")
        
        id_taxi, taxi = asignar_taxi(destino, taxis)
        if id_taxi:
            cliente_socket.sendall(b'OK')
            print(f"Servicio asignado al taxi: {id_taxi}")
            # Aquí podrías iniciar la secuencia para mover el taxi
        else:
            cliente_socket.sendall(b'KO')
            print("No hay taxis disponibles")
        
        cliente_socket.close()

iniciar_servidor()
