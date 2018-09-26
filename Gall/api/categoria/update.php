<?php

	header('Acess-Control-Allow-Origin: *');
	header('Content-Type: application/json');
	
	require_once '../../config/Conexao.php';
	require_once '../../models/Categoria.php';

    if($_SERVER['REQUEST_METHOD'] == 'PUT') {
    	$db = new Conexao();
    	$con = $db->getConexao();

        $categoria = new Categoria($con);
        $dados = json_decode(file_get_contents("php://input"));

        $categoria->id = $dados->id;
        $categoria->nome = $dados->nome;
        $categoria->descricao = $dados->descricao;

        if($categoria->update()) {
        	$res = array('mensagem','Categoria atualiza');
        } else {
        	$res = array('mensagem','Erro na atualização da categoria');
        }
        echo json_encode($res);
    }