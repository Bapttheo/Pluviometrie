// Creation d'une carte dans la balise div "map"
// Positionne la vue sur un point donné et un niveau de zoom
var map = L.map('map').setView([45.756,4.8401], 10);


// Ajout d'une couche de dalles OpenStreetMap
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', 
{attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
 

function load_data () {

	// objet pour l'envoi d'une requête Ajax
	var xhr = new XMLHttpRequest();

	console.log("Loading data...");

	// fonction appelée lorsque la réponse à la requête (liste des lieux insolites) sera arrivée
	xhr.onload = function() {
		console.log("Analyse réponse requette /location...")
		// transformation des données renvoyées par le serveur
		// responseText est du type string, data est une liste
		var data = JSON.parse(this.responseText);
		console.log(data)
		// boucle sur les lieux
		for ( n = 0; n < data.length; n++ ) {
			// insertion d'un marqueur à la position du lieu,
			// attachement d'une popup, capture de l'événement 'clic'
			// ajout d'une propriété personnalisée au marqueur
			L.marker([data[n].lat,data[n].lon]).addTo(map)
			.bindPopup('Lieu = '+data[n].name)
			.addEventListener('click',OnMarkerClick)
			.idnum = data[n].id;
		}
		console.log("Marqueurs ajoutés sur la carte !")
	};

	// Envoi de la requête Ajax pour la récupération de la liste des lieux
	console.log("Envoie requette /location...")
	xhr.open('GET','/location',true);
	xhr.send();
}



function OnMarkerClick (e) {
	console.log("HERE")
    var xhr = new XMLHttpRequest();
	  xhr.onload = function() {   // fonction callback
		// On change l'image affichée sur le site
		var data = JSON.parse(this.responseText)
		console.log(data)
		console.log(data.nom)
		var x = document.getElementById("graph");
		x.setAttribute("src", data.nom);
		};
	console.log(e.target.idnum)
	var debut = document.getElementById('debut').value,
		fin = document.getElementById('fin').value,
		pas = document.getElementById('pas').value
	;	
    xhr.open('GET','/click/'+e.target.idnum+"/"+debut+"/"+fin+"/"+pas,true);  // on récupère la courbe par un appel au serveur
	xhr.send();
	
}


// Gestion annimation du footer
document.getElementById("credit").addEventListener("click", start);
element=document.getElementById("footer");
function start() {
	console.log("here")
	element.classList.remove("run-animation");
	void element.offsetWidth;
	element.classList.add("run-animation");
}