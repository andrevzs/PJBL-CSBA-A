# PjBL A - Bichomon
# André Vinícius Zicka Schmidt
# Eduardo Scaburi Costa Barros
# Pedro Eduardo Galvan Moreira
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from random import *
import sqlite3
import os.path


# Classe responsavel pelas interacoes essenciais com o banco de dados
class Banco:
    def __init__(self):  
        # Se conecta ao banco de dados e deixa o cursor pronto
        BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
        caminhoBanco    = os.path.join(BASE_DIR, "DB_Bichomon.db")
        self.conexão    = sqlite3.connect(caminhoBanco)
        self.cursor     = self.conexão.cursor()

    # Procura as informacoes da tabela Historia relacionadas ao nivel escolhido
    def recuperaDadosHistoria(self, nv):
        self.cursor.execute(F"SELECT * FROM Historia WHERE TIPO = {nv};")
        
        # Salva
        historia = self.cursor.fetchall()
        return historia

    # Adiciona o nome do heroi e a dificuldade
    def CadastraPartida(self, nome, cod):
        self.cursor.execute(f"INSERT INTO PARTIDA VALUES(NULL, {cod}, \"{nome}\");")
        self.cursor.execute("SELECT COUNT(codPartida) FROM PARTIDA")
        dados = self.cursor.fetchall()
        
        # Salva
        self.conexão.commit()
        self.cursor.close()

    # Acessa a lista de bichos de acordo com a dificuldade
    def recuperaListaBicho(self, cod):
        if cod == 5 or cod == 6 or cod == 9 or cod == 10:
            cod = 1
        else:
            cod = 2
        self.cursor.execute(f"SELECT * FROM BICHO WHERE CODHISTORIA = {cod};")
        
        bichos = self.cursor.fetchall()
        return bichos

    # Modifica a vida do personagem
    def infoPersonagem(self, dano):
        self.cursor    = self.conexão.cursor()
        # Seleciona a vida do personagem
        self.cursor.execute(f"SELECT vida FROM Personagem;")
        # Salva
        self.vidaAtual = self.cursor.fetchall()
        # Diminui
        self.novaVida  = self.vidaAtual[0][0] - dano
        # Atualiza
        self.cursor.execute(f"UPDATE Personagem SET vida = {self.novaVida};")
        
        self.conexão.commit()
        self.cursor.close() 
        return self.novaVida

    # Funciona igual infoPersonagem
    def danoBichos(self, cod, dano):
        self.cursor.execute(f"SELECT pontosEnergia FROM BICHO WHERE codBicho = {cod};")
        self.vidaAtual = self.cursor.fetchall()
        self.novaVida  = self.vidaAtual[0][0] - dano
        self.cursor.execute(f"UPDATE BICHO SET pontosEnergia = {self.novaVida} WHERE codBicho = {cod};") 
        
        self.conexão.commit()
        self.cursor.close() 
        return self.novaVida
    
    # Devolve os valores padrao das vidas
    def VoltarVidas(self):
        self.cursor.execute("UPDATE BICHO SET pontosEnergia = 80 WHERE CODHISTORIA = 1;")
        self.cursor.execute("UPDATE BICHO SET pontosEnergia = 150 WHERE CODHISTORIA = 2;")
        self.cursor.execute("UPDATE Personagem SET VIDA = 175;")
        
        self.conexão.commit()

    # Determina quantos bichos faltam, util para o ciclo
    def quantInimigos(self, nv):
        self.cursor.execute(f"SELECT COUNT (pontosEnergia) FROM BICHO WHERE codHistoria = {nv} AND pontosEnergia > 0;")
        self.quant = self.cursor.fetchall()
        return self.quant


# Classe responsavel pelo funcionamento do personagem do usuario
class Personagem:
    def __init__(self, nome):
        self.banco          = Banco()
        self.nome           = nome
        self.pontosEnergia  = 175
        self.ataquemax      = 40
        self.ataquemin      = 20
    
    def atacar(self):
        # Sorteia um valor aleatorio entre o max e o min de ataque
        self.dano = randint(self.ataquemin, self.ataquemax)
        return self.dano

    def critico(self):
        p = Personagem(self)
        # Sorteia o numero
        self.sorte = randint(0, 10)
        print("sorteio:", self.sorte)
        
        if self.sorte < 2:
            # Adiciona 100 no dano, a string ajuda na identificacao
            return p.atacar() + 100, "dano"
        else:
            # Multiplica o valor por 3 e soma na vida
            self.vida = 3*self.sorte
            return self.vida, "cura"  # Facilita a identificacao da acao
    
    def sofreDano(self, quant):
        # Diminui a vida do personagem
        self.pontosEnergia = self.banco.infoPersonagem(quant)
        return self.pontosEnergia


