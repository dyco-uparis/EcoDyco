# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 09:23:43 2018

@author: stagiaire
"""
import numpy as np
import matplotlib.pyplot as plt


def extractGoodwinParameters( fichier):
    fichier = open(fichier, "r")
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
    p = extractGoodwinParameters( rep_p + fichier)
    delta = phySphere.cells[0].cell.delta    #pour l'instant 26/06, delta est défini
    return EcoSphere(deltat, p[0], p[1], p[2], p[3], p[4], delta, p[5], p[6], p[7], p[8], p[9]) 

##############################################################

class EcoSphere :
    
    
    
    def __init__(self, deltat, phi0, phi1, alpha, q, PN, delta, nu, omega0, lamda0, N0, recycling):
        #constructeur
        self.t = 0
        self.deltat = deltat
        self.phi0 = phi0                         #paramètres de la courbe de Phillips
        self.phi1 = phi1
        self.alpha = alpha                       #taux de croissance de la productivité du travail
        self.q = q                               #q et PN paramètrent l'évolution de la population active 
        self.PN = PN
        self.delta = delta                       #delta est le taux de dépréciation du capital
        self.nu = nu                             #capital-output ratio
        self.recycling = recycling               #ce paramètre définit le pourentage du flux de déchet produit que l'on souhaite recycler. 
                                                         #On pourrait très simplement décider de ne pas indexer la demande en recyclage sur le flux de déchets produits, mais sur la quantité totale de déchets présent dans la poubelle. 
                                                         #Pour cela, il suffit de changer la fonction eco.recipeRequestArray.
        
        self.omega = omega0                      #part de l'output dédiée aux salaires (compris entre 0 et 1)
        self.lamda = lamda0                      #taux d'emploi de la population active
        self.N = N0                              #population active
        
        self.record = Record(deltat, omega0, lamda0, N0)      #registre consignant toutes les valeurs passées de omega, lambda et N. Permet de tracer les courbes d'évolution temporelles de ces variables
 

       
    def iterate(self, phySphere):
        #actualise les attributs de la sphère éco
        self.t = self.t + self.deltat
        
        beta = self.q*(1 - self.N/self.PN)                     #taux instantané de croissance de la population
        
        z = np.array([self.lamda, self.omega])                 #les lignes suivantes ainsi que la fonction F correspondent à la methode d'intégration numérique RK4.
        k1 = self.F(z, beta)
        k2 = self.F(z+self.deltat/2*k1, beta)
        k3 = self.F(z+self.deltat/2*k2, beta)
        k4 = self.F(z+self.deltat*k3, beta)
        z1 = z + self.deltat/6*(k1 + 2*k2 + 2*k3 + k4)
        lamda = z1[0]
        omega = z1[1]
        
        N = self.N*(1 + self.deltat*beta)
        
        self.omega = omega
        self.lamda = lamda
        self.N = N
        
        self.delta = self.delta                         #si l'on souhaite modifier le paramètre EcoSphere.delta, c'est ici
        self.recycling = self.recycling                 #si l'on souhaite modifier le paramètre EcoSphere.recycling, c'est ici
        
        self.record.actualize(omega, lamda, N)
        
        
    def F(self, z, beta):
        #methode auxilliaire pour intégration numérique RK4
        a = 1/self.nu - self.alpha - beta - self.delta
        b = 1/self.nu
        c = self.phi1
        d = self.alpha - self.phi0
        return np.array([z[0]*(a-b*z[1]), z[1]*(c*z[0]-d)])        
        
        
    
    
    def inputsToPhySphere(self, phySphere):
        #Renvoie les valeurs de tous les paramètres physiques que le modèle économique peut faire varier
        #Ne pas modifier cette fonction, mais les fonctions filles (Rp, recyclingEnergyFlux etc...) ci-dessous
        cellsInputs = []
        for i in range(phySphere.n_cells):
            if phySphere.cells[i].type == "stock":
                cellsInputs.append([self.K(phySphere, i), self.recyclingEnergyFlux(phySphere, i), self.to(phySphere, i), self.stock_cible(phySphere, i), self.newdelta(phySphere, i)])
            elif phySphere.cells[i].type == "flow":
                cellsInputs.append([self.efficiency(phySphere, i), self.K1(phySphere, i), self.K2(phySphere, i), self.newdelta(phySphere, i)])
        globalInputs = [self.recipeMatrix(phySphere), self.recipeRequestArray(phySphere), self.requestedEnergyMix(phySphere)]
        return (cellsInputs, globalInputs)
    
    
    
    #les méthodes suivantes correspondent aux lois décrivant l'évolution de tous les paramètres correspondants.
        #on peut décider de faire varier ces paramètres de manière "extérieure",
        #ou de manière rétroactive, en réagissant à l'évolution de 
    
    
    
    def K(self, phySphere, i):
        #renvoie la nouvelle valeur de la résistance de l'appareil de production de la ième feuille de phySphere (stockcell)
        cell = phySphere.cells[i].cell
        K = cell.K + self.deltat*cell.record.Gused[-1]*(1-self.omega)                #on investit une part 1-omega de la production
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
        K1 = cell.K1 + self.deltat*cell.record.Gused[-1]*(1-self.omega)*0.55              #on investit une part 1-omega de la production
        return K1
    
    def K2(self, phySphere, i):
        #renvoie la nouvelle valeur du paramètre K2 (qui controle la variable stockMax d'une cellule flux) de la ième feuille de phySphere (flowcell)
        cell = phySphere.cells[i].cell
        K2 = cell.K2 + self.deltat*cell.record.Gused[-1]*(1-self.omega)*(1-0.55)              #on investit une part 1-omega de la production
        return K2
    
    def recipeMatrix(self, phySphere):
        #renvoie la nouvelle matrice des recettes
        return phySphere.recipeMatrix
    
    def recipeRequestArray(self, phySphere):
        #renvoie la requête en production de biens finaux pour l'instant suivant
        lastRequest = phySphere.recipeRequestArray
        produced = phySphere.record.production[-1]
        newRequest = [0]*len(lastRequest)
        for i in range(len(lastRequest)):
            ind = phySphere.isARecyclingRecipe(i)
            if ind > -1 :             #si la recette i est une recette de recyclage (elle permet de recycler la ressource d'indice ind dans le tableau cells de phySphere)
                newRequest[i] = phySphere.cells[ind].cell.deltaXl(1)*self.recycling
            elif ind == -1 :          #sinon, c'est une recette de production de bien final
                if self.t > self.deltat :                                      #(car produced[t=0] = 0 - initialisation)
                    newRequest[i] = produced[i]*(1 + self.deltat*((1-self.omega)/self.nu - self.delta))
                else :
                    return lastRequest     
        return newRequest
    
    def requestedEnergyMix(self, phySphere):
        #renvoie la requête en mix énergétique pour l'instant suivant
        return phySphere.requestedEnergyMix
    
    
    def Ypoint(self, phySphere):
        Y = (np.array(phySphere.record.production[1:])-np.array(phySphere.record.production[:-1]))/self.deltat
        return Y
    
    def plot(self):
        record = self.record
        plt.figure()

        plt.subplot(2, 2, 1)
        plt.plot(record.t, record.omega, label='omega')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 2, 2)
        plt.plot(record.t, record.lamda, label='lamda')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 2, 3)
        plt.plot(record.t, record.N, label='N')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
    
#################################################################################################################
class Record:
    
    def __init__(self, deltat, omega0, lamda0, N0):
        self.deltat = deltat
        self.t = [0]
#        self.Yd = [Yd0]
        self.omega = [omega0]
        self.lamda = [lamda0]
        self.N = [N0]
        
    def actualize(self, omega, lamda, N):
        self.t.append(self.t[-1] + self.deltat)
#        self.Yd.append(Yd)
        self.omega.append(omega)
        self.lamda.append(lamda)
        self.N.append(N)
    
    
    
    
    
    
    
    
