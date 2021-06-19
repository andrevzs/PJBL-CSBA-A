# PjBL A - Bichomon
# André Vinícius Zicka Schmidt
# Eduardo Scaburi Costa Barros
# Pedro Eduardo Galvan Moreira
from typing import TextIO
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from random import *
import sqlite3
import os.path

class Banco:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        caminhoBanco = os.path.join(BASE_DIR, "DB_Bichomon.db")
        self.conexão = sqlite3.connect(caminhoBanco)
    def recuperaDadosHistoria(self, nv):
        self.cursor = self.conexão.cursor()
        self.cursor.execute(F"SELECT * FROM Historia WHERE TIPO = {nv};")
        historia = self.cursor.fetchall()
        self.codHist = historia[0][0]
        self.Hist = historia[0][1]
        self.tipo = historia [0][2]
        return self.codHist, self.Hist, self.tipo
    def CadastraPartida(self, nome, cod):
        self.cursor = self.conexão.cursor()
        self.cursor.execute(f"INSERT INTO PARTIDA VALUES(NULL, {cod}, \"{nome}\");")
        dados = self.cursor.fetchall()
        self.conexão.commit()
        self.cursor.close()
        return print(dados)
    def recuperaListaBicho(self, cod):
        self.cursor = self.conexão.cursor()
        self.cursor.execute(f"SELECT * FROM BICHO WHERE CODHISTORIA = {cod};")
        bichos = self.cursor.fetchall()
        return bichos

class Personagem:
    def __init__(self, nome):
        self.nome = nome
        self.pontosEnergia = 175
        self.ataquemax = 40
        self.ataquemin = 20
    def atacar(self):
        self.dano = randint(self.ataquemin, self.ataquemax)
        return self.dano
    def critico(self):
        p = Personagem(self)
        self.sorte = randint(0, 10)
        print(self.sorte)
        if self.sorte < 2:
            return p.atacar() + 100
        else:
            self.vida = 3*self.sorte
            self.pontosEnergia += self.vida
    def sofreDano(self, quant):
        self.pontosEnergia -= quant
        return self.pontosEnergia

class Bicho:
    def __init__(self, *lista):
        self.codBicho = lista[0][0][0]
        self.nome = lista[0][0][2]
        self.energia = lista[0][0][3]
        self.ataqmax = lista[0][0][4]
        self.ataqmin = lista[0][0][5]
    def atacar(self):
        self.dano = randint(self.ataqmin, self.ataqmax)
        return self.dano
    def sofredano(self, quant):
        self.energia -= quant
        return self.energia

class Partida:
    def __init__(self, heroi, jornada, inimigos, ContadorBatalhas):
        self.personagem = heroi
        self.hist = jornada
        self.bichos = inimigos
        self.contador = ContadorBatalhas
    def ExecutaTurnoPartida(self, tipo):
        if tipo == "ataque":
            nome = self.personagem
            self.heroi = Personagem(nome)
            danoHeroi = self.heroi.atacar()
            self.inimigos = Bicho(self.bichos)
            danoInimigo = self.inimigos.atacar()
            vidaInimigo =self.inimigos.sofredano(danoHeroi)
            vidaHeroi = self.heroi.sofreDano(danoInimigo)

        else: pass
        return print(f"Dano dado pelo heroi {nome}: {danoHeroi}, vida: {vidaHeroi}\nDano dado pelo bichomon {self.inimigos.nome}: {danoInimigo}, vida: {vidaInimigo}")

class Bichomon(BoxLayout):
    def dificuldade_spinner(self, nv):
        self.nivel = nv
        if self.nivel == "facil":
            self.nivel = 3
        else:
            self.nivel = 4
        self.banco = Banco()
        self.texto = self.banco.recuperaDadosHistoria(self.nivel)
        self.cod = self.texto[0]
        self.historia = self.texto[1]
        self.tipo = self.texto[2]
        return self.texto
    def botão_começar(self):
        self.banco = Banco()
        self.nome = self.ids["Nome"].text
        self.bicho = self.banco.recuperaListaBicho(self.cod)
        #self.banco.CadastraPartida(self.nome, self.cod)
    def teste(self):
        self.ir = Partida(self.nome, self.historia, self.bicho, 7)
        self.ir.ExecutaTurnoPartida("ataque")

class PJBLApp(App):
    def build(self):
        return Bichomon()

App = PJBLApp()
App.run()


