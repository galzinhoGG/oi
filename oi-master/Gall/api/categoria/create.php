<?php
	header('Content-Type: application/json');
	
	require_once '../../config/Conexao.php';
	require_once '../../models/Categoria.php';
    if($_SERVER['REQUEST_METHOD'] == 'POST') {
    	$db = new Conexao();
    	$con = $db->getConexao();

        $dados = json_decode(file_get_contents("php://input"));

        $categoria = new Categoria($con);
        $categoria->nome = $dados->nome;
        $categoria->descricao = $dados->descricao;

        if($categoria->create()) {
        	$res = array('mensagem','Categoria criada');
        } else {
        	$res = array('mensagem','Erro na criação da categoria');
        }
        echo json_encode($res);
    }