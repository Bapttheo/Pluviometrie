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

	// Envoi de la requête Ajax pour la récupération de la liste des lieux insolites
	console.log("Envoie requette /location...")
	xhr.open('GET','/location',true);
	xhr.send();
}



function OnMarkerClick (e) {
	/*
    var xhr = new XMLHttpRequest();
  var image =  document.querySelector('#reponse img'),
        legende = document.querySelector('#reponse p');
  xhr.onload = function() {   // fonction callback
      var data = JSON.parse(this.responseText)
      image.src = data.img;
      image.alt = data.title;
      legende.innerHTML = data.title;
      };
    xhr.open('GET','/ponctualite/'+e.target.idreg,true);  // on récupère la courbe par un appel au serveur
	xhr.send();
	*/
}



document.getElementById('button').addEventListener('click', envoiformulaire);

function envoiformulaire(e) {
	var xhr = new XMLHttpRequest(); 
	// On récupère les paramètres
	var lieu = document.getElementById('lieu').value,
		debut = document.getElementById('debut').value,
		fin = document.getElementById('fin').value,
		pas = document.getElementById('pas').value,
		interactif = document.getElementById('interactif').value
	;

	if  ((lieu!=="") && (debut!=="") && (fin!=="") && (pas!=="")) {
		xhr.open('GET','/toctoc?'+'Lieu='+lieu+'&'+'Debut='+debut+'&'+'Fin='+fin+'&'+'Pas='+pas+'&'+'Interactif='+interactif,true);  // requête au serveur avec une "query string"
		xhr.send();

		xhr.onload = function() {   // fonction callback
			// récupération des données renvoyées par le serveur
			var data = JSON.parse(this.responseText);
			// affichage dans la zone 'reponse' des données récupérées par l'appel au serveur
			document.getElementById('reponse').innerHTML = "Données de "  + data.lieu + ' entre le ' + data.debut + " et le " + data.fin + " avec un pas de " + data.pas;
			
			var x = document.getElementById("graph");
			x.setAttribute("src", "images/1.png");
		};
	}
	else {
		console.log("Formulaire pas remplit entièrement")
	}
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