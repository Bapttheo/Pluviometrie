# -*- coding: utf-8 -*-
# PluviomÃ©trie.py
# Serveur du site web

import http.server
import socketserver
from urllib.parse import urlparse, parse_qs, unquote
import json
import os

from matplotlib import pyplot as plt
from matplotlib import dates
#from datetime import datetime
import datetime as datetime
from math import floor, ceil, sqrt
from statistics import mean, variance
import os
from decimal import Decimal



import sqlite3

#Pour pouvoir utiliser le site sur Heroku
PORT = int(os.environ.get("PORT", 8080))

# Définition du nouveau handler
class RequestHandler(http.server.SimpleHTTPRequestHandler):

	# sous-rÃ©pertoire racine des documents statiques
	static_dir = '/client'

  	# On surcharge la mÃ©thode qui traite les requÃªtes GET  
	def send_json(self,data,headers=[]):
		body = bytes(json.dumps(data),'utf-8') # encodage en json et UTF-8
		self.send_response(200)
		self.send_header('Content-Type','application/json')
		self.send_header('Content-Length',int(len(body)))
		[self.send_header(*t) for t in headers]
		self.end_headers()
		self.wfile.write(body)
    
	def do_GET(self):

		# On rÃ©cupÃ¨re les Ã©tapes du chemin d'accÃ¨s
		self.init_params() 
		
 		# le chemin d'accÃ¨s commence par /location
		if self.path_info[0] == "location":
			datatest=self.send_stations()
			data=[]
			for (i,x,y,n) in datatest:
				data.append({'id':i,'lon':x,'lat':y,'name':n})
			self.send_json(data)

        ## Requête "date" - Retourne l'adresse de l'image contenant le graphe de pluviométrie (et la crée si elle n'existe pas)
		
		elif self.path_info[0] == "click" :

			# Récupération des infos contenues dans l'adresse de la requête GET :
			id = self.path_info[1] # ex: "1-%20SAINT%20GERMAIN" => gid = "1"
			datedeb = self.path_info[2].split('T')[0] # ex: "2011-02-01-"
			heuredeb = self.path_info[2].split('T')[1] # ex: "18:32"
			datefin = self.path_info[3].split('T')[0]
			heurefin = self.path_info[3].split('T')[1]
			pas_minutes = self.path_info[4]

			in_format = "%Y-%m-%d"
			out_format = "%d/%m/%Y"
			
			datedeb = datetime.datetime.strptime(datedeb, in_format).strftime(out_format)
			datefin = datetime.datetime.strptime(datefin, in_format).strftime(out_format)

			parametres = [id] + datedeb.split('/') + heuredeb.split(':') + datefin.split('/') + heurefin.split(':') + [pas_minutes]            
			nom_image_new = "_".join(parametres) 

			# Connexion à la base de données :
			conn = sqlite3.connect('station_pluvio.sqlite')
			c = conn.cursor()
			# Envoi de la requête :
			
			c.execute("SELECT nom_graph FROM cache WHERE nom_graph = " + "'"+str(nom_image_new)+"'")
			a = c.fetchall() # Tableau contenant les réponses à la requête

			nom_complet = 'client/graphes/' + nom_image_new + '.png'
			
			if not (len(a)>0 and os.path.isfile(nom_complet)) : # ie. aucune image ne correspond => construction du graphe
				# Connexion à la base de données
				conn = sqlite3.connect('station_pluvio.sqlite')
				c = conn.cursor()

				identifiant = id
				
				# Récupération des données de pluviométrie :
				texte_sta = 'sta_' + str(identifiant)
				r = c.execute('SELECT date, ' + texte_sta + ' FROM pluvio_histo_2020')
				a = r.fetchall()                
				
				def creation_date(date) :
					JJ = int(date[:2]) # Année
					MM = int(date[3:5]) # Mois
					YYYY = int(date[6:10]) # Jour
					hh = int(date[11:-3]) # Heure
					mm = int(date[-2:]) # Minute
					return datetime.datetime(YYYY, MM, JJ, hh, mm)
				
				
				date_min = creation_date(datedeb+heuredeb)
				date_max = creation_date(datefin+heurefin)


				n=len(a)
				
				D = [] # Liste des dates
				Y = [] # Liste des valeurs


				for i in range(n) :
					if not a[i][0]==None:
						date = creation_date(a[i][0])
						if date_min <= date and date <= date_max :
							val = a[i][1]
							if val == '' or val == None :
								val = 0
							else :
								val = float(val)
							D.append(date)
							Y.append(val)
				

				# Conversion des dates pour matplotlib :
				fds = [] 
				for el in D :
					fds.append(dates.date2num(el))
				
				
				########## AFFICHAGE GRAPHE #################################################################
				
				fig = plt.figure(figsize=(14,9), dpi=150)
				ax = fig.add_subplot(111)
				
				## ===== Gestion des graduations ================================================
				# Unités de graduations :
				annee = datetime.timedelta(365)
				mois = datetime.timedelta(31)
				jour = datetime.timedelta(1)
				heure = datetime.timedelta(0,0,3600)
				
				n_unites = 3 # Nombre de graduations minimales pour le graphe
				diff = date_max-date_min # Intervalle de temps du graphe
				
				L_xticks = [] # Liste des valeurs des graduations
				
				if diff > n_unites*annee : # On gradue en années :
					y = date_min.year
					i = 0
					while y+i <= date_max.year :
						L_xticks.append( datetime.datetime(y+i,1,1) )
						i += 1
					hfmt = dates.DateFormatter('%Y') # Format d'affichage des graduations
					angle_rotation = 0 # Angle d'affichage des graduations
					
				elif diff > mois : # On gradue en mois :
					y = date_min.year
					m = date_min.month
					(i, j) = (0, m)
					while not( y+i >= date_max.year and j > date_max.month ) :
						L_xticks.append( datetime.datetime(y+i, j, 1) )
						if j == 12 :
							j = 1
							i += 1
						else :
							j += 1
					hfmt = dates.DateFormatter('%m/%Y')
					angle_rotation = 40
					
				elif diff > n_unites*jour : # On gradue en jours :
					y = date_min.year
					m = date_min.month
					d = date_min.day
					(i, j, k) = (0, m, d)
					while not( y+i >= date_max.year and j >= date_max.month and k >= date_max.day) :
						L_xticks.append( datetime.datetime(y+i, j, k) )
						if (j in [1,3,5,7,8,10,12] and k == 31) or (j == 2 and k == 28) or (j not in [1,2,3,5,7,8,10,12] and k == 30) :
							k = 1
							if j == 12 :
								i += 1                
								j = 1
							else :
								j += 1
						else :
							k+=1
					hfmt = dates.DateFormatter('%d/%m/%Y')
					angle_rotation = 70
					
				elif diff > n_unites*heure : # On gradue en heures :
					delta = diff/10
					L_xticks = dates.drange(date_min, date_max+delta, delta)
					hfmt = dates.DateFormatter('%d/%m/%Y %H:00')
					angle_rotation = 70
					
				else :  # On gradue en minutes :
					delta = diff/10
					L_xticks = dates.drange(date_min, date_max+delta, delta)
					hfmt = dates.DateFormatter('%d/%m/%Y %H:%M')
					angle_rotation = 70
				
				
				# ===== Regroupement des données suivant le pas ====================================

				# Conversion de la valeur de 'pas_minutes' au format compris par Python :
				pas = datetime.timedelta(0, int(pas_minutes)*60)
				
				resolution = datetime.timedelta(0,1) # Plus petit pas de temps possible           
				
				n_i = 1 # Numéro de l'intervalle de temps étudié
				inf_intervalle = date_min+(n_i-1)*pas # Borne inférieure de l'intervalle
				sup_intervalle = date_min+n_i*pas # Borne supérieure de l'intervalle
				
				fds_tronc = [dates.date2num(inf_intervalle)] # Nouvelle liste des dates converties
				Y_tronc = [0] # Nouvelle liste des valeurs
				
				somme = 0
				while i < len(fds) :
					if fds[i] < dates.date2num(sup_intervalle) :
						# Le point appartient à l'intervalle étudié donc on le rajoute à la somme :
						somme += Y[i]
						i += 1
					else :
						# Le point n'appartient pas à l'intervalle étudié donc on passe à l'intervalle suivant :
						n_i += 1
						# On trace artificiellement un graphe en barres :
						fds_tronc.append(dates.date2num(inf_intervalle+resolution))
						Y_tronc.append(somme)
						fds_tronc.append(dates.date2num(sup_intervalle-resolution))
						Y_tronc.append(somme)
						fds_tronc.append(dates.date2num(sup_intervalle))
						Y_tronc.append(0)
						# On change les bornes de l'intervalle étudié
						inf_intervalle = sup_intervalle
						sup_intervalle = date_min+n_i*pas
						somme = 0
				
				
				# ===== Tracé du graphe  ==============================================================
				plt.grid(color='#888888', linestyle=':')  
				
				plt.plot(fds_tronc, Y_tronc)
				
				plt.fill_between(fds_tronc, Y_tronc, 0, color='#0055ff')
				plt.xlim([date_min, date_max]) # Définition des limites temporelles du graphique
				plt.ylabel("Précipitations en mm") # Ajout du nom des axes
				plt.title("Pluviométrie du " + datedeb + ' ' + heuredeb + " au " + datefin + ' ' + heurefin +'\n Station n°' + id)
				plt.subplots_adjust(bottom=0.15)
				
				ax.xaxis.set_major_formatter(hfmt) # Format d'affichage des graduations
				plt.xticks(L_xticks, rotation=angle_rotation) # Ajout des graduations (et de leur angle d'affichage)
				
				
				# ===== Sauvegarde du graphe et mise à jour de la base de données =======================

				fig.savefig(nom_complet) # Sauvegarde de l'image
				
				plt.close() # Fermeture de l'image (ouverte par Spyder lors du 'plot')

			
				row = [nom_image_new, id, datedeb, datefin, pas_minutes]
				
				conn = sqlite3.connect('station_pluvio.sqlite')
				c = conn.cursor()
				c.execute('INSERT INTO cache VALUES (?, ?, ?, ?, ?)', tuple(v for v in row))
				conn.commit()                
			

				
			# Nom complet d'accès à l'image (vu depuis la page HTML) :
			nom_image_new = 'graphes/'+ nom_image_new + '.png'
				
			# Envoi de l'adresse de l'image à la page WEB, au format JSON :
			#self.send_json([{"nom":nom_image_new}])

			body = json.dumps({'nom': nom_image_new})

			# on envoie
			headers = [('Content-Type','application/json')]
			self.send(body,headers)


		# ou pas...
		else:
			self.send_static()


	# On surcharge la mÃ©thode qui traite les requÃªtes HEAD
	def do_HEAD(self):
		self.send_static()


	# On envoie le document statique demandÃ©
	def send_static(self):

		# on modifie le chemin d'accÃ¨s en insÃ©rant un rÃ©pertoire prÃ©fixe
		self.path = self.static_dir + self.path

		# on appelle la mÃ©thode parent (do_GET ou do_HEAD)
		# Ã  partir du verbe HTTP (GET ou HEAD)
		if (self.command=='HEAD'):
			http.server.SimpleHTTPRequestHandler.do_HEAD(self)
		else:
			http.server.SimpleHTTPRequestHandler.do_GET(self)
  
 
  	# on analyse la requÃªte pour initialiser nos paramÃ¨tres
	def init_params(self):
		# analyse de l'adresse
		info = urlparse(self.path)
		self.path_info = [unquote(v) for v in info.path.split('/')[1:]]  # info.path.split('/')[1:]
		self.query_string = info.query
		self.params = parse_qs(info.query)

		# rÃ©cupÃ©ration du corps
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
    
	############################################################
	# On gÃ©nÃ¨re et on renvoie la liste des sations et leur coordonnÃ©es 
	def send_stations(self):		
		conn = sqlite3.connect('station_pluvio.sqlite')
		c = conn.cursor()
		c.execute("SELECT identifian,X,Y,nom FROM stations_pluvio_2020")
		r = c.fetchall()
		return(r)


  	# On envoie les entÃªtes et le corps fourni
	def send(self,body,headers=[]):

		# on encode la chaine de caractÃ¨res Ã  envoyer
		encoded = bytes(body, 'UTF-8')

		# on envoie la ligne de statut
		self.send_response(200)

		# on envoie les lignes d'entÃªte et la ligne vide
		[self.send_header(*t) for t in headers]
		self.send_header('Content-Length',int(len(encoded)))
		self.end_headers()

		# on envoie le corps de la rÃ©ponse
		self.wfile.write(encoded)


# Instanciation et lancement du serveur
httpd = socketserver.TCPServer(("", PORT), RequestHandler)
print ("serveur sur port : {}".format(PORT))
httpd.serve_forever()