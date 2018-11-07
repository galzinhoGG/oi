const categorias = document.querySelector('#categorias')


async function josias(){

	let res = await fetch("http://localhost/oi-master/Gall/api/categoria/read.php ", {
		method: 'GET'
	})
	let data = await res.json()
	data.forEach(id=>{
		let div= document.createElement('div')
		div.setAttribute('id', id.id)
		categorias.appendChild(div)
		div.innerHTML=(id.nome)	

		div.addEventListener('click', function(){
			joseias(this.id)
		})
	})


}





josias()




const oi = document.querySelector('#post')
const conteudo = document.querySelector('#conteudo')


async function joseias(id){
console.log("ui")
	id = id || 0;
	if(id==0){
		var url = "http://localhost/oi-master/Gall/api/post/read.php";
	}else{
		var url = "http://localhost/oi-master/Gall/api/post/read.php?idcategoria="+id;		
	}
	let resp = await fetch(url, {
		method: 'GET'

	})

	let data1 = await resp.json()
	conteudo.innerHTML = ''
	data1.forEach(id=>{
		let post = document.createElement('div')
			post.setAttribute('class','post')
	
			let titulo = document.createElement('div')
			titulo.innerHTML = (id.titulo)
			post.appendChild(titulo)
	
			let texto = document.createElement('div')
			texto.innerHTML = (id.texto)
			post.appendChild(texto)
			conteudo.appendChild(post)


	})


}
joseias()
var el = document.querySelector('img'); 
el.addEventListener("click",function(){
	joseias()
});
console.log(el);














// posts = document.querySelector("main>div:last-child")
// async function pegarPosts(){
// 	let reqPost = await fetch('http://localhost:80/oi-master/Gall/api/categoria/read.php', {
//         method: "GET"
//     })
// 	let respPost = await reqPost.json()
// 	respPost.forEach(id => {
// 		divpost = document.querySelector("main>div:last-child")
// 		let titulo = document.querySelector("main>div:last-child>div:first-child").innerHTML=(id.titulo)
// 		let texto = document.querySelector("main>div:last-child>div:last-child").innerHTML=(id.texto)
// 	})
// 	console.log(respPost)
// }

// pegarPosts()