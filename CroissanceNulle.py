# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 09:23:43 2018

@author: stagiaire
"""
import numpy as np
import matplotlib.pyplot as plt
import math

###CROISSANCE LINEAIRE AVEC PAS D'INVESTISSEMENT (DONC METTRE UNE DEPRECIATION DU CAPITAL NULLE DANS WORLD.TXT)

def createEcoSphere(phySphere, deltat):
    #renvoie une instance de la classe EcoSphere.
    K = 0
    for i in range(phySphere.n_cells):
        if phySphere.cells[i].type == "stock":
            K += phySphere.cells[i].cell.K
    return EcoSphere(deltat, K) 

##############################################################

class EcoSphere :
    
    
    
    def __init__(self, deltat, K):
        #constructeur
        self.t = 0
        self.deltat = deltat
        self.K = K
        self.recycling = 0
        
        self.record = Record(deltat, self.K)
 

       
    def iterate(self, phySphere):
        #actualise les attributs de la sphère éco
        self.t = self.t + self.deltat    
        K = 0
        for i in range(phySphere.n_cells):
            if phySphere.cells[i].type == "stock":
                K += phySphere.cells[i].cell.K
            if phySphere.cells[i].type == "flow" :
                K+= phySphere.cells[i].cell.K1 + phySphere.cells[i].cell.K2
        self.K = K
        
        self.recycling = self.recycling   
            
        self.record.actualize(self.K)
    
    
    
    def inputsToPhySphere(self, phySphere):
        #Renvoie les valeurs de tous les paramètres physiques que le modèle économique peut faire varier
        #Ne pas modifier cette fonction, mais les fonctions filles (Rp, recyclingEnergyFlux etc...) ci-dessous
        cellsInputs = []
        for i in range(phySphere.n_cells):
            if phySphere.cells[i].type == "stock":
                cellsInputs.append([self.newK(phySphere, i), self.recyclingEnergyFlux(phySphere, i), self.to(phySphere, i), self.stock_cible(phySphere, i), self.newdelta(phySphere, i)])
            elif phySphere.cells[i].type == "flow":
                cellsInputs.append([self.efficiency(phySphere, i), self.K1(phySphere, i), self.K2(phySphere, i), self.newdelta(phySphere, i)])
        globalInputs = [self.recipeMatrix(phySphere), self.recipeRequestArray(phySphere), self.requestedEnergyMix(phySphere)]
        return (cellsInputs, globalInputs)
    
    
    
    
    def newK(self, phySphere, i):
        #renvoie la nouvelle valeur de la résistance de l'appareil de production de la ième feuille de phySphere (stockcell)
        return phySphere.cells[i].cell.K
    
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
    
    def efficiency(self, phySphere, i):
        #renvoie la nouvelle valeur du paramètre efficiency de la ième feuille de phySphere (flowcell)
        return phySphere.cells[i].cell.efficiency
    
    def K1(self, phySphere, i):
        #renvoie la nouvelle valeur du paramètre K1 (qui controle la variable surface_installee d'une cellule flux) de la ième feuille de phySphere (flowcell)    
        return phySphere.cells[i].cell.K1
    
    def K2(self, phySphere, i):
        #renvoie la nouvelle valeur du paramètre K2 (qui controle la variable stockMax d'une cellule flux) de la ième feuille de phySphere (flowcell)
        return phySphere.cells[i].cell.K2 
    
    def recipeMatrix(self, phySphere):
        #renvoie la nouvelle matrice des recettes
        return phySphere.recipeMatrix
    
    def recipeRequestArray(self, phySphere):
        #renvoie la requête en production de biens finaux pour l'instant suivant
        lastRequest = phySphere.recipeRequestArray
        newRequest = [0]*len(lastRequest)
        for i in range(len(lastRequest)):
            ind = phySphere.isARecyclingRecipe(i)
            if ind > -1 :       #si la recette i est une recette de recyclage (elle permet de recycler la ressource d'indice ind dans le tableau cells de phySphere)
                newRequest[i] = phySphere.cells[ind].cell.deltaXl(1)*self.recycling
            elif ind == -1 :    #sinon (c'est une recette de production de bien final)
                if self.t > self.deltat :
                    newRequest[i] = phySphere.record.request[-1][i]
                else :
                    return lastRequest
        return newRequest
    
    def requestedEnergyMix(self, phySphere):
        #renvoie la requête en mix énergétique pour l'instant suivant
        return phySphere.requestedEnergyMix
    
    
    
    
    def plot(self):
        record = self.record
        plt.figure()
        plt.plot(record.t, record.K, label='K')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        

#################################################################################################################
class Record:
    
    def __init__(self, deltat, K0):
        self.deltat = deltat
        self.t = [0]
        self.K = [K0]
        
    def actualize(self, K):
        self.t.append(self.t[-1] + self.deltat)
        self.K.append(K)
