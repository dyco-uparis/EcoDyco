# EcoDyco
A macroeconomic software for a ﬁnite world

EcoDyco est une surcouche pour les modèles macro-économiques visant à prendre en compte les contraintes croisées liées aux ressources, notamment dans leur quantité et leur qualité. On trouvera dans le manuel *Manual EcoDyco V1.pdf* les explications des différents paramètres et dans le papier *XX* la methode de  constuction du modèle.


### Requirements
La version actuelle est prévue pour fonctionner avec python 3 et les librairies suivantes:
- numpy
- matplotlib
- pandas
- xlswriter
- tkinter

### World settings
Les paramètres généraux sont dans l'entete de *main.py*. Pour créer de nouvelles cellules et de nouveaux moteurs économiques voir le manuel *Manual EcoDyco V1.pdf*


### Run the world
Une configuration minimale comprend les fichiers *main.py*, *PhysicalWorld.py*, au moins un moteur économique (par exemple *Goodwin.py*, *CroissanceNulle.py*, *Solow2.py*) et les fichiers de paramètres correspondant dans preproc/

Enuite, à partir d'un terminal, executer :
```
python3 main.py
```
ou dans une console ipython (via spyder ou autre)
```
run main.py
```

### New economical engine
Voir le manuel *Manual EcoDyco V1.pdf*


### New resource sheet
Voir le manuel *Manual EcoDyco V1.pdf*


