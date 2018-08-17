import numpy as np
import struct
import random as rand
import math
from tkinter import *

#Создаем популяцию
def createPopulation(min, max, size):
    return np.random.sample(size)* (max - min) + min

#Считаем производную
def res(popup):
    y = np.cos(popup)+popup/3
    #y = np.around(y, 4)
    return y

#Сортировка массивов для удобства элитарной селекции
def sort(popup, fit, ord):
    for i in range(fit.size):
        for j in range(fit.size-1):
            if(fit[j]<fit[j+1] and ord) or(fit[j]>fit[j+1] and (not ord)):
                buf = fit[j+1]
                fit[j + 1] = fit[j]
                fit[j] = buf
                buf = popup[j+1]
                popup[j + 1] = popup[j]
                popup[j] = buf
    return popup, fit

def calcFitness(y):
    fit = y
    if fit.min() <= 0:
        m = fit.min()
        fit = fit-m+0.1
    fit = fit/fit.max()
    return fit

#Функции переупаковки из float в int и обратно, для возможности реализации скрещивания побитовыми операциясм
def floatToBin(num):
    return struct.unpack('I', struct.pack("f", num))[0]

def binToFloat(num):
    return struct.unpack('f', struct.pack('I', int(num)))[0]

def arrBinToFloat(popup):
    newPopup = (np.zeros(popup.size)).astype(float)
    for i in range(popup.size):
        newPopup[i] = binToFloat(popup[i])
    return  newPopup

#Сумма  приспособленности (при полном массиве всегда 1, иное, если уже выбран один родителя и удален из массива)
def calcSumFitness(fit):
    sum = 0
    for f in fit:
        sum+=f
    return sum

#Выбираем родителя на основании их приспособленности
#fit - вероятности, par1 - индеск первого родителя. Если первый родитель не выбран, то = -1
def getParent(fit, par1):
    fitBuf = fit
    if(par1 != -1):
        fitBuf = np.delete(fitBuf, par1)
    sumFit = calcSumFitness(fit)
    pr = rand.random()*sumFit
    sumPr = 0
    i = 0
    for ver in fitBuf:
        sumPr += ver
        if(pr < sumPr):
            if(par1 != -1 & par1 <= i):
                i+=1
            return  i
        i+=1
    return  0


def mutation(popup, numMut, min, max):
    i = 0
    for i in range(numMut):
        st = rand.randint(2, 28)
        mut = pow(2, st)
        num = rand.randint(0, popup.size-1)
        try:
            popup[num] = popup[num]^mut
            test = binToFloat(popup[num])
            if test > max:
                popup[num] = floatToBin(max)
            if test < min:
                popup[num] = floatToBin(min)
        except OverflowError:
            print("Результат слишком велик для типа данных")

    return popup

#Скрещивание
def cross(popup, fit):
    newPopup = np.arange(popup.size, dtype =  np.uint32)
    for i in range(popup.size):
        parent1 = getParent(fit, -1)
        parent2 = getParent(fit, parent1)
        parent1 = floatToBin(popup[parent1])
        parent2 = floatToBin(popup[parent2])
        child = (parent1&4294901760)|(parent2&65535)
        newPopup[i] = child
    return newPopup

def selection(popup, newPopup, ord, min, max):
    allPopup = np.union1d(popup, newPopup)
    d = res(allPopup)
    fit = calcFitness(d)
    allPopup, fit = sort(allPopup, fit, ord)
    return allPopup[0:popup.size]

def createDots(popup, res, fit):
    list = []
    for i in range(popup.size):
        x = popup[i]*50+500
        y = 250-res[i]*50
        color = '#%02x%02x%02x' % (int((1-fit[i])*255), int(fit[i]*255), 0)

        list.append(canv.create_oval(x-5, y-5, x+5, y+5, fill=color))
    return list

def redrDots(dots, popup, res, fit):
    for i in range(popup.size):
        x = popup[i]*50+500
        y = 250 -res[i]*50
        canv.coords(dots[i], x-5, y-5, x+5, y+5)
        color = '#%02x%02x%02x' % (int((1-fit[i])*255), int(fit[i]*255), 0)
        canv.itemconfig(dots[i], fill=color)


def GA(popup, kMut, max, min, d, ord):
    global j
    global n
    y = res(popup)
    fit = calcFitness(y)
    redrDots(d, popup, y, fit)
    newPopup = cross(popup, fit)
    newPopup = mutation(newPopup, kMut, min, max)

    newPopup = arrBinToFloat(newPopup)
    population = selection(popup, newPopup, ord, min, max)

    #Если популяция стабилизируется, то продвигаемся к выходу из рекурсии
    if n == population.mean():
       j+=300
    n = population.mean()

    if j < 1000:
        j +=1
        root.after(5, GA, population, kMut, max, min, d, ord)
    else:

        print("end")
        print(round(population[0], 7))
        return


def mainFunc(min, max, sizePopulation, kMut, ord):
    canv.create_line(min*50+500, 0, min*50+500, 500, width=0.5, fill='blue')
    canv.create_line(max*50+500, 0, max*50+500, 500, width=0.5, fill='blue')
    population = createPopulation(min, max, sizePopulation)
    y = res(population)
    fit = calcFitness(y)
    dots = createDots(population, y, fit)
    numElit = int(sizePopulation/3)
    elit = population[0: numElit]
    GA(population, kMut, max, min, dots, ord)

j=0
n = 0

root = Tk()
canv = Canvas(root, width = 1000, height = 500, bg = "white")
canv.create_line(500, 500,500,0,width=2,arrow=LAST)
canv.create_line(0,250,1000,250,width=2,arrow=LAST)
First_x = -500
for i in range(32000):
    if (i % 800 == 0):
        k = First_x + (1 / 16) * i
        canv.create_line(k + 500, -3 + 250, k + 500, 3 + 250, width = 0.5, fill = 'black')
        canv.create_text(k + 515, -10 + 250, text = str(i/800-10), fill="purple", font=("Helvectica", "10"))
        if (5-i/800 != 0):
            canv.create_line(-3 + 500, k + 500, 3 + 500, k + 500, width = 0.5, fill = 'black')
            canv.create_text(20 + 500, k + 500, text = str(5-i/800), fill="purple", font=("Helvectica", "10"))
    try:
        x = -10 + (1 / 640) * i
        y =math.cos(x) + x/3
        x= x*50+500
        y =250 - y * 50
        canv.create_oval(x, y, x + 1, y + 1, fill = 'black')
    except:
        pass
canv.pack()
root.after(500, mainFunc, -2*math.pi+1.2344, 2*math.pi+1.234,  75, 25, False)
root.mainloop()
