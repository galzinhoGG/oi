<?php

    header('Acess-Control-Allow-Origin: *');
    header('Content-Type: application/json');
    
    require_once '../../config/Conexao.php';
    require_once '../../models/Post.php';

    $db = new Conexao();
    $con = $db->getConexao();

    $post= new Post($con);

//verificar 3 situações:
    //1 - não veio nenhum parametro - read()
    //2 - veio o parametro id - read(id)
    //3 - veio o parametro idcategoria - todos os posts dessa categoria - readByCat(idcategoria)
    if (isset($_GET['id'])){
        $resultado = $post->read($_GET['id']);
    }elseif (isset($_GET['idcategoria'])) {
        $resultado = $post->readByCat($_GET['idcategoria']);
    }else{
        $resultado = $post->read();
    }


    $qtde_cats = sizeof($resultado);

    if($qtde_cats>0){
        // $arr_categorias = array();
        // $arr_categorias['data'] = array();

        echo json_encode($resultado);
    }else{
        echo json_encode(array('mensagem' => 'nenhuma POST encontrada'));
    }