from tkinter import *
from random import *
import msvcrt
import os

FOOD='.'
MINE='v'
BLANK=' '

ESC = chr(27)
ESTILOS={'RESET':0,'BOLD':1,'ITALICS':3,'UNDERLINE':4,'STRIKE':7}
COLORS={'BLACK':30,'RED':31,'GREEN':32,'YELLOW':33,'BLUE':34,'VIOLET':35,'CYAN':36,'WHITE':37}
BCKCOLORS={'BLACK':40,'RED':41,'GREEN':42,'YELLOW':43,'BLUE':44,'VIOLET':45,'CYAN':46,'WHITE':47}

def reset():
    print(ESC+"["+str(ESTILOS['RESET'])+";"+str(COLORS['WHITE'])+"m",end='')

def miprint(Style,Color, Bckcolor, text):
    if Bckcolor :
        print(ESC+"["+str(ESTILOS[Style])+";"+str(COLORS[Color])+";"+ str(BCKCOLORS[Bckcolor])+"m"+text,end='')
    else :
        print(ESC+"["+str(ESTILOS[Style])+";"+str(COLORS[Color])+"m"+text,end='')

def print_map(alto, ancho, Players, Strmap):

    print ('-- AGAINST ALL BOARD --'.center(ancho*2+2,'#'))
    # Impresión de los jugadores
    
    for i in range(len(Players)):
        print (Players[i].center(ancho*2+2,' '))
    
    #print (Strplayers)

    # Impresión de la primera fila
    print('  ',end='')
    for i in range (ancho):
        print ('%2s' % (str(i)), end='')
    print()

    # Impresión del mapa
    for i in range(alto):
        print('\x1b[0;37m'+'%2s' % (str(i)), end='')
        for j in range(ancho):
            if Strmap[i*ancho+j] == BLANK:
                print(Strmap[i*ancho+j],end=' ')
            elif Strmap[i*ancho+j] == FOOD:
                miprint ('BOLD','GREEN','',Strmap[i*ancho+j]+' ')
            elif Strmap[i*ancho+j] == MINE:
                miprint ('BOLD','RED', '', Strmap[i*ancho+j]+' ')
            else : # Si no es ninguno de los anteriores es porque hay un jugador
                miprint ('BOLD','BLUE','YELLOW',Strmap[i*ancho+j]+' ')
                reset()
        print('\x1b[0;37m'+ '%2s' %(str(i)))

    # Impresión de la última fila
    print('  ',end='')
    for i in range (ancho):
        print ('%2s' % (str(i)), end='')
    print()
    



def create_screen(alto, ancho, title,color,mapa):

    raiz=Tk()
    raiz.title(title)
    raiz.config(bg=color)

    miFrame=Frame(raiz)
    miFrame.pack()
    miFrame.config(bg=color)
    miFrame.config(width=ancho, height=alto)

    miMapa = Label(miFrame,text=mapa)
    miMapa.grid()
    miMapa.place(x=10,y=10)

    


    #miMapa.pack()
    

    raiz.mainloop()

def create_map(alto,ancho):
    map=[[' ' for i in range(ancho)] for j in range(alto)]
    Strmap=""

    for i in range(alto):
        for j in range(ancho):
            map[i][j]="".join(choices([FOOD,BLANK,MINE],[4,16,1],k=1)) 
        Strmap+="".join(map[i])
       
    return map, Strmap



