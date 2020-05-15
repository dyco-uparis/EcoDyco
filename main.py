# coding: utf-8
"""
Created on Fryday Sept 27 11:58:52 2018

"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import PhysicalWorld as phy


######################################################
# begin  PARAMS users

# Growth Model
# Choose a Growth Modeling:
    #goodwin
    #solow
    #ZeroGrowth
eco_engine = "solow"

# Temporal Resolution
deltat = 0.1

# Maximum number of iteration
tmax = 2000

# path for cells and growth model parameters
rep_p = 'preproc/'

# save data using xls format
save_xls = False

# save figures
save_plot = True                # True = save figures OR False = show figures
plot_name = 'fig-out'

# end PARAMS users
######################################################
print('')
print('Economical model is :\t\t' + eco_engine)
print('Figures will be saved :\t\t' + str(save_plot))
print('Data will be saved :\t\t' + str(save_xls))

phySphere = phy.createPhysicalWorld("world.txt", rep_p, deltat)

if eco_engine == "solow":
    import Solow as eco 
    ecoSphere = eco.createEcoSphere("solow.txt", rep_p, phySphere, deltat)   
    rep = '_solow'

elif eco_engine == "goodwin":
    import Goodwin as eco
    ecoSphere = eco.createEcoSphere("goodwin.txt", rep_p, phySphere, deltat)   
    rep = '_goodwin'

elif eco_engine == "ZeroGrowth":
    import ZeroGrowth as eco
    ecoSphere = eco.createEcoSphere( phySphere, deltat)
    rep = '_ZeroGrowth'

else:
    print('\t World Was Not Created ! ')

print("\n>>\t WORLD SUCESSFULLY CREATED \n")



for k in range(int(tmax/deltat)):
    phySphere.iterate()
    ecoSphere.iterate(phySphere)
    inputs = ecoSphere.inputsToPhySphere(phySphere)
    phySphere.actualize(inputs)

 
# plot graphs
plt.close("all")
phySphere.plot()
ecoSphere.plot()


# 
#*****************************************************************************************************
# Export Figures
#*****************************************************************************************************
# 


def ensure_dir( f):
    d = os.path.dirname( f)
    if not os.path.exists( d):
        os.makedirs( d)

if save_plot:

    f = 'postproc' + rep + '/'
    ensure_dir( f)

    def multipage( filename, format='png', dpi=300):

        figs = [plt.figure(n) for n in plt.get_fignums()]
        inc = 0
        for fig in figs:
            inc += 1
            fig.savefig(f + filename + '_' + str(inc),
                         papertype='a4', format=format, dpi=dpi)
        print('\n>>\t FIG SAVED \n')


    multipage( plot_name)

else :
    plt.show( block=False)
#
#*****************************************************************************************************
# Export data using CSV format to be opened with excell
#*****************************************************************************************************
# 

if save_xls:
    
            
    f = 'postproc' + rep + '/'
    ensure_dir( f)
    
    for j in  range(phySphere.n_cells):
        df = pd.DataFrame(vars(phySphere.cells[j].cell.record))
        fichier = "Feuillet_" + str(j) + ".xlsx"
        #print fichier
        writer = pd.ExcelWriter( f + fichier, engine='xlsxwriter')
        name = "Feuillet_" + str(j)
        df.to_excel(writer, sheet_name=name)
        writer.save()
        
        nature = phySphere.cells[j].type
        #print nature
        if nature == "stock":
            piH = np.asarray(phySphere.cells[j].cell.record.piH)
            piL = np.asarray(phySphere.cells[j].cell.record.piL)
            Exergy = ( piH-piL ) / piH
            dfEx = pd.DataFrame(Exergy)
            nameEx = "Exergy_" + str(j)
            fichierEx = nameEx + ".xlsx"
            writer = pd.ExcelWriter(f + fichierEx, engine='xlsxwriter')
            dfEx.to_excel(writer, sheet_name=nameEx)
            writer.save()

    np.savetxt(f + "Production.csv", phySphere.record.production, delimiter=";")
    np.savetxt(f + "Time.csv", phySphere.record.t, delimiter=";")
    np.savetxt(f + "Request.csv", phySphere.record.request, delimiter=";")
    np.savetxt(f + "RealEnergyMix.csv", phySphere.record.realEnergyMix, delimiter=";")
    np.savetxt(f + "RequestEnergyMix.csv", phySphere.record.requestedEnergyMix, delimiter=";")
    print('\n>>\t DATA SAVED \n')

#*******************************************************************************************
#   - add code here to plot additional graphs, using phySphere.record, phySphere.cells[i].cell.record, 
#     and ecoSphere.record (if existing)

                #   - phySphere.record contains arrays :
#           - phySphere.record.t
#           - phySphere.record.production
#           - phySphere.record.request
#           - phySphere.record.realEnergyMix
#           - phySphere.record.requestedEnergyMix

#   - phySphere.cells[i].cell.record contains arrays :
#           - if phySphere.cells[i].type == "stock" :
#                   t, Xh, Xl, Xs, Xb, piH, piL, Fhp, Flp, G, Gused, Fr, Fnr, Ip, Ipd, Ipmax, efficiency, hasStock, isLimitated, K, Rp
#           - if phySphere.cells[i].cell.type == "flow" :
#                   t, G, Gused, Xs, Xb, eff, surface_installee, stockMax, K1, K2
#
