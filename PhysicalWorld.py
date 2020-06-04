# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 09:13:54 2018

@author: simon
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import matplotlib.collections as collections

couleurs = ['tab:blue',
            'tab:orange',
            'tab:green',
            'tab:red',
            'tab:purple',
            'tab:brown',
            'tab:pink',
            'tab:gray',
            'tab:olive',
            'tab:cyan']


class StockCellRecord :
    #registre de tous les états et flux passés d'une cellule

    def __init__(self, deltat, resourceName,
                 Xt, Xh_init, Xl_init, Xs_init,
                 piH_init, piL_init, K0, Rp0 ) :

        self.deltat = deltat
        self.resourceName = resourceName
        #vecteur temps
        self.t = [0]
        #état des réservoirs
        self.Xt = Xt
        self.Xh = [Xh_init]
        self.Xl = [Xl_init]
        self.Xs = [Xs_init]
        self.Xb = [0]
        #potentiels
        self.piH = [piH_init]
        self.piL = [piL_init]
        #flux
        self.Fhp = [0]
        self.Flp = [0]
        self.G = [0]
        self.Gused = [0]
        self.Fr = [0]
        self.Fnr = [0]
        #intensités
        self.Ip = [0]
        self.Ipd = [0]
        self.Ipmax = [0]
        #autre
        self.efficiency = [0]
        self.hasStock = [-1] #-1 si pas de stock, 0 si stock compris "proche" de stock_cible, 1 si stock > autre
        self.isLimitated = [False]
        self.K = [K0]
        self.Rp = [Rp0]

    def toString(self) :
        s = "ressource : " + str(self.resourceName)
        s+= "t = " +str(self.t[-1])
        s += "Xt = " + str(self.Xt)
        s += "Xh = " + str(self.Xh[-1])
        s += "Xl = " + str(self.Xl[-1])
        s += "Xs = " + str(self.Xs[-1])
        s += "Xs = " + str(self.Xs[-1])
        s += "Xb = " + str(self.Xb[-1])
        s += "piH = " + str(self.piH[-1])
        s += "piL = " + str(self.piL[-1])
        s += "Fhp = " + str(self.Fhp[-1])
        s += "Flp = " + str(self.Flp[-1])
        s += "G = " + str(self.G[-1])
        s += "Gused = " + str(self.Gused[-1])
        s += "Fr = " + str(self.Fr[-1])
        s += "Fnr = " + str(self.Fnr[-1])
        s += "Ip = " + str(self.Ip[-1])
        s += "Ipd = " + str(self.Ipd[-1])
        s += "Ipmax = " + str(self.Ipmax[-1])
        s += "efficiency = " + str(self.efficiency[-1])
        s += "hasStock = "  + str(self.hasStock[-1])
        s += "isLimitated = " + str(self.isLimitated[-1])
        s += "Rp = " + str(self.Rp[-1])
        s += "\n"
        return s
    
    def actualize(self,
                  Xh, Xl, Xs, Xb, piH, piL, Fhp, Flp, G, Gused, Fr, Fnr, Ip, Ipd, Ipmax,
                  efficiency, hasStock, isLimitated, K, Rp):
        self.t.append(self.t[-1] + self.deltat)
        self.Xh.append(Xh)
        self.Xl.append(Xl)
        self.Xs.append(Xs)
        self.Xb.append(Xb)
        self.piH.append(piH)
        self.piL.append(piL)
        self.Fhp.append(Fhp)
        self.Flp.append(Flp)
        self.G.append(G)
        self.Gused.append(Gused)
        self.Fr.append(Fr)
        self.Fnr.append(Fnr)
        self.Ip.append(Ip)
        self.Ipd.append(Ipd)
        self.Ipmax.append(Ipmax)
        self.efficiency.append(efficiency)
        self.hasStock.append(hasStock)
        self.isLimitated.append(isLimitated)
        self.K.append(K)
        self.Rp.append(Rp)

#----------------------------------------------------------------------------------------    