# Classe responsavel pelo funcionamento do bicho no duelo
class Bicho:
    def __init__(self, num, *lista):
        # Lista de bichos da dificuldade selecionada
        # Num usado para saber a posicao na lista
        self.codBicho   = lista[0][num][0]
        self.nome       = lista[0][num][2]
        self.energia    = lista[0][num][3]
        self.ataqmax    = lista[0][num][4]
        self.ataqmin    = lista[0][num][5]
    
    def atacar(self):
        self.dano = randint(self.ataqmin, self.ataqmax)
        return self.dano
    
    def sofredano(self, quant):
        self.banco   = Banco()
        self.energia = self.banco.danoBichos(self.codBicho, quant)
        return self.energia


# Classe responsavel pelo gerenciamento da partida
class Partida:
    def __init__(self, heroi, jornada, inimigos, ContadorBatalhas):
        self.personagem = heroi
        self.hist       = jornada
        self.bichos     = inimigos
        self.contador   = ContadorBatalhas

    def ExecutaTurnoPartida(self, tipo):
        self.banco  = Banco()
        self.nome   = self.personagem 
        self.heroi  = Personagem(self.nome)
        # Confere quantos bichos ainda estao vivos
        self.ordem  = self.banco.quantInimigos(self.bichos[0][1])
        # Ordena os bichos
        self.ordem  = 5 - self.ordem[0][0]
        
        # Confere se todos bichos estao mortos
        if self.ordem == 5:
            return print("Todos os bichomon já foram derrotados!")
        
        print(self.ordem)
        # Passa o numero do bicho e a lista deles
        self.inimigos = Bicho(self.ordem, self.bichos)
        
        if tipo == "ataque":  # Atacou
            self.danoHeroi = self.heroi.atacar()
            self.danoInimigo = self.inimigos.atacar()
            self.vidaInimigo =self.inimigos.sofredano(self.danoHeroi)
            self.vidaHeroi = self.heroi.sofreDano(self.danoInimigo)
            
            if self.vidaHeroi <= 0:
                return print(f"{self.nome} morreu após sofrer {self.danoInimigo} de dano por {self.inimigos.nome}")
            if self.vidaInimigo <= 0:
                return print(f"{self.inimigos.nome} morreu após sofrer {self.danoHeroi} de dano por {self.nome}" ) 
            
            return print(f"""Dano dado pelo heroi {self.nome}: {self.danoHeroi}, 
            vida: {self.vidaHeroi}\n
            Dano dado pelo bichomon {self.inimigos.nome}: {self.danoInimigo}, 
            vida: {self.vidaInimigo}""")
        
        else:  # Tentou a sorte
            self.result = self.heroi.critico()
            if self.result[1] == "dano":  # Aqui que entra aquela string
                self.danoHeroi   = self.result[0]  # Pra chamar so o numero
                self.danoInimigo = self.inimigos.atacar()
                self.vidaInimigo = self.inimigos.sofredano(self.danoHeroi)
                self.vidaHeroi   = self.heroi.sofreDano(self.danoInimigo)
                
                if self.vidaHeroi <= 0:
                    return print(f"{self.nome} morreu após sofrer {self.danoInimigo} de dano por {self.inimigos.nome}")
                if self.vidaInimigo <= 0:
                    return print(f"{self.inimigos.nome} morreu após sofrer {self.danoHeroi} de dano critico por {self.nome}" )
                else:
                    return print(f"""Dano critico dado pelo heroi {self.nome}: {self.danoHeroi}, 
                    vida: {self.vidaHeroi}\n
                    Dano dado pelo bichomon {self.inimigos.nome}: {self.danoInimigo}, 
                    vida: {self.vidaInimigo}""")
            
            else: # Vai se curar
                self.cura = self.heroi.sofreDano(int(-self.result[0]))#menos para somar ao inves de subtrair
                if self.cura > 175:
                    self.cura = 175

                self.danoInimigo = self.inimigos.atacar()#o personagem leva dano mesmo se curando
                self.vidaHeroi   = self.heroi.sofreDano(self.danoInimigo)

                if self.vidaHeroi <= 0:
                    return print(f"{self.nome} morreu após sofrer {self.danoInimigo} de dano de {self.inimigos.nome}")
                else:
                    return print(f"""{self.result[0]} de vida regenerada pelo heroi {self.nome}, 
                    vida: {self.vidaHeroi}\n
                    Dano dado pelo bichomon {self.inimigos.nome}: {self.danoInimigo}, o bichomon nao levou dano""")


