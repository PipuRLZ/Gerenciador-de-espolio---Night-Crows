import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random
import shutil
import urllib.request
from datetime import datetime

ARQUIVO_DADOS = 'dados_cruzada.json'
ARQUIVO_TERRITORIOS = 'territorios.json'
ARQUIVO_HISTORICO = 'historico.json'
ARQUIVO_CONFIG = 'config.json'
PASTA_BACKUPS = 'backups_cruzada'
LIMITE_ELEGIVEL = 30_000_000  # valor de bid a partir do qual o jogador vira elegível ao sorteio

JOGADORES_INICIAIS = [
    {"nome": "Tokuki", "equipe": "A"}, {"nome": "Alcamax", "equipe": "A"}, {"nome": "Hajden", "equipe": "A"},
    {"nome": "Xizord", "equipe": "A"}, {"nome": "Sheyla97", "equipe": "A"}, {"nome": "Thaufa", "equipe": "A"},
    {"nome": "Wraths", "equipe": "A"}, {"nome": "cdo", "equipe": "A"}, {"nome": "Kaely", "equipe": "A"},
    {"nome": "magrovei", "equipe": "A"}, {"nome": "PipuRLZ", "equipe": "A"}, {"nome": "MidnightLady", "equipe": "A"},
    {"nome": "N99 • BL4KZ", "equipe": "A"}, {"nome": "ATHENA武", "equipe": "A"}, {"nome": "Thauf4s", "equipe": "A"},
    {"nome": "Alkamax", "equipe": "A"}, {"nome": "MtDoiido", "equipe": "A"}, {"nome": "ShadowCroww", "equipe": "A"},
    {"nome": "ZK丶Smith", "equipe": "A"}, {"nome": "くそAkm", "equipe": "A"},
    {"nome": "secovei", "equipe": "B"}, {"nome": "AmandaRR", "equipe": "B"}, {"nome": "Feek", "equipe": "B"},
    {"nome": "tatãoxd", "equipe": "B"}, {"nome": "nos4a2", "equipe": "B"}, {"nome": "MasterSá", "equipe": "B"},
    {"nome": "MagodoBad", "equipe": "B"}, {"nome": "Guerra07", "equipe": "B"}, {"nome": "ByClevaツ", "equipe": "B"},
    {"nome": "FOOOFINHA", "equipe": "B"}, {"nome": "愛RicoSurf", "equipe": "B"}, {"nome": "LndYnk", "equipe": "B"},
    {"nome": "EduElfoPower", "equipe": "B"}, {"nome": "LITRAÇODE4", "equipe": "B"}, {"nome": "robinUllr", "equipe": "B"},
    {"nome": "Gumaシ", "equipe": "B"}, {"nome": "MERTONOMO", "equipe": "B"}, {"nome": "Fizz", "equipe": "B"},
    {"nome": "zumbakura", "equipe": "B"}, {"nome": "Joy", "equipe": "B"},
    {"nome": "Colgate", "equipe": "Reserva"}
]

TERRITORIOS_PADRAO = {
    "A": {"nome": "Território 1", "morions": "200", "diamantes": "1096", "moedas": "100000", "ouro": "100"},
    "B": {"nome": "Território 2", "morions": "200", "diamantes": "1096", "moedas": "100000", "ouro": "100"},
}


# ---------------------------------------------------------------------------
# Funções "puras" (sem Tkinter) — ficam fora da classe de propósito, para
# poderem ser testadas isoladamente e para separar a lógica de negócio da
# interface gráfica.
# ---------------------------------------------------------------------------

