<?php

	header('Acess-Control-Allow-Origin: *');
	header('Content-Type: application/json');
	
	require_once '../../config/Conexao.php';
	require_once '../../models/Post.php';

    if($_SERVER['REQUEST_METHOD'] == 'PUT') {
    	$db = new Conexao();
    	$con = $db->getConexao();

        $post = new Post($con);
        $dados = json_decode(file_get_contents("php://input"));

        $post->id = $post->id;
        $post->titulo = $dados->titulo;
        $post->texto = $dados->texto;
        $post->id_categoria = $dados->id_categoria;
        $post->autor = $dados->autor;

        if($post->update()) {
        	$res = array('mensagem' => 'post atualizada');
        } else {
        	$res = array('mensagem' => 'Erro na atualização da post');
        }
        echo json_encode($res);
    }