class StockCell :
    #feuille qui décrit une ressource stock

    def __init__(self,
                 deltat,
                 name,
                 Xt,
                 Xh_init,
                 Xl_init,
                 Rp0,
                 K0,
                 recyclingEnergyFlux,
                 isEnergy,
                 r,
                 to,
                 stock_cible,
                 alpha,
                 delta,
                 xc,
                 x0):
        if Xh_init + Xl_init != Xt :
            print("ERROR : {} : Xh_init + Xl_init != Xt".format(name))
        self.deltat = deltat
        self.name = name
        self.Xt = Xt            # total recoverable quantity 
        self.Xh = Xh_init
        self.Xl = Xl_init
        self.Xs = Xt - Xh_init - Xl_init
        self.Xb = 0                                     # Xbuffer : ce qui est "en attente", pret à être utilisé pour production de la recette, ou à partir au stock, à l'instant suivant
        self.Ip = 0.1                                     #intensité nominale de fonctionnement
        self.Ipd = self.Ip
        self.K = K0
        self.Rp0 = Rp0
        self.recyclingEnergyFlux = recyclingEnergyFlux  #flux d'énergie nécessaire pour obtenir un flux de recyclage de 1 unité de ressource par unité de temps
        self.isEnergy = isEnergy                        #-1 si ce n'est pas une cellule énergie, beta > 0 si c'est une cellule qui peut produire de l'énergie. beta est le flux de ressource nécessaire pour produire une unité d'énergie
        self.r = r
        self.to = to
        self.stock_cible = stock_cible
        self.alpha = alpha
        self.delta = delta
        self.xc = xc
        self.x0 = x0
        self.RT = 1
        self.piH0 = -1 * self.RT * math.log( xc ) # RT * math.log( x0/xc )  # piH0 is set such as piH(xH=0)=0
        self.piL0 = -1 * self.RT * math.log( xc ) # RT * math.log( x0/xc )  # piLO is set such as piL(xL=1)=0 (<=> to piH0 = piL0)
        self.record = StockCellRecord(deltat, name, Xt, Xh_init, Xl_init, Xt - Xh_init - Xl_init, self.piH(), self.piL(), K0, Rp0)


    def toString(self) :
        print(self.record.toString())


    def piH(self) :
        # print(self.Xh) # virer
        if self.Xh > self.xc:
            return self.piH0 + self.RT * math.log( self.Xh / self.Xt * self.x0  )
        if self.Xh <= self.xc:  # minimal concentration is xc
            return self.piH0 + self.RT * math.log( self.xc  )


    def piL(self) :
        # print(self.piL0 + self.RT * math.log( self.xc  )) # virer
        return self.piL0 + self.RT * math.log( self.xc  )



    def deltaXl(self, i) :
        return self.record.Flp[-i] + self.record.Gused[-i]


    def deltaXs(self) :
        return self.record.Xb[-1] - self.record.Gused[-1]*self.deltat



    def deltaPi(self) :
        # print(self.piH() - self.piL())# virer
        return self.piH() - self.piL()


    def Ipmax(self) :
        return (self.deltaPi())/(2*self.Rp())


    def Ipopt(self, Gd) :
        delta = self.deltaPi()*self.deltaPi() - 4*self.Rp()*(Gd - self.Xs/self.deltat)
        if delta < 0 :
            return self.IpMax()
        else :
            Ip =(self.deltaPi() - math.sqrt(delta))/(2*self.Rp())
            if Ip < 0 :            # forbid negative flux
                Ip = 0
                return Ip
            else :
                return Ip
    
    
    def actualize(self, inputs):
        self.K = inputs[0]
        self.recyclingEnergyFlux = inputs[1]
        self.to = inputs[2]
        self.stock_cible = inputs[3]
        self.delta = inputs[4]
    
    
    def Rp(self) :
        Rp = self.Rp0*self.record.K[0]/self.K + 4e-6
        if Rp > 1e100 :
            Rp = 1e100
        return Rp
    
    def iterate(self, Gused, Fr) :
        #Cette fonction réalise une itération de Xh, Xl et Xs  
        
        self.K = self.K*(1-self.delta*self.deltat)
        if self.K < 1e-100 :
            self.K = 1e-100
        Rp = self.Rp()
        
        x = self.Xs
        dx = (self.record.G[-1] - self.record.Gused[-1])*self.deltat
        self.Ipd += 10/self.stock_cible/self.Xt * \
            (self.stock_cible*self.Xt - x - 25*dx/self.deltat) * self.deltat

        if self.Ipd < 1e-14 :
            self.Ipd = 1e-14
        
        isLimitated = False  
        if self.Ipd > self.Ipmax() :
            self.Ipd = self.Ipmax()
            isLimitated = True
            
        self.Ip = (self.Ip + (self.deltat/self.to)*self.Ipd)/(1 + self.deltat/self.to)
        
        if self.Ip > self.Ipmax():
            self.Ip = self.Ipmax()
        
        # EH: ajout du 03/10/2018 pour empecher la les valeurs negatives de Ip 
        if self.Ip < 0 :
            self.Ip = 0
        
        #on calcule toutes les flux pendant ce pas de temps 
        #dans la zone de production, étant donné Xh et Xl au début de la période
        if self.piH()*self.Ip < self.piL()*self.Ip + Rp*self.Ip*self.Ip : 
            # remarque : on ne devrait jamais rentrer dans cette boucle, 
            # puisque que on tourne a intensité qui est au maximum égale à 
            # l'intensité qui permet la production maximale, mais on ne 
            # dépasse jamais cette intensité.
            print("\n\t si ce message apparait c'est que quelque chose cloche!!!")
            print(self.Ipd)
            print(self.Ip)
            print(self.Ipmax())
            print(self.Rp())
            print(self.K)
         
        else :
            Fhp = self.piH()*self.Ip
            Flp = self.piL()*self.Ip + Rp*self.Ip*self.Ip
            if Fhp > self.Xh/self.deltat :
                Fhp = self.Xh/self.deltat
                self.Ip = Fhp/self.piH()
                self.Ipd = Fhp/self.piH()
                Flp = self.piL()*self.Ip + Rp*self.Ip*self.Ip
            G = Fhp - Flp
            
        efficiency = 0
        if Fhp != 0 :
            efficiency = G/Fhp
        
        # on calcule ce qui va être recyclé naturellement pendant ce pas de temps, 
        # étant donné Xh et Xl au début de la période
        Fnr = 0
        if self.r > 0 :
            #attention la fonction dans le papier est self.r*self.Xh*(1 - Th) *(Th/self.s - 1)
            Fnr = self.r*self.Xl*(1-math.exp(-(self.Xl/self.Xt)/0.5))
