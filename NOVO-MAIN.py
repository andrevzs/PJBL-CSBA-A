# PjBL A - Bichomon
# André Vinícius Zicka Schmidt
# Eduardo Scaburi Costa Barros
# Pedro Eduardo Galvan Moreira
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
        self.cursor = self.conexão.cursor()
    def recuperaDadosHistoria(self, nv):
        self.cursor.execute(F"SELECT * FROM Historia WHERE TIPO = {nv};")
        historia = self.cursor.fetchall()
        self.codHist = historia[0][0]
        self.Hist = historia[0][1]
        self.tipo = historia [0][2]
        return self.codHist, self.Hist, self.tipo
    def CadastraPartida(self, nome, cod):
        self.cursor.execute(f"INSERT INTO PARTIDA VALUES(NULL, {cod}, \"{nome}\");")
        self.cursor.execute("SELECT COUNT(codPartida) FROM PARTIDA")
        dados = self.cursor.fetchall()
        self.conexão.commit()
        self.cursor.close()
        return print(dados[0][0])
    def recuperaListaBicho(self, cod):
        self.cursor.execute(f"SELECT * FROM BICHO WHERE CODHISTORIA = {cod};")
        bichos = self.cursor.fetchall()
        return bichos
    def infoPersonagem(self, dano):
        self.cursor.execute(f"SELECT vida FROM Personagem;")
        self.vidaAtual = self.cursor.fetchall()
        self.novaVida = self.vidaAtual[0][0] - dano
        self.cursor.execute(f"UPDATE Personagem SET vida = {self.novaVida};") 
        self.conexão.commit()
        self.cursor.close() 
        return self.novaVida
    def danoBichos(self, cod, dano):
        self.cursor.execute(f"SELECT pontosEnergia FROM BICHO WHERE codBicho = {cod};")
        self.vidaAtual = self.cursor.fetchall()
        self.novaVida = self.vidaAtual[0][0] - dano
        self.cursor.execute(f"UPDATE BICHO SET pontosEnergia = {self.novaVida} WHERE codBicho = {cod};") 
        self.conexão.commit()
        self.cursor.close() 
        return self.novaVida
    def VoltarVidas(self):
        self.cursor.execute("UPDATE BICHO SET pontosEnergia = 80 WHERE CODHISTORIA = 1;")
        self.cursor.execute("UPDATE BICHO SET pontosEnergia = 150 WHERE CODHISTORIA = 2;")
        self.cursor.execute("UPDATE Personagem SET VIDA = 175;")
        self.conexão.commit()
    def quantInimigos(self, nv):
        self.cursor.execute(f"SELECT COUNT (pontosEnergia) FROM BICHO WHERE codHistoria = {nv} AND pontosEnergia > 0;")
        self.quant = self.cursor.fetchall()
        return self.quant

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
        print("sorteio:", self.sorte)
        if self.sorte < 2:
            return p.atacar() + 100, "dano"
        else:
            self.vida = 3*self.sorte
            return self.vida, "cura"
    def sofreDano(self, quant):
        self.banco = Banco()
        self.pontosEnergia = self.banco.infoPersonagem(quant) 
        return self.pontosEnergia

class Bicho:
    def __init__(self, num, *lista):
        self.codBicho = lista[0][num][0]
        self.nome = lista[0][num][2]
        self.energia = lista[0][num][3]
        self.ataqmax = lista[0][num][4]
        self.ataqmin = lista[0][num][5]
    def atacar(self):
        self.dano = randint(self.ataqmin, self.ataqmax)
        return self.dano
    def sofredano(self, quant):
        self.banco = Banco()
        self.energia = self.banco.danoBichos(self.codBicho, quant) 
        return self.energia

class Partida:
    def __init__(self, heroi, jornada, inimigos, ContadorBatalhas):
        self.personagem = heroi
        self.hist = jornada
        self.bichos = inimigos
        self.contador = ContadorBatalhas
    def ExecutaTurnoPartida(self, tipo):
        self.banco = Banco()
        nome = self.personagem
        self.heroi = Personagem(nome)
        self.ordem = self.banco.quantInimigos(self.bichos[0][1])
        print(self.ordem[0][0])
        self.ordem = 5 - self.ordem[0][0]
        if self.ordem == 5:
            return print("todos os bichomons já foram derrotados")
        print(self.ordem)
        self.inimigos = Bicho(self.ordem, self.bichos)
        if tipo == "ataque":
            danoHeroi = self.heroi.atacar()
            danoInimigo = self.inimigos.atacar()
            vidaInimigo =self.inimigos.sofredano(danoHeroi)
            vidaHeroi = self.heroi.sofreDano(danoInimigo)
            if vidaHeroi <= 0:
                return print(f"{nome} morreu após sofrer {danoInimigo} de dano de {self.inimigos.nome}")
            if vidaInimigo <= 0:
                return print(f"{self.inimigos.nome} morreu após sofrer {danoHeroi} de dano de {nome}" ) 
            return print(f"Dano dado pelo heroi {nome}: {danoHeroi}, vida: {vidaHeroi}\nDano dado pelo bichomon {self.inimigos.nome}: {danoInimigo}, vida: {vidaInimigo}")
        else: 
            self.result = self.heroi.critico()
            if self.result[1] == "dano":
                self.danoHeroi = self.result[0]
                self.danoInimigo = self.inimigos.atacar()
                vidaInimigo =self.inimigos.sofredano(self.danoHeroi)
                vidaHeroi = self.heroi.sofreDano(self.danoInimigo)
                if vidaHeroi <= 0:
                    return print(f"{nome} morreu após sofrer {self.danoInimigo} de dano de {self.inimigos.nome}")
                if vidaInimigo <= 0:
                    return print(f"{self.inimigos.nome} morreu após sofrer {self.danoHeroi} de dano critico de {nome}" ) 
                else:
                    return print(f"Dano critico dado pelo heroi {nome}: {self.danoHeroi}, vida: {vidaHeroi}\nDano dado pelo bichomon {self.inimigos.nome}: {self.danoInimigo}, vida: {vidaInimigo}")
            else: 
                self.cura = self.heroi.sofreDano(int(-self.result[0]))
                self.danoInimigo = self.inimigos.atacar()
                vidaHeroi = self.heroi.sofreDano(self.danoInimigo)
                if vidaHeroi <= 0:
                    return print(f"{nome} morreu após sofrer {self.danoInimigo} de dano de {self.inimigos.nome}")
                else:
                    return print(f"{self.result[0]} de vida regenerada pelo heroi {nome}, vida: {vidaHeroi}\nDano dado pelo bichomon {self.inimigos.nome}: {self.danoInimigo}, o bichomon nao levou dano")
    

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
        self.banco.VoltarVidas()
        self.nome = self.ids["Nome"].text
        self.bicho = self.banco.recuperaListaBicho(self.cod)
        self.cont = self.banco.CadastraPartida(self.nome, self.cod)
        self.ids["hist"].text= self.historia
        self.ids["inicio-texto"].text = ''
        self.ids['aliado'].text = self.nome
        self.ids['inimigo'].text = ''
    def ataque(self):
        self.ir = Partida(self.nome, self.historia, self.bicho, self.cont)
        self.ir.ExecutaTurnoPartida("ataque")
    def sorte(self):
        self.ir = Partida(self.nome, self.historia, self.bicho, self.cont)
        self.ir.ExecutaTurnoPartida("sorte")
class PJBLApp(App):
    def build(self):
        return Bichomon()

App = PJBLApp()
App.run()
