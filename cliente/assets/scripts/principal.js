const nomedolugar = document.querySelector('.categorias')

async function josias(){
	let res = await fetch("http://localhost:80/oi-master/Gall/api/categoria/read.php ", {
		method: 'GET'
	})
	let data = await res.json()
	console.log(data);
	data.forEach(id=>{
		let div= document.createElement('div')
		categorias.appendChild(div)
		div.innerHTML=(id.nome)	
	})

}

josias()