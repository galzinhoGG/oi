<?php

	header('Acess-Control-Allow-Origin: *');
	header('Content-Type: application/json; charset=utf-8');
	
	require_once '../../config/Conexao.php';
	require_once '../../models/Categoria.php';

	 if($_SERVER['REQUEST_METHOD'] == 'DELETE') {
    	$db = new Conexao();
    	$con = $db->getConexao();

        $categoria = new Categoria($con);
        $dados = json_decode(file_get_contents("php://input"));

        $categoria->id = $dados->id;

        if($categoria->delete()) {
        	$res = ['mensagem'=>'Categoria deletada'];
        } else {
        	$res = ['mensagem'=>'Erro na deletação da categoria'];
        }
    	echo json_encode($res);   
    }