#            s = 0.3
#            Th = self.Xh/self.Xt
#            Fnr = self.r*self.Xl*(1 - Th) *max(0, (Th/s - 1))
        
            
        if Fr + Fnr > self.Xl/self.deltat :
            print("attention on perd de l'énergie - voir calcul de Fr de la cellule {}".format(self.name))
            if Fnr > self.Xl/self.deltat  :
                Fnr = self.Xl/self.deltat
                Fr = 0
            elif Fr > self.Xl/self.deltat :
                Fr = self.Xl/self.deltat
                Fnr = 0
            else :
                Fnr = self.Xl/self.deltat- Fr
                
        efficiency = 0
        if Fhp != 0 :
            efficiency = G/Fhp
        
        if self.Xs < 1e-14 :
            hasStock = 0
        elif self.Xs < self.stock_cible*self.Xt*0.9 :
            hasStock = 0.5
        elif self.Xs > self.stock_cible*self.Xt*1.1 :
            hasStock = 1.5
        else : 
            hasStock = 1.0
        
        #on actualise Xh, Xl, Xs
        self.Xs = self.Xs + self.Xb - Gused*self.deltat
        self.Xh = self.Xh + (- Fhp + Fr + Fnr)*self.deltat
        self.Xl = self.Xl + (Flp + Gused - Fr - Fnr)*self.deltat
        self.Xb = G * self.deltat
        
        self.record.actualize(self.Xh, self.Xl, self.Xs, self.Xb, self.piH(), self.piL(), Fhp, Flp, G, Gused, Fr, Fnr, self.Ip, self.Ipd, self.Ipmax(), efficiency, hasStock, isLimitated, self.K, Rp)

        
    def plot(self, indFigure):
        
        record = self.record
        
        plt.figure(indFigure)
        fs = 13
        plt.subplot(3,3,1)
        plt.plot(record.t, record.Xh,label='$X_h}$',linewidth=1)
        plt.plot(record.t, record.Xl,label='$X_l}$',linewidth=1)
        plt.xlabel('$Time$',fontsize=fs)
        plt.ylabel('$Reservoirs$',fontsize=fs)
        plt.legend()
        plt.grid(True)

    
        plt.subplot(3,3,2)
        plt.plot(record.t, record.Fhp,label='$F_hp}$',linewidth=1)
        plt.plot(record.t, record.Flp,label='$F_lp}$',linewidth=1)
        plt.xlabel('$Time$',fontsize=fs)
        plt.ylabel('$Fluxes$',fontsize=fs)
        plt.legend()
        plt.grid(True)
    
    
        plt.subplot(3,3,3)
        plt.plot(record.t, record.G,label='$G}$',linewidth=1)
        plt.plot(record.t, record.Gused,label='$G_{used}$',linewidth=1)
