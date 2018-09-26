<?php
	header('Content-Type: application/json, charset=utf-8');
	
	require_once '../../config/Conexao.php';
	require_once '../../models/Post.php';
    if($_SERVER['REQUEST_METHOD'] == 'POST') {
    	$db = new Conexao();
    	$con = $db->getConexao();

        $dados = json_decode(file_get_contents("php://input"));

        $post = new Post($con);
        $post->titulo = $dados->titulo;
        $post->texto = $dados->texto;
        $post->id_categoria = $dados->id_categoria;
        $post->autor = $dados->autor;

        if($post->create()) {
        	$res = array('Mensagem: ','Publicação criada');
        } else {
        	$res = array('Mensagem: ','Erro na criação da publicação');
        }
        echo json_encode($res);
    }