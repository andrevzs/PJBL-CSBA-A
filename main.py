# PjBL A - Bichomon
# André Vinícius Zicka Schmidt
# Eduardo Scaburi Costa Barros
# Pedro Eduardo Galvan Moreira
from typing import TextIO
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
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
        return self.codHist, self.Hist
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
        return print(bichos)


class Bichomon(BoxLayout):
    def dificuldade(self, nv):
        self.nivel = nv
        if self.nivel == "facil":
            self.nivel = 3
        else:
            self.nivel = 4
        self.banco = Banco()
        self.texto = self.banco.recuperaDadosHistoria(self.nivel)
        self.cod = self.texto[0]
        self.historia = self.texto[1]
        return self.texto
    def partida(self):
        self.banco = Banco()
        self.nome = self.ids["Nome"].text
        self.banco.recuperaListaBicho(self.cod)
        self.banco.CadastraPartida(self.nome, self.cod)
        self.ids['hist'].text = f"{self.nome} {self.historia}"
        
class PJBLApp(App):
    def build(self):
        return Bichomon()

App = PJBLApp()
App.run()

