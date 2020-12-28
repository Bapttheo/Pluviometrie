# Pluviométrie.py
# Serveur du site web

import http.server
import socketserver
from urllib.parse import urlparse, parse_qs, unquote
import json

import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as pltd

import sqlite3

PORT = 8000

# Définition du nouveau handler
class RequestHandler(http.server.SimpleHTTPRequestHandler):

	# sous-répertoire racine des documents statiques
	static_dir = '/client'

  	# On surcharge la méthode qui traite les requêtes GET  
	def send_json(self,data,headers=[]):
		body = bytes(json.dumps(data),'utf-8') # encodage en json et UTF-8
		self.send_response(200)
		self.send_header('Content-Type','application/json')
		self.send_header('Content-Length',int(len(body)))
		[self.send_header(*t) for t in headers]
		self.end_headers()
		self.wfile.write(body)
    
	def do_GET(self):

		# On récupère les étapes du chemin d'accès
		self.init_params()

		# le chemin d'accès commence par /time
		if self.path_info[0] == 'time':
			self.send_time()
		
 		# le chemin d'accès commence par /location
		elif self.path_info[0] == "location":
			data=[{'id':1,'lat':45.76843,'lon':4.82667,'name':"Rue Couverte"},{'id':2,'lat':45.77128,'lon':4.83251,'name':"Rue Caponi"},{'id':3,'lat':45.78061,'lon':4.83196,'name':"Jardin Rosa-Mir"}]
			self.send_json(data)

		# requete description - retourne la description du lieu dont on passe l'id en paramètre dans l'URL
		elif self.path_info[0] == "description":
			data=[{'id':1,'desc':"Il ne faut pas être <b>trop grand</b> pour marcher dans cette rue qui passe sous une maison"},
					{'id':2,'desc':"Cette rue est <b>si étroite</b> qu'on touche les 2 côtés en tendant les bras !"},
					{'id':3,'desc':"Ce jardin <b>méconnu</b> évoque le palais idéal du Facteur Cheval"}]
			for c in data:
				if c['id'] == int(self.path_info[1]):
					self.send_json(c)
					break
 
		elif self.path_info[0] == "toctoc":
			self.send_toctoc()	
        		
		# ou pas...
		else:
			self.send_static()


	# On surcharge la méthode qui traite les requêtes HEAD
	def do_HEAD(self):
		self.send_static()


	# On envoie le document statique demandé
	def send_static(self):

		# on modifie le chemin d'accès en insérant un répertoire préfixe
		self.path = self.static_dir + self.path

		# on appelle la méthode parent (do_GET ou do_HEAD)
		# à partir du verbe HTTP (GET ou HEAD)
		if (self.command=='HEAD'):
			http.server.SimpleHTTPRequestHandler.do_HEAD(self)
		else:
			http.server.SimpleHTTPRequestHandler.do_GET(self)
  
 
  	# on analyse la requête pour initialiser nos paramètres
	def init_params(self):
		# analyse de l'adresse
		info = urlparse(self.path)
		self.path_info = [unquote(v) for v in info.path.split('/')[1:]]  # info.path.split('/')[1:]
		self.query_string = info.query
		self.params = parse_qs(info.query)

		# récupération du corps
		length = self.headers.get('Content-Length')
		ctype = self.headers.get('Content-Type')
		if length:
			self.body = str(self.rfile.read(int(length)),'utf-8')
		if ctype == 'application/x-www-form-urlencoded' : 
			self.params = parse_qs(self.body)
		else:
			self.body = ''
	
		# traces
		print('info_path =',self.path_info)
		print('body =',length,ctype,self.body)
		print('params =', self.params)
		print(type(self.params))
    

	# On envoie un document avec l'heure
	def send_time(self):
		
		# on récupère l'heure
		time = self.date_time_string()

		# on génère un document au format html
		body = '<!doctype html>' + \
			'<meta charset="utf-8">' + \
			'<title>l\'heure</title>' + \
			'<div>Voici l\'heure du serveur :</div>' + \
			'<pre>{}</pre>'.format(time)

		# pour prévenir qu'il s'agit d'une ressource au format html
		headers = [('Content-Type','text/html;charset=utf-8')]

		# on envoie
		self.send(body,headers)

	############################################################
	# On génère et on renvoie la liste des sations et leur coordonnées 
	def send_stations(self):
		""" EXEMPLE A MODIFIER POUR BONNES STATIONS
		conn = sqlite3.connect('ter.sqlite')
		c = conn.cursor()
		
		c.execute("SELECT * FROM 'regions'")
		r = c.fetchall()
		
		headers = [('Content-Type','application/json')];
		body = json.dumps([{'nom':n, 'lat':lat, 'lon': lon} for (n,lat,lon) in r])
		self.send(body,headers)
  		"""
    
    
    
    
    
	
	# Réponse au questionnaire de paramètres
	def send_toctoc(self):    
		# on construit une chaîne de caractère json
		body = json.dumps({
		'lieu': self.params['Lieu'][0], \
		'debut': self.params['Debut'][0], \
		'fin': self.params['Fin'][0], \
		'pas': self.params['Pas'][0], \
		'interactif': self.params['Interactif'][0] \
		})

		# on envoie
		headers = [('Content-Type','application/json')];
		self.send(body,headers)

 	############################################################
	# Genère et renvoie graphique (voir TD4)
  	#def send_ponctualite(self):
   
   
   
   
   
    
  	# On envoie les entêtes et le corps fourni
	def send(self,body,headers=[]):

		# on encode la chaine de caractères à envoyer
		encoded = bytes(body, 'UTF-8')

		# on envoie la ligne de statut
		self.send_response(200)

		# on envoie les lignes d'entête et la ligne vide
		[self.send_header(*t) for t in headers]
		self.send_header('Content-Length',int(len(encoded)))
		self.end_headers()

		# on envoie le corps de la réponse
		self.wfile.write(encoded)

 
# Instanciation et lancement du serveur
httpd = socketserver.TCPServer(("", PORT), RequestHandler)
print ("serveur sur port : {}".format(PORT))
httpd.serve_forever()

