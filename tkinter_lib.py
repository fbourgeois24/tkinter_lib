from tkinter import * # Pour l'interface graphique
from tkinter.messagebox import * # Pour les messages popup
from tkinter.filedialog import * # Pour la sélection d'un fichier
from tkinter.ttk import * # Pour la création du tableau
from tkinter import font
from pythonLib.utilLib import get_os


#################################################################################################################################################################################
# Gestion fenêtres
#################################################################################################################################################################################


''' Barre de défilement'''
class auto_scrollbar(Scrollbar):
	def set(self, lo, hi):
		if float(lo) <= 0.0 and float(hi) >= 1.0:
			# grid_remove is currently missing from Tkinter!
			self.tk.call("grid", "remove", self)
		else:
			self.grid()
		Scrollbar.set(self, lo, hi)
	def pack(self, **kw):
		raise TclError("cannot use pack with this widget")
	def place(self, **kw):
		raise TclError("cannot use place with this widget")



''' Gestion de fenêtres '''
class window:
	""" Classe pour la gestion des fenêtres"""


	def __init__(self, title, size, main = False, scrollbar = False, menu = None, function = None, on_close_function=None):
		""" Constructeur qui stocke le titre et la taille de la fenêtre
		function: fonction appelée à lé réouverture de la fenêtre (pour refresh)
		on_close_function:  Fonction appelée à la fermeture de la fenêtre
		"""
		self.title = title
		self.size = size
		self.is_main = main
		self.scrollbar_activate = scrollbar
		self.menu = menu
		self.function = function
		self.on_close_function = on_close_function 



	def open(self, title=None, function_on_return=None, on_close_function=None):
		""" Méthode qui ouvre la fenêtre ou la fait passer au premier plan si elle est déjà ouverte
		Elle peut afficher un menu ou une barre de défilement sur la fenêtre
		function_on_return : fonction appelée quand la touche enter est pressée
		on_close_function : fonction appelée à la fermeture de la fenêtre
		"""
		if on_close_function is not None:
			self.on_close_function = on_close_function
		try:
			self.w.focus_force()
			self.w.lift()
			return True
		except:
			self.w = Tk()
			if title == None:
				self.w.title(self.title)
			else:
				self.w.title(title)
			self.w.geometry(self.size)

			if self.on_close_function is not None:	# Fonction appelée à la fermeture
				def close_function():
					self.on_close_function()
					self.w.destroy()
				self.w.protocol("WM_DELETE_WINDOW", close_function)

			# Affichage du menu
			if self.menu != None:
				self.menu_bar = Menu(self.w)
				
				# Boucle qui lit le dicttionnaire des menus et qui les génèrent
				for item in self.menu:	
					new_menu = Menu(self.menu_bar, tearoff=0)
					self.menu_bar.add_cascade(label=item["nom"], menu = new_menu)
					for sub_item1 in item["enfants"]:
						new_menu2 = Menu(self.menu_bar, tearoff=0)
						try:
							# on teste si il y a des enfants, si oui c'est un sous menu
							sub_item1["enfants"]
						except:
							# Elément de menu
							if sub_item1["nom"] == "_":
								new_menu.add_separator()
							else:
								new_menu.add_command(label=sub_item1["nom"], command=sub_item1["fonction"])
								if sub_item1["raccourci"] != None:
									new_menu.bind_all(sub_item1["raccourci"], sub_item1["fonction"])
						else:
							# Sous-menu
							new_menu2 = Menu(new_menu, tearoff=0)
							new_menu.add_cascade(label=sub_item1["nom"], menu = new_menu2)
							for sub_item2 in sub_item1["enfants"]:
								if sub_item2["nom"] == "_":
									new_menu2.add_separator()
								else:
									new_menu2.add_command(label=sub_item2["nom"], command=sub_item2["fonction"])
									if sub_item2["raccourci"] != None:
										new_menu2.bind_all(sub_item2["raccourci"], sub_item2["fonction"])

				# On attache le menu à la fenêtre principale
				self.w.config(menu = self.menu_bar)

			# Affichage de la barre de défilement
			if self.scrollbar_activate:
				self.v_scrollbar = auto_scrollbar(self.w)
				self.v_scrollbar.grid(row=0, column=1, sticky=N+S, rowspan=3)
				self.h_scrollbar = auto_scrollbar(self.w, orient=HORIZONTAL)
				self.h_scrollbar.grid(row=3, column=0, sticky=E+W)
				self.up_fix_frame = Frame(self.w)
				self.up_fix_frame.grid(row=0, column=0, sticky=E+W)
				self.canvas = Canvas(self.w, yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
				self.canvas.grid(row=1, column=0, sticky=N+S+E+W)
				self.dn_fix_frame = Frame(self.w)
				self.dn_fix_frame.grid(row=2, column=0, sticky=E+W)
				self.v_scrollbar.config(command=self.canvas.yview)
				self.h_scrollbar.config(command=self.canvas.xview)
				self.w.grid_rowconfigure(1, weight=1)
				self.w.grid_columnconfigure(0, weight=1)
				self.scrl_frame = Frame(self.canvas)
				self.scrl_frame.rowconfigure(1, weight=1)
				self.scrl_frame.columnconfigure(1, weight=1)	
				self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)
			else:
				self.up_fix_frame = Frame(self.w)
				self.up_fix_frame.pack(fill="both")
				self.scrl_frame = Frame(self.w)
				self.scrl_frame.pack(fill="both", expand="yes")
				self.dn_fix_frame = Frame(self.w)
				self.dn_fix_frame.pack(fill="both")

			if function_on_return is not None:	
				def return_key_pressed(event):
					function_on_return()
				self.w.bind("<Return>", return_key_pressed)


			return False

	def close(self, ask = False, title = None, message = None):
		""" Méthode qui ferme la fenêtre"""
		if title != None or message != None or ask == True:
			if title != None:
				box_title = title
			else:
				box_title = "Fermer cette fenêtre ?"
			if message != None:
				box_message = message
			else:
				box_message = "Êtes vous sur de vouloir fermer cette fenêtre ?"
			if not askyesno(box_title, box_message):
				return
		try:
			self.w.destroy()
		except:
			pass


	def reopen(self, parameter=None):
		""" Méthode qui ferme puis réouvre la fenêtre"""
		try:
			self.w.destroy()
		except:
			pass
		if parameter == None:
			self.function()
		else:
			self.function(parameter)


	def loop(self):
		""" Méthode pour que la scrollbar fonctionne, à appeler en fin de fonction"""
		if self.scrollbar_activate:
			self.canvas.create_window(0, 0, anchor=NW, window=self.scrl_frame)
			self.scrl_frame.update_idletasks()
			self.canvas.config(scrollregion=self.canvas.bbox("all"))
		if self.is_main:
			self.w.mainloop()


	def onMouseWheel(self, event):
		""" Méthode pour défiler la fenêtre à l'aide de la roulette """
		shift = (event.state & 0x1) != 0
		scroll = -1 if event.delta > 0 else 1
		if shift:
		   self.canvas.xview_scroll(scroll*4, "units")
		else:
		   self.canvas.yview_scroll(scroll, "units")

	def dataSaved(self):
		""" Affichage de la fenêtre de sauvegarde réussie """
		self.data_saved_window = Toplevel()
		self.data_saved_window.title("Données sauvegardées")
		self.data_saved_window.geometry("550x50+250+300")
		Label(self.data_saved_window, text="Les données ont bien été sauvegardées", font=("Helvetica, 30")).pack()
		# self.data_saved_window.wx_attributes("-topmost", 1)
		self.data_saved_window.after(1000, self.data_saved_window.destroy)




	def show_as_table(self,titles,data,select_fn=None,ajout=True, edit=True,edit_fn=None,suppr_fn=None, center_items=True, select_child=True, unfold_by_default=False):
		""" Méthode pour afficher une liste comme tableau
		La scrollbar de la fenêtre doit être désactivée
		titles est une liste qui contient les titres des colonnes
		data contient les infos à afficher (liste sur 2 niveaux pour lignes et colonnes)
			Dans les colonnes, la permière ne sera pas affichée et servira de valeur renvoyée à la sélection d'une ligne
		select_fn : Fonction appelée par le bouton "Sélectionner". Appelle la fonction passée avec le paramètre id=id de la ligne sélectionnée
		edit_fn : Fonction déclenchée par le bouton "Ajout" ou "Modification" appelle la fonction passée avec les paramètres 
			- id=0 et create=True si ajout (paramètre ajout=True)
			- id=id de la ligne sélectionnée et create = False si modification(paramètre edit=True)
		suppr_fn : Fonction déclenchée par le bouton "Supprimer", appelle la fonction passée avec le paramètre id=id de la ligne sélectionnée
		center_items : Permet de centrer ou non les éléments dans les colonnes
		select_child : Définit si une ligne enfant peut-être sélectionnée
		unfold_by_default : Définit dans le cas de lignes enfant si les lignes parent doivent être dépliées par défaut ou non

		Pour mettre à jour le tableau, il suffit de rappeler la fonction, le précédent sera supprimé
		"""
		
		if self.scrollbar_activate is True:
			raise AttributeError("La scrollbar de la fenêtre doit être désactivée pour un résultat correct")


		# Mémorisation des titres et données pour si il faut appliquer un filtre par après
		titles = titles
		data = data
		

		def fixed_map(option):
			""" Fonction pour résoudre un bug dans l'affichage des lignes colorées """
			return [elm for elm in style.map('Treeview', query_opt=option) if
				elm[:2] != ('!disabled', '!selected')]

	
		def action_selected(suppr=False, create=False, select=False):
			""" Vérifier si une ligne a bien été sélectionnée si bouton editer ou supprimer """
			# Si suppr ou create = False on vérifie si une ligne a bien été sélectionnée
			if (suppr or ((not suppr) and not create)) and self.tableau.focus() == "":
				# Le message est adapté suivant le type d'action (de bouton pressé)
				if (not suppr) and not select:
					action = "modifier"
				elif not suppr:
					action = "sélectionner"
				else:
					action = "supprimer"
				showwarning("Pas de ligne sélectionnée","Aucune ligne n'a été sélectionnée, veuillez sélectionner une ligne pour pouvoir la " + action, master=self.frame_tableau)
				return
	
			# On récupère l'id et s'il est plus grand que 100000 c'est que c'est une ligne enfant qui est sélectionnée, on en déduit l'id du parent
			if self.tableau.focus() != "":
				id = int(self.tableau.focus())
				if id >= 100000:
					id = int(id / 100000)

			# Si sélection
			if select:
				select_fn(id=id)
			# Si suppression
			elif suppr:
				suppr_fn(id=id)
			# Si création
			elif create:
				edit_fn(id=0, create=True)
			# Sinon modification
			else:
				edit_fn(id=id, create=False)


		# Vérification si des infos à afficher ont bien été transmises
		if data is None:
			print("Aucune info à afficher !")
			return

		# Suppression d'un éventuel tableau déjà existant
		try:
			self.frame_boutons.destroy()
			self.frame_tableau.destroy()
		except:
			pass



		# Définition du style pour le tableau
		style = Style()
		style.theme_use('default')
		# style.configure('Treeview', bg='#D3D3D3', fg='black', rowheight=25, fieldbackground='#D3D3D3')
		# style.map('Treeview',bg=[('selected','#347083')])
		style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))

		
		# Création d'une frame pour y mettre le tableau
		self.frame_tableau = Frame(self.scrl_frame)
		self.frame_tableau.pack(pady=10, expand=YES, fill=BOTH)

		# Création d'une frame pour mettre les boutons au dessus du tableau
		self.frame_boutons = Frame(self.frame_tableau)
		self.frame_boutons.pack(fill=X)

		# Ajout des boutons, on active seulement les boutons pour lesquels une fonction a été fournie
		if select_fn != None:
			Button(self.frame_boutons, text="Sélectionner", command=lambda: action_selected(select=True)).pack(side=LEFT, padx=10, pady=10)
		if edit_fn != None:
			if ajout:
				Button(self.frame_boutons, text="Ajouter", command=lambda: action_selected(create=True)).pack(side=LEFT, padx=10, pady=10)
			if edit:
				Button(self.frame_boutons, text="Editer", command=lambda: action_selected(create=False)).pack(side=LEFT, padx=10, pady=10)
		if suppr_fn != None:
			Button(self.frame_boutons, text="Supprimer", command=lambda: action_selected(suppr=True)).pack(side=LEFT, padx=10, pady=10)


		# Création de la barre de défilement pour le tableau
		scrollbar_Y_tableau = Scrollbar(self.frame_tableau)
		scrollbar_Y_tableau.pack(side=RIGHT,fill=Y)
		scrollbar_X_tableau = Scrollbar(self.frame_tableau, orient='horizontal')
		scrollbar_X_tableau.pack(side=BOTTOM,fill=X)

		# Création du tableau et définition des colonnes (le nom de la colonne = le titre de la colonne)
		self.tableau = Treeview(self.frame_tableau, yscrollcommand=scrollbar_Y_tableau.set, xscrollcommand=scrollbar_X_tableau.set, selectmode='extended', columns=(titles))
		# Spécification des colonnes
		for item in titles:
			if center_items == True:
				anchor = 'center'
			else:
				anchor = 'w'
			self.tableau.column(item, anchor=anchor)
		scrollbar_Y_tableau.config(command=self.tableau.yview)
		scrollbar_X_tableau.config(command=self.tableau.xview)
		

		# Sera utilisé pour mémoriser le tri des colonnes
		self.tableau.dict_sort = {}

		def fn_sort(column):
			""" Trier une colonne """
			# On détecte si le nom de la colonne est le même qu'au tour précédent
			if self.tableau.dict_sort.get(column) is not None:
				# Si c'est le même on inverse juste le sens de tri de la colonne dans le dictionnaire
				self.tableau.dict_sort[column] = not self.tableau.dict_sort[column]
			else:
				# Si ce n'est pas la même colonne 
				# on supprime la flèche de la colonne précédente
				# On vide le dictionnaire et on ajoute la nouvelle
				if self.tableau.dict_sort != {}:
					self.tableau.heading(column=tuple(self.tableau.dict_sort.keys())[0], text=tuple(self.tableau.dict_sort.keys())[0])
				self.tableau.dict_sort.clear()
				self.tableau.dict_sort[column] = False
			# Lister les éléments de la colonne
			try:
				l = [(float(self.tableau.set(k, column)), k) for k in self.tableau.get_children()]
			except ValueError:
				l = [(self.tableau.set(k, column), k) for k in self.tableau.get_children()]
			# Trier les éléments de la colonne
			l.sort(key=lambda t: t[0], reverse=self.tableau.dict_sort[column])
			# On déplace les lignes dans le tableau
			for index, (_, k) in enumerate(l):
				self.tableau.move(k, '', index)
				if index % 2 == 0:
					# Si c'est une ligne paire, c'est une ligne blanche
					self.tableau.item(k, tags=("ligne_blanche",))
				else:
					# Si c'est une ligne impaire, c'est une ligne colorée
					self.tableau.item(k, tags=("ligne_couleur",))
			# On change le titre pour indiquer le sens de tri
			if self.tableau.dict_sort[column]:
				self.tableau.heading(column=column, text=column + " ▼")
			else:
				self.tableau.heading(column=column, text=column + " ▲")




		# Attribution du titre à la colonne
		for title in titles:
			self.tableau.heading(column=title, text=title, anchor='center', command=lambda _title = title: fn_sort(_title))
		# On masque la colonne "text" qui apparait à gauche
		self.tableau['show'] = 'headings'

		self.tableau.pack(pady = (0, 10), expand=YES, fill=BOTH)


		# Remplissage du tableau
		for id, item in enumerate(data):
			# Si le premier élément de la liste n'est pas une liste, c'est une simple ligne
			if type(item[0]) is not list:
				# Si c'est une ligne impaire, on la colorie
				if id % 2 != 0:
					self.tableau.insert('', 'end', iid=item[0], values=(item[1:]), tags=("ligne_couleur",))
				else:
					self.tableau.insert('', 'end', iid=item[0], values=(item[1:]), tags=("ligne_blanche",))
			if type(item[0]) is list:
				# Si le premier élément de la liste est une liste, c'est une ligne avec des enfants
				# La première ligne sera le parent
				if id % 2 != 0:
					self.tableau.insert('', 'end', iid=item[0][0], values=item[0][1:], tags=("ligne_couleur",), open=unfold_by_default)
				else:
					self.tableau.insert('', 'end', iid=item[0][0], values=item[0][1:], tags=("ligne_blanche",), open=unfold_by_default)
				# Les lignes suivantes seront les enfants
				for subid, subitem in enumerate(item[1:]):
					if subid % 2 == 0:
						self.tableau.insert(parent=item[0][0], index='end', iid=item[0][0]*100000+subid, values=["    " + str(i) for i in subitem[1:]], tags=("sous_ligne_couleur",))
					else:
						self.tableau.insert(parent=item[0][0], index='end', iid=item[0][0]*100000+subid, values=["    " + str(i) for i in subitem[1:]], tags=("sous_ligne_blanche",))


		# Configuration des tags pour la coloration d'une ligne sur 2
		self.tableau.tag_configure('ligne_couleur', background='lightblue')
		self.tableau.tag_configure('ligne_blanche', background='white')
		self.tableau.tag_configure('sous_ligne_couleur', background='lightgrey')
		self.tableau.tag_configure('sous_ligne_blanche', background='white')


		# Autosize des colonnes
		# Pour chaque colonne on définit l'élément le plus grand
		dict_column_size = {}
		for column in titles:
			dict_column_size[column] = 0
			for k in self.tableau.get_children():
				# Ajout d'un coef pour faire une marge
				taille_element = font.nametofont("TkDefaultFont").measure(self.tableau.set(k, column)) + 30
				if taille_element > dict_column_size[column]:
					dict_column_size[column] = taille_element
		# On configure la colonne en fonction des valeurs récupérées
		for column, size in dict_column_size.items():
			column_size = font.nametofont("TkDefaultFont").measure(column) + 20
			# Si le titre de la colonne est plus large, on adapte la taille
			if column_size > size:
				size = column_size
			self.tableau.column(column, width=size, stretch=False)

		# Sélection simple ligne
		self.tableau['selectmode'] = "browse"
	
			

