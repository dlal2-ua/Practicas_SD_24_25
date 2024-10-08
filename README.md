MEMORIA

En relacion con la base de datos [BBDD]:
  -Hemos decidido hacer una base de datos usando SQLite dado que en comparación con el fichero, el manejo de datos con sql es mucho más sencillo y fácil de obtener la información
  -Hemos decidido estos campos para la base de datos:
    ·El id del taxi (uniques)
    ·El Destino (char)
    ·El estado (booleano)
    ·La coordenada (int)
      -Coordenada X
      -Coordenada Y

En relacion al taxi:
  -Hemos decidido que el digital engine sera el servidor por lo tanto en los argumentos del digital engine no vamos a poner que esten ni la ip ni el puerto del servidor, 
  con lo que el servidor no hace falta que conozca la ip ni el puerto del cliente.