#        plt.plot(record.t, (np.array(record.Xb) + np.array(record.Xs))/self.deltat,label='$Available$',linewidth=1)
        plt.xlabel('$Time$',fontsize=fs)
        plt.ylabel('$Production$',fontsize=fs)
        plt.legend()
        plt.grid(True)
        
        
        plt.subplot(3,3,4)
        plt.plot(record.t, record.Fnr,label='$F_{nr}$',linewidth=1)
        plt.plot(record.t, record.Fr,label='$F_r}$',linewidth=1)
        plt.xlabel('$Time$',fontsize=fs)
        plt.ylabel('$Recycling$',fontsize=fs)
        plt.legend()
        plt.grid(True)

        
        plt.subplot(3,3,5)
        plt.plot(record.t,record.Ip,label='$I_p}$',linewidth=1)
        plt.plot(record.t,record.Ipmax, label='$I_p^{max}}$', linewidth=1)
        plt.plot(record.t, record.Ipd, label='$I_p^{d}}$', linewidth=1)
        plt.xlabel('$Time$',fontsize=fs)
        plt.ylabel('$Prod Intensity$',fontsize=fs-5)
        plt.legend()
        plt.grid(True)
        
    
        plt.subplot(3,3,6)
        plt.plot(record.t, record.Xs,linewidth=1)
        plt.xlabel('$Time$',fontsize=fs)
        plt.ylabel('$Stock$',fontsize=fs)
        #plt.legend()
        plt.grid(True)
#        plt.yscale('log')
    
        
        plt.subplot(3,3,7)
        plt.yscale('log')
        plt.plot(record.t, record.Rp,linewidth=1)
        plt.xlabel('$Time$',fontsize=fs)
        plt.ylabel('$R_p$',fontsize=fs)
        #plt.legend()
        plt.grid(True)
        
    
        plt.subplot(3,3,8)
        plt.plot(record.t, np.array(record.piH)-np.array(record.piL),linewidth=1)
        plt.xlabel('$Time$',fontsize=fs)
        plt.ylabel('$\Delta \pi$',fontsize=fs)
        # plt.ylim((0, 1))
        #plt.legend()
        plt.grid(True)
    
        
        plt.subplot(3,3,9)
        plt.xticks([])
        plt.yticks([])
        
        plt.text(0.05, 0.85 , self.name, fontsize=fs-5)
        plt.text(0.05, 0.70 , r'$Total=$'    +str(self.Xt), fontsize=fs-5)
        plt.text(0.05, 0.55 , r'$Nat_R=$'    +str(self.r), fontsize=fs-5)
        plt.text(0.05, 0.40 , r'$Duration=$' +str(int(len(record.t)-1)*self.deltat), fontsize=fs-5)
        plt.text(0.05, 0.25 , r'$Time_{step}=$'+str(self.deltat), fontsize=fs-5)

    
        plt.grid(False)
    
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.7, hspace=0.6)
        plt.tight_layout()
        
#############################################################################################################################################

class FlowCellRecord :
    
    def __init__(self, deltat, name, eff_init, surface_installee_init, stockMax_init, K1_init, K2_init):
        self.deltat = deltat
        self.name = name
        self.t = [0]
        self.G = [0]
        self.Gused = [0]
        self.Xs = [0]
        self.Xb = [0]
        self.eff = [eff_init]
        self.surface_installee = [surface_installee_init]
        self.stockMax = [stockMax_init]
        self.K1 = [K1_init]
        self.K2 = [K2_init]

    def actualize(self, G, Gused, Xs, Xb, eff, surface_installee, stockMax, K1, K2):
        self.t.append(self.t[-1] + self.deltat)
        self.G.append(G)
        self.Gused.append(Gused)
        self.Xs.append(Xs)
        self.Xb.append(Xb)
        self.eff.append(eff)
        self.surface_installee.append(surface_installee)
        self.stockMax.append(stockMax)
        self.K1.append(K1)
        self.K2.append(K2)

#-----------------------------------------------------------------------------------------------------------------------

