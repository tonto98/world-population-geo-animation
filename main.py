# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 14:42:18 2018

@author: Home
"""

from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
import xlrd
import glob
import os
from PIL import Image


# otvaranje excela s podacima o emigrantima
workbook = xlrd.open_workbook('Eurostat_Table.xls')
worksheet = workbook.sheet_by_name('Sheet0')

# otvaranje datoteke s lat i lon vrijednosti o državi
datotekaLonLat = open('pozicije.txt', 'r')
pozicije = datotekaLonLat.readlines()

# polje u koje cemo zapisivati broj stanovnika po godinama i lat i lon vrijednosti
podaci = []

# varijable za određivanje granica broja stanovnika
minimum = float('Inf')
maksimum = float(0)

k = 0

# iteriranje po redovima excela (gledaju se samo stupci s podacima koji nas zanimaju)  (drzave)
for i in range(6, 52):
    red = []
    # iteriranje po stupcima excela (godine)
    for j in np.arange(1, 24, 2):
        # ako nema definirane vrijednosti zapisi ':'
        if(worksheet.cell(i,j).value == ':'):
            red.append(':')
        # min i max, zapisi u polje float vrijednost za odredjenu godinu
        else:
            red.append(worksheet.cell(i,j).value)
            if worksheet.cell(i,j).value < minimum:
               minimum = worksheet.cell(i,j).value
            if worksheet.cell(i,j).value > maksimum:
               maksimum = worksheet.cell(i,j).value    
    # iteriranje kroz txt, usporedjivanje kada drzava iz excela i txt-a  ima isto ime
    for linija in pozicije:
        linija = linija.strip('\n')
        linija = linija.split('\t')
        if worksheet.cell(i, 0).value == linija[3]:
           # prvih 12 stupaca su podaci o emigrantima, predzadnji i zadnji lat i lon
            red.append(float(linija[1]))
            red.append(float(linija[2]))
            continue

    podaci.append(red)


# geometrijska razdioba za 'buckete' s brojem stanovnika, na pocetku su manji, s povecanjem broja stanovnika se sirina povecava
bucketEmigranti = np.geomspace(minimum, maksimum+1, 20)

# pocetne vrijednosti za sirinu markera i boju
markerBrojEmigranata = 1.0
bojaMarkera = 'crimson'

# iteriranje po godinama
for j in range(3):
    # crtanje mape za svaku godinu zbog problema s plt.figure()
    m = Basemap(width=12000000,height=9000000,projection='lcc',
                resolution='l',lat_0=55., lon_0=10., lat_1=0, lat_2=-35)
    m.drawcountries()
    m.drawmapboundary(fill_color='aquamarine')
    m.fillcontinents(color='limegreen',lake_color='aquamarine')    
    
    # iteriranje po polju podaci gdje su informacije o drzavama (redovi)
    for i in range(len(podaci)):
        lat, lon = podaci[i][12], podaci[i][13]
        # skaliranje lon i lat u koordinate na plotu
        xpt,ypt = m(lon,lat)
        # lonpt, latpt = m(xpt,ypt,inverse=True)  
        
        # odredjivanje u kojem je 'bucketu' trenutni podatak, po tome skaliramo velicinu markera
        for k in range(len(bucketEmigranti)-1):
            if podaci[i][j] == ':':
                bojaMarkera = 'gray'
                markerBrojEmigranata = 1
            elif podaci[i][j] > bucketEmigranti[k] and podaci[i][j] < bucketEmigranti[k+1]:
                bojaMarkera = 'crimson'
                markerBrojEmigranata = (k + 1) * 1.
        
        # crtanje tocaka na karti
        m.plot(xpt, ypt, c=bojaMarkera, marker='o', ms=markerBrojEmigranata, alpha=0.8)
    
    plt.title('Broj emigranata ' + str(j+2004) + '. godine')
    plt.savefig('mapa' + str(j+2004) + '.png')
    plt.cla()
    plt.clf()
    plt.close()

# prazno polje u koje spremamo ranije generirane slike
imgList = []

# pretrazivanje lokalne mape po nastavku
for filename in glob.iglob(os.path.join('*.png')):
    img = Image.open(filename)
    imgList.append(img)

from matplotlib import animation

fig = plt.figure()
im = plt.imshow(imgList[0], cmap=plt.get_cmap('jet'), vmin=0, vmax=255)

# function to update figure
def updatefig(j):
    # set the data in the axesimage object
    im.set_array(imgList[j])
    # return the artists set
    return [im]
# kick off the animation
anim = animation.FuncAnimation(fig, updatefig, frames=range(40), 
                              interval=300, blit=True)

plt.show()


#Writer = animation.writers['ffmpeg']
#writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
