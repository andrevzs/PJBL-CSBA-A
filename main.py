# PjBL A - Bichomon
# André Vinícius Zicka Schmidt
# Eduardo Scaburi Costa Barros
# Pedro Eduardo Galvan Moreira


class UtilizaBanco:
    def __init__(self, nomeB):
        self.nomeBanco          = nomeB


class Historia:
    def __init__(self, codH, txtIntro, tipo):
        self.codHistoria        = codH
        self.textoIntro         = txtIntro
        self.tipo               = tipo


class Personagem:
    def __init__(self, nome, ptsEnrg, atkMax, atkMin):
        self.nome               = nome
        self.pontosEnergia      = ptsEnrg
        self.ataqueMax          = atkMax
        self.ataqueMin          = atkMin

    def Atacar():
        pass

    def Critico():
        pass

    def SofreDano(dano):
        pass


class Bicho:
    def __init__(self, codB, nome, ptsEnrg, atkMax, atkMin):
        self.codBicho           = codB
        self.nome               = nome
        self.pontosEnergia      = ptsEnrg
        self.ataqueMax          = atkMax
        self.ataqueMin          = atkMin
    
    def Atacar(min, max):
        pass

    def SofreDano(dano):
        pass


class Partida:
    def __init__(self, char, hist, mobs, contB):
        self.personagem         = char
        self.historia           = hist
        self.bichos             = mobs
        self.contadorBatalhas   = contB
