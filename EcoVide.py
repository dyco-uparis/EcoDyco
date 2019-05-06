# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 09:23:43 2018

@author: stagiaire
"""
import numpy as np
import matplotlib.pyplot as plt

def createEcoSphere(deltat):
    #renvoie une instance de la classe EcoSphere.
    return EcoSphere(deltat)

##############################################################

class EcoSphere :
    
    
    
    def __init__(self, deltat):
        #constructeur
        self.t = 0
        self.deltat = deltat
        
    def iterate(self, phySphere):
        #actualise les attributs de la sphère éco
        self.t = self.t + self.deltat
        
        
        
        
    def inputsToPhySphere(self, phySphere):
        #Renvoie les valeurs de tous les paramètres physiques que le modèle économique peut faire varier
        #NE PAS MODIFIER CETTE FONCTION, MAIS LES FONCTIONS FILLES Rp, recyclingEnergyFlux etc... ci-dessous
        cellsInputs = []
        for i in range(phySphere.n_cells):
            if phySphere.cells[i].type == "stock":
                cellsInputs.append([self.newK(phySphere, i), self.recyclingEnergyFlux(phySphere, i), self.to(phySphere, i), self.stock_cible(phySphere, i), self.newdelta(phySphere, i)])
            elif phySphere.cells[i].type == "flow":
                cellsInputs.append([self.K1(phySphere, i), self.K2(phySphere, i), self.newdelta(phySphere, i)])
        globalInputs = [self.recipeMatrix(phySphere), self.recipeRequestArray(phySphere), self.requestedEnergyMix(phySphere)]
        return (cellsInputs, globalInputs)
    
    
    
    
    def newK(self, phySphere, i):
        #renvoie la nouvelle valeur de la résistance de l'appareil de production de la ième feuille de phySphere (stockcell)
        return phySphere.cells[i].cell.Rp
    
    def recyclingEnergyFlux(self, phySphere, i) :
        #renvoie la nouvelle valeur de recyclingEnergyFlux de la ième feuille de phySphere (stockcell)
        return phySphere.cells[i].cell.recyclingEnergyFlux
    
    def to(self, phySphere, i):
        #renvoie la nouvelle valeur du temps caractéristique de la ième feuille de phySphere (stockcell)
        return phySphere.cells[i].cell.to
    
    def stock_cible(self, phySphere, i):
        #renvoie la nouvelle valeur du stock_cible (en pourcentage de la quantité totale de ressource i) de la ième feuille de phySphere (stockcell)
        return phySphere.cells[i].cell.stock_cible
    
    def newdelta(self, phySphere, i):
        #renvoie la nouvelle valeur du taux de dépréciation du capital de la ième feuille de phySphere (stockcell)
        return phySphere.cells[i].cell.delta
    
    def K1(self, phySphere, i):
        #renvoie la nouvelle valeur du paramètre K1 (qui controle la variable efficiency d'une cellule flux) de la ième feuille de phySphere (flowcell)
        return phySphere.cells[i].cell.K1
    
    def K2(self, phySphere, i):
        #renvoie la nouvelle valeur du paramètre K2 (qui controle la variable surface_installee d'une cellule flux) de la ième feuille de phySphere (flowcell)
        return phySphere.cells[i].cell.K2
    
    def K3(self, phySphere, i):
        #renvoie la nouvelle valeur du paramètre K3 (qui controle la variable stockMax d'une cellule flux) de la ième feuille de phySphere (flowcell)
        return phySphere.cells[i].cell.K3
    
    def recipeMatrix(self, phySphere):
        #renvoie la nouvelle matrice des recettes
        return phySphere.recipeMatrix
    
    def recipeRequestArray(self, phySphere):
        #renvoie la requête en production de biens finaux pour l'instant suivant
        return phySphere.recipeRequestArray
    
    def requestedEnergyMix(self, phySphere):
        #renvoie la requête en mix énergétique pour l'instant suivant
        return phySphere.requestedEnergyMix
    
    
    
    
    def plot(self):
        return
    
    
    
    
    
    
    
    
    
    
    
    