class FlowCell :
    #décrit une resource flow

    def __init__(self, deltat, name, incidentFlow, eff_init, surface_installee, isEnergy, stockMax_init, delta):
        self.deltat = deltat
        self.name = name        
        self.incidentFlow = incidentFlow
        self.Xs = 0
        self.Xb = 0
        self.efficiency = eff_init      
        self.surface_installee_init = surface_installee
        self.isEnergy = isEnergy
        self.stockMax_init = stockMax_init
        self.K1 = 1
        self.K2 = 1
        self.delta = delta
        self.record = FlowCellRecord(deltat, name, eff_init, self.surface_installee_init, stockMax_init, self.K1, self.K2)
        
    
    def actualize(self, inputs):
        self.efficiency = inputs[0]
        self.K1 = inputs[1]
        self.K2 = inputs[2]
        self.delta = inputs[3]


    def surface_installee(self):
        surface_installee = self.surface_installee_init*math.log(1+self.K1/self.record.K1[0])
        if surface_installee > 1 :
            surface_installee = 1
        return surface_installee
        
    def stockMax(self):
        return self.stockMax_init*math.log(1+self.K2/self.record.K2[0])
    
        
    def iterate(self, Gused):
        self.K1 = self.K1*(1 - self.deltat*self.delta)
        self.K2 = self.K2*(1 - self.deltat*self.delta)
        
        surface_installee = self.surface_installee()
        stockMax = self.stockMax()
        
        G = self.efficiency * surface_installee * self.incidentFlow
        self.Xb = G * self.deltat
        self.Xs = self.Xs + self.Xb - Gused * self.deltat
        
        if self.Xs > stockMax :
            self.Xs = stockMax
        
        self.record.actualize(G, Gused, self.Xs, self.Xb, self.efficiency, surface_installee, stockMax, self.K1, self.K2)
        
        
    def plot(self, indFigure):
        record = self.record
        plt.figure()
        
        plt.subplot(2, 3, 1)
        plt.plot(record.t, record.G, label='$G$')
        plt.plot(record.t, record.Gused, label='$G_{used}$')
        plt.grid(True)
        plt.legend()
        
        plt.subplot(2, 3, 2)
        plt.plot(record.t, record.Xs, label='$Stock$')
        plt.plot(record.t, record.stockMax, label='$Stock Max$', linestyle='-.')
        plt.grid(True)
        plt.legend()   
        
        plt.subplot(2, 3, 3)
        plt.plot(record.t, record.eff, label='$efficiency$')
        plt.grid(True)
        plt.legend()
        
        plt.subplot(2, 3, 4)
        plt.plot(record.t, record.K1, label='$K1$')
        plt.plot(record.t, record.K2, label='$K2$')
        plt.grid(True)
        plt.legend()
        
        plt.subplot(2, 3, 5)
        plt.plot(record.t, record.surface_installee, label='$surface installee$')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
                
#############################################################################################################################################
            
class Cell :
    
    def __init__(self, cell, type):
        self.type = type
        self.cell = cell
        
    def iterate(self, Gd, *args):
        if self.type == "flow" :
            return self.cell.iterate(Gd)
        if self.type == "stock" :
            return self.cell.iterate(Gd, args[0])
    
        
    def plot(self, indFigure):
        return self.cell.plot(indFigure)
    
    
    
    
#############################################################################################################################################
        
class PhysicalWorldRecord :
    
    def __init__(self, deltat, n_recipe, n_cells) :
        self.deltat = deltat
        self.t = [0]
        self.production = [[0]*n_recipe]
        self.request = [[0]*n_recipe]
        self.realEnergyMix = [[0]*n_cells]
        self.requestedEnergyMix = [[0]*n_cells]
        
    def actualize(self, production, request, realEnergyMix, requestedEnergyMix) :
        self.t.append(self.t[-1] + self.deltat)
        self.production.append(production)
        self.request.append(request)
        self.realEnergyMix.append(realEnergyMix)
        self.requestedEnergyMix.append(requestedEnergyMix)

#----------------------------------------------------------------------------------        
        
