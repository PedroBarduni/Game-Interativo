#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O RESGATE DA PRINCESA  -  Escolhas e Consequências

Aventura medieval em texto. Resgate a princesa Aurora e enfrente o
Senhor das Trevas. Tudo o que você diz e faz muda sua REPUTAÇÃO, seus
ALIADOS e o que você descobre sobre o vilão, e isso leva a 8 finais.

Como jogar:   python3 resgate_da_princesa.py
Modo rápido:  python3 resgate_da_princesa.py --rapido   (sem pausas)
Dica: digite 's' em qualquer escolha para ver a sua ficha.
"""

import random
import sys
import time

RAPIDO = "--rapido" in sys.argv
HEROI = None
TOTAL_FINAIS = 8


class FimDeJogo(Exception):
    pass


# ---------------------------------------------------------------- utilidades
def pausa(s=0.6):
    if not RAPIDO:
        time.sleep(s)


def titulo(texto):
    print("\n" + "=" * 60)
    print(texto.center(60))
    print("=" * 60)


def narrar(texto):
    print("\n" + texto)
    pausa()


def fala(quem, texto):
    print(f'\n{quem}: "{texto}"')
    pausa()


def ficha():
    h = HEROI
    nomes_itens = {
        "amuleto": "Amuleto da Luz",
        "medalhao": "Medalhão de Lyanna",
        "retrato": "Retrato de Lyanna",
    }
    nomes_aliados = {
        "lyra": "Lyra (arqueira)",
        "aurora": "Princesa Aurora",
        "prisioneiros": "Prisioneiros libertos",
    }
    itens = [nomes_itens.get(i, i) for i in sorted(h.itens)]
    aliados = [nomes_aliados.get(a, a) for a in sorted(h.aliados)
               if not (a == "lyra" and "lyra_foi" in h.marcas)]
    print("\n" + "-" * 44)
    print(f"  {h.nome}  ({h.origem})")
    print(f"  Vida: {h.vida}/{h.vida_max}   Ouro: {h.ouro}   Poções: {h.pocoes}")
    print(f"  Ataque: {h.ataque[0]}-{h.ataque[1]}   Defesa: {h.defesa}")
    print(f"  Reputação: {h.reputacao()}")
    print(f"  Itens: {', '.join(itens) if itens else 'nenhum'}")
    print(f"  Aliados: {', '.join(aliados) if aliados else 'ninguém'}")
    print("-" * 44)


def escolher(opcoes):
    """Mostra opções numeradas e devolve o número escolhido (1..n)."""
    print()
    for i, op in enumerate(opcoes, 1):
        print(f"  [{i}] {op}")
    while True:
        resp = input("\n> ").strip().lower()
        if resp in ("s", "status", "ficha") and HEROI is not None:
            ficha()
            continue
        if resp.isdigit() and 1 <= int(resp) <= len(opcoes):
            return int(resp)
        print("Opção inválida. Digite o número de uma das escolhas.")


def escolher_chave(ops):
    """ops = [(chave, texto), ...]. Devolve a chave escolhida."""
    c = escolher([t for _, t in ops])
    return ops[c - 1][0]


def menu(ops, usados):
    """Menu em que cada opção só pode ser usada uma vez."""
    disp = [(k, t) for k, t in ops if k not in usados]
    k = escolher_chave(disp)
    usados.add(k)
    return k


def pagar(h, valor):
    if h.ouro >= valor:
        h.ouro -= valor
        print(f"   (-{valor} de ouro)")
        return True
    print("   Você não tem ouro suficiente.")
    return False


def ferir(h, qtd, causa):
    h.vida -= qtd
    print(f"   💔 Você perde {qtd} PV.")
    if h.vida <= 0:
        game_over(causa)


def game_over(motivo):
    titulo("FIM DE JOGO")
    print(f"\n{motivo}")
    print("\nO reino mergulha na escuridão... mas toda lenda pode ser tentada de novo.")
    raise FimDeJogo()


def tem_lembranca(h):
    return "medalhao" in h.itens or "retrato" in h.itens


def nome_lembranca(h):
    return "o medalhão de Lyanna" if "medalhao" in h.itens else "o retrato de Lyanna"


# ------------------------------------------------------------------- herói
class Heroi:
    def __init__(self, nome):
        self.nome = nome
        self.origem = ""
        self.vida_max = 100
        self.vida = 100
        self.ataque = (8, 14)
        self.defesa = 0
        self.pocoes = 2
        self.ouro = 40
        self.honra = 0
        self.itens = set()
        self.aliados = set()
        self.pistas = set()
        self.marcas = set()

    def status(self):
        return f"{self.nome}: {self.vida}/{self.vida_max} PV | Poções: {self.pocoes}"

    def curar(self, qtd):
        antes = self.vida
        self.vida = min(self.vida_max, self.vida + qtd)
        return self.vida - antes

    def honra_mudou(self, n):
        self.honra += n
        if n > 0:
            print("   ⚖️  [Sua reputação melhorou]")
        elif n < 0:
            print("   ⚖️  [Sua reputação piorou]")

    def reputacao(self):
        if self.honra <= -4:
            return "Temido e desprezado"
        if self.honra <= -1:
            return "Duvidosa"
        if self.honra == 0:
            return "Desconhecida"
        if self.honra <= 2:
            return "Respeitada"
        if self.honra <= 5:
            return "Honrada"
        return "Lendária"


# ------------------------------------------------------------------ combate
def evento_aurora(h, defendendo):
    narrar("O Senhor das Trevas desvia o olhar de você... e aponta a mão\n"
           "sombria para AURORA!")
    c = escolher([
        "Jogar-se na frente dela para protegê-la.",
        "Gritar para Aurora se esconder atrás de uma coluna.",
        "Ignorar e continuar atacando: é a chance de ferir o feiticeiro.",
    ])
    if c == 1:
        dano = max(1, random.randint(20, 26) - h.defesa)
        if defendendo:
            dano //= 2
        h.vida -= dano
        print(f"\n🛡️  Você recebe a rajada no lugar dela e sofre {dano} de dano!")
        h.honra_mudou(1)
        h.marcas.add("aurora_protegida")
        return 0
    if c == 2:
        if random.random() < 0.5:
            narrar("Aurora mergulha atrás da coluna. A rajada estilhaça a pedra,\n"
                   "mas ela está a salvo!")
        else:
            narrar("Aurora tropeça e a rajada a atinge de raspão. Ela cai no chão,\n"
                   "pálida e imóvel!")
            h.marcas.add("aurora_ferida")
        return 0
    narrar("Você aproveita a distração e golpeia o feiticeiro. A rajada atinge\n"
           "Aurora em cheio. Ela cai sem um som.")
    h.honra_mudou(-2)
    h.marcas.add("aurora_ferida")
    return 20


def combate(h, nome, vida, dano_base, chefe=False, sombrio=False,
            atordoado=False, dano_inicial=0, furia=False):
    """Retorna 'vitoria', 'derrota', 'fuga' ou (só chefe) 'misericordia'."""
    vida_total = vida
    turno = 0
    amuleto_usado = False
    evento_feito = False

    def causar(d):
        nonlocal vida
        vida -= d
        if chefe and vida < 1:   # o chefe só cai pela escolha final
            vida = 1

    titulo(f"COMBATE: {nome}")
    if dano_inicial:
        causar(dano_inicial)
        print(f"\n⚔️  Seu golpe inicial causa {dano_inicial} de dano!")
    if atordoado:
        print(f"\n😵 {nome} está atordoado e perderá o primeiro turno!")
    if furia:
        print(f"\n😡 {nome} está FURIOSO e golpeia com mais força!")

    while True:
        turno += 1
        if chefe and vida <= vida_total * 0.3:
            return "misericordia"
        if vida <= 0:
            return "vitoria"
        defendendo = False

        print(f"\n--- Turno {turno} ---")
        print(h.status())
        print(f"{nome}: {max(vida, 0)}/{vida_total} PV")
        if chefe and turno % 4 == 3:
            print("⚠️  O ar fica pesado... uma energia sombria se acumula!")

        ops = [("atacar", "Atacar"), ("defender", "Defender"),
               ("pocao", f"Usar poção ({h.pocoes})")]
        if "amuleto" in h.itens and sombrio and not amuleto_usado:
            ops.append(("amuleto", "Erguer o Amuleto da Luz"))
        if not chefe:
            ops.append(("fugir", "Tentar fugir"))
        acao = escolher_chave(ops)

        if acao == "atacar":
            d = random.randint(*h.ataque)
            if random.random() < 0.15:
                d *= 2
                print("⚔️  GOLPE CRÍTICO!")
            causar(d)
            print(f"Você acerta {nome} e causa {d} de dano.")
        elif acao == "defender":
            defendendo = True
            print("🛡️  Você se prepara para bloquear o próximo ataque.")
        elif acao == "pocao":
            if h.pocoes > 0:
                h.pocoes -= 1
                print(f"🧪 Você bebe a poção e recupera {h.curar(40)} PV.")
            else:
                print("Você não tem poções! Perdeu o turno procurando na bolsa.")
        elif acao == "amuleto":
            amuleto_usado = True
            if "amuleto_roubado" in h.marcas:
                print("✨ O Amuleto brilha, mas queima suas mãos: ele foi roubado!")
                h.vida -= 15
                d = 30
            else:
                print("✨ O Amuleto da Luz brilha com fúria e rasga as sombras!")
                d = 45
            causar(d)
            print(f"{nome} sofre {d} de dano!")
            if h.vida <= 0:
                return "derrota"
        elif acao == "fugir":
            if random.random() < 0.5:
                print("Você consegue escapar!")
                return "fuga"
            print("Você tenta fugir, mas é cercado!")

        if vida <= 0:
            return "vitoria"

        # aliados
        if "lyra" in h.aliados and "lyra_foi" not in h.marcas:
            d = random.randint(5, 9)
            causar(d)
            print(f"🏹 Lyra dispara uma flecha certeira: {d} de dano em {nome}.")
            if vida <= 0:
                return "vitoria"

        if chefe and vida <= vida_total * 0.3:
            return "misericordia"

        # turno do inimigo
        pausa(0.5)
        if atordoado and turno == 1:
            print(f"\n{nome} cambaleia e não consegue atacar.")
            continue

        if chefe and turno == 3 and "aurora" in h.aliados and not evento_feito:
            evento_feito = True
            causar(evento_aurora(h, defendendo))
            if h.vida <= 0:
                return "derrota"
            continue

        if chefe and turno % 4 == 0:
            dano = random.randint(24, 32)
            print(f"\n🌑 {nome} conjura a RAJADA SOMBRIA!")
        else:
            dano = random.randint(dano_base - 3, dano_base + 3)
            print(f"\n{nome} ataca!")
        if furia:
            dano += 3
        dano = max(1, dano - h.defesa)
        if "prisioneiros" in h.aliados and chefe:
            dano = max(1, dano - 3)
        if defendendo:
            dano //= 2
            print("Seu bloqueio absorve metade do impacto.")
        h.vida -= dano
        print(f"Você sofre {dano} de dano.")
        if h.vida <= 0:
            return "derrota"


def lutar(h, nome, vida, dano, causa, **kw):
    r = combate(h, nome, vida, dano, **kw)
    if r == "derrota":
        game_over(causa)
    return r


# ----------------------------------------------------------------- prólogo
def prologo():
    titulo("O RESGATE DA PRINCESA")
    print("Escolhas e Consequências".center(60))
    narrar(
        "O reino de Eldoria vive dias sombrios. Há três noites, o SENHOR\n"
        "DAS TREVAS invadiu o castelo e levou a princesa Aurora para sua\n"
        "fortaleza no Monte Sombrio."
    )
    narrar(
        "Nesta aventura, o que você diz e faz tem peso: sua reputação, seus\n"
        "aliados e o que você descobre mudam o rumo da história.\n"
        "(Digite 's' em qualquer escolha para ver a sua ficha.)"
    )
    nome = input("\nQual é o nome do seu herói? ").strip() or "Sir Galahad"
    h = Heroi(nome)

    narrar("Antes de ser chamado ao castelo, quem você era?")
    c = escolher([
        "Ex-soldado da guarda real (mais resistente e respeitado)",
        "Mercenário (mais ouro e ataque, mas fama duvidosa)",
        "Estudioso das lendas antigas (sabe coisas que poucos sabem)",
    ])
    if c == 1:
        h.origem = "Ex-soldado"
        h.vida_max = h.vida = 120
        h.honra = 1
        h.marcas.add("soldado")
    elif c == 2:
        h.origem = "Mercenário"
        h.ouro += 40
        h.ataque = (10, 16)
        h.honra = -1
        h.marcas.add("mercenario")
    else:
        h.origem = "Estudioso"
        h.pocoes += 1
        h.pistas.add("malakar")
        h.marcas.add("erudito")
        narrar("Em seus livros, você já viu o nome MALAKAR ligado a um selo\n"
               "sombrio. Talvez isso seja útil. (pista descoberta)")
    return h


# ------------------------------------------------------------- ato 1: trono
def rei_conta_verdade(h):
    fala("Rei Aldric",
         "Malakar era meu irmão mais novo, mago da corte. Quando a esposa dele,\n"
         "Lyanna, morreu, ele tentou trazê-la de volta com magia proibida.\n"
         "Eu o exilei. Fiquei com o medalhão dela... e com a culpa.\n"
         "Hoje ele se faz chamar Senhor das Trevas.")
    h.pistas.add("malakar")
    narrar("[Pista descoberta: o Senhor das Trevas é Malakar, irmão do rei]")


def ato_trono(h):
    titulo("ATO 1 - O SALÃO DO TRONO")
    narrar("Você é conduzido ao salão do trono, onde o rei Aldric o aguarda,\n"
           "com o rosto marcado por noites sem dormir.")
    fala("Rei Aldric",
         f"{h.nome}... dizem que você é nossa última esperança. Minha filha\n"
         "Aurora foi levada. O que deseja saber, ou pedir, antes de partir?")
    usados = set()
    while True:
        ops = [
            ("sobre", "Perguntar quem é o Senhor das Trevas."),
            ("juramento", "Fazer um juramento ao rei."),
            ("recompensa", "Pedir pagamento adiantado."),
            ("mapa", "Pedir um mapa do reino."),
            ("orin", "Conversar com o mago real, Orin."),
        ]
        if "malakar" in h.pistas and not tem_lembranca(h) \
                and "rei_confia" not in h.marcas:
            ops.append(("medalhao", "Pedir ao rei o medalhão de Lyanna."))
        ops.append(("sair", "Partir para a missão."))
        k = menu(ops, usados)

        if k == "sobre":
            fala("Rei Aldric", "Um feiticeiro antigo e cruel. É tudo o que posso dizer.")
            narrar("O rei desvia o olhar. Há algo que ele não está contando.")
            ops2 = []
            if "erudito" in h.marcas:
                ops2.append(("confiar", "Eu conheço as lendas, majestade. O nome "
                                        "'Malakar' lhe diz algo?"))
            else:
                ops2.append(("confiar", "Majestade, confie em mim. Preciso da "
                                        "verdade para vencê-lo."))
            ops2 += [("exigir", "Diga o que sabe, ou procure outro herói!"),
                     ("recuar", "Pedir desculpas e mudar de assunto.")]
            r = escolher_chave(ops2)
            if r == "confiar":
                narrar("O rei hesita, e então suspira, vencido pela sinceridade.")
                rei_conta_verdade(h)
                h.marcas.add("rei_confia")
                h.honra_mudou(1)
            elif r == "exigir":
                narrar("O rei se ergue, ofendido, mas cede.")
                rei_conta_verdade(h)
                h.marcas.add("rei_ofendido")
                h.honra_mudou(-1)
            else:
                fala("Rei Aldric", "Compreendo. São tempos difíceis para todos.")

        elif k == "juramento":
            fala("Rei Aldric", "Então jure. O que fará com o Senhor das Trevas?")
            r = escolher_chave([
                ("vivo", "Juro trazê-lo vivo, para ser julgado."),
                ("cabeca", "Juro trazer a cabeça dele."),
                ("nada", "Não faço juramentos que talvez não possa cumprir."),
            ])
            if r == "vivo":
                h.marcas.add("promessa_vivo")
                h.honra_mudou(1)
                fala("Rei Aldric", "Misericórdia... que raro. Aceito sua palavra.")
            elif r == "cabeca":
                h.marcas.add("promessa_cabeca")
                h.ouro += 20
                fala("Rei Aldric", "Assim seja. Aqui está um adiantamento: 20 de ouro.")
            else:
                fala("Rei Aldric", "Ao menos é sincero. Isso vale algo.")

        elif k == "recompensa":
            fala("Rei Aldric", "Pagamento... antes mesmo de partir?")
            h.ouro += 30
            print("   (+30 de ouro)")
            h.honra_mudou(-1)
            narrar("Os cortesãos murmuram. O rei entrega a bolsa sem olhar para você.")

        elif k == "mapa":
            fala("Rei Aldric", "Meus cartógrafos mapearam as passagens do Monte Sombrio.")
            h.marcas.add("mapa")
            narrar("[Você recebeu um mapa. Ele mostra uma passagem secreta no esgoto "
                   "da fortaleza.]")

        elif k == "orin":
            narrar("O velho mago Orin o puxa para um canto, falando baixo.")
            fala("Orin", "A magia do Senhor das Trevas é sombria. Só a LUZ pode feri-lo\n"
                         "de verdade. Procure o eremita Elias, na Floresta Sussurrante,\n"
                         "ou o troll Grok, que guarda um amuleto na ponte.")
            h.marcas.add("dica_amuleto")
            if "malakar" in h.pistas:
                fala("Orin", "E se for mesmo Malakar... uma lembrança de Lyanna pode\n"
                             "alcançar o que resta dele. Não o enfrente às cegas.")
            if h.honra >= 1:
                h.pocoes += 1
                narrar("Orin sorri e lhe entrega uma poção. (+1 poção)")

        elif k == "medalhao":
            fala("Rei Aldric", "O medalhão de Lyanna? Por que o quer?")
            r = escolher_chave([
                ("insistir", "Insistir com respeito: acredito que ele pode salvar vidas."),
                ("roubar", "Fingir que desiste e roubar o medalhão do cofre à noite."),
                ("deixar", "Deixar para lá."),
            ])
            if r == "insistir":
                if h.honra >= 2:
                    fala("Rei Aldric", "Sua fama o precede. Leve-o... e traga-o de volta.")
                    h.itens.add("medalhao")
                    h.honra_mudou(1)
                    narrar("[Item obtido: Medalhão de Lyanna]")
                else:
                    fala("Rei Aldric", "Não conheço o bastante de você para confiar "
                                       "uma relíquia dessas.")
            elif r == "roubar":
                if random.random() < 0.55:
                    h.itens.add("medalhao")
                    h.marcas.add("furto")
                    h.honra_mudou(-2)
                    narrar("Você esgueira-se até o cofre e leva o medalhão sem ser visto.\n"
                           "[Item obtido: Medalhão de Lyanna]")
                else:
                    h.honra_mudou(-1)
                    narrar("Guardas o flagram e o espancam antes de soltá-lo.")
                    ferir(h, 15, "Os guardas reais foram implacáveis.")

        elif k == "sair":
            if "rei_confia" in h.marcas and not tem_lembranca(h):
                narrar("Quando você se vira para partir, o rei o chama de volta.")
                fala("Rei Aldric", "Leve isto. Era de Lyanna. Se restar algo do meu\n"
                                   "irmão naquele monstro, talvez isto o alcance.")
                h.itens.add("medalhao")
                narrar("[Item obtido: Medalhão de Lyanna]")
            break


# ------------------------------------------------------------ ato 2: taverna
def ato_taverna(h):
    titulo("ATO 2 - A ESTALAGEM DO JAVALI CINZENTO")
    narrar("Na última cidade antes da estrada sombria, você para na estalagem.\n"
           "O lugar está cheio de rumores e de gente com segredos.")
    usados = set()
    while True:
        ops = [
            ("bardo", "Ouvir o bardo Fenn no canto da sala."),
            ("berta", "Conversar com a taverneira, Berta."),
            ("dados", "Jogar dados com um estranho encapuzado."),
            ("lyra", "Falar com a arqueira solitária, na mesa do fundo."),
            ("mendigo", "Conversar com o mendigo à porta."),
            ("sair", "Sair da estalagem."),
        ]
        k = menu(ops, usados)

        if k == "bardo":
            narrar("Fenn, de chapéu emplumado, dedilha o alaúde com um sorriso.")
            r = escolher_chave([
                ("gratis", "Ouvir a canção do dia, de graça."),
                ("pago", "Dar 5 moedas e pedir a canção antiga, a que ninguém canta."),
            ])
            if r == "gratis":
                narrar("Ele canta sobre um herói desconhecido que salvará Eldoria.\n"
                       "É bonito, mas vago.")
            elif pagar(h, 5):
                narrar("Os olhos de Fenn ficam sérios. Ele canta a Balada do Mago que\n"
                       "Perdeu a Luz: Malakar, o mago da corte que se perdeu\n"
                       "no luto, e cuja torre ainda existe numa vila abandonada.")
                h.pistas.add("malakar")
                h.marcas.add("dica_vila")
                narrar("[Pista descoberta: Malakar e a torre na vila de Pedra Cinzenta]")

        elif k == "berta":
            fala("Berta", "O que vai ser, forasteiro?")
            r = escolher_chave([
                ("prato", "Um prato quente (5 de ouro)."),
                ("info", "Pagar 8 de ouro por notícias da região."),
                ("nada", "Só cumprimentar."),
            ])
            if r == "prato" and pagar(h, 5):
                narrar(f"A comida é farta. Você recupera {h.curar(20)} PV.")
            elif r == "info" and pagar(h, 8):
                fala("Berta", "A vila de Pedra Cinzenta foi abandonada. Dizem que um\n"
                              "mago morava lá. E soldados do Monte Sombrio vigiam o\n"
                              "portão, mas há uma passagem de esgoto atrás da cachoeira.")
                h.marcas.add("dica_vila")
                h.marcas.add("dica_esgoto")
            elif r == "nada":
                fala("Berta", "Boa sorte lá fora, forasteiro. Vai precisar.")

        elif k == "dados":
            narrar("O estranho balança os dados e sorri por baixo do capuz.")
            r = escolher_chave([
                ("apostar", "Apostar 20 de ouro, na sorte."),
                ("trapacear", "Trocar os dados por outros viciados."),
                ("recusar", "Recusar educadamente."),
            ])
            if r == "apostar" and pagar(h, 20):
                if random.random() < 0.45:
                    h.ouro += 40
                    narrar("Os dados sorriem para você! (+40 de ouro)")
                else:
                    narrar("Os dados viram contra você. O estranho ri.")
            elif r == "trapacear":
                h.honra_mudou(-1)
                if random.random() < 0.75:
                    h.ouro += 25
                    narrar("Ninguém percebe a troca. (+25 de ouro)")
                else:
                    h.ouro = max(0, h.ouro - 10)
                    narrar("O estranho agarra sua mão! Você leva um soco e perde\n"
                           "10 de ouro na confusão.")
                    ferir(h, 10, "Uma briga de taverna foi o seu fim.")

        elif k == "lyra":
            narrar("Uma arqueira de olhar afiado afia flechas: LYRA, mercenária\n"
                   "famosa na região.")
            fala("Lyra", "Procurando companhia? Não ando com qualquer um.")
            preco = 25 if h.honra >= 0 else 40
            r = escolher_chave([
                ("pagar", f"Oferecer {preco} de ouro por seus serviços."),
                ("honra", "Apelar à sua consciência: Eldoria precisa de você."),
                ("deixar", "Deixá-la em paz."),
            ])
            if r == "pagar" and pagar(h, preco):
                h.aliados.add("lyra")
                fala("Lyra", "Dinheiro é dinheiro. Estou dentro.")
            elif r == "honra":
                if h.honra >= 1:
                    h.aliados.add("lyra")
                    fala("Lyra", "Raro ouvir isso de alguém. Eu vou, e sem cobrar.")
                else:
                    fala("Lyra", "Palavras bonitas. Mas ouvi coisas sobre você que\n"
                                 "não combinam com elas.")

        elif k == "mendigo":
            narrar("Um velho mendigo estende a mão trêmula.")
            r = escolher_chave([
                ("dar", "Dar 5 moedas e um pouco de pão."),
                ("ignorar", "Ignorar."),
                ("expulsar", "Mandá-lo embora da porta."),
            ])
            if r == "dar" and pagar(h, 5):
                h.honra_mudou(1)
                fala("Mendigo", "Que a luz o acompanhe. Se encontrar um velho na floresta,\n"
                                "ajude-o: ele guarda a luz que Eldoria precisa.")
                h.marcas.add("dica_amuleto")
            elif r == "expulsar":
                h.honra_mudou(-1)
                narrar("Os fregueses param de conversar e o encaram em silêncio.")

        elif k == "sair":
            break


# ------------------------------------------------------------ ato 3: armeiro
def ato_armeiro(h):
    titulo("ATO 3 - O ARMEIRO")
    narrar("Antes de pegar a estrada, você visita a oficina do armeiro Bruno,\n"
           "um anão de barba trançada e poucas palavras.")
    mult = 1.0
    haggled = False
    comprados = set()

    def preco(base):
        return max(1, int(base * mult))

    while True:
        print(f"\n💰 Você tem {h.ouro} de ouro.")
        ops = []
        if "espada" not in comprados:
            ops.append(("espada", f"Espada de aço élfico (+ataque) - {preco(30)} ouro"))
        if "escudo" not in comprados:
            ops.append(("escudo", f"Escudo reforçado (+defesa) - {preco(25)} ouro"))
        if "cota" not in comprados:
            ops.append(("cota", f"Cota de malha (+25 vida máxima) - {preco(35)} ouro"))
        ops.append(("pocao", f"Poção de cura - {preco(12)} ouro"))
        if not haggled:
            ops.append(("regatear", "Tentar regatear os preços."))
        ops.append(("sair", "Seguir viagem."))
        k = escolher_chave(ops)

        if k == "espada" and pagar(h, preco(30)):
            comprados.add("espada")
            h.ataque = (h.ataque[0] + 4, h.ataque[1] + 6)
            narrar("A espada canta ao cortar o ar.")
        elif k == "escudo" and pagar(h, preco(25)):
            comprados.add("escudo")
            h.defesa += 4
            narrar("O escudo é pesado, mas aguentaria um dragão.")
        elif k == "cota" and pagar(h, preco(35)):
            comprados.add("cota")
            h.vida_max += 25
            h.vida += 25
            narrar("A cota de malha o deixa bem mais resistente.")
        elif k == "pocao" and pagar(h, preco(12)):
            h.pocoes += 1
            print("   (+1 poção)")
        elif k == "regatear":
            haggled = True
            if h.honra >= 1:
                mult = 0.8
                fala("Bruno", "Ouvi falar de você. Vinte por cento de desconto.")
            elif h.honra <= -1:
                mult = 1.25
                fala("Bruno", "Sua fama o precede. Os preços sobem.")
            elif random.random() < 0.5:
                mult = 0.9
                fala("Bruno", "Hmpf. Dez por cento. Só porque gostei de sua cara.")
            else:
                mult = 1.1
                fala("Bruno", "Insistiu demais. Dez por cento a mais.")
        elif k == "sair":
            break


# ------------------------------------------------------------ ato 4: estrada
def dar_amuleto(h, de_quem):
    h.itens.add("amuleto")
    narrar(f"[Item obtido: Amuleto da Luz, entregue por {de_quem}]")


def caminho_floresta(h):
    narrar("As árvores se fecham sobre você. De repente, três lobos famintos\n"
           "surgem das sombras!")
    r = lutar(h, "Lobos Famintos", 45, 8, "Os lobos foram mais rápidos que você.")
    if r == "fuga":
        narrar("Você escapa de volta à estrada, sem coragem de voltar à floresta.")
        return
    narrar("Quando o último lobo cai, você ouve um gemido: um velho eremita\n"
           "ferido, com um amuleto de luz suave brilhando no pescoço.")
    fala("Eremita Elias", "Ah... um herói. Os lobos me pegaram desprevenido...")
    ops = []
    if h.pocoes > 0:
        ops.append(("pocao", f"Dar uma poção de cura a ele ({h.pocoes} restantes)."))
    ops += [
        ("bandagem", "Cuidar dos ferimentos dele com bandagens e água."),
        ("negociar", "Perguntar sobre o amuleto antes de ajudar."),
        ("roubar", "Pegar o amuleto dele enquanto está fraco."),
        ("ignorar", "Seguir viagem sem olhar para trás."),
    ]
    r = escolher_chave(ops)
    if r == "pocao":
        h.pocoes -= 1
        h.honra_mudou(2)
        fala("Elias", "Você gastou algo valioso por mim. Então ouça: fui aprendiz do\n"
                      "mago Malakar. Ele era bom, até a dor quebrá-lo. Leve a luz.")
        h.pistas.add("malakar")
        dar_amuleto(h, "Elias")
    elif r == "bandagem":
        h.honra_mudou(1)
        fala("Elias", "Gentileza de graça... há tempos não via. Leve o amuleto,\n"
                      "ele o merece mais que eu.")
        dar_amuleto(h, "Elias")
    elif r == "negociar":
        if h.honra >= 1:
            fala("Elias", "Ao menos você é honesto. Está bem, a luz é sua.")
            dar_amuleto(h, "Elias")
        else:
            fala("Elias", "Um herói que negocia a luz? Não. Siga seu caminho.")
            h.marcas.add("eremita_recusou")
    elif r == "roubar":
        h.honra_mudou(-3)
        h.itens.add("amuleto")
        h.marcas.add("amuleto_roubado")
        narrar("Você arranca o amuleto. O velho murmura: 'A luz roubada queima\n"
               "quem a empunha.' [Item obtido: Amuleto da Luz (roubado)]")
    else:
        h.honra_mudou(-1)
        narrar("O eremita o observa partir em silêncio.")


def caminho_ponte(h):
    narrar("Uma ponte de pedra sobre um rio rasgado. No meio dela, um troll\n"
           "enorme, de braços cruzados, bloqueia a passagem.")
    fala("Grok, o troll",
         "Ninguém passa pela minha ponte sem pagar o preço... ou me\n"
         "responder uma pergunta!")
    ops = [
        ("enigma", "Aceitar o desafio: ouvir o enigma."),
        ("conversar", "Perguntar por que ele guarda a ponte."),
    ]
    if h.ouro >= 20:
        ops.append(("subornar", "Pagar 20 de ouro pela passagem."))
    ops += [("ameacar", "Ameaçar o troll."), ("lutar", "Sacar a arma e lutar.")]
    r = escolher_chave(ops)

    if r == "enigma":
        fala("Grok", "Quanto mais se tira de mim, maior eu fico. O que sou?")
        a = escolher_chave([("rio", "Um rio."), ("buraco", "Um buraco."),
                            ("sombra", "Uma sombra.")])
        if a == "buraco":
            fala("Grok", "Hah! Esperto! Pode passar, e leve isto.")
            dar_amuleto(h, "Grok")
        else:
            fala("Grok", "ERRADO!")
            troll_luta(h)
    elif r == "conversar":
        narrar("O troll pisca, surpreso. Ninguém nunca perguntou.")
        fala("Grok", "Meu rebanho foi morto por soldados do Monte Sombrio. Mas\n"
                     "antes... um mago gentil chamado Malakar curou minha esposa.\n"
                     "Ele era bom. Era.")
        h.pistas.add("malakar")
        h.honra_mudou(1)
        fala("Grok", "Você ouviu, em vez de lutar. Leve isto, e que ele encontre paz.")
        dar_amuleto(h, "Grok")
    elif r == "subornar":
        pagar(h, 20)
        fala("Grok", "Hmpf. Dinheiro fácil. Passe.")
    elif r == "ameacar":
        chance = 0.6 if ("mercenario" in h.marcas or h.ataque[1] >= 20) else 0.35
        if random.random() < chance:
            h.honra_mudou(-1)
            fala("Grok", "T-tá bom, tá bom! Passe, passe!")
        else:
            fala("Grok", "Hah! Você acha que me assusta?!")
            troll_luta(h)
    else:
        troll_luta(h)


def troll_luta(h):
    r = lutar(h, "Grok, o Troll", 70, 12, "A clava do troll pôs fim à sua jornada.")
    if r == "fuga":
        narrar("Você recua e dá a volta pelo rio, perdendo tempo.")
        return
    narrar("Grok tomba. Entre seus pertences, você encontra um amuleto brilhante.")
    h.honra_mudou(-1)
    dar_amuleto(h, "o corpo do troll")


def caminho_vila(h):
    narrar("A vila de Pedra Cinzenta está em silêncio. Portas batendo ao vento,\n"
           "cinzas na rua. No alto da colina, uma torre meio em ruínas.")
    usados = set()
    while True:
        conhecida = "dica_vila" in h.marcas or "malakar" in h.pistas
        ops = [
            ("aldeoes", "Chamar quem estiver escondido no porão da taverna."),
            ("torre", "Subir à torre do mago, como lhe disseram." if conhecida
             else "Investigar a torre em ruínas na colina."),
            ("casas", "Vasculhar as casas abandonadas atrás de suprimentos."),
            ("sair", "Seguir viagem."),
        ]
        k = menu(ops, usados)

        if k == "aldeoes":
            narrar("Do porão sobem quatro aldeões esfarrapados, liderados por\n"
                   "Dona Maren.")
            fala("Dona Maren", "Pela luz! Pensamos que eram os soldados dele...")
            r = escolher_chave([
                ("escoltar", "Escoltá-los até a estrada principal e dividir suas provisões."),
                ("saquear", "Exigir comida e ouro em troca de 'proteção'."),
                ("ignorar", "Dizer que não pode ajudar."),
            ])
            if r == "escoltar":
                h.honra_mudou(2)
                h.marcas.add("aldeoes_aliados")
                h.pocoes += 1
                fala("Dona Maren", "Nunca esqueceremos isto. Se um dia precisar de nós,\n"
                                   "estaremos no Monte Sombrio, quando ele ouvir nosso grito.")
                narrar("Ela pressiona uma poção em sua mão. (+1 poção)")
            elif r == "saquear":
                h.honra_mudou(-2)
                h.ouro += 25
                h.marcas.add("aldeoes_traidos")
                narrar("Eles entregam tudo, de olhos baixos. (+25 de ouro)")
            else:
                narrar("Eles voltam para o porão, em silêncio.")

        elif k == "torre":
            narrar("Runas brilham nas pedras da torre. No saguão, um ESPECTRO\n"
                   "GUARDIÃO ergue a cabeça.")
            if "malakar" in h.pistas:
                narrar("Você fala em voz alta: 'Malakar'. O espectro hesita, e então\n"
                       "se curva, deixando a passagem livre.")
            else:
                narrar("O espectro avança para atacar!")
                r = lutar(h, "Espectro Guardião", 50, 10,
                          "O espectro drenou o que restava de sua vida.", sombrio=True)
                if r == "fuga":
                    narrar("Você foge da torre, sem descobrir o que ela guarda.")
                    continue
            narrar("No andar de cima, um escritório empoeirado. Na escrivaninha, um\n"
                   "diário aberto e, ao lado, um RETRATO de uma mulher sorridente\n"
                   "ao lado de Malakar, jovem e feliz.")
            fala("Diário de Malakar (você lê em voz baixa)",
                 "Lyanna se foi. Ninguém me ouve. O rei me chama de louco. Se eu\n"
                 "não tiver nada, nada mais me impedirá...")
            h.pistas.add("malakar")
            if "retrato" not in h.itens and "medalhao" not in h.itens:
                h.itens.add("retrato")
                narrar("[Pista confirmada] [Item obtido: Retrato de Lyanna]")
            else:
                narrar("[Pista confirmada]")

        elif k == "casas":
            x = random.random()
            if x < 0.5:
                h.pocoes += 1
                h.ouro += 10
                narrar("Num baú escondido, você acha uma poção e algumas moedas.\n"
                       "(+1 poção, +10 de ouro)")
            elif x < 0.8:
                narrar("O assoalho cede e você cai sobre ferros enferrujados!")
                ferir(h, 10, "Você morreu num acidente tolo numa casa abandonada.")
            else:
                narrar("Nada além de poeira e memórias de uma vida interrompida.")

        elif k == "sair":
            break


def ato_estrada(h):
    titulo("ATO 4 - A ESTRADA PARA O MONTE SOMBRIO")
    narrar("A estrada se divide em três caminhos.")
    if "dica_amuleto" in h.marcas:
        narrar("Você lembra do que ouviu: a luz está com o eremita da floresta\n"
               "ou com o troll da ponte.")
    c = escolher_chave([
        ("floresta", "Floresta Sussurrante (curta, mas assombrada)."),
        ("ponte", "Ponte de Pedra do Troll (direta, mas guardada)."),
        ("vila", "Vila de Pedra Cinzenta (silenciosa demais...)."),
    ])
    if c == "floresta":
        caminho_floresta(h)
    elif c == "ponte":
        caminho_ponte(h)
    else:
        caminho_vila(h)

    narrar("Ao fim do dia, você acampa à sombra do Monte Sombrio.")
    r = escolher_chave([
        ("descansar", "Acender uma fogueira e descansar bem (recupera 25 PV)."),
        ("seguir", "Seguir adiante no escuro, sem descansar."),
    ])
    if r == "descansar":
        narrar(f"Você recupera {h.curar(25)} PV.")
    else:
        h.honra_mudou(0)
        narrar("Você segue, cansado, mas sem perder tempo.")


# --------------------------------------------------------- ato 5: fortaleza
def ato_fortaleza(h):
    titulo("ATO 5 - A FORTALEZA SOMBRIA")
    if "lyra" in h.aliados and h.honra <= -3:
        h.marcas.add("lyra_foi")
        fala("Lyra", "Eu sou mercenária, não cúmplice. O que vi você fazer... "
                     "não vou mais seguir você.")
        narrar("Lyra vira as costas e desaparece na noite.")

    narrar("A fortaleza do Senhor das Trevas se ergue negra sob um céu sem\n"
           "estrelas. Você precisa entrar.")
    ops = [
        ("portao", "Pelo portão principal (guardado)."),
        ("esgoto", "Pela passagem de esgoto."),
    ]
    if "lyra" in h.aliados and "lyra_foi" not in h.marcas:
        ops.append(("muralha", "Escalar a muralha com a ajuda de Lyra."))
    k = escolher_chave(ops)

    if k == "portao":
        narrar("Um Cavaleiro Negro, SIR DORIAN, bloqueia o portão, com a espada\n"
               "desembainhada.")
        fala("Sir Dorian", "Meia-volta, ou morra.")
        ops = [
            ("persuadir", "Apelar ao juramento de cavaleiro que ele já fez a Eldoria."),
            ("lutar", "Sacar a arma e atacar."),
        ]
        if h.ouro >= 30:
            ops.insert(1, ("subornar", "Oferecer 30 de ouro para que ele olhe para o lado."))
        if "aldeoes_aliados" in h.marcas:
            ops.insert(0, ("aldeoes", "Fazer o sinal combinado para os aldeões."))
        r = escolher_chave(ops)
        if r == "aldeoes":
            narrar("Gritos ecoam ao longe: Dona Maren e os aldeões fazem barulho\n"
                   "na floresta. Dorian corre para investigar!")
            h.honra_mudou(1)
            narrar("Você passa pelo portão, sem lutar.")
        elif r == "persuadir":
            if h.honra >= 2 or "malakar" in h.pistas:
                fala("Sir Dorian", "Eu... eu servia ao rei antes de tudo isto. "
                                   "Passe. E salve a princesa.")
                h.marcas.add("dorian_aliado")
                h.honra_mudou(1)
            else:
                fala("Sir Dorian", "Palavras vazias de alguém sem honra!")
                lutar(h, "Sir Dorian", 65, 11, "Sir Dorian o derrotou diante do portão.")
                narrar("O cavaleiro cai. Você entra pela porta destruída.")
        elif r == "subornar":
            pagar(h, 30)
            h.honra_mudou(-1)
            fala("Sir Dorian", "Eu não vi nada.")
        else:
            lutar(h, "Sir Dorian", 65, 11, "Sir Dorian o derrotou diante do portão.")
            narrar("O cavaleiro cai. Você entra pela porta destruída.")

    elif k == "esgoto":
        if "mapa" in h.marcas or "dica_esgoto" in h.marcas:
            narrar("Atrás da cachoeira, a passagem está exatamente onde indicado.\n"
                   "Você avança em silêncio e descansa um pouco.")
            narrar(f"Você recupera {h.curar(10)} PV.")
        else:
            narrar("O esgoto é um labirinto fedorento. Você se perde, e RATOS\n"
                   "GIGANTES atacam!")
            lutar(h, "Ratos Gigantes", 35, 7, "Os ratos o devoraram nas trevas.")
            if random.random() < 0.4:
                narrar("Uma mordida infecciona!")
                ferir(h, 10, "A infecção foi fatal.")
    else:
        narrar("Lyra dispara uma flecha com corda por cima da muralha.")
        chance = 0.9 if "mapa" in h.marcas else 0.7
        if random.random() < chance:
            narrar("Vocês sobem em silêncio e passam pelas sombras dos guardas.")
        else:
            narrar("Um guarda os avista!")
            lutar(h, "Guarda da Muralha", 50, 10, "O guarda da muralha o derrubou.")


def socorrer_aurora(h):
    if "aurora_ferida" not in h.marcas:
        return
    narrar("Aurora está caída, pálida, com um ferimento profundo.")
    if h.pocoes > 0:
        k = escolher_chave([
            ("dar", f"Dar uma poção a Aurora (restam {h.pocoes})."),
            ("guardar", "Guardar a poção. Ela não vai aguentar."),
        ])
        if k == "dar":
            h.pocoes -= 1
            h.marcas.discard("aurora_ferida")
            narrar("A cor volta ao rosto dela. Aurora respira fundo, viva.")
            return
        h.honra_mudou(-2)
    else:
        narrar("Você não tem nenhuma poção para dar a ela...")
    h.marcas.add("aurora_morta")
    narrar("Aurora fecha os olhos. Não os abre mais.")


def ato_masmorras(h):
    titulo("ATO 6 - AS MASMORRAS")
    narrar("Você desce às masmorras. No corredor, dezenas de prisioneiros\n"
           "estendem as mãos entre as grades, pedindo ajuda.")
    k = escolher_chave([
        ("libertar", "Libertar os prisioneiros (o barulho pode chamar os guardas)."),
        ("ignorar", "Seguir em frente. Sua prioridade é a princesa."),
    ])
    if k == "libertar":
        h.honra_mudou(1)
        h.aliados.add("prisioneiros")
        narrar("Os prisioneiros choram de alívio.")
        if random.random() < 0.45:
            narrar("O barulho das correntes atrai guardas!")
            lutar(h, "Guardas da Masmorra", 40, 9, "Os guardas o cercaram.")
    else:
        h.honra_mudou(-1)
        narrar("Os pedidos de socorro ecoam atrás de você por muito tempo.")

    narrar("Você chega à cela de Aurora, selada por uma fechadura mágica.")
    ops = [
        ("forcar", "Quebrar a fechadura à força (arriscado)."),
        ("carcereiro", "Furtar a chave do carcereiro Brutus, adormecido."),
    ]
    if "amuleto" in h.itens:
        ops.append(("amuleto", "Aproximar o Amuleto da Luz da fechadura."))
    if "lyra" in h.aliados and "lyra_foi" not in h.marcas:
        ops.append(("lyra", "Pedir a Lyra que arrombe a fechadura."))
    k = escolher_chave(ops)
    if k == "forcar":
        narrar("A magia da fechadura o repele! A porta cede.")
        ferir(h, 10, "A explosão mágica foi demais para você.")
    elif k == "carcereiro":
        if random.random() < 0.6:
            narrar("Com cuidado, você pega a chave sem acordar Brutus.")
        else:
            narrar("Brutus acorda com um rugido!")
            lutar(h, "Brutus, o Carcereiro", 55, 10, "Brutus o esmagou contra a parede.")
    elif k == "amuleto":
        if "amuleto_roubado" in h.marcas:
            narrar("A luz estoura a fechadura, mas queima sua mão.")
            ferir(h, 5, "A luz roubada o consumiu.")
        else:
            narrar("A luz dissolve a magia como névoa. A porta se abre sozinha.")
    else:
        narrar("Lyra trabalha a fechadura com ferramentas finas. Clique! "
               "A porta se abre.")

    narrar("Dentro da cela, uma jovem de olhar firme levanta-se do chão frio.")
    fala("Aurora", "Você... é real? Pensei que ninguém viria.")
    k = escolher_chave([
        ("recompensa", "Seu pai me enviou. Ele prometeu uma recompensa."),
        ("cuidado", "Vim levá-la para casa. Consegue andar? Está ferida?"),
        ("silencio", "Silêncio, princesa. Não temos tempo para conversa."),
    ])
    h.aliados.add("aurora")
    if k == "recompensa":
        h.honra_mudou(-1)
        h.marcas.add("aurora_fria")
        fala("Aurora", "Então é só isso que importa...")
        narrar("Ela o segue em silêncio gelado.")
    elif k == "cuidado":
        h.honra_mudou(1)
        h.marcas.add("aurora_confia")
        fala("Aurora", "Obrigada. Ouça: meu captor é meu tio, Malakar. Ele nunca me\n"
                       "machucou. Só queria que meu pai o olhasse nos olhos. A dor o\n"
                       "alimenta. Se alguém lembrar a ele de Lyanna...")
        h.pistas.add("malakar")
        narrar("[Pista confirmada: o Senhor das Trevas é Malakar]")
    else:
        narrar("Aurora aperta os lábios e o segue, calada.")

    narrar("Antes de subir ao salão do trono, você tem um momento de calma.")
    k = escolher_chave([
        ("descansar", "Descansar um pouco no corredor (recupera 25 PV)."),
        ("subir", "Subir logo, sem perder tempo."),
    ])
    if k == "descansar":
        if "prisioneiros" in h.aliados or random.random() > 0.3:
            narrar(f"Você recupera {h.curar(25)} PV.")
        else:
            narrar("Uma patrulha o encontra descansando!")
            lutar(h, "Patrulha Sombria", 45, 9, "A patrulha o pegou desprevenido.")


# --------------------------------------------------------------- ato final
def dialogo_chefe(h):
    d = {"res": "luta", "atordoado": False, "dano_ini": 0, "furia": False}
    narrar("As portas do salão se abrem sozinhas. No trono de obsidiana, uma\n"
           "figura envolta em sombras se levanta lentamente.")
    fala("Senhor das Trevas", "Então o rei enviou mais um peão...")
    k = escolher_chave([
        ("exigir", "Em nome de Eldoria, entregue-se! A princesa já está a salvo."),
        ("ouvir", "Ouvir o que ele tem a dizer."),
        ("surpresa", "Atacar de surpresa, sem dizer nada."),
    ])
    if k == "exigir":
        fala("Senhor das Trevas", "Que ousadia! Então venha.")
        return d
    if k == "surpresa":
        h.honra_mudou(-1)
        narrar("Você avança no escuro e acerta o feiticeiro antes que ele reaja!")
        d["dano_ini"] = 25
        return d

    # ouvir
    if "malakar" in h.pistas:
        fala("Senhor das Trevas",
             "Você sabe quem eu sou. Vejo nos seus olhos. Meu irmão, o 'bom\n"
             "rei', me expulsou por amar demais. Roubaram minha Lyanna da\n"
             "morte. E agora ele manda um herói para me matar?")
    else:
        fala("Senhor das Trevas",
             "Perguntem ao rei quem me expulsou do reino. Perguntem a ele\n"
             "o que ele guardou de mim.")
    fala("Senhor das Trevas",
         "Junte-se a mim. Eldoria será nossa e você não será mais um peão.")
    ops = []
    if "malakar" in h.pistas and tem_lembranca(h):
        ops.append(("lembranca", f"Mostrar {nome_lembranca(h)}."))
    if "malakar" in h.pistas:
        ops.append(("nome", "Chamá-lo pelo nome verdadeiro: Malakar."))
    ops += [("oferta", "Considerar a oferta dele."),
            ("lutar", "Recusar e lutar.")]
    k = escolher_chave(ops)

    if k == "lembranca":
        narrar(f"Você ergue {nome_lembranca(h)}. O feiticeiro congela.")
        if "aurora_fria" not in h.marcas:
            fala("Aurora", "Tio... por favor. Ela não iria querer isso.")
        if h.honra >= 1:
            narrar("A sombra ao redor dele tremula, e por um instante você vê o\n"
                   "homem que ele foi.")
            fala("Malakar", "Lyanna...")
            r = escolher_chave([
                ("perdoar", "Oferecer perdão e levá-lo de volta para casa."),
                ("atacar", "Aproveitar a fraqueza dele e atacar."),
            ])
            if r == "perdoar":
                d["res"] = "redimido"
            else:
                h.honra_mudou(-3)
                h.marcas.add("traicao")
                narrar("Você golpeia o homem que acabara de baixar a guarda.")
                d["atordoado"] = True
                d["dano_ini"] = 30
        else:
            fala("Senhor das Trevas",
                 "Você roubou isto de um túmulo, não foi? Alguém sem honra "
                 "não tem direito de falar o nome dela!")
            d["furia"] = True
    elif k == "nome":
        narrar("O nome ecoa pelo salão. O feiticeiro recua, como se tivesse sido\n"
               "esbofeteado.")
        d["atordoado"] = True
    elif k == "oferta":
        r = escolher_chave([
            ("aceitar", "Aceitar: ajoelhar-se diante dele."),
            ("recusar", "Recusar e lutar."),
        ])
        if r == "aceitar":
            d["res"] = "trevas"
        else:
            fala("Senhor das Trevas", "Então morra, tolo!")
    else:
        fala("Senhor das Trevas", "Então morra, tolo!")
    return d


def epilogo(h, chefe_morto):
    linhas = []
    if "lyra" in h.aliados and "lyra_foi" not in h.marcas:
        linhas.append("🏹 Lyra volta às estradas, mas deixa uma flecha cravada no "
                      "portão do castelo como lembrança.")
    if "aldeoes_aliados" in h.marcas:
        linhas.append("🏘️  Dona Maren e os aldeões reconstroem Pedra Cinzenta e "
                      "batizam a praça com o seu nome.")
    if "aldeoes_traidos" in h.marcas:
        linhas.append("🏘️  Em Pedra Cinzenta, ninguém fala o seu nome: lembram "
                      "bem do que você tirou deles.")
    if "prisioneiros" in h.aliados:
        linhas.append("⛓️  Os prisioneiros libertos espalham a sua história por "
                      "todo o reino.")
    if "dorian_aliado" in h.marcas:
        linhas.append("🛡️  Sir Dorian volta à guarda real, grato por ter "
                      "podido escolher o lado certo.")
    if "furto" in h.marcas:
        linhas.append("💎 O rei sabe que o medalhão sumiu do cofre. Ele finge "
                      "não saber quem o levou.")
    if "amuleto_roubado" in h.marcas:
        linhas.append("🕯️  As cicatrizes nas suas mãos nunca desaparecem: a luz "
                      "roubada cobrou o preço.")
    if "promessa_vivo" in h.marcas and chefe_morto:
        linhas.append("👑 O rei lembra que você jurou trazer o irmão dele vivo. "
                      "Ele agradece, mas não sorri.")
    if "promessa_cabeca" in h.marcas and not chefe_morto:
        linhas.append("👑 O rei esperava a cabeça do irmão. Suas escolhas o "
                      "deixam dividido entre a raiva e o alívio.")
    if "aurora_protegida" in h.marcas:
        linhas.append("💛 Aurora jamais esquece que você se jogou na frente "
                      "do golpe por ela.")
    if "aurora_morta" in h.marcas:
        linhas.append("🕊️  A perda de Aurora deixa uma sombra no reino que "
                      "nenhuma vitória apaga.")
    if linhas:
        print("\n--- O que aconteceu depois ---")
        for ln in linhas:
            print(f"\n{ln}")
            pausa(0.4)


def mostrar_final(num, nome, texto):
    titulo(f"FINAL {num} DE {TOTAL_FINAIS}: {nome}")
    narrar(texto)


def encerrar(h, chefe_morto):
    epilogo(h, chefe_morto)
    print(f"\nReputação final: {h.reputacao()}")
    print(f"Este foi o final em que você chegou. Existem {TOTAL_FINAIS} no total.")
    print("Jogue de novo, fazendo escolhas diferentes, para descobrir os outros!")
    print("\nObrigado por jogar! 🏰")


def final_luz(h):
    mostrar_final(1, "O PORTADOR DA LUZ",
        "Sob o brilho do Amuleto, a escuridão que consumia o feiticeiro se\n"
        "dissolve em luz dourada. O que resta é um velho cansado, que sussurra\n"
        "um nome (Lyanna) e então descansa em paz. A fortaleza desmorona em\n"
        "cinzas brilhantes.\n\n"
        f"Ao amanhecer, {h.nome} cruza os portões de Eldoria ao lado de Aurora e\n"
        "é coroado o PORTADOR DA LUZ, guardião do reino. O seu caminho de honra\n"
        "valeu cada passo.")
    encerrar(h, True)


def final_heroi(h):
    mostrar_final(2, "O HERÓI DE ELDORIA",
        "O Senhor das Trevas se desfaz em fumaça negra. A fortaleza treme e\n"
        "você corre com Aurora pelos corredores que desabam.\n\n"
        f"Ao amanhecer, {h.nome} é aclamado herói de Eldoria. Mas a história\n"
        "guardou segredos que você nunca soube...")
    encerrar(h, True)


def final_amargo(h):
    mostrar_final(3, "A VITÓRIA AMARGA",
        "O Senhor das Trevas cai, e o salão se enche de silêncio. Mas Aurora\n"
        "não se levanta mais.\n\n"
        f"{h.nome} volta a Eldoria carregando uma princesa que não respira.\n"
        "O reino comemora a queda do vilão, mas o rei só enxerga o filho que\n"
        "perdeu. Em algumas vitórias, ninguém ganha.")
    encerrar(h, True)


def final_temido(h):
    mostrar_final(4, "O HERÓI TEMIDO",
        "O vilão cai, mas o seu rastro de crueldade e ganância já o precedia.\n"
        "Em Eldoria, as portas se fecham quando você passa.\n\n"
        f"Os bardos cantam sobre {h.nome}, mas ninguém sabe dizer se o reino\n"
        "trocou um senhor das trevas por outro. Aurora o olha com desconfiança.")
    encerrar(h, True)


def final_traicao(h):
    mostrar_final(5, "O GUME DA TRAIÇÃO",
        "Você venceu, mas golpeando o homem que baixara a guarda ao ver a\n"
        "lembrança da esposa. Aurora viu tudo.\n\n"
        f"{h.nome} é coroado herói, mas ela nunca mais lhe dirige a palavra. À\n"
        "noite, você ainda vê os olhos de Malakar quando ele reconheceu o rosto\n"
        "de Lyanna, um instante antes da lâmina.")
    encerrar(h, True)


def final_redencao(h):
    mostrar_final(6, "O IRMÃO PERDIDO",
        f"Você estende a mão e Malakar, sem forças, deixa cair o cajado. As\n"
        "sombras evaporam como se nunca tivessem existido. Aurora o abraça\n"
        "chorando.\n\n"
        "Dias depois, no salão do trono, os dois irmãos se encontram. Nenhum\n"
        "deles diz nada por muito tempo. Então o rei estende o braço e Malakar\n"
        "o aperta. Eldoria ganha uma paz que nenhuma espada poderia ter dado.\n"
        f"{h.nome} é lembrado como o PACIFICADOR.")
    encerrar(h, False)


def final_sombras(h):
    mostrar_final(7, "AS SOMBRAS RETORNAM",
        "Você baixa a espada e poupa o feiticeiro. Mas faltou a ele algo que o\n"
        "tocasse e lhe devolvesse a humanidade.\n\n"
        "'Tolo misericordioso', ele murmura, antes de se desfazer em sombras.\n"
        f"{h.nome} leva Aurora para casa, e há um ano de paz. Então, numa noite\n"
        "sem lua, as torres de Eldoria escurecem de novo...")
    encerrar(h, False)


def final_trevas(h):
    mostrar_final(8, "O TRONO DAS TREVAS",
        "Você se ajoelha. O feiticeiro sorri e coloca uma coroa de obsidiana\n"
        "em sua cabeça.\n\n"
        "Aurora grita seu nome do corredor, mas você não ouve mais. Eldoria cai\n"
        f"em uma noite sem fim, e {h.nome}, o Rei das Trevas, governa ao lado\n"
        "de Malakar. Há quem diga que, em algum lugar, ainda resiste uma luz...")
    encerrar(h, False)


def ato_chefe(h):
    titulo("ATO FINAL - O SENHOR DAS TREVAS")
    if "aurora_fria" not in h.marcas:
        narrar("Antes de subir, Aurora lhe entrega um frasco restaurador que\n"
               f"guardava. Você recupera {h.curar(20)} PV.")
    else:
        narrar("Aurora o segue em silêncio. Ela não oferece nada.")

    if "amuleto" in h.itens:
        narrar("O Amuleto da Luz pulsa no seu peito.")
    if tem_lembranca(h):
        narrar(f"Você sente o peso de {nome_lembranca(h)} no bolso.")

    d = dialogo_chefe(h)
    if d["res"] == "trevas":
        return final_trevas(h)
    if d["res"] == "redimido":
        return final_redencao(h)

    r = lutar(h, "Senhor das Trevas", 130, 11,
              "O Senhor das Trevas ri enquanto a luz se apaga em seus olhos.",
              chefe=True, sombrio=True, atordoado=d["atordoado"],
              dano_inicial=d["dano_ini"], furia=d["furia"])

    desfecho = "morto"
    if r == "misericordia":
        narrar("O Senhor das Trevas cai de joelhos, sem forças. O salão fica em\n"
               "silêncio. Todos esperam o que você vai fazer.")
        k = escolher_chave([
            ("matar", "Desferir o golpe final."),
            ("poupar", "Baixar a espada e poupá-lo."),
        ])
        if k == "poupar":
            if "malakar" in h.pistas and tem_lembranca(h) and h.honra >= 1:
                desfecho = "redimido"
            else:
                desfecho = "poupado"
            if "promessa_cabeca" in h.marcas:
                h.honra_mudou(-1)
        else:
            if "promessa_vivo" in h.marcas:
                h.honra_mudou(-2)
                narrar("Você quebra o juramento feito ao rei.")
    socorrer_aurora(h)

    if desfecho == "redimido":
        return final_redencao(h)
    if desfecho == "poupado":
        return final_sombras(h)
    if "aurora_morta" in h.marcas:
        return final_amargo(h)
    if "traicao" in h.marcas:
        return final_traicao(h)
    if h.honra <= -3:
        return final_temido(h)
    if "amuleto" in h.itens and "amuleto_roubado" not in h.marcas and h.honra >= 3:
        return final_luz(h)
    return final_heroi(h)


# ------------------------------------------------------------------- jogo
def jogar():
    global HEROI
    HEROI = prologo()
    h = HEROI
    ato_trono(h)
    ato_taverna(h)
    ato_armeiro(h)
    ato_estrada(h)
    ato_fortaleza(h)
    ato_masmorras(h)
    ato_chefe(h)


def main():
    while True:
        try:
            jogar()
        except FimDeJogo:
            pass
        if input("\nJogar novamente? (s/n) ").strip().lower() != "s":
            break
    print("\nAté a próxima aventura!")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nVocê abandonou a aventura. Até a próxima!")