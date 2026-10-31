require('dotenv').config();
const express = require('express');
const cors = require('cors');
const mysql = require('mysql2');

const app = express();
app.use(cors());
app.use(express.json());

// Conecta ao banco usando as senhas protegidas do .env
const db = mysql.createConnection({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME
});

db.connect((err) => {
    if (err) {
        console.error('Erro ao conectar ao banco de dados:', err);
        return;
    }
    console.log('Conectado ao MySQL com sucesso!');
});

// Cria a rota que envia os filmes para o front-end
app.get('/filmes', (req, res) => {
    const sql = 'SELECT * FROM filmes';
    
    db.query(sql, (err, results) => {
        if (err) {
            console.error('Erro na consulta:', err);
            return res.status(500).json({ erro: 'Erro ao buscar filmes no banco de dados' });
        }
        res.json(results);
    });
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Servidor da API rodando na porta ${PORT}`);
});