class PhysicalWorld :
    #ensemble de feuilles stock et flow
    
    def __init__(self, deltat, cells, recipeMatrix, recipeRequestArray_init, requestedEnergyMix) :
        self.deltat = deltat
        self.cells = cells
        self.recipeMatrix = recipeMatrix        #cette matrice indique la recette (ingrédients et flux nécessaire) pour produire un flux de une unité de produit par unité de temps. Elle a un nombre de ligne égal au nombre de recettes, et un nombre de colonnes égal au nombre de cellules (ingrégients)
                                                #la i_ème ligne k_ème colonne de cette matrice correspond à la demande en ressource k de la recette i à l'instant considéré. C'est la demande non-agrégée.
        
        self.n_cells = len(cells)
        self.recipeToRecycle = [-1]*self.n_cells  #tableau de correspondance entre une ressource et la position de la recette pour la recycler dans la matrice des recettes. Position = -1 si pas de recette pour recycler la ressource
        
        self.recipeRequestArray = []
        for i in range(len(recipeRequestArray_init)):
            self.recipeRequestArray.append(recipeRequestArray_init[i])
        
        
        for i in range(self.n_cells) :            #ajout des recettes de recyclage à recipeMatrix et remplissage de recipeToRecycle
            if self.cells[i].type == "stock" :
                ind = np.shape(recipeMatrix)[0]
                if self.cells[i].cell.recyclingEnergyFlux >= 0 :
                    array = [0]*(self.n_cells+1)
                    array[-1] = self.cells[i].cell.recyclingEnergyFlux
                    self.recipeMatrix.append(array)
                    self.recipeToRecycle[i] = ind
                    self.recipeRequestArray.append(0)
                    ind += 1
        self.requestedEnergyMix = requestedEnergyMix
        self.record = PhysicalWorldRecord(deltat, len(self.recipeRequestArray), self.n_cells)

    def isARecyclingRecipe(self, i):
        #renvoie l'emplacement de la ressource dans self.cells si la recette a la ligne i dans RecipeMatrix est une recette de recyclage, renvoie -1 sinon
        for k in range(self.n_cells):
            if self.recipeToRecycle[k] == i :
                return k
        return -1
    
    
    
    def availableResource(self):
        availableResource =  [0]*(self.n_cells + 1)
        for i in range(self.n_cells) :
            availableResource[i] = (self.cells[i].cell.record.Xb[-1] + self.cells[i].cell.record.Xs[-1])/self.deltat
            if self.cells[i].cell.isEnergy:
                availableResource[-1] += availableResource[i]
        return availableResource
       
        
    
    def actualizeRecipeRequest(self, newProdRequest) :  
        for i in range(len(self.recipeRequestArray)):
            self.recipeRequestArray[i] = newProdRequest[i]
    
    
    def test(self, array):
        for i in range(len(array)):
            if array[i] :
                return True
        return False
    
    def somme(self, rec, j):
        s = 0
        for i in range(len(rec)):
            if rec[i]:
                s += self.recipeRequestArray[i]*self.recipeMatrix[i][j]
        return s

    def indMiniPos(self, l):
        ind = -0.1
        for i in range(len(l)):
            if l[i] > 0 :
                ind = i
                miniPos = l[i]
        for i in range(len(l)):
            if l[i] > 0 and l[i] < miniPos :
                miniPos = l[i]
                ind = i
        return ind
    
    
    def produce(self) :
        #renvoie le tableau used contenant les quantités prélevées à chaque ressource pour production (Gused).
        #renvoie également le quantités produites pour chaque recette à cette itération
        #voir fichier algo "attributionResourcesauxRecettes
        n_ing = self.n_cells + 1
        n_rec = len(self.recipeRequestArray)
        coeff = self.recipeRequestArray
        dispo = self.availableResource()
        used = [0]*n_ing
        prod = [0]*n_rec

        disp = []
        for i in range(len(dispo)):
            disp.append(dispo[i])
    
        rec = [True]*n_rec
        prodNeeded = [True]*n_rec   
        s = []
        k = 0
        
        while self.test(rec) and self.test(prodNeeded):
            array = []
            for j in range(n_ing):
                if self.somme(rec, j) != 0:
                    array.append(disp[j]/self.somme(rec, j))
                else :
                    array.append(-1)
            s.append(array)
            
            j0 = self.indMiniPos(s[k])
            if j0 != - 0.1 : 
                for i in range(n_rec) :
                    if self.recipeMatrix[i][j0] > 0 and rec[i] :
                        prod[i] = coeff[i]*min(s[k][j0], 1)
                        for j in range(n_ing):
                            disp[j] -= self.recipeMatrix[i][j]*prod[i]
                            used[j] += self.recipeMatrix[i][j]*prod[i]
                        rec[i] = False
                for i in range(n_rec) :
                    if prod[i] >= coeff[i]:
                        prodNeeded[i] = False
                k += 1
            else :
                for i in range(n_rec) :
                    rec[i] = False
                

        #répartition de l'usage de l'énergie sur les différentes cellules énergie
        tempNrjMix = []
        for j in range(len(self.requestedEnergyMix)):
            tempNrjMix.append(self.requestedEnergyMix[j])
        flags = []
        for j in range(self.n_cells):
            if self.requestedEnergyMix[j] > 0 :
                flags.append(True)
            else :
                flags.append(False)
        Utemp = 0  
        
        while self.test(flags):
            array = []
            for j in range(self.n_cells):
                if tempNrjMix[j] != 0 and flags[j]:
                    array.append(dispo[j]/tempNrjMix[j])
                else :
                    array.append(-1)
            j0 = self.indMiniPos(array)
            if j0 != -0.1 :
                Utemptemp = Utemp
                for j in range(self.n_cells) :
                    if flags[j]:
                        add = min(tempNrjMix[j]*(used[-1] - Utemp), tempNrjMix[j]*array[j0])
                        used[j] += add
                        dispo[j] -= add
                        Utemptemp += add
                tempNrjMix[j0] = 0
                flags[j0] = False
                Utemp = Utemptemp
                somme = sum(tempNrjMix)
                if somme > 0:
                    for j in range(len(tempNrjMix)):
                        tempNrjMix[j] = tempNrjMix[j]/somme
            else : #on sort du while
                for j in range(self.n_cells):
                    flags[j] = False
                    
