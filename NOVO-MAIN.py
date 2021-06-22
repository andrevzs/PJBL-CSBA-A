# PjBL A - Bichomon
# André Vinícius Zicka Schmidt
# Eduardo Scaburi Costa Barros
# Pedro Eduardo Galvan Moreira
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from random import *
import sqlite3
import os.path

class Banco:#Serve para pegar todas as informações que a gente vai precisar do banco
    def __init__(self):#Essa parte é para se conectar ao banco e para deixar pronto o cursor para nao precisar ficar repetindo as mesmas linhas de codifo nas outras linhas
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        caminhoBanco = os.path.join(BASE_DIR, "DB_Bichomon.db")
        self.conexão = sqlite3.connect(caminhoBanco)
        self.cursor = self.conexão.cursor()
    def recuperaDadosHistoria(self, nv):
        self.cursor.execute(F"SELECT * FROM Historia WHERE TIPO = {nv};") #Procura todas as informações da tabela historia que tem relação ao nivel escolhido
        historia = self.cursor.fetchall()#salva
        return historia
    def CadastraPartida(self, nome, cod):
        self.cursor.execute(f"INSERT INTO PARTIDA VALUES(NULL, {cod}, \"{nome}\");")#Cadastra a partida adicionando o nome do heroi e a dificuldade
        self.cursor.execute("SELECT COUNT(codPartida) FROM PARTIDA")
        dados = self.cursor.fetchall()
        self.conexão.commit()
        self.cursor.close()

    def recuperaListaBicho(self, cod):
        if cod == 5 or cod == 6:
            cod = 1
        if cod == 4 or cod == 3 or cod == 7:
            cod = 2
        self.cursor.execute(f"SELECT * FROM BICHO WHERE CODHISTORIA = {cod};")
        bichos = self.cursor.fetchall()#Recupera a lista de bichos de acordo com a dificuldade
        return bichos
    def infoPersonagem(self, dano):#Isso serve para modificar a vida do personagem
        self.cursor = self.conexão.cursor()
        self.cursor.execute(f"SELECT vida FROM Personagem;")#seleciona a vida do personagem
        self.vidaAtual = self.cursor.fetchall()#salva
        self.novaVida = self.vidaAtual[0][0] - dano#diminui
        self.cursor.execute(f"UPDATE Personagem SET vida = {self.novaVida};") #atualiza
        self.conexão.commit()#salva na base de dados
        self.cursor.close() 
        return self.novaVida
    def danoBichos(self, cod, dano):#mesma coisa que o personagem
        self.cursor.execute(f"SELECT pontosEnergia FROM BICHO WHERE codBicho = {cod};")
        self.vidaAtual = self.cursor.fetchall()
        self.novaVida = self.vidaAtual[0][0] - dano
        self.cursor.execute(f"UPDATE BICHO SET pontosEnergia = {self.novaVida} WHERE codBicho = {cod};") 
        self.conexão.commit()
        self.cursor.close() 
        return self.novaVida
    def VoltarVidas(self):#Quando clica no botão começar, as vidas voltam para o padrão inicial
        self.cursor.execute("UPDATE BICHO SET pontosEnergia = 80 WHERE CODHISTORIA = 1;")
        self.cursor.execute("UPDATE BICHO SET pontosEnergia = 150 WHERE CODHISTORIA = 2;")
        self.cursor.execute("UPDATE Personagem SET VIDA = 175;")
        self.conexão.commit()
    def quantInimigos(self, nv):#Vê quantos bichos faltam, é util para o ciclo de bichos 
        self.cursor.execute(f"SELECT COUNT (pontosEnergia) FROM BICHO WHERE codHistoria = {nv} AND pontosEnergia > 0;")
        self.quant = self.cursor.fetchall()
        return self.quant