def parse_valor(val_str):
    """Converte texto de bid ('30m', '32.5m', '1.500.000', '500k') para inteiro.

    O sufixo (m/k) é separado ANTES de tratar pontos/vírgulas, então '32.5m'
    vira corretamente 32.500.000 (e não 325.000.000)."""
    if not val_str:
        return 0

    val = str(val_str).lower().strip()
    if not val:
        return 0

    try:
        sufixo = None
        if val.endswith('m') or val.endswith('k'):
            sufixo = val[-1]
            val = val[:-1]

        if ',' in val and '.' in val:
            val = val.replace('.', '').replace(',', '.')
        elif ',' in val:
            val = val.replace(',', '.')
        elif val.count('.') > 1:
            val = val.replace('.', '')
        elif '.' in val:
            inteiro, frac = val.rsplit('.', 1)
            if len(frac) == 3 and not sufixo:
                val = inteiro + frac
            # senão mantemos o ponto como decimal (ex: "32.5m")

        numero = float(val) if val else 0.0

        if sufixo == 'm':
            return int(round(numero * 1_000_000))
        elif sufixo == 'k':
            return int(round(numero * 1_000))
        return int(round(numero))
    except (ValueError, TypeError):
        return 0


def calcular_distribuicao_pura(jogadores_validos, tot_morions, tot_diamantes, tot_moedas, tot_ouro):
    """Calcula a distribuição de espólio proporcional ao bid de cada
    jogador. Retorna (resultados, total_bids). A sobra de arredondamento
    vai sempre para o "Alcamax"."""
    total_bids = sum(j['valor'] for j in jogadores_validos)
    if total_bids == 0:
        return [], 0

    resultados = []
    for j in jogadores_validos:
        pct = j['valor'] / total_bids
        resultados.append({
            "nome": j['nome'],
            "equipe": j['equipe'],
            "bid": j['valor'],
            "pct": pct,
            "morions": int(tot_morions * pct),
            "diamantes": int(tot_diamantes * pct),
            "moedas": (int(tot_moedas * pct) // 1000) * 1000,
            "ouro": int(tot_ouro * pct),
            "valor": j['valor'],
        })

    sobra_m = tot_morions - sum(r['morions'] for r in resultados)
    sobra_d = tot_diamantes - sum(r['diamantes'] for r in resultados)
    sobra_c = tot_moedas - sum(r['moedas'] for r in resultados)
    sobra_o = tot_ouro - sum(r['ouro'] for r in resultados)

    alcamax_encontrado = False
    for r in resultados:
        if r['nome'].lower() == 'alcamax':
            r['morions'] += sobra_m
            r['diamantes'] += sobra_d
            r['moedas'] += sobra_c
            r['ouro'] += sobra_o
            alcamax_encontrado = True
            break

    if not alcamax_encontrado and (sobra_m > 0 or sobra_d > 0 or sobra_c > 0 or sobra_o > 0):
        resultados.append({
            "nome": "Alcamax (Sobras)",
            "equipe": "A",
            "bid": 0,
            "pct": 0.0,
            "morions": sobra_m,
            "diamantes": sobra_d,
            "moedas": sobra_c,
            "ouro": sobra_o,
            "valor": 0,
        })

    return resultados, total_bids


def escolher_vencedor_sorteio(candidatos):
    """Escolhe um vencedor aleatório. Isolado para poder ser testado
    (ex: com seed fixa) sem precisar abrir a GUI."""
    if not candidatos:
        return None
    return random.choice(candidatos)


def jogador_vazio():
    return {
        "nome": "", "equipe": "", "bidou": False, "bid_valor": 0,
        "presente": False, "ganhou_caixa": False, "elegivel_sorteio": False
    }


# ---------------------------------------------------------------------------
# Interface gráfica
# ---------------------------------------------------------------------------

class CruzadaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerenciador de Cruzada - Interface Gráfica")
        self.geometry("1150x760")
        self.configure(padx=10, pady=10)

        self.dados = self.carregar_dados()
        self.config_app = self.carregar_config()
        self.player_vars = []  # cada item guarda as StringVar/BooleanVar + os widgets da linha (para busca/remoção)

        self.criar_interface()

    # -- persistência: jogadores --------------------------------------------

    def carregar_dados(self):
        dados_atuais = []
        if os.path.exists(ARQUIVO_DADOS):
            try:
                with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
                    dados_atuais = json.load(f)
            except Exception as e:
                messagebox.showwarning(
                    "Aviso",
                    f"Não foi possível ler '{ARQUIVO_DADOS}' ({e}).\n"
                    "A lista foi reiniciada com os jogadores padrão. "
                    "O arquivo original não foi apagado — verifique-o manualmente se necessário."
                )
                dados_atuais = []

        if not dados_atuais:
            for p in JOGADORES_INICIAIS:
                novo = jogador_vazio()
                novo["nome"] = p["nome"]
                novo["equipe"] = p["equipe"]
                dados_atuais.append(novo)

        return dados_atuais

    def fazer_backup(self):
        """Copia o arquivo de dados atual para uma pasta de backups antes de
        sobrescrevê-lo, para não perder dados de semanas anteriores por
        engano."""
        if not os.path.exists(ARQUIVO_DADOS):
            return
        try:
            os.makedirs(PASTA_BACKUPS, exist_ok=True)
            carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
            destino = os.path.join(PASTA_BACKUPS, f"dados_cruzada_{carimbo}.json")
            shutil.copy2(ARQUIVO_DADOS, destino)
        except Exception:
            pass  # backup é best-effort

    def salvar_dados_json(self, mostrar_msg=True):
        self.fazer_backup()

        novos_dados = []
        for p in self.player_vars:
            if p.get('removido'):
                continue
            nome = p['nome_var'].get().strip()
            if not nome:
                continue
            novos_dados.append({
                "nome": nome,
                "equipe": p['equipe_var'].get().strip(),
                "bidou": p['bidou'].get(),
                "bid_valor": parse_valor(p['valor'].get()),
                "presente": p['presente'].get(),
                "ganhou_caixa": p['caixa'].get(),
                "elegivel_sorteio": p['elegivel'].get(),
                "data_registro": datetime.now().strftime("%Y-%m-%d")
            })

        with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
            json.dump(novos_dados, f, indent=4, ensure_ascii=False)
        self.dados = novos_dados

        self.salvar_territorios_json()

        if mostrar_msg:
            messagebox.showinfo("Sucesso", "Dados salvos com sucesso! (backup automático criado)")

    def limpar_bids(self):
        resposta = messagebox.askyesno(
            "Confirmação",
            "Tem certeza que deseja limpar TODOS os Bids e marcações (Elegível e Presente)? "
            "Isso irá zerar a semana para todos."
        )
        if resposta:
            for p in self.player_vars:
                p['bidou'].set(False)
                p['valor'].set("")
                p['presente'].set(False)
                p['elegivel'].set(False)
            messagebox.showinfo(
                "Limpeza concluída",
                "Todos os campos de Bids e presenças foram limpos na tela. "
                "Lembre-se de 'Salvar Dados' para gravar no arquivo."
            )

    # -- persistência: territórios (loot por equipe) -------------------------

    def carregar_territorios(self):
        dados = {k: dict(v) for k, v in TERRITORIOS_PADRAO.items()}
        if os.path.exists(ARQUIVO_TERRITORIOS):
            try:
                with open(ARQUIVO_TERRITORIOS, 'r', encoding='utf-8') as f:
                    salvo = json.load(f)
                for equipe in dados:
                    if equipe in salvo:
                        dados[equipe].update(salvo[equipe])
            except Exception:
                pass
        return dados

    def salvar_territorios_json(self):
        dados = {}
        for equipe, vars_dict in self.territorio_vars.items():
            dados[equipe] = {chave: var.get() for chave, var in vars_dict.items()}
        try:
            with open(ARQUIVO_TERRITORIOS, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    # -- persistência: histórico ---------------------------------------------

    def carregar_historico(self):
        if os.path.exists(ARQUIVO_HISTORICO):
            try:
                with open(ARQUIVO_HISTORICO, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def registrar_historico(self, entrada):
        historico = self.carregar_historico()
        entrada['data_hora'] = datetime.now().strftime("%d/%m/%Y %H:%M")
        historico.append(entrada)
        try:
            with open(ARQUIVO_HISTORICO, 'w', encoding='utf-8') as f:
                json.dump(historico, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def mostrar_historico(self):
        historico = self.carregar_historico()
        if not historico:
            messagebox.showinfo("Histórico", "Nenhum registro de histórico ainda.")
            return

        linhas = []
        for h in reversed(historico):
            if h.get('tipo') == 'sorteio':
                linhas.append(
                    f"[{h['data_hora']}] SORTEIO — Equipe {h['equipe']} ({h.get('territorio', '')})\n"
                    f"  Vencedor: {h['vencedor']}\n"
                    f"  Candidatos ({len(h['candidatos'])}): {', '.join(h['candidatos'])}\n"
                )
            elif h.get('tipo') == 'distribuicao':
                linhas.append(
                    f"[{h['data_hora']}] DISTRIBUIÇÃO — Equipe {h['equipe']} ({h.get('territorio', '')})\n"
                    f"  Total de bids: {h['total_bids']:,}\n"
                    f"  Loot: {h['morions']} morions | {h['diamantes']} diamantes | "
                    f"{h['moedas']} moedas | {h['ouro']} ouro\n"
                    f"  Jogadores premiados: {h['qtd_jogadores']}\n"
                )
        texto = "\n".join(linhas)
        self.mostrar_resultado("Histórico de Sorteios e Distribuições", texto, permitir_discord=False)

    # -- persistência: configuração (webhook do Discord) ---------------------

    def carregar_config(self):
        if os.path.exists(ARQUIVO_CONFIG):
            try:
                with open(ARQUIVO_CONFIG, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def salvar_config(self):
        dados = {"discord_webhook": self.var_discord_webhook.get().strip()}
        try:
            with open(ARQUIVO_CONFIG, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Configuração", "Webhook do Discord salvo!")
        except Exception as e:
            messagebox.showerror("Configuração", f"Erro ao salvar: {e}")

    def enviar_discord(self, mensagem):
        url = self.var_discord_webhook.get().strip()
        if not url:
            messagebox.showwarning(
                "Discord",
                "Configure a URL do Webhook do Discord no topo da janela e clique em 'Salvar Webhook' primeiro."
            )
            return
        try:
            conteudo = "```\n" + mensagem[:1900] + "\n```"
            payload = json.dumps({"content": conteudo}).encode('utf-8')
            req = urllib.request.Request(
                url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
            )
            urllib.request.urlopen(req, timeout=10)
            messagebox.showinfo("Discord", "Mensagem enviada com sucesso para o Discord!")
        except Exception as e:
            messagebox.showerror(
                "Discord",
                f"Não foi possível enviar para o Discord: {e}\n\n"
                "Verifique se a URL do webhook está correta e se há conexão com a internet."
            )

    # -- interface -------------------------------------------------------------

    def criar_interface(self):
        # -- configuração do Discord ------------------------------------------
        frame_discord = ttk.LabelFrame(self, text="Integração com Discord (opcional)", padding=(10, 5))
        frame_discord.pack(fill="x", pady=(0, 10))
        ttk.Label(frame_discord, text="Webhook URL:").pack(side="left", padx=(0, 5))
        webhook_salvo = self.config_app.get("discord_webhook", "")
        self.var_discord_webhook = tk.StringVar(value=webhook_salvo)
        ttk.Entry(frame_discord, textvariable=self.var_discord_webhook, width=60).pack(side="left", padx=(0, 5))
        ttk.Button(frame_discord, text="Salvar Webhook", command=self.salvar_config).pack(side="left")

        # -- territórios / loot por equipe -------------------------------------
        territorios_salvos = self.carregar_territorios()
        frame_territorios = ttk.Frame(self)
        frame_territorios.pack(fill="x", pady=(0, 10))
        frame_territorios.columnconfigure(0, weight=1)
        frame_territorios.columnconfigure(1, weight=1)

        self.territorio_vars = {}
        for col, equipe in enumerate(("A", "B")):
            terr = territorios_salvos[equipe]
            sub = ttk.LabelFrame(frame_territorios, text=f"Equipe {equipe} — Território e Loot", padding=(10, 5))
            sub.grid(row=0, column=col, padx=5, sticky="nsew")

            ttk.Label(sub, text="Território:").grid(row=0, column=0, padx=5, pady=3, sticky="w")
            var_nome = tk.StringVar(value=terr.get('nome', ''))
            ttk.Entry(sub, textvariable=var_nome, width=16).grid(row=0, column=1, padx=5, pady=3)

            ttk.Label(sub, text="Morions:").grid(row=1, column=0, padx=5, pady=3, sticky="w")
            var_morions = tk.StringVar(value=terr.get('morions', '0'))
            ttk.Entry(sub, textvariable=var_morions, width=10).grid(row=1, column=1, padx=5, pady=3)

            ttk.Label(sub, text="Diamantes:").grid(row=2, column=0, padx=5, pady=3, sticky="w")
            var_diamantes = tk.StringVar(value=terr.get('diamantes', '0'))
            ttk.Entry(sub, textvariable=var_diamantes, width=10).grid(row=2, column=1, padx=5, pady=3)

            ttk.Label(sub, text="Moedas Guild:").grid(row=3, column=0, padx=5, pady=3, sticky="w")
            var_moedas = tk.StringVar(value=terr.get('moedas', '0'))
            ttk.Entry(sub, textvariable=var_moedas, width=10).grid(row=3, column=1, padx=5, pady=3)

            ttk.Label(sub, text="Sacos de Ouro:").grid(row=4, column=0, padx=5, pady=3, sticky="w")
            var_ouro = tk.StringVar(value=terr.get('ouro', '0'))
            ttk.Entry(sub, textvariable=var_ouro, width=10).grid(row=4, column=1, padx=5, pady=3)

            ttk.Button(sub, text=f"Calcular Distribuição - Equipe {equipe}",
                       command=lambda eq=equipe: self.calcular_distribuicao(eq)).grid(
                row=5, column=0, columnspan=2, pady=(8, 2)
            )

            self.territorio_vars[equipe] = {
                'nome': var_nome, 'morions': var_morions, 'diamantes': var_diamantes,
                'moedas': var_moedas, 'ouro': var_ouro,
            }

        # -- barra de busca --------------------------------------------------
        frame_busca = ttk.Frame(self)
        frame_busca.pack(fill="x", pady=(0, 5))
        ttk.Label(frame_busca, text="Buscar jogador:").pack(side="left", padx=(0, 5))
        self.var_busca = tk.StringVar()
        self.var_busca.trace_add("write", lambda *a: self.filtrar_jogadores())
        ttk.Entry(frame_busca, textvariable=self.var_busca, width=30).pack(side="left")

        # -- lista de jogadores -------------------------------------------------
        frame_lista = ttk.LabelFrame(self, text="Jogadores (Equipes A, B e Reservas)", padding=(10, 10))
        frame_lista.pack(fill="both", expand=True, pady=(0, 10))

        self.canvas = tk.Canvas(frame_lista, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # corrige o scroll do mouse: sem isto, era preciso clicar na barra de
        # rolagem manualmente. Ativa a rolagem com a roda do mouse apenas
        # quando o cursor está sobre a lista (não afeta outros widgets, como
        # os Combobox de equipe).
        self.canvas.bind("<Enter>", lambda e: self._ativar_scroll_mouse())
        self.canvas.bind("<Leave>", lambda e: self._desativar_scroll_mouse())

        cabecalhos = ["Nome", "Equipe", "Bidou?", "Valor do Bid (ex: 32.5m)", "Presente?",
                      "Já Ganhou Caixa?", "Elegível Sorteio?", ""]
        for col, texto in enumerate(cabecalhos):
            ttk.Label(self.scrollable_frame, text=texto, font=("Arial", 10, "bold")).grid(
                row=0, column=col, padx=10, pady=5, sticky="w"
            )

        self.proxima_linha = 1
        for p in self.dados:
            self.criar_linha_jogador(p)

        # -- botões gerais --------------------------------------------------
        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(fill="x", pady=10)

        ttk.Button(frame_botoes, text="Salvar Dados", command=self.salvar_dados_json).pack(side="left", padx=10)
        ttk.Button(frame_botoes, text="Limpar Todos os Bids", command=self.limpar_bids).pack(side="left", padx=10)
        ttk.Button(frame_botoes, text="+ Adicionar Jogador", command=self.adicionar_jogador).pack(side="left", padx=10)
        ttk.Button(frame_botoes, text="Ver Histórico", command=self.mostrar_historico).pack(side="left", padx=10)
        ttk.Button(frame_botoes, text="Sortear Caixa - Equipe B",
                   command=lambda: self.realizar_sorteio("B")).pack(side="right", padx=10)
        ttk.Button(frame_botoes, text="Sortear Caixa - Equipe A",
                   command=lambda: self.realizar_sorteio("A")).pack(side="right", padx=10)

    # -- rolagem do mouse -----------------------------------------------------

    def _ativar_scroll_mouse(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _desativar_scroll_mouse(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel_windows(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    # -- linhas da lista de jogadores -----------------------------------------

    def criar_linha_jogador(self, jogador_dict):
        row = self.proxima_linha
        self.proxima_linha += 1

        var_nome = tk.StringVar(value=jogador_dict.get('nome', ''))
        ent_nome = ttk.Entry(self.scrollable_frame, textvariable=var_nome, width=18)
        ent_nome.grid(row=row, column=0, padx=10, pady=2, sticky="w")

        var_equipe = tk.StringVar(value=jogador_dict.get('equipe', ''))
        cb_equipe = ttk.Combobox(self.scrollable_frame, textvariable=var_equipe,
                                  values=["A", "B", "Reserva", ""], width=8, state="normal")
        cb_equipe.grid(row=row, column=1, padx=10, pady=2)

        var_bidou = tk.BooleanVar(value=jogador_dict.get('bidou', False))
        ttk.Checkbutton(self.scrollable_frame, variable=var_bidou).grid(row=row, column=2, padx=10, pady=2)

        val_atual = jogador_dict.get('bid_valor', 0)
        val_str = "" if not val_atual else str(val_atual)
        var_valor = tk.StringVar(value=val_str)
        ttk.Entry(self.scrollable_frame, textvariable=var_valor, width=15).grid(row=row, column=3, padx=10, pady=2)

        var_presente = tk.BooleanVar(value=jogador_dict.get('presente', False))
        ttk.Checkbutton(self.scrollable_frame, variable=var_presente).grid(row=row, column=4, padx=10, pady=2)

        var_caixa = tk.BooleanVar(value=jogador_dict.get('ganhou_caixa', False))
        ttk.Checkbutton(self.scrollable_frame, variable=var_caixa).grid(row=row, column=5, padx=10, pady=2)

        var_elegivel = tk.BooleanVar(value=jogador_dict.get('elegivel_sorteio', False))
        ttk.Checkbutton(self.scrollable_frame, variable=var_elegivel).grid(row=row, column=6, padx=10, pady=2)

        v_dict = {
            'nome_var': var_nome,
            'equipe_var': var_equipe,
            'bidou': var_bidou,
            'valor': var_valor,
            'presente': var_presente,
            'caixa': var_caixa,
            'elegivel': var_elegivel,
            'removido': False,
        }

        btn_remover = ttk.Button(
            self.scrollable_frame, text="Remover", width=8,
            command=lambda v=v_dict: self.remover_jogador(v)
        )
        btn_remover.grid(row=row, column=7, padx=10, pady=2)

        v_dict['widgets'] = [ent_nome, cb_equipe,
                              self.scrollable_frame.grid_slaves(row=row, column=2)[0],
                              self.scrollable_frame.grid_slaves(row=row, column=3)[0],
                              self.scrollable_frame.grid_slaves(row=row, column=4)[0],
                              self.scrollable_frame.grid_slaves(row=row, column=5)[0],
                              self.scrollable_frame.grid_slaves(row=row, column=6)[0],
                              btn_remover]

        def auto_check_elegivel(var_name, index, mode, v=v_dict):
            valor_num = parse_valor(v['valor'].get())
            if valor_num >= LIMITE_ELEGIVEL:
                v['elegivel'].set(True)
                v['bidou'].set(True)
            else:
                v['elegivel'].set(False)

        var_valor.trace_add("write", auto_check_elegivel)

        self.player_vars.append(v_dict)
        return v_dict

    def adicionar_jogador(self):
        self.criar_linha_jogador(jogador_vazio())
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(1.0)

    def remover_jogador(self, v_dict):
        nome = v_dict['nome_var'].get().strip() or "(sem nome)"
        if not messagebox.askyesno("Remover jogador", f"Remover '{nome}' da lista?\n"
                                    "Ele será removido ao salvar os dados."):
            return
        v_dict['removido'] = True
        for w in v_dict['widgets']:
            w.grid_remove()

    def filtrar_jogadores(self):
        termo = self.var_busca.get().strip().lower()
        for p in self.player_vars:
            if p.get('removido'):
                continue
            nome = p['nome_var'].get().strip().lower()
            visivel = termo == "" or termo in nome
            for w in p['widgets']:
                if visivel:
                    w.grid()
                else:
                    w.grid_remove()

    # -- exibição de resultados (distribuição / sorteio / histórico) --------

    def mostrar_resultado(self, titulo, texto, permitir_discord=True):
        win = tk.Toplevel(self)
        win.title(titulo)
        win.geometry("620x520")

        text_area = tk.Text(win, font=("Courier", 10), padx=10, pady=10, wrap="word")
        text_area.pack(fill="both", expand=True)
        text_area.insert("1.0", texto)
        text_area.configure(state="disabled")

        frame_btns = ttk.Frame(win)
        frame_btns.pack(fill="x", pady=5)
        ttk.Button(frame_btns, text="Copiar Texto",
                   command=lambda: self.copiar_para_area_transferencia(texto)).pack(side="left", padx=10)
        if permitir_discord:
            ttk.Button(frame_btns, text="Enviar para Discord",
                       command=lambda: self.enviar_discord(texto)).pack(side="left", padx=10)
        return win

    def copiar_para_area_transferencia(self, texto):
        self.clipboard_clear()
        self.clipboard_append(texto)
        messagebox.showinfo("Copiado", "Texto copiado para a área de transferência!")

    # -- distribuição e sorteio ------------------------------------------------

    def calcular_distribuicao(self, equipe):
        terr_vars = self.territorio_vars[equipe]
        territorio_nome = terr_vars['nome'].get().strip() or f"Território (Equipe {equipe})"
        try:
            tot_morions = int(terr_vars['morions'].get())
            tot_diamantes = int(terr_vars['diamantes'].get())
            tot_moedas = int(terr_vars['moedas'].get())
            tot_ouro = int(terr_vars['ouro'].get())
        except ValueError:
            messagebox.showerror("Erro", f"Os valores de espólio da Equipe {equipe} devem ser números.")
            return

        # persiste a configuração do território assim que é usada (loot pode
        # se manter igual na próxima semana, ou ser alterado se a equipe
        # conquistar outro território)
        self.salvar_territorios_json()

        jogadores_validos = []
        for p in self.player_vars:
            if p.get('removido'):
                continue
            if p['equipe_var'].get().strip().upper() != equipe:
                continue
            nome = p['nome_var'].get().strip()
            if not nome or not p['bidou'].get():
                continue
            val = parse_valor(p['valor'].get())
            if val > 0:
                jogadores_validos.append({"nome": nome, "equipe": p['equipe_var'].get(), "valor": val})

        resultados, total_bids = calcular_distribuicao_pura(
            jogadores_validos, tot_morions, tot_diamantes, tot_moedas, tot_ouro
        )

        if total_bids == 0:
            messagebox.showwarning("Aviso", f"Nenhum valor de bid registrado para a Equipe {equipe}.")
            return

        texto_final = f"EQUIPE {equipe} — {territorio_nome}\n"
        texto_final += f"TOTAL ARRECADADO: {total_bids:,}\n"
        texto_final += "=" * 50 + "\n"

        for r in resultados:
            texto_final += f"\n{r['nome']} | Bid: {r['bid']:,} ({r['pct']*100:.2f}%)\n"
            texto_final += f"  > Morions: {r['morions']}\n"
            texto_final += f"  > Diamantes: {r['diamantes']}\n"
            texto_final += f"  > Moedas: {r['moedas']}\n"
            texto_final += f"  > Ouro: {r['ouro']}\n"

        self.mostrar_resultado(f"Resultado da Distribuição — Equipe {equipe}", texto_final)

        self.registrar_historico({
            "tipo": "distribuicao",
            "equipe": equipe,
            "territorio": territorio_nome,
            "total_bids": total_bids,
            "morions": tot_morions,
            "diamantes": tot_diamantes,
            "moedas": tot_moedas,
            "ouro": tot_ouro,
            "qtd_jogadores": len(resultados),
        })

    def realizar_sorteio(self, equipe):
        """Sorteia a caixa apenas entre os jogadores atualmente cadastrados
        na equipe informada ('A' ou 'B'). Cada equipe joga em um território
        separado, então tem seu próprio sorteio — mas o cadastro de
        jogadores continua único: quem o líder mover de equipe no campo
        'Equipe' automaticamente concorre pela equipe nova, sem precisar
        duplicar cadastro."""
        candidatos_dict = {
            p['nome_var'].get().strip(): p
            for p in self.player_vars
            if not p.get('removido')
            and p['equipe_var'].get().strip().upper() == equipe
            and p['elegivel'].get() and not p['caixa'].get()
            and p['nome_var'].get().strip()
        }
        candidatos = list(candidatos_dict.keys())

        if not candidatos:
            messagebox.showinfo(
                f"Sorteio - Equipe {equipe}",
                f"Nenhum jogador da Equipe {equipe} está elegível ao sorteio "
                "(ou todos os elegíveis já ganharam a caixa)."
            )
            return

        vencedor = escolher_vencedor_sorteio(candidatos)

        candidatos_dict[vencedor]['caixa'].set(True)
        self.salvar_dados_json(mostrar_msg=False)

        territorio_nome = self.territorio_vars[equipe]['nome'].get().strip() or f"Território (Equipe {equipe})"

        msg = f"EQUIPE {equipe} — {territorio_nome}\n"
        msg += f"Jogadores no sorteio: {len(candidatos)}\n\n" + ", ".join(candidatos) + "\n\n"
        msg += f"🎉 O VENCEDOR DA CAIXA (EQUIPE {equipe}) É: {vencedor.upper()} 🎉\n\n"
        msg += "(marcado automaticamente como 'Já Ganhou Caixa' e salvo)"

        self.mostrar_resultado(f"Resultado do Sorteio - Equipe {equipe}", msg)

        self.registrar_historico({
            "tipo": "sorteio",
            "equipe": equipe,
            "territorio": territorio_nome,
            "vencedor": vencedor,
            "candidatos": candidatos,
        })


if __name__ == '__main__':
    app = CruzadaApp()
    app.mainloop()