#        print("\nt: {}, availableResource : {}, Gused : {}".format(self.record.t[-1], self.availableResource(), used))

        return (used, prod)
    
    
    
    def computeEnergyMix(self, Gused) :
        energyMix = [0]*self.n_cells
        for i in range(self.n_cells):
            if self.cells[i].cell.isEnergy and Gused[-1] > 0 :
                energyMix[i] = Gused[i]/Gused[-1]
        return energyMix
    
    
    def quantityProduced(self):
        qty = [0]*len(self.recipeRequestArray)
        for i in range(len(qty)) :
            for k in range(len(self.record.t)) :
                qty[i] += self.record.production[k][i]*self.deltat
        return qty
    
    
    
    def iterate(self):
        #produce
        (Gused, produced) = self.produce()
        
        #actualize record
        request = []
        for i in range(len(self.recipeRequestArray)):
            request.append(self.recipeRequestArray[i])
        self.record.actualize(produced, request, self.computeEnergyMix(Gused), self.requestedEnergyMix)
        
        #iterate cells
        Fr = [0]*self.n_cells
        for i in range(self.n_cells):
            if self.cells[i].type =="stock" and self.cells[i].cell.recyclingEnergyFlux >= 0 :
                Fr[i] = produced[self.recipeToRecycle[i]]
        for i in range(len(self.cells)) :
            if self.cells[i].type =="stock":
                self.cells[i].iterate(Gused[i], Fr[i])
            else : 
                self.cells[i].iterate(Gused[i])
        
    
    
    def actualize(self, inputs):
        cellsInputs = inputs[0]
        globalInputs = inputs[1]
        for i in range(self.n_cells):
            self.cells[i].cell.actualize(cellsInputs[i])
        self.recipeMatrix = globalInputs[0]
        self.recipeRequestArray = globalInputs[1]
        self.requestedEnergyMix = globalInputs[2]
        
    
    
    
    def plot(self) :
        
        for k in range(self.n_cells):
            self.cells[k].plot(k+1)
            
        plt.figure()
        fs = 18
        productionRecord = np.array(self.record.production)
        requestRecord = np.array(self.record.request)
        energyMix = np.array(self.record.realEnergyMix)
        qty = self.quantityProduced()
        for i in range(len(self.recipeRequestArray)) :
            plt.plot(self.record.t, productionRecord[:, i], label='recipe ' + str(i), color=couleurs[i])
            plt.plot(self.record.t, requestRecord[:, i], ls = '--', color=couleurs[i])
            plt.xlabel('$Time$',fontsize=fs)
            plt.ylabel('$Production$',fontsize=fs)
            plt.grid(True)
            print("recipe {}, aggregated production : {}".format(i, qty[i]))
        plt.legend()
        plt.tight_layout()
        
        plt.figure()
        plt.subplot(1, 2, 1)
        for i in range(self.n_cells):
            if self.cells[i].cell.isEnergy :
                plt.plot(self.cells[0].cell.record.t, energyMix[:, i], label='instant ' + str(self.cells[i].cell.name))
                plt.xlabel('$Time$',fontsize=fs)
                plt.ylabel('$Energy Mix$',fontsize=fs)    
                plt.grid(True)
        plt.legend()
        
        
        plt.subplot(1, 2, 2)
        energyConsumption = np.zeros(len(self.cells[0].cell.record.t))
        for i in range(self.n_cells):
            if self.cells[i].cell.isEnergy :
                energyConsumption += np.array(self.cells[i].cell.record.Gused)
        plt.plot(self.cells[0].cell.record.t, energyConsumption)
        plt.grid(True)
        plt.xlabel('$Time$',fontsize=fs)
        plt.ylabel('$Energy Consumption$',fontsize=fs) 
        plt.tight_layout()
        
        fig, axs = plt.subplots(self.n_cells, 1, sharex = True)
        fig.subplots_adjust(hspace=0)
        for i in range(self.n_cells):
            record = self.cells[i].cell.record
            t = np.array(record.t)
            if self.cells[i].type == "stock" :
                axs[i].plot(t, np.array(record.Xs)/(self.cells[i].cell.stock_cible*self.cells[i].cell.Xt), label='% stock cible', color = 'tab:orange')
                axs[i].grid(True)
                hasStock = np.array(record.hasStock)
                isLimitated = np.array(record.isLimitated)
                ymaxi = max(record.Xs)/(self.cells[i].cell.stock_cible*self.cells[i].cell.Xt)
                collection = collections.BrokenBarHCollection.span_where(
                        t, ymin=0, ymax=ymaxi, where=hasStock == 1.5, facecolor='black', alpha=0.8)
                axs[i].add_collection(collection)
                collection = collections.BrokenBarHCollection.span_where(
                    t, ymin=0, ymax=ymaxi, where=hasStock == 1.0, facecolor='grey', alpha=0.8)
                axs[i].add_collection(collection)
                collection = collections.BrokenBarHCollection.span_where(
                    t, ymin=0, ymax=ymaxi, where=hasStock == 0.5, facecolor='grey', alpha=0.2)
                axs[i].add_collection(collection)
                collection = collections.BrokenBarHCollection.span_where(
                    t, ymin=0, ymax=ymaxi/10.0, where=isLimitated == True, facecolor='red', alpha=0.2)
                axs[i].add_collection(collection)
                ax = axs[i].twinx()
                ax.plot(t, np.array(record.piH) - np.array(record.piL),label='$\Delta \pi$')
                ax.legend()
            if self.cells[i].type == "flow" :
                axs[i].plot(t, np.array(record.Xs)/(record.stockMax), label='% stock max', color = 'tab:orange')
                axs[i].grid(True)
                stockMax=self.cells[i].cell.stockMax
                ymaxi = max(record.Xs)
                collection = collections.BrokenBarHCollection.span_where(
                        t, ymin=0, ymax=ymaxi, where=np.array(record.Xs)>1e-14, facecolor='grey', alpha=0.2)
                axs[i].add_collection(collection)
                collection = collections.BrokenBarHCollection.span_where(
                        t, ymin=0, ymax=ymaxi, where=np.array(record.Xs) ==stockMax, facecolor='grey', alpha=0.8)
                axs[i].add_collection(collection)
                
            axs[i].legend()
            axs[i].set_title(self.cells[i].cell.name, loc='center', x=-0.05, y=0.5, rotation='horizontal')
            plt.tight_layout()
    

