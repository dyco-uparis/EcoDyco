# EcoDyco
A macroeconomic software for a ﬁnite world

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
    
EcoDyco est une surcouche pour les modèles macro-économiques visant à prendre en compte les contraintes croisées liées aux ressources, notamment dans leur quantité et leur qualité. On trouvera dans le manuel *Manual EcoDyco V1.pdf* les explications des différents paramètres et dans le papier *XX* la methode de  constuction du modèle.


### Requirements
Proposed version of EcoDyco works with Python 3. Required libraries:
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