# Sorteio e exibicao da historia
class Historia:
    def __init__(self, *list):
        sorteio     = randint(0, 4)
        self.cod    = list[0][sorteio][0]
        self.intro  = list[0][sorteio][1]
        self.difi   = list[0][sorteio][2]
    
    def exibeIntro(self, nome):
        self.intro = self.intro.replace("[personagem]", nome)
        return self.cod, self.intro , self.difi


# Montagem da estrutura em Kivy
class Bichomon(BoxLayout):
    def dificuldade_spinner(self, nv):
        self.nivel = nv
        if self.nivel == "facil":
            self.nivel  = 3
        else:
            self.nivel  = 4

    def botão_começar(self):
        self.banco      = Banco()
        self.banco.VoltarVidas()
        self.nome       = self.ids["Nome"].text
        self.banco      = Banco()
        try:
            self.texto = self.banco.recuperaDadosHistoria(self.nivel)
            self.historia = Historia(self.texto).exibeIntro(self.nome)
        except AttributeError:
            self.ids["hist"].text="Escolha a dificuldade"
            return

        self.cod = self.historia[0]
        self.intro = self.historia[1]
        self.tipo = self.historia[2]

        if self.nome == '':
            self.ids["hist"].text = "Erro, você não digitou seu nome"
            return
        else:pass
        
        self.bicho  = self.banco.recuperaListaBicho(self.cod)
        self.cont   = self.banco.CadastraPartida(self.nome, self.cod)
        self.ir     = Partida(self.nome, self.historia, self.bicho, self.cont)
        
        self.ids["hist"].text= self.intro
        self.ids["inicio-texto"].text = ''
        self.ids['aliado'].text       = f"Heroi:\nNome:{self.nome}\nVida: 175\nDano: 40-20"
        self.ids['inimigo'].text      = "Bichomon:\nNome:???????\nVida:???????\nDano:???????"

    def ataque(self):
        self.ir.ExecutaTurnoPartida("ataque")
    
    def sorte(self):
        self.ir.ExecutaTurnoPartida("sorte")
    
    def info(self):
        self.vervida = Personagem(self.nome)
        try:
            self.ids['aliado'].text         = f"Heroi:\nNome:{self.nome}\nVida: {self.ir.vidaHeroi}\nDano:{self.ir.danoHeroi}"
            self.ids['inimigo'].text        = f"Bichomon:\nNome:{self.ir.inimigos.nome}\nVida:{self.ir.vidaInimigo}\nDano:{self.ir.danoInimigo}"
        
        except AttributeError:
            self.ids['aliado'].text         = f"Heroi:\nNome:{self.nome}\nVida: {self.ir.vidaHeroi}\nDano: 0"
            self.ids['inimigo'].text        = f"Bichomon:\nNome:{self.ir.inimigos.nome}\nVida:???????\nDano:{self.ir.danoInimigo}"
        
        if self.ir.vidaHeroi < 0:
            self.ids['aliado'].text         = ''
            self.ids['inimigo'].text        = ''
            self.ids['inicio-texto'].text   = "É uma pena, você perdeu"
            self.ids["Ataque"].disabled = True
            self.ids['sorte'].disabled = True
        
        if self.ir.ordem == 5:
            self.ids['aliado'].text         = ''
            self.ids['inimigo'].text        = ''
            self.ids['inicio-texto'].text   = "Parabens, Você venceu!"
            self.ids["Ataque"].disabled = True
            self.ids['sorte'].disabled = True
    
class PJBLApp(App):
    def build(self):
        return Bichomon()

App = PJBLApp()
App.run()
