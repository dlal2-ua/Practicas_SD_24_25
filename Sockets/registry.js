const https = require('https'); 
const express = require("express"); 
const mysql = require("mysql")
const fs = require('fs'); 

const bodyParser = require("body-parser"); 

const appSD = express(); 

const port=3000; 

// Configuración de la conexión a la base de datos MySQL 

// Arrancar el servidor 
https 
    .createServer( 
//Se indican el certificado público y la clave privada 
        { 
            key: fs.readFileSync("certServ.pem"), 
            cert: fs.readFileSync("certServ.pem"), 
        }, 
        appSD   
    ) 
    .listen(port, () => { 
        console.log("https API Server listening: "+port); 
    });
/*
const db = new sqlite3.Database("database.db", (err) => {
    if (err) {
        console.error("Error al conectar con la base de datos:", err.message);
        return;
    }
    console.log("Conexión a la base de datos SQLite correcta");
});*/
const connection = mysql.createConnection({ 
    host: 'localhost', 
    user:'root', 
    password: '1234', 
    database:'bbdd' 
    }); 
appSD.use(bodyParser.json());


// Listado de todos los usuarios 
appSD.get("/taxis", (request, response) => {
    console.log('Listado de todos los taxis');

    // Consulta para obtener toda la información de la tabla taxis
    const sql = 'SELECT * FROM taxis';

    // Ejecutar la consulta en la base de datos MySQL
    connection.query(sql, (error, rows) => {
        if (error) {
            console.error("Error ejecutando la consulta:", error.message);
            response.status(500).send("Error en la base de datos");
            return;
        }

        // Verificar si hay resultados
        if (rows.length > 0) {
            response.json(rows); // Devolver los resultados como JSON
        } else {
            response.send("No hay resultados");
        }
    });
});
appSD.get("/taxis/:id", (request, response) => {
    const { id } = request.params; // Obtener el id de los parámetros de la URL
    console.log(`Buscando taxi con id: ${id}`);

    // Consulta para obtener el taxi con el id especificado
    const sql = 'SELECT * FROM taxis WHERE id = ?';

    // Ejecutar la consulta en la base de datos MySQL
    connection.query(sql, [id], (error, rows) => {
        if (error) {
            console.error("Error ejecutando la consulta:", error.message);
            response.status(500).send("Error en la base de datos");
            return;
        }

        if (rows.length > 0) { // Verificar si se encontraron resultados
            response.json(rows); // Devolver el resultado como JSON
        } else {
            response.status(404).send("Taxi no encontrado");
        }
    });
});
appSD.post("/taxis", (request, response) => {
    console.log("Añadir nuevo taxi");

    // Consulta para insertar un nuevo taxi solo con el id
    const sql = `
        INSERT INTO taxis (id, destino_a_cliente, destino_a_final, estado, coordX, coordY, pasajero) 
        VALUES (?, NULL, NULL, NULL, 1, 1, 0)
    `;

    // Obtener el id del cuerpo de la solicitud
    const { id } = request.body;

    // Validar que el campo 'id' exista
    if (!id) {
        return response.status(400).send("El campo 'id' es obligatorio");
    }

    // Ejecutar la consulta
    connection.query(sql, [id], (error, results) => {
        if (error) {
            // Manejar error de restricción UNIQUE
            if (error.code === "SQLITE_CONSTRAINT") {
                console.error("Error: El ID del taxi ya existe en la base de datos");
                return response.status(409).send("Este taxi ya está registrado");
            }

            console.error("Error al insertar en la base de datos:", error.message);
            return response.status(500).send("Error en la base de datos");
        }

        // Responder con éxito
        response.status(201).send(`Taxi creado con ID: ${id}`);
    });
});
appSD.delete("/taxis/:id", (request, response) => {
    console.log("Borrar taxi");

    // Obtener el id del parámetro de la URL
    const { id } = request.params;

    // Consulta para eliminar el taxi con el id especificado
    const sql = "DELETE FROM taxis WHERE id = ?";

    // Ejecutar la consulta
    connection.query(sql, [id], (error, results) => {
        if (error) {
            console.error("Error al eliminar en la base de datos:", error.message);
            return response.status(500).send("Error en la base de datos");
        }

        // Verificar si alguna fila fue eliminada
        if (results.affectedRows > 0) {
            response.send(`Taxi con ID: ${id} eliminado`);
        } else {
            response.status(404).send("Taxi no encontrado");
        }
    });
});