class Personagem:
    def __init__(self, nome):
        self.banco = Banco()
        self.nome = nome
        self.pontosEnergia = 175
        self.ataquemax = 40
        self.ataquemin = 20
    def atacar(self):
        self.dano = randint(self.ataquemin, self.ataquemax)#escolhe um valor entre o ataque maximo e o ataque minimo
        return self.dano
    def critico(self):
        p = Personagem(self)
        self.sorte = randint(0, 10)#faz o sorteio de que numero vai cair
        print("sorteio:", self.sorte)
        if self.sorte < 2:
            return p.atacar() + 100, "dano" #caiu menos de dois então a função de dano do personagem é chamada e depois é adicionado mais 100, o "dano" serve para identidicar no turno que tipo de ação ocorreu
        else:
            self.vida = 3*self.sorte #caiu mais de dois então vai multiplicar por 3 o valor e vai somar na vida
            return self.vida, "cura"#aqui tambem serve para ser mais facil de identificar que tipo de ação ocorreu
    def sofreDano(self, quant):
        self.pontosEnergia = self.banco.infoPersonagem(quant)#Diminui a vida do personagem
        return self.pontosEnergia

class Bicho:
    def __init__(self, num, *lista):#lista de bichos da dificuldade e num para saber em que bicho q tá, é ai que entra a parte da classe banco "quantInimigos", vai dar para entender melhor na classe partida
        self.codBicho = lista[0][num][0]
        self.nome = lista[0][num][2]
        self.energia = lista[0][num][3] #posição de cada componente na lista
        self.ataqmax = lista[0][num][4]
        self.ataqmin = lista[0][num][5]
    def atacar(self):
        self.dano = randint(self.ataqmin, self.ataqmax) #mesma coisa com o personagem
        return self.dano
    def sofredano(self, quant):
        self.banco = Banco()
        self.energia = self.banco.danoBichos(self.codBicho, quant) #mesma coisa com o personagem
        return self.energia

class Partida:
    def __init__(self, heroi, jornada, inimigos, ContadorBatalhas):
        self.personagem = heroi
        self.hist = jornada
        self.bichos = inimigos
        self.contador = ContadorBatalhas
    def ExecutaTurnoPartida(self, tipo):
        self.banco = Banco() #Chama a função banco
        self.nome = self.personagem#Pega o nome do personagem
        self.heroi = Personagem(self.nome)#Chama a função personagem
        self.ordem = self.banco.quantInimigos(self.bichos[0][1])#VÊ quantos bichos ainda estão vivos
        self.ordem = 5 - self.ordem[0][0] # Se 5 estão vivos então essa variavel vai armazenar 0, 0 é o primeiro bicho da dificuldade
        if self.ordem == 5:#ve se todos estão mortos 
            return print("todos os bichomons já foram derrotados")
        print(self.ordem)
        self.inimigos = Bicho(self.ordem, self.bichos)#passa o numero do bicho e a lista de bichos
        if tipo == "ataque":#clicou no botão de ataque
            self.danoHeroi = self.heroi.atacar()#chama a função de atacar e salva ela numa variavel
            self.danoInimigo = self.inimigos.atacar()#mesma coisa
            self.vidaInimigo =self.inimigos.sofredano(self.danoHeroi)#diminui a vida do bicho
            self.vidaHeroi = self.heroi.sofreDano(self.danoInimigo)#mesma coisa
            if self.vidaHeroi <= 0:
                return print(f"{self.nome} morreu após sofrer {self.danoInimigo} de dano de {self.inimigos.nome}")
            if self.vidaInimigo <= 0:
                return print(f"{self.inimigos.nome} morreu após sofrer {self.danoHeroi} de dano de {self.nome}" ) 
            return print(f"Dano dado pelo heroi {self.nome}: {self.danoHeroi}, vida: {self.vidaHeroi}\nDano dado pelo bichomon {self.inimigos.nome}: {self.danoInimigo}, vida: {self.vidaInimigo}")
        else: #quer dizer que clicou  no botão da sorte
            self.result = self.heroi.critico()#chama a função
            if self.result[1] == "dano":#ai que entra aquela string
                self.danoHeroi = self.result[0]#para chamar so o numero, não a string 
                self.danoInimigo = self.inimigos.atacar()#aqui para baixo é a mesma coisa que o ataque
                self.vidaInimigo =self.inimigos.sofredano(self.danoHeroi)
                self.vidaHeroi = self.heroi.sofreDano(self.danoInimigo)
                if self.vidaHeroi <= 0:
                    return print(f"{self.nome} morreu após sofrer {self.danoInimigo} de dano de {self.inimigos.nome}")
                if self.vidaInimigo <= 0:
                    return print(f"{self.inimigos.nome} morreu após sofrer {self.danoHeroi} de dano critico de {self.nome}" ) 
                else:
                    return print(f"Dano critico dado pelo heroi {self.nome}: {self.danoHeroi}, vida: {self.vidaHeroi}\nDano dado pelo bichomon {self.inimigos.nome}: {self.danoInimigo}, vida: {self.vidaInimigo}")
            else: #vai se curar
                self.cura = self.heroi.sofreDano(int(-self.result[0]))#menos para somar ao inves de subtrair
                if self.cura > 175:
                    self.cura = 175
                self.danoInimigo = self.inimigos.atacar()#o personagem leva dano mesmo se curando
                self.vidaHeroi = self.heroi.sofreDano(self.danoInimigo)
                if self.vidaHeroi <= 0:
                    return print(f"{self.nome} morreu após sofrer {self.danoInimigo} de dano de {self.inimigos.nome}")
                else:
                    return print(f"{self.result[0]} de vida regenerada pelo heroi {self.nome}, vida: {self.vidaHeroi}\nDano dado pelo bichomon {self.inimigos.nome}: {self.danoInimigo}, o bichomon nao levou dano")
    