#######################################################################################################################################################    
#------------------------- GET PARAMETERS------------------------------------------------------------

def extractCellParameters(fichier, rep_p) :  # Read data from *.txt
    fichier = open(rep_p + fichier, "rU")
    array = []
    line = fichier.readline()
    ind_line = 0
    while line != "" :
        splitline = line.split(": ")
        value = splitline[1].split("\n")[0]
        name = splitline[0]
        if ind_line > 1:
            if name == 'isEnergy ':
                value = value == 'True' or value == 'True '
            else :
                value = float(value)
                #print value
        array.append(value)
        line = fichier.readline()
        ind_line += 1
    # print(array)
    return array

def createCell(fichier, rep_p, stock_cible, alpha, delta, deltat):  # 
    p = extractCellParameters(fichier, rep_p)
    if p[0]== "stock" :
        return StockCell(deltat, p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10], stock_cible, alpha, delta, xc=p[11], x0=p[12])
    if p[0] == "flow" :
        return FlowCell(deltat, p[1], p[2], p[3], p[4], p[5], p[6], delta)
    
def extractWorldParameters(fichier, rep_p):  # 
    fichier = open(rep_p + fichier, "rU")
    array = []
    line = fichier.readline()
    while line != "" :
        splitline = line.split(": ")
        name = splitline[0]
        value = splitline[1].split("\n")[0]
        if name == "alpha " or name == "delta " or name == "stock_cible ":
            value = float(value)
        elif name == "recipeMatrix " or name=="recipeRequestArray_init " or name == "energyMix ":
            value = value.split("], ")
            value[0] = value[0][1:]
            value[-1] = value[-1][:-1]
            for j in range(len(value)):
                if j < len(value)-1 :
                    value[j] += "]"
                value[j] = value[j].split(", ")
                if name == "recipeMatrix " :
                    value[j][0] = value[j][0][1:]
                    value[j][-1] = value[j][-1][:-1]
                for i in range(len(value[j])):
                    value[j][i] = float(value[j][i])  
                if name =="recipeRequestArray_init " or name =="energyMix ":
                    value = value[0]
        elif name == "cells ":
            value = value.split(", ")
            value[0] = value[0][1:]
            value[-1] = value[-1][:-1]
        array.append(value)    
        line = fichier.readline()
    return array

def createPhysicalWorld(fichier, rep_p, deltat):  # 
    p = extractWorldParameters(fichier, rep_p)
    #print p
    cells = []
    for i in range(len(p[6])):      # get resource cell content (Wood, oil...)
        cellName = p[5][i] + ".txt"  
        q = extractCellParameters(cellName, rep_p)
        cells.append(Cell(createCell(cellName, rep_p, p[0], p[1], p[2], deltat), q[0]))
    return PhysicalWorld(deltat, cells, p[3], p[4], p[6])
