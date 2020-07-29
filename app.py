import cv2
import numpy as np
from time import sleep
from constantes import *


def pega_centro(x, y, largura, altura):
    """
    :param x: x do objeto
    :param y: y do objeto
    :param largura: largura do objeto
    :param altura: altura do objeto
    :return: tupla que contém as coordenadas do centro de um objeto
    """
    x1 = largura // 2
    y1 = altura // 2
    cx = x + x1
    cy = y + y1
    return cx, cy


def set_info(detec):
    global carros
    for (x, y) in detec:
        if (pos_linha + offset) > y > (pos_linha - offset):
            carros += 1
            cv2.line(frame1, (25, pos_linha), (1200, pos_linha), (0, 127, 255), 3)
            detec.remove((x, y))
            print("Porcos detectados até o momento: " + str(carros))


def show_info(frame1, dilatada):
    #text = f'Porco: {carros}'
    #cv2.putText(frame1, text, (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
    cv2.imshow("Video Original", frame1)
    cv2.imshow("Detectar", dilatada)

def media_posicao(pos1,pos2):
    # montar app para media
   return pos1 + pos2 / 2

carros = caminhoes = 0
cap = cv2.VideoCapture('Porco.mp4') # [frame1, frame2, frame_n]
subtracao = cv2.createBackgroundSubtractorMOG2()  # Pega o fundo e subtrai do que está se movendo
pepino = 0
cont = 0

while True:
    pepino = pepino+1
    cont = cont+1
    ret, frame1 = cap.read()  # Pega cada frame do vídeo
    tempo = float(1 / 0.05)
    frame1 = cv2.resize(frame1,(720,480),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
    sleep(0.0000001)  # Dá um delay entre cada processamento
    grey = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)  # Pega o frame e transforma para preto e branco
    blur = cv2.GaussianBlur(grey, (5, 5), 5)  # Faz um blur para tentar remover as imperfeições da imagem
    img_sub = subtracao.apply(blur)  # Faz a subtração da imagem aplicada no blur
    dilat = cv2.dilate(img_sub, np.ones((5, 5)))  # "Engrossa" o que sobrou da subtração
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (
        5, 5))  # Cria uma matriz 5x5, em que o formato da matriz entre 0 e 1 forma uma elipse dentro
    dilatada = cv2.morphologyEx(dilat, cv2.MORPH_CLOSE, kernel)  # Tenta preencher todos os "buracos" da imagem
    dilatada = cv2.morphologyEx(dilatada, cv2.MORPH_CLOSE, kernel)
    dilatada = cv2.threshold(dilatada, 250, 255, cv2.THRESH_BINARY)[1]
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 30))
    dilatada = cv2.morphologyEx(dilatada, cv2.MORPH_CLOSE, rect_kernel)

    contorno, img = cv2.findContours(dilatada, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.line(frame1, (25, pos_linha), (1200, pos_linha), (255, 127, 0), 3)
    '''for (i, c) in enumerate(contorno):
        (x, y, w, h) = cv2.boundingRect(c)
        validar_contorno = (w >= largura_min) and (h >= altura_min)
        if not validar_contorno:
            continue
        hull = cv2.convexHull(i)
        cv2.drawContours(frame1, [hull], i, (0,255,0), 3)
        print("Posição do porco: ",(x, y), (x + w, y + h) )
        cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
        centro = pega_centro(x, y, w, h)
        detec.append(centro)
        cv2.circle(frame1, centro, 4, (0, 0, 255), -1)

    set_info(detec)'''

    for cnt in contorno:
        (x, y, w, h) = cv2.boundingRect(cnt)
        validar_contorno = (w >= largura_min) and (h >= altura_min)
        if not validar_contorno:
            continue
        # get convex hull
        hull = cv2.convexHull(cnt)

    ## (1) Crop the bounding rect
    x,y,w,h = cv2.boundingRect(hull)
    croped = frame1[y:y+h, x:x+w].copy()

    ## (2) make mask
    contorno = np.array(hull)
    contorno = contorno - contorno.min(axis=0)

    mask = np.zeros(croped.shape[:2], np.uint8)
    cv2.drawContours(mask, [contorno], -1, (255, 255, 255), -1, cv2.LINE_AA)

    ## (3) do bit-op
    dst = cv2.bitwise_and(croped, croped, mask=mask)

    if cont == 8:
        cont = 0
        cv2.imwrite('porco/{}.png'.format(pepino),dst)


    cv2.drawContours(frame1, [hull], -1, (0, 0, 255), 1)


    show_info(frame1, dilatada)

    if cv2.waitKey(1) == 27:
        break
cv2.destroyAllWindows()
cap.release()