class Historia:
    def __init__(self, *list):
        sorteio = randint(0, 1)
        print("Sorteio lista=", sorteio)
        self.cod = list[0][sorteio][0]
        self.intro = list[0][sorteio][1]
        self.difi = list[0][sorteio][2]
    def exibeIntro(self, nome):
        print(self.intro)
        self.intro = self.intro.replace("[personagem]", nome)
        return self.cod, self.intro , self.difi
class Bichomon(BoxLayout):
    def dificuldade_spinner(self, nv):
        self.nivel = nv
        if self.nivel == "facil":
            self.nivel = 3
        else:
            self.nivel = 4
    def botão_começar(self):
        self.banco = Banco()
        self.banco.VoltarVidas()
        self.nome = self.ids["Nome"].text
        self.banco = Banco()
        self.texto = self.banco.recuperaDadosHistoria(self.nivel)
        self.historia = Historia(self.texto).exibeIntro(self.nome)

        self.cod = self.historia[0]
        self.intro = self.historia[1]
        self.tipo = self.historia[2]

        if self.nome == '' or self.tipo == '':
            self.ids["hist"].text = "Erro, você não digitou seu nome e/ou esqueceu de selecionar a dificuldade"
            return
        else:pass
        self.bicho = self.banco.recuperaListaBicho(self.cod)
        self.cont = self.banco.CadastraPartida(self.nome, self.cod)
        self.ir = Partida(self.nome, self.historia, self.bicho, self.cont)
        self.ids["hist"].text= self.intro
        self.ids["inicio-texto"].text = ''
        self.ids['aliado'].text = f"Heroi:\nNome:{self.nome}\nVida: 175\nDano: 40-20"
        self.ids['inimigo'].text = "Bichomon:\nNome:???????\nVida:????????\nDano:????????????????"
    def ataque(self):
        self.ir.ExecutaTurnoPartida("ataque")
    def sorte(self):
        self.ir.ExecutaTurnoPartida("sorte")
    def info(self):
        self.vervida = Personagem(self.nome)
        try:
            self.ids['aliado'].text = f"Heroi:\nNome:{self.nome}\nVida: {self.ir.vidaHeroi}\nDano:{self.ir.danoHeroi}"
            self.ids['inimigo'].text = f"Bichomon:\nNome:{self.ir.inimigos.nome}\nVida:{self.ir.vidaInimigo}\nDano:{self.ir.danoInimigo}"
        except AttributeError:
            self.ids['aliado'].text = f"Heroi:\nNome:{self.nome}\nVida: {self.ir.vidaHeroi}\nDano: 0"
            self.ids['inimigo'].text = f"Bichomon:\nNome:{self.ir.inimigos.nome}\nVida:????????\nDano:{self.ir.danoInimigo}"
        if self.ir.vidaHeroi < 0:
            self.ids['aliado'].text = ''
            self.ids['inimigo'].text = ''
            self.ids['inicio-texto'].text = "É uma pena, você perdeu"
        if self.ir.ordem == 5:
            self.ids['aliado'].text = ''
            self.ids['inimigo'].text = ''
            self.ids['inicio-texto'].text = "Parabens, Você venceu!"

    
class PJBLApp(App):
    def build(self):
        return Bichomon()

App = PJBLApp()
App.run()
