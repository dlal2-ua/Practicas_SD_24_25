const https = require('https'); 
const express = require("express"); 
const sqlite3= require ("sqlite3").verbose(); 
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

const db = new sqlite3.Database("database.db", (err) => {
    if (err) {
        console.error("Error al conectar con la base de datos:", err.message);
        return;
    }
    console.log("Conexión a la base de datos SQLite correcta");
});

appSD.use(bodyParser.json());


// Se define el puerto 

appSD.get("/",(req, res) => { res.json({message:'Página de inicio de aplicación de ejemplo de SD'}) 
}); 



// Listado de todos los usuarios 
appSD.get("/taxis", (request, response) => {
    console.log('Listado de todos los taxis');

    // Consulta para obtener toda la información de la tabla taxis
    const sql = 'SELECT * FROM taxis';

    // Ejecutar la consulta en la base de datos SQLite
    db.all(sql, [], (error, rows) => {
        if (error) {
            console.error("Error ejecutando la consulta:", error.message);
            response.status(500).send("Error en la base de datos");
            return;
        }

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

    // Ejecutar la consulta en la base de datos SQLite
    db.get(sql, [id], (error, row) => {
        if (error) {
            console.error("Error ejecutando la consulta:", error.message);
            response.status(500).send("Error en la base de datos");
            return;
        }

        if (row) {
            response.json(row); // Devolver el resultado como JSON
        } else {
            response.status(404).send("Taxi no encontrado");
        }
    });
});
appSD.post("/taxis", (request, response) => {
    console.log("Añadir nuevo taxi");

    // Consulta para insertar un nuevo taxi solo con el id
    const sql = "INSERT INTO taxis (id, destino_a_cliente, destino_a_final, estado, coordX, coordY, pasajero) VALUES (?, NULL, NULL, NULL, 1, 1, 0)";

    // Obtener el id del cuerpo de la solicitud
    const { id } = request.body;

    if (!id) {
        return response.status(400).send("El campo 'id' es obligatorio");
    }

    // Ejecutar la consulta
    db.run(sql, [id], function (error) {

        if (error) {
            if(error.message == "SQLITE_CONSTRAINT: UNIQUE constraint failed: taxis.id") {
                console.error("Error al registrar un taxi ya registrado en la base de datos")
                return response.status(500).send("Este taxi ya está registrado")
            }
            console.error("Error al insertar en la base de datos:", error.message);
            return response.status(500).send("Error en la base de datos");
        }

        response.send(`Taxi creado con ID: ${id}`);
    });
});
appSD.delete("/taxis/:id", (request, response) => {
    console.log("Borrar taxi");

    // Obtener el id del parámetro de la URL
    const { id } = request.params;

    // Consulta para eliminar el taxi con el id especificado
    const sql = "DELETE FROM taxis WHERE id = ?";

    // Ejecutar la consulta
    db.run(sql, [id], function (error) {
        if (error) {
            console.error("Error al eliminar en la base de datos:", error.message);
            return response.status(500).send("Error en la base de datos");
        }

        if (this.changes > 0) {
            response.send(`Taxi con ID: ${id} eliminado`);
        } else {
            response.status(404).send("Taxi no encontrado");
        }
    });
});
