<?php

include_once '../config/Conexao.php';
include_once '../models/Categoria.php';

// Instancia o objeto de conexão
$db = new Conexao();

// recebe a conexão feita
$conexao = $db->getConexao();

// instancia o objeto categoria
// passa a conexao
$cat = new Categoria($conexao);

// invoca o método read
$resultado = $cat->read();

$resultado2 = $cat->create();

$resultado3 = $cat->update();

print_r($resultado);