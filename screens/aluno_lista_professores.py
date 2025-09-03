# screens/aluno_lista_professores.py
import os
import logging
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

from utils.aulas_manager import AulasManager

# Configurar logging
logger = logging.getLogger('degeo_app')

class AlunoListaProfessoresScreen(Screen):
    """
    Tela que lista os professores e disciplinas disponíveis para o aluno escolher.
    """
    def __init__(self, **kwargs):
        super(AlunoListaProfessoresScreen, self).__init__(**kwargs)
        self.name = "aluno_lista_professores"
        self.aulas_manager = AulasManager(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
        self.professores_disciplinas_layout = None
        logger.debug("AlunoListaProfessoresScreen inicializada.")

    def on_enter(self, *args):
        """Método chamado quando a tela é exibida"""
        logger.info("Entrando na tela de seleção de professor/disciplina")
        Clock.schedule_once(self.construir_interface, 0)

    def construir_interface(self, dt=None):
        """Constrói a interface da tela de seleção de professor/disciplina"""
        logger.debug("Construindo interface de seleção de professor/disciplina")

        # Limpa qualquer conteúdo anterior
        self.clear_widgets()

        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=30)

        # Título
        titulo = Label(
            text="Escolha um Professor/Disciplina",
            font_size=20,
            bold=True,
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=0.1,
            halign='center'
        )
        main_layout.add_widget(titulo)

        # Espaço
        main_layout.add_widget(Widget(size_hint_y=0.05))

        # ScrollView para a lista de professores/disciplinas
        scroll = ScrollView()
        # Garante que o layout seja criado e atribuído aqui
        self.professores_disciplinas_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=15
        )
        self.professores_disciplinas_layout.bind(minimum_height=self.professores_disciplinas_layout.setter('height'))

        # Carrega e exibe os professores/disciplinas
        # Esta chamada agora tem acesso ao layout recém-criado
        self.carregar_professores_disciplinas()

        scroll.add_widget(self.professores_disciplinas_layout)
        main_layout.add_widget(scroll)
        # FIM ScrollView

        # Espaço
        main_layout.add_widget(Widget(size_hint_y=0.05))

        # Botão Voltar
        btn_voltar = Button(
            text="Voltar",
            background_color=[0.7, 0.7, 0.7, 1],
            color=[0, 0, 0, 1],
            size_hint_y=None,
            height="50dp",
            pos_hint={'center_x': 0.5}
        )
        btn_voltar.bind(on_release=self.voltar_para_home)
        main_layout.add_widget(btn_voltar)

        self.add_widget(main_layout)

    # --- FUNÇÃO INDENTADA CORRETAMENTE DENTRO DA CLASSE ---
    def carregar_professores_disciplinas(self):
        """Carrega e exibe os pares únicos de professor/disciplina como botões"""
        logger.debug("--- INICIANDO carregar_professores_disciplinas ---")
        
        # Verificação de sanidade
        logger.debug(f"1. Verificando self.professores_disciplinas_layout: {self.professores_disciplinas_layout}")
        if not self.professores_disciplinas_layout:
            logger.error("1.ERRO CRÍTICO: professores_disciplinas_layout é None em carregar_professores_disciplinas")
            return # Não há nada a fazer se o layout não existir
        logger.debug("1. OK: self.professores_disciplinas_layout existe.")

        # Limpa o layout antes de começar
        logger.debug("2. Limpando layout de professores_disciplinas...")
        self.professores_disciplinas_layout.clear_widgets()
        logger.debug("2. OK: Layout limpo.")

        try:
            logger.debug("3. Iniciando carregamento de pares professor/disciplina")
            import json
            import os
            professores_file = os.path.join(os.path.dirname(__file__), "..", "data", "professores.json")
            logger.debug(f"3. Tentando carregar professores de: {professores_file}")

            professores = []
            if os.path.exists(professores_file):
                logger.debug(f"3. Arquivo {professores_file} encontrado.")
                with open(professores_file, 'r', encoding='utf-8') as f:
                    try:
                        conteudo_bruto = f.read()
                        logger.debug(f"3. Conteúdo bruto do arquivo (primeiros 500 chars): {conteudo_bruto[:500]}")
                        professores = json.loads(conteudo_bruto)
                        logger.debug(f"3. Professores carregados via json.loads: {professores}")
                    except json.JSONDecodeError as je:
                        logger.error(f"3. Erro ao decodificar JSON em {professores_file}: {je}")
                        self._adicionar_mensagem(self.professores_disciplinas_layout, "Erro no formato do arquivo de professores.", nivel="erro")
                        logger.debug("--- FINALIZANDO carregar_professores_disciplinas (ERRO JSON) ---")
                        return
                logger.info(f"3. Total de professores carregados: {len(professores)}")
            else:
                logger.warning(f"3. Arquivo {professores_file} NÃO encontrado.")
                self._adicionar_mensagem(self.professores_disciplinas_layout, "Arquivo de professores não encontrado.", nivel="erro")
                logger.debug("--- FINALIZANDO carregar_professores_disciplinas (ARQUIVO NÃO ENCONTRADO) ---")
                return

            if not professores:
                logger.debug("4. Nenhum professor encontrado no arquivo ou arquivo vazio.")
                self._adicionar_mensagem(self.professores_disciplinas_layout, "Nenhum professor cadastrado no momento.", nivel="info")
                logger.debug("--- FINALIZANDO carregar_professores_disciplinas (NENHUM PROFESSOR) ---")
                return
            logger.debug("4. OK: Lista de professores NÃO está vazia.")

            # Verificar estrutura dos dados e criar pares
            logger.debug("5. Verificando estrutura dos dados dos professores...")
            pares_unicos = set()
            logger.debug(f"5. Iterando sobre {len(professores)} professores...")
            for i, professor in enumerate(professores):
                logger.debug(f"5. Processando item {i}: {professor} (tipo: {type(professor)})")
                # Verifica se é um dicionário
                if not isinstance(professor, dict):
                    logger.warning(f"5. Item {i} não é um dicionário: {professor}")
                    continue

                # --- Verificação de string vazia com .strip() ---
                nome_raw = professor.get("nome", "")
                disciplina_raw = professor.get("disciplina", "")
                logger.debug(f"5. Valores brutos para item {i}: nome='{nome_raw}' (tipo: {type(nome_raw)}), disciplina='{disciplina_raw}' (tipo: {type(disciplina_raw)})")
                
                # Garantir que sejam strings antes de .strip()
                nome = str(nome_raw).strip() if nome_raw is not None else ""
                disciplina = str(disciplina_raw).strip() if disciplina_raw is not None else ""
                
                logger.debug(f"5. Processando professor {i}: Nome='{nome}', Disciplina='{disciplina}'")

                # Adicionar ao conjunto apenas se ambos existirem e não forem vazios
                if nome and disciplina:
                    pares_unicos.add((nome, disciplina))
                    logger.debug(f"5. Par adicionado: ({nome}, {disciplina})")
                else:
                    logger.debug(f"5. Professor {i} ignorado por nome ('{nome}') ou disciplina ('{disciplina}') vazios/ausentes.")

            logger.info(f"5. Total de pares únicos encontrados: {len(pares_unicos)}")
            logger.debug(f"5. Pares únicos encontrados: {list(pares_unicos)}")

            # Se não encontrou pares válidos
            logger.debug("6. Verificando se há pares para exibir...")
            if not pares_unicos:
                logger.debug("6. Nenhum par válido (nome e disciplina) encontrado.")
                self._adicionar_mensagem(self.professores_disciplinas_layout, "Nenhum professor com disciplina cadastrada.", nivel="info")
                logger.debug("--- FINALIZANDO carregar_professores_disciplinas (NENHUM PAR) ---")
                return # Importante: parar aqui se não houver pares
            logger.debug("6. OK: Existem pares para exibir.")

            # Ordenar os pares
            logger.debug("7. Ordenando pares...")
            pares_ordenados = sorted(list(pares_unicos), key=lambda x: (x[0], x[1]))
            logger.debug(f"7. Pares ordenados: {pares_ordenados}")

            # Criar botões - Esta parte só é executada se houver pares
            logger.debug("8. Criando botões para os pares encontrados...")
            for nome, disciplina in pares_ordenados:
                logger.debug(f"8. Criando botão para: {nome} - {disciplina}")
                item_layout = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=80,
                    spacing=5
                )

                btn_prof_disc = Button(
                    text=f"{nome}\n{disciplina}",
                    background_color=[0.05, 0.15, 0.35, 1],
                    color=[1, 1, 1, 1],
                    size_hint_y=None,
                    height=60,
                    halign='center',
                    valign='middle',
                    font_size=16,
                    text_size=(None, None) # Para permitir wrapping
                )
                # Passar professor e disciplina para o lambda usando default arguments
                btn_prof_disc.bind(on_release=lambda instance, n=nome, d=disciplina: self.selecionar_professor_disciplina(n, d))
                item_layout.add_widget(btn_prof_disc)

                self.professores_disciplinas_layout.add_widget(item_layout)
                logger.debug(f"8. Botão criado e adicionado para: {nome} - {disciplina}")

            logger.info("9. Finalizado carregamento e exibição de pares professor/disciplina com sucesso.")
            logger.debug("--- FINALIZANDO carregar_professores_disciplinas (SUCESSO) ---")

        except Exception as e:
            logger.error(f"X. Erro crítico ao carregar professores/disciplinas: {e}", exc_info=True)
            # Tentar mostrar erro no layout, se ainda estiver acessível
            if self.professores_disciplinas_layout and len(self.professores_disciplinas_layout.children) == 0:
                self._adicionar_mensagem(self.professores_disciplinas_layout, "Erro ao carregar lista de professores.", nivel="erro")
            logger.debug("--- FINALIZANDO carregar_professores_disciplinas (EXCEÇÃO) ---")


    def _adicionar_mensagem(self, layout, mensagem, nivel="info"):
        """Adiciona uma mensagem de erro ou informação a um layout específico."""
        if not layout:
            logger.warning("Tentativa de adicionar mensagem a um layout None.")
            return
        # Define a cor com base no nível
        cor = [1, 0, 0, 1] if nivel == "erro" else [0.5, 0.5, 0.5, 1] # Vermelho ou Cinza
        # Cria o label
        label_msg = Label(
            text=mensagem,
            color=cor,
            size_hint_y=None,
            height=50,
            halign='center',   # Alinha horizontalmente ao centro
            valign='middle'    # Alinha verticalmente ao meio
        )
        # Permite wrapping de texto e ajusta o tamanho da caixa de texto
        label_msg.bind(size=label_msg.setter('text_size'))
        # Adiciona ao layout fornecido
        layout.add_widget(label_msg)
        logger.debug(f"Mensagem '{mensagem}' (nível: {nivel}) adicionada ao layout.")


    def selecionar_professor_disciplina(self, professor, disciplina):
        """
        Chamado quando o aluno seleciona um professor/disciplina.
        Transfere os filtros para a tela AlunoAulasScreen e navega para ela.
        """
        logger.info(f"Professor '{professor}' e Disciplina '{disciplina}' selecionados")
        try:
            # Obter a instância da tela de listagem de aulas
            screen_aulas = self.manager.get_screen('aluno_aulas')
            if screen_aulas:
                screen_aulas.filtrar_por_professor = professor
                # screen_aulas.filtrar_por_disciplina = disciplina # Se quiser filtrar por disciplina também
                screen_aulas.titulo_personalizado = f"Aulas de {professor} ({disciplina})"
                logger.debug(f"Filtros definidos: Professor='{professor}', Disciplina='{disciplina}'")
                self.manager.current = 'aluno_aulas'
            else:
                logger.error("Tela 'aluno_aulas' não encontrada.")
        except Exception as e:
            logger.error(f"Erro ao selecionar professor/disciplina: {e}", exc_info=True)

    def voltar_para_home(self, instance):
        """Volta para a tela inicial do aluno"""
        logger.info("Voltando para a tela inicial do aluno")
        self.manager.current = 'aluno_home'

    def mostrar_erro(self, mensagem):
        """Mostra uma mensagem de erro"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        popup = Popup(
            title='Erro - Lista de Professores',
            content=Label(text=mensagem),
            size_hint=(0.8, 0.3)
        )
        popup.open()

# --- FIM DA CLASSE ---