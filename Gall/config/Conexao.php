<?php


/*
	Classe que contém os parâmetros para conexão e o método que retona a conexão
*/

class Conexao {
	//credenciais de acesso ao BD
	private $host = 'localhost';
	private $dbname = 'meu_blog';
	private $user = 'root';
	private $passwd = '';

	//variável para a conexão
	private $conexao;

	public function getConexao() {
		//estabelecer uma conexão e retornar a variável com a conexão
		$this->conexao = null;

		try {
			$this->conexao = new PDO('mysql:host='.$this->host.';dbname='.$this->dbname, $this->user, $this->passwd);
		} catch(PDOException $e) {
			echo "Erro na conexão: " . $e->getMessage();
		}

		return $this->conexao;
	}
}