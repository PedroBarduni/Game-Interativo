#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O RESGATE DA PRINCESA
Um jogo de aventura e escolhas em texto, no tema medieval.
Resgate a princesa e derrote o Senhor das Trevas!

Como jogar: python3 resgate_da_princesa.py
"""

import random
import sys
import time


# ---------------------------------------------------------------- utilidades
def pausa(segundos=0.7):
    time.sleep(segundos)


def titulo(texto):
    print("\n" + "=" * 56)
    print(texto.center(56))
    print("=" * 56)


def narrar(texto):
    print("\n" + texto)
    pausa()


def escolher(opcoes):
    """Mostra opções numeradas e devolve o número escolhido (1..n)."""
    print()
    for i, op in enumerate(opcoes, 1):
        print(f"  [{i}] {op}")
    while True:
        resp = input("\n> ").strip()
        if resp.isdigit() and 1 <= int(resp) <= len(opcoes):
            return int(resp)
        print("Opção inválida. Digite o número de uma das escolhas.")


# ------------------------------------------------------------------ jogador
class Heroi:
    def __init__(self, nome):
        self.nome = nome
        self.vida_max = 100
        self.vida = 100
        self.ataque = (8, 14)      # dano mínimo e máximo
        self.defesa = 0            # reduz dano recebido
        self.pocoes = 1
        self.itens = set()

    def status(self):
        return f"{self.nome}: {self.vida}/{self.vida_max} PV | Poções: {self.pocoes}"

    def curar(self, qtd):
        antes = self.vida
        self.vida = min(self.vida_max, self.vida + qtd)
        return self.vida - antes

    def esta_vivo(self):
        return self.vida > 0


# ------------------------------------------------------------------ combate
def combate(heroi, nome_inimigo, vida_inimigo, dano_inimigo, chefe=False):
    """Retorna True se o herói vencer, False se morrer ou (não-chefe) fugir sem sucesso."""
    vida_inimigo_max = vida_inimigo
    turno = 0
    amuleto_usado = False

    titulo(f"COMBATE: {nome_inimigo}")

    while heroi.esta_vivo() and vida_inimigo > 0:
        turno += 1
        defendendo = False

        print(f"\n--- Turno {turno} ---")
        print(heroi.status())
        print(f"{nome_inimigo}: {vida_inimigo}/{vida_inimigo_max} PV")

        opcoes = ["Atacar", "Defender", f"Usar poção ({heroi.pocoes})"]
        if "amuleto" in heroi.itens and chefe and not amuleto_usado:
            opcoes.append("Erguer o Amuleto da Luz")
        elif not chefe:
            opcoes.append("Tentar fugir")

        acao = escolher(opcoes)
        texto = opcoes[acao - 1]

        if texto == "Atacar":
            dano = random.randint(*heroi.ataque)
            if random.random() < 0.15:
                dano *= 2
                print("⚔️  GOLPE CRÍTICO!")
            vida_inimigo -= dano
            print(f"Você acerta {nome_inimigo} e causa {dano} de dano.")

        elif texto == "Defender":
            defendendo = True
            print("🛡️  Você se prepara para bloquear o próximo ataque.")

        elif texto.startswith("Usar poção"):
            if heroi.pocoes > 0:
                heroi.pocoes -= 1
                cura = heroi.curar(40)
                print(f"🧪 Você bebe a poção e recupera {cura} PV.")
            else:
                print("Você não tem poções! Perdeu o turno procurando na bolsa.")

        elif texto == "Erguer o Amuleto da Luz":
            amuleto_usado = True
            dano = 45
            vida_inimigo -= dano
            print("✨ O Amuleto brilha com fúria e rasga as sombras!")
            print(f"O Senhor das Trevas uiva e sofre {dano} de dano!")

        elif texto == "Tentar fugir":
            if random.random() < 0.5:
                print("Você consegue escapar!")
                return False
            print("Você tenta fugir, mas é cercado!")

        if vida_inimigo <= 0:
            break

        # ---- turno do inimigo
        pausa(0.5)
        if chefe and turno % 3 == 0:
            dano = random.randint(28, 36)
            print(f"\n🌑 {nome_inimigo} conjura a RAJADA SOMBRIA!")
        else:
            dano = random.randint(dano_inimigo - 3, dano_inimigo + 3)
            print(f"\n{nome_inimigo} ataca!")

        dano = max(1, dano - heroi.defesa)
        if defendendo:
            dano //= 2
            print("Seu bloqueio absorve metade do impacto.")
        heroi.vida -= dano
        print(f"Você sofre {dano} de dano.")

    return heroi.esta_vivo()


def game_over(motivo):
    titulo("FIM DE JOGO")
    print(f"\n{motivo}")
    print("\nO reino mergulha na escuridão... mas toda lenda pode ser tentada de novo.")
    sys.exit()


# ------------------------------------------------------------------- história
def introducao():
    titulo("O RESGATE DA PRINCESA")
    narrar(
        "O reino de Eldoria vive dias sombrios. Há três noites, o\n"
        "SENHOR DAS TREVAS invadiu o castelo e levou a princesa Aurora\n"
        "para sua fortaleza no Monte Sombrio."
    )
    narrar(
        "O rei, de joelhos no salão do trono, procura um herói corajoso\n"
        "o bastante para trazê-la de volta."
    )
    nome = input("\nQual é o nome do seu herói? ").strip() or "Sir Galahad"
    return Heroi(nome)


def ato_armeiro(h):
    titulo("ATO 1 - O ARMEIRO")
    narrar(
        f"\"{h.nome}, você aceitou a missão. Que os deuses o protejam!\"\n"
        "disse o rei. Antes de partir, você visita o armeiro real,\n"
        "que oferece UM item de sua oficina."
    )
    c = escolher([
        "Espada de aço élfico (ataque maior)",
        "Escudo de carvalho reforçado (defesa maior)",
        "Cota de malha leve + 2 poções de cura",
    ])
    if c == 1:
        h.ataque = (12, 20)
        narrar("Você empunha a espada. Ela canta ao cortar o ar.")
    elif c == 2:
        h.defesa = 4
        narrar("O escudo é pesado, mas parece capaz de aguentar um dragão.")
    else:
        h.vida_max = 120
        h.vida = 120
        h.pocoes += 2
        narrar("A cota de malha o deixa mais resistente, e você guarda as poções.")


def ato_caminho(h):
    titulo("ATO 2 - A ESTRADA PARA O MONTE SOMBRIO")
    narrar("A estrada se divide em três caminhos. Qual você segue?")
    c = escolher([
        "Floresta Sussurrante (curta, mas assombrada)",
        "Ponte de Pedra do Troll (direta, mas guardada)",
        "Vilarejo abandonado (silencioso demais...)",
    ])

    if c == 1:
        narrar("Entre as árvores, você ouve rosnados. Três lobos famintos surgem!")
        if not combate(h, "Lobos Famintos", 45, 8):
            if not h.esta_vivo():
                game_over("Os lobos foram mais rápidos que você.")
            narrar("Você foge para a estrada, ferido e sem tempo a perder.")
        else:
            narrar("Após a luta, você encontra um velho eremita ferido.")
            if escolher(["Ajudar o eremita", "Seguir viagem"]) == 1:
                h.itens.add("amuleto")
                h.curar(15)
                narrar(
                    "Agradecido, o eremita lhe entrega o AMULETO DA LUZ:\n"
                    "\"Só a luz fere quem vive nas trevas.\" (item obtido!)"
                )
            else:
                narrar("Você segue em frente. A pressa é inimiga da bondade.")

    elif c == 2:
        narrar(
            "Um troll enorme bloqueia a ponte.\n"
            "\"Passa quem responder: quanto mais se tira, mais eu cresço.\n"
            "O que sou eu?\""
        )
        r = escolher(["Um buraco", "Uma sombra", "Um rio"])
        if r == 1:
            h.itens.add("amuleto")
            narrar(
                "O troll ri alto: \"Esperto! Pode passar, e leve isto.\"\n"
                "Ele lhe dá o AMULETO DA LUZ. (item obtido!)"
            )
        else:
            narrar("\"ERRADO!\" ruge o troll, erguendo a clava.")
            if not combate(h, "Troll da Ponte", 70, 12):
                if not h.esta_vivo():
                    game_over("A clava do troll pôs fim à sua jornada.")
                narrar("Você recua e dá a volta pelo rio, perdendo tempo.")

    else:
        narrar("As casas estão vazias. Em uma delas, há um baú trancado.")
        if escolher(["Arrombar o baú", "Ignorar e seguir"]) == 1:
            if random.random() < 0.5:
                h.pocoes += 2
                narrar("Dentro há 2 poções de cura! Sorte sua.")
            else:
                dano = 15
                h.vida -= dano
                narrar(f"Era uma armadilha! Dardos o atingem: -{dano} PV.")
                if not h.esta_vivo():
                    game_over("Os dardos envenenados foram fatais.")
        else:
            narrar("Você ignora o baú e deixa o vilarejo para trás.")


def ato_fortaleza(h):
    titulo("ATO 3 - A FORTALEZA SOMBRIA")
    narrar(
        "A fortaleza do Senhor das Trevas se ergue diante de você,\n"
        "negra como carvão sob um céu sem estrelas. Há duas entradas."
    )
    c = escolher([
        "Portão principal (guardas à vista)",
        "Passagem secreta pelos esgotos",
    ])

    if c == 1:
        narrar("Um Cavaleiro Negro bloqueia o portão. Não há como evitar o duelo!")
        if not combate(h, "Cavaleiro Negro", 65, 11):
            game_over("O Cavaleiro Negro o derrotou diante do portão.")
        narrar("O cavaleiro cai. Você entra pela porta destruída.")
    else:
        narrar("O esgoto fede, mas está vazio. Você emerge perto das masmorras.")
        h.curar(10)
        narrar("Você aproveita o silêncio para descansar um pouco (+10 PV).")

    narrar("Nas masmorras, você encontra a cela da princesa Aurora!")
    narrar("Ela está presa por uma fechadura mágica. Como você abre?")
    c = escolher([
        "Quebrar a fechadura à força",
        "Procurar a chave no guarda adormecido ao lado",
    ])
    if c == 1:
        h.vida -= 10
        narrar("A magia da fechadura o repele! (-10 PV), mas a porta cede.")
        if not h.esta_vivo():
            game_over("A explosão mágica foi demais para você.")
    else:
        narrar("Com cuidado, você pega a chave sem acordar o guarda.")

    narrar(
        "\"Eu sabia que alguém viria!\" diz Aurora. \"Mas cuidado: o\n"
        "Senhor das Trevas está no salão acima. Ele sabe que você chegou.\""
    )
    h.itens.add("princesa")


def ato_chefe(h):
    titulo("ATO FINAL - O SENHOR DAS TREVAS")
    narrar(
        "As portas do salão se abrem sozinhas. No trono de obsidiana,\n"
        "uma figura envolta em sombras se levanta lentamente."
    )
    narrar("\"Então você é o herói... Que patético.\"")

    if "amuleto" in h.itens:
        narrar("O Amuleto da Luz pulsa no seu peito. Talvez haja esperança.")
    else:
        narrar("Sem nenhuma relíquia sagrada, você só conta com a sua coragem.")

    h.curar(20)
    narrar("Aurora lhe entrega um frasco restaurador antes da batalha (+20 PV).")

    if not combate(h, "Senhor das Trevas", 150, 14, chefe=True):
        game_over("O Senhor das Trevas ri enquanto a luz se apaga em seus olhos.")


def final(h):
    titulo("VITÓRIA!")
    narrar(
        "O Senhor das Trevas se desfaz em fumaça negra, e a fortaleza\n"
        "começa a ruir. Você pega Aurora pela mão e corre."
    )
    narrar("Ao amanhecer, os dois cruzam os portões de Eldoria sob aplausos.")
    if "amuleto" in h.itens:
        narrar(
            f"FINAL VERDADEIRO: {h.nome}, o Portador da Luz, é coroado\n"
            "protetor do reino. A bondade ao longo do caminho valeu a pena."
        )
    else:
        narrar(
            f"FINAL BOM: {h.nome} é aclamado herói de Eldoria, mas dizem\n"
            "que existia uma relíquia capaz de tornar a batalha mais fácil..."
        )
    print("\nObrigado por jogar! 🏰")


def main():
    heroi = introducao()
    ato_armeiro(heroi)
    ato_caminho(heroi)
    ato_fortaleza(heroi)
    ato_chefe(heroi)
    final(heroi)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nVocê abandonou a aventura. Até a próxima!")