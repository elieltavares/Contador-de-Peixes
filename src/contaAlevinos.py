#!/usr/bin/python
# -*- coding: utf-8 -*-
#
"""
=============================================
Conta Alevinos
=============================================

Protótipo bastante simplificado de um contador de alevinos
de Pintado Real passando por uma determinada região. O sistema
erra bastante pois envolve técnicas muito básicas. O objetivo
é ter um código inicial a partir do qual versões mais
sofisticadas e funcionais possam ser criadas

Autor: Hemerson Pistori (pistori@ucdb.br)

"""

import Tkinter, tkMessageBox
import numpy as np
import cv2

# Valores mínimos e máximos definidos manualmente para
# serem utilizados na limiarização no espaço BGR
minCor = (50,49,52)
maxCor = (67,61,70)

# Tamanho mínimo e máximos (com valores extremos pois
# ainda não estão sendo usados para valer)
minTamanho = 1
maxTamanho = 20000000

# Distância em relação ao centro anterior (se o centro anterior do alevino
# estiver a uma distância menor que esta, considera-se que trata-se
# do mesmo peixe)
erroDistancia = 6

# Abre um vídeo real gravado na fazendo do Projeto Pacu
video = cv2.VideoCapture('../data/pintado_real_crop.avi')

# Carrega o banner com as logos do Projeto Pacu, UCDB e IFMS
banner = cv2.imread('../data/banner.png')

# Lê o primeiro quadro/frame do vídeo
ret, quadro = video.read()

# Pega as dimensões do quadro
altura, largura, canais = quadro.shape

# Define qual a linha será utilizada como "linha de chegada". Quando
# os alevinos passam por esta linha é que são contados
lin = altura - 40

# Contador de alevinos que vai sendo incrementado
totalAlevinos = 0

# Desenha uma janela retângular ao redor da linha de chegada
janelaChegada = (0, lin - 1, largura - 1, lin + 1)

# Guarda os valores dos centros dos alevinos encontrados no
# quadro anterior. Como apenas uma linha é analisada, basta
# guardar a coordenada y do centro
ultimosCentros = []

# Apenas para parar depois de mostrar o primeiro quadro
primeiroQuadro = True
root = Tkinter.Tk()
root.withdraw()


# Dentro deste laço serão lidos todos os quadros do vídeo
while (ret == True):

    linha = quadro[lin:lin+1,0:largura]  # Pega a linha de chegada
    linhaMaisGrossa  = cv2.resize(linha, (largura, 100))  # Engrossa em 100 vezes a linha para permitir
                            # uma melhor visualização e também a aplicações de morfologia matemática e
                            # detecção de contornos

    linhaSegmentada = cv2.inRange(linhaMaisGrossa, minCor, maxCor ) # Limiarização no espaço BGR
    nucleo = np.ones((3,3),np.uint8)    # Núcleo para a operação morfológica
    linhaFiltrada = cv2.dilate(linhaSegmentada,nucleo,iterations = 2)
    linhaFiltrada = cv2.erode(linhaFiltrada,nucleo,iterations = 2)
    cv2.imshow('Linha Filtrada',linhaFiltrada)

    # Detecta os contornos (na linha ampliada)
    linhaContornos, contornos, hierarquia = cv2.findContours(linhaFiltrada,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    #print 'Encontrou %d contornos -------------' % len(contornos)

    novosCentros = []
    for contorno in contornos:
        momentos = cv2.moments(contorno)

        tamanho = momentos['m00']

        if momentos['m00'] > 0:   # Nunca deveria ser 0, mas está ocorrendo com colunas de tamanho 1
            posicao = int(momentos['m10']/momentos['m00'])

        #print 'tamanho = %d' % tamanho
        #print 'posicao = %d' % posicao

        # A linha abaixo está sem efeito pois os valores mínimos e máximos são extremos. Tem que melhor isso.
        if tamanho > minTamanho and tamanho < maxTamanho:

            jaContou = False

            # Verificando se no quadro anterior tinha algum centro próximo
            for posicaoAnterior in ultimosCentros:
                if abs(posicaoAnterior-posicao) < erroDistancia:
                    jaContou = True

            # Se já não foi contado no quadro anterior, conta e guarda o centro
            if not jaContou:
                totalAlevinos += 1
                novosCentros = novosCentros + [posicao]

    ultimosCentros = novosCentros

    # Mostra a linha de chegada e o texto com a contagem
    quadroResultado = cv2.rectangle(quadro,janelaChegada[0:2],janelaChegada[2:4],(20,200,20),1)
    quadroResultado = cv2.putText(quadroResultado,'Contagem = '+str(totalAlevinos),(largura/2-50,lin+30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,100,250),2)

    # Mostra o vídeo e as janelas com resultados intermediários
    cv2.imshow('Projeto Pacu', banner)
    cv2.imshow('Entrada', quadroResultado)
    cv2.imshow('Linha',linhaMaisGrossa)
    cv2.imshow('Linha Segmentada',linhaSegmentada)

    # Ajusta as posições das janelas para não ficar uma em cima da outra
    cv2.moveWindow('Projeto Pacu', 100,50)
    cv2.moveWindow('Entrada', 100, 178)
    cv2.moveWindow('Linha',470,178)
    cv2.moveWindow('Linha Segmentada',470, 305)
    cv2.moveWindow('Linha Filtrada',470, 437)


    # Mostra o vídeo em câmera lenta. Se teclar 'ESC' sai do programa
    k = cv2.waitKey(200) & 0xff
    if( k == 27):
        break
    elif (k == 32):
        k = cv2.waitKey() & 0xff

    ret, quadro = video.read()

    if primeiroQuadro == True:
        cv2.waitKey(2000) # Espera mais um pouco para dar tempo de desenhar todas as janelas
        tkMessageBox.showinfo("Contador de Alevinos", "Posso iniciar a contagem ?")
        primeiroQuadro = False


cv2.waitKey(2000) # Espera mais um pouco para dar tempo de desenhar todas as janelas
tkMessageBox.showinfo("Contador de Alevinos", 'Contei %d alevinos. Posso sair ?' % totalAlevinos)

cv2.destroyAllWindows()
video.release()
