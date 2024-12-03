const express = require("express"); 
const sqlite3= require ("sqlite3").verbose(); 
const bodyParser = require("body-parser"); 

const appSD = express(); 

// Configuración de la conexión a la base de datos MySQL 


const db = new sqlite3.Database("database.db", (err) => {
    if (err) {
        console.error("Error al conectar con la base de datos:", err.message);
        return;
    }
    console.log("Conexión a la base de datos SQLite correcta");
});

appSD.use(bodyParser.json());


// Se define el puerto 
const port=3000; 

appSD.get("/",(req, res) => { res.json({message:'Página de inicio de aplicación de ejemplo de SD'}) 
}); 



// Ejecutar la aplicacion 
appSD.listen(port, () => { 
    console.log(`Ejecutando la aplicación API REST de SD en el puerto ${port}`); 
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
