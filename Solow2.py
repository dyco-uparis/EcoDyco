# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 09:23:43 2018

@author: stagiaire
"""
import numpy as np
import matplotlib.pyplot as plt
import math


def extractSolowParameters(fichier):
    fichier = open(fichier, "rU")
    array = []
    line = fichier.readline()
    while line != "" :
        splitline = line.split(" = ")
        value = splitline[1].split("\n")[0]
        value = float(value)
        array.append(value)    
        line = fichier.readline()
    return array


def createEcoSphere(fichier, rep_p, phySphere, deltat):
    #renvoie une instance de la classe EcoSphere.
    p = extractSolowParameters(rep_p + fichier)
    delta = phySphere.cells[0].cell.delta
    K = 0
    for i in range(phySphere.n_cells):
        if phySphere.cells[i].type == "stock":
            K += phySphere.cells[i].cell.K
    return EcoSphere(deltat, p[0], p[1], p[2], p[3], p[4], p[5], p[6], delta, K) 

##############################################################

class EcoSphere :
    
    
    
    def __init__(self, deltat, alpha, q, PN, L0, s, g, recycling_init, delta, K):
        #constructeur
        self.t = 0
        self.deltat = deltat
        self.alpha = alpha
        self.q = q
        self.PN = PN
        self.s = s
        self.L = L0
        self.delta = delta
        self.K = K
        self.A = 1  #productivité du travail
        self.g = g  #taux de croissance de A
        self.recycling = recycling_init
        
        self.record = Record(deltat, self.K, self.L, self.A)
 

       
    def iterate(self, phySphere):
        #actualise les attributs de la sphère éco
        self.t = self.t + self.deltat    
        self.L = self.L*(1 + self.deltat*self.q*(1 - self.L/self.PN))
        K = 0
        for i in range(phySphere.n_cells):
            if phySphere.cells[i].type == "stock":
                K += phySphere.cells[i].cell.K
            if phySphere.cells[i].type == "flow" :
                K+= phySphere.cells[i].cell.K1 + phySphere.cells[i].cell.K2
        self.K = K
        
        self.A = self.A*(1+self.deltat*self.g)
        self.recycling = self.recycling         #si on veut faire évoluer ce paramètre, c'est ici qu'il faut le faire
        self.record.actualize(self.K, self.L, self.A)
    
    
    
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
        cell = phySphere.cells[i].cell
        K = cell.K + self.deltat*cell.record.Gused[-1]*self.s
        return K
    
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
        cell = phySphere.cells[i].cell
        K1 = cell.K1 + self.deltat*cell.record.Gused[-1]*self.s*0.55        
        return K1
    
    def K2(self, phySphere, i):
        #renvoie la nouvelle valeur du paramètre K2 (qui controle la variable stockMax d'une cellule flux) de la ième feuille de phySphere (flowcell)
        cell = phySphere.cells[i].cell
        K2 = cell.K2 + self.deltat*cell.record.Gused[-1]*self.s*(1-0.45)
        return K2
    
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
                    #fonction de requête : Y = K^alpha * (AL)^(1-alpha)
                    var = math.pow(self.K/self.record.K[-2], self.alpha)*math.pow(self.A/self.record.A[-2]*self.L/self.record.L[-2], 1-self.alpha)
                    newRequest[i] = var*phySphere.record.production[-1][i]
                else :
                    return lastRequest
        return newRequest
    
    def requestedEnergyMix(self, phySphere):
        #renvoie la requête en mix énergétique pour l'instant suivant
        return phySphere.requestedEnergyMix
    
    
    
    
    def plot(self):
        record = self.record
        plt.figure()

        plt.subplot(2, 2, 1)
        plt.plot(record.t, record.L, label='L')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 2, 2)
        plt.plot(record.t, record.K, label='K')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 2, 3)
        plt.plot(record.t, np.array(record.K)/np.array(record.L)/np.array(record.A), label='K/AL')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()

#################################################################################################################
class Record:
    
    def __init__(self, deltat, K0, L0, A0):
        self.deltat = deltat
        self.t = [0]
        self.K = [K0]
        self.L = [L0]
        self.A = [A0]
        
    def actualize(self, K, L, A):
        self.t.append(self.t[-1] + self.deltat)
        self.K.append(K)
        self.L.append(L)
        self.A.append(A)