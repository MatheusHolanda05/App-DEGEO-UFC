# screens/professor_home.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import os
import json
from utils.aulas_manager import AulasManager
# Import correto do AtualizacoesManager (certifique-se de que o arquivo exista)
from utils.atualizacoes_manager import AtualizacoesManager # ✅ VERIFICAR SE O ARQUIVO EXISTE
import logging

# Configurar logging
logger = logging.getLogger('degeo_app')

class ProfessorHomeScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfessorHomeScreen, self).__init__(**kwargs)
        self.name = "professor_home"
        self.aulas_manager = AulasManager(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
        # ✅ CORREÇÃO: Inicializar atualizacoes_manager
        try:
            # Tenta inicializar o AtualizacoesManager
            self.atualizacoes_manager = AtualizacoesManager(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
            logger.debug("AtualizacoesManager inicializado com sucesso.")
        except Exception as e:
            # Se falhar, define como None e loga o erro
            self.atualizacoes_manager = None
            logger.error(f"Falha ao inicializar AtualizacoesManager: {e}", exc_info=True)

        self.nome_professor = ""  # Deve ser preenchido pela tela de login/home
        # ✅ CORREÇÃO: Inicializar genero
        self.genero = None  # Deve ser preenchido pela tela de login/home
        self.disciplina_professor = ""  # Deve ser preenchido pela tela de login/home
        # Armazena o estado dos badges
        self.badges = {}
        # Armazena os layouts dos badges para atualização
        self.badge_layouts = {}
        # Cache para evitar verificações excessivas
        self.ultima_verificacao = 0
        self.intervalo_minimo_verificacao = 300  # 5 minutos
        # Dicionário para armazenar os botões
        self.botoes = {}  # ✅ Inicialização do dicionário de botões
        logger.debug("ProfessorHomeScreen inicializada.")

    def on_enter(self, *args):
        """Método chamado quando a tela é exibida"""
        logger.info(f"Entrando na tela inicial do professor: {self.nome_professor}")
        Clock.schedule_once(self.construir_interface, 0)
        # Iniciar verificação de atualizações em segundo plano
        Clock.schedule_once(self.iniciar_verificacao_atualizacoes, 0.5)

    def iniciar_verificacao_atualizacoes(self, dt):
        """Inicia a verificação de atualizações em segundo plano"""
        logger.debug("Iniciando verificação de atualizações em segundo plano")
        # O método verificar_todas_atualizacoes não existe em AtualizacoesManager
        # As verificações individuais já são feitas em atualizar_badges
        # Mantendo vazio conforme sugestão anterior
        pass

    def construir_interface(self, dt=None):
        """Constrói a interface da tela inicial do professor"""
        logger.debug("Construindo interface da tela inicial do professor")

        # Limpa qualquer conteúdo anterior
        self.clear_widgets()

        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=30)

        # Saudação personalizada baseada no gênero
        # ✅ CORREÇÃO: Verificar se self.genero existe antes de usá-lo
        if self.genero == "Feminino":
            saudacao_texto = f"Bem-vinda, {self.nome_professor}!"
        elif self.genero == "Masculino":
            saudacao_texto = f"Bem-vindo, {self.nome_professor}!"
        else:  # Outros ou None
            saudacao_texto = f"Bem-vindo(a), {self.nome_professor}!"

        saudacao = Label(
            text=saudacao_texto,
            font_size=24,
            bold=True,
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=0.1,
            halign='center'
        )
        main_layout.add_widget(saudacao)

        # Subtítulo com disciplina
        if self.disciplina_professor:
            disciplina = Label(
                text=f"Disciplina: {self.disciplina_professor}",
                font_size=18,
                color=[0.05, 0.15, 0.35, 1],
                size_hint_y=0.05,
                halign='center'
            )
            main_layout.add_widget(disciplina)

        # Espaço
        main_layout.add_widget(Widget(size_hint_y=0.07))

        # Botão Criar Aula
        btn_criar = Button(
            text="Criar Aula",
            background_color=[0.05, 0.15, 0.35, 1],
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height="50dp"
        )
        btn_criar.bind(on_release=self.abrir_criar_aula)
        main_layout.add_widget(btn_criar)

        # Espaçamento PADRONIZADO
        main_layout.add_widget(Widget(size_hint_y=0.01))

        # Botão Visualizar Aulas
        btn_visualizar = Button(
            text="Visualizar Aulas",
            background_color=[0.05, 0.15, 0.35, 1],
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height="50dp"
        )
        btn_visualizar.bind(on_release=self.abrir_visualizar_aulas)
        main_layout.add_widget(btn_visualizar)

        # Espaçamento PADRONIZADO
        main_layout.add_widget(Widget(size_hint_y=0.01))

        # ✅ CORREÇÃO: Botão Excluir Conta (em vermelho)
        btn_excluir_conta = Button(
            text="Excluir minha conta",
            background_color=[0.8, 0.2, 0.2, 1],  # Vermelho
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height="50dp"
        )
        # ✅ CORREÇÃO: Vincular ao método correto (com sublinhado)
        btn_excluir_conta.bind(on_release=self.excluir_conta) # <-- Esta linha é a chave
        main_layout.add_widget(btn_excluir_conta)

        # Espaçamento PADRONIZADO
        main_layout.add_widget(Widget(size_hint_y=0.01))

        # Botão Voltar
        btn_voltar = Button(
            text="Voltar",
            background_color=[0.7, 0.7, 0.7, 1],
            color=[0, 0, 0, 1],
            size_hint_y=None,
            height="50dp",
            pos_hint={'center_x': 0.5}
        )
        btn_voltar.bind(on_release=self.voltar_para_login)
        main_layout.add_widget(btn_voltar)

        self.add_widget(main_layout)

        # Atualizar indicadores de atualização (apenas se o manager existir)
        if self.atualizacoes_manager:
             self.atualizar_badges()

    def abrir_criar_aula(self, instance):
        """Abre a tela para criar uma nova aula"""
        logger.info("Abrindo tela para criar nova aula")
        self.manager.current = 'professor_criar_aula'

    def abrir_visualizar_aulas(self, instance):
        """Abre a tela para visualizar aulas criadas"""
        logger.info("Abrindo tela para visualizar aulas criadas")
        # Obter a instância da tela de visualização
        try:
            screen = self.manager.get_screen('professor_visualizar_aulas')
            # ✅ CORREÇÃO: Passar o nome do professor logado para a tela de visualização
            # Isso garante que a tela visualize apenas as aulas deste professor
            screen.nome_professor = self.nome_professor # self.nome_professor vem do login
            logger.debug(f"Nome do professor '{self.nome_professor}' passado para a tela de visualização.")
            # Mudar para a tela
            self.manager.current = 'professor_visualizar_aulas'
        except Exception as e:
            logger.error(f"Erro ao abrir tela de visualização de aulas: {e}", exc_info=True)

    def _confirmar_exclusao_conta(self):
        """Executa a exclusão da conta do professor após confirmação"""
        try:
            # ✅ CORREÇÃO: Obter o email do professor logado de forma segura
            # Supondo que você tenha um atributo self.nome_professor ou self.professor_logado
            # Você precisa ter acesso ao email do professor logado.
            # Uma forma comum é passar o email durante o login e armazená-lo.
            # Se você não tiver self.email, você precisa obtê-lo de outra forma.
            # Vamos supor que você tenha self.nome_professor e possa buscá-lo no arquivo.

            # Verificar se o nome do professor está disponível
            if not hasattr(self, 'nome_professor') or not self.nome_professor:
                logger.error("Nome do professor não encontrado para exclusão.")
                self.mostrar_erro("Erro ao identificar professor para exclusão.") # ✅ CORREÇÃO: Usar mostrar_erro
                return

            # Carregar os professores do arquivo
            professores = self.carregar_professores()

            # ✅ CORREÇÃO: Encontrar o professor pelo nome em vez do email
            # Isso pressupõe que o nome seja único. Se não for, você precisa usar o ID ou email.
            # Vamos tentar pelo nome primeiro.
            professor_atual = next((p for p in professores if p.get("nome", "").strip() == self.nome_professor.strip()), None)

            # Se não encontrar pelo nome, tentar carregar o email de outra forma
            # (por exemplo, se você o passou durante o login e armazenou em outro lugar)
            if not professor_atual:
                 # Tentativa alternativa: Se você tiver acesso ao email de outra forma
                 # (por exemplo, se estiver armazenado em uma variável global ou em um manager)
                 # Substitua 'self.email_alternativo' pelo nome correto do atributo, se existir.
                 email_professor = getattr(self, 'email_professor', None) # Exemplo de atributo alternativo
                 if email_professor:
                      professor_atual = next((p for p in professores if p.get("email", "").strip().lower() == email_professor.strip().lower()), None)

            # Se ainda não encontrar, mostrar erro
            if not professor_atual:
                logger.error(f"Professor '{self.nome_professor}' não encontrado para exclusão.")
                self.mostrar_erro("Professor não encontrado para exclusão.") # ✅ CORREÇÃO: Usar mostrar_erro
                return

            # Obter o ID ou email do professor para exclusão
            professor_id = professor_atual.get("id")
            professor_email = professor_atual.get("email", "").strip().lower()

            if not professor_id and not professor_email:
                logger.error("ID ou email do professor não encontrado para exclusão.")
                self.mostrar_erro("Dados do professor incompletos para exclusão.") # ✅ CORREÇÃO: Usar mostrar_erro
                return

            # Remover o professor da lista
            # Filtrar a lista para excluir o professor
            professores_atualizados = [p for p in professores if not (
                (professor_id and p.get("id") == professor_id) or
                (professor_email and p.get("email", "").strip().lower() == professor_email)
            )]

            # Salvar a lista atualizada
            self.salvar_professores(professores_atualizados)

            # Remover as aulas do professor (se aplicável)
            # Nota: Certifique-se de que o método excluir_aulas_do_professor exista em AulasManager
            # ou implemente a lógica aqui.
            # sucesso_aulas, mensagem_aulas = self.aulas_manager.excluir_aulas_do_professor(self.nome_professor)
            # if not sucesso_aulas:
            #     logger.warning(f"Falha ao excluir aulas do professor: {mensagem_aulas}")
            #     # Você pode decidir se quer continuar com a exclusão da conta mesmo assim

            logger.info(f"Conta do professor '{self.nome_professor}' excluída com sucesso.")
            self.mostrar_sucesso("Conta excluída com sucesso!") # ✅ CORREÇÃO: Usar mostrar_sucesso

            # Voltar para a tela de login após um curto período
            Clock.schedule_once(lambda dt: self.voltar_para_login(None), 2)

        except Exception as e:
            logger.error(f"Erro ao excluir conta: {e}", exc_info=True)
            self.mostrar_erro(f"Erro ao excluir conta: {str(e)}") # ✅ CORREÇÃO: Usar mostrar_erro

    def excluir_conta(self, instance):
        """Solicita confirmação antes de excluir a conta do professor"""
        logger.info(f"Solicitando exclusão da conta do professor: {getattr(self, 'nome_professor', 'Desconhecido')}")
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout

        # Criar conteúdo do popup de confirmação
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=f"Tem certeza que deseja excluir sua conta?\nTodos os seus dados e aulas serão perdidos permanentemente.",
            halign='center',
            valign='middle'
        ))
        
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        
        btn_cancelar = Button(text="Cancelar")
        # Usar uma variável local para o popup
        popup_ref = None
        btn_cancelar.bind(on_release=lambda x: popup_ref.dismiss() if popup_ref else None)
        btn_layout.add_widget(btn_cancelar)
        
        btn_confirmar = Button(text="Excluir", background_color=[0.8, 0.2, 0.2, 1])
        btn_confirmar.bind(on_release=lambda x: (
            popup_ref.dismiss() if popup_ref else None,
            self._confirmar_exclusao_conta() # Chama a exclusão real aqui
        ))
        btn_layout.add_widget(btn_confirmar)
        
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Confirmar Exclusão',
            content=content,
            size_hint=(0.8, 0.4)
        )
        # Atribuir a referência do popup
        popup_ref = popup
        popup.open()
        """Solicita confirmação antes de excluir a conta do professor"""
        logger.info(f"Solicitando exclusão da conta do professor: {getattr(self, 'nome_professor', 'Desconhecido')}")
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout

        # Criar conteúdo do popup de confirmação
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=f"Tem certeza que deseja excluir sua conta?\nTodos os seus dados e aulas serão perdidos permanentemente.",
            halign='center',
            valign='middle'
        ))
        
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        
        btn_cancelar = Button(text="Cancelar")
        # Usar uma variável local para o popup
        popup_ref = None
        btn_cancelar.bind(on_release=lambda x: popup_ref.dismiss() if popup_ref else None)
        btn_layout.add_widget(btn_cancelar)
        
        btn_confirmar = Button(text="Excluir", background_color=[0.8, 0.2, 0.2, 1])
        btn_confirmar.bind(on_release=lambda x: (
            popup_ref.dismiss() if popup_ref else None,
            self._confirmar_exclusao_conta() # Chama a exclusão real aqui
        ))
        btn_layout.add_widget(btn_confirmar)
        
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Confirmar Exclusão',
            content=content,
            size_hint=(0.8, 0.4)
        )
        # Atribuir a referência do popup
        popup_ref = popup
        popup.open()
        """Exclui a conta do professor e todos os seus dados"""
        logger.info(f"Solicitando exclusão da conta do professor: {getattr(self, 'nome_professor', 'Desconhecido')}")
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout

        # Criar conteúdo do popup de confirmação
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=f"Tem certeza que deseja excluir sua conta?\nTodos os seus dados e aulas serão perdidos permanentemente.",
            halign='center',
            valign='middle'
        ))

        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)

        btn_cancelar = Button(text="Cancelar")
        # Usar uma variável local para o popup
        popup_ref = None
        btn_cancelar.bind(on_release=lambda x: popup_ref.dismiss() if popup_ref else None)
        btn_layout.add_widget(btn_cancelar)

        btn_confirmar = Button(text="Excluir", background_color=[0.8, 0.2, 0.2, 1])
        btn_confirmar.bind(on_release=lambda x: (
            popup_ref.dismiss() if popup_ref else None,
            self._confirmar_exclusao_conta()
        ))
        btn_layout.add_widget(btn_confirmar)

        content.add_widget(btn_layout)

        popup = Popup(
            title='Confirmar Exclusão',
            content=content,
            size_hint=(0.8, 0.4)
        )
        # Atribuir a referência do popup
        popup_ref = popup
        popup.open()

    def carregar_professores(self):
        """Carrega a lista de professores do arquivo JSON"""
        try:
            professores_file = os.path.join(os.path.dirname(__file__), "..", "data", "professores.json")
            logger.debug(f"Tentando carregar professores de: {professores_file}")

            if not os.path.exists(professores_file):
                logger.warning(f"Arquivo {professores_file} não existe")
                return []

            with open(professores_file, "r") as f:
                professores = json.load(f)
                logger.info(f"Carregados {len(professores)} professores do arquivo")
                return professores
        except Exception as e:
            logger.error(f"Erro ao carregar professores: {str(e)}", exc_info=True)
            return []

    def salvar_professores(self, professores):
        """Salva a lista de professores no arquivo JSON"""
        try:
            professores_file = os.path.join(os.path.dirname(__file__), "..", "data", "professores.json")

            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(professores_file), exist_ok=True)

            with open(professores_file, "w") as f:
                json.dump(professores, f, indent=2)

            logger.info(f"Salvou {len(professores)} professores no arquivo")
        except Exception as e:
            logger.error(f"Erro ao salvar professores: {str(e)}", exc_info=True)
            self.mostrar_erro("Erro ao salvar cadastro. Tente novamente.")

    def mostrar_erro(self, mensagem):
        """Mostra uma mensagem de erro"""
        from kivy.uix.popup import Popup
        popup = Popup(
            title='Erro',
            content=Label(text=mensagem),
            size_hint=(0.8, 0.3)
        )
        popup.open()

    def mostrar_sucesso(self, mensagem):
        """Mostra uma mensagem de sucesso"""
        from kivy.uix.popup import Popup
        popup = Popup(
            title='Sucesso',
            content=Label(text=mensagem),
            size_hint=(0.8, 0.3)
        )
        popup.open()

    def voltar_para_login(self, instance):
        """Volta para a tela de login"""
        logger.info("Voltando para a tela de login")
        self.manager.current = 'login'

    def atualizar_badges(self, dt=None):
        """Atualiza os badges de notificação com otimizações de desempenho"""
        # Verifica se a tela ainda está ativa
        if self.manager.current != 'professor_home':
            return False  # Cancela o agendamento futuro

        # Verifica se o atualizacoes_manager foi inicializado
        if not self.atualizacoes_manager:
            logger.warning("AtualizacoesManager não inicializado. Badges não serão atualizados.")
            return False # Cancela o agendamento futuro

        # Define callbacks para cada verificação
        def criar_callback(chave):
            def callback(resultado):
                self._atualizar_badge(chave, resultado)
            return callback

        # Inicia verificações assíncronas
        self.atualizacoes_manager.verificar_atualizacao(
            "noticias",
            "https://geologia.ufc.br/wp-json/wp/v2/posts    ",
            criar_callback('noticias')
        )

        self.atualizacoes_manager.verificar_atualizacao(
            "calendario",
            "https://www.ufc.br/calendario-universitario/2025    ",
            criar_callback('calendario')
        )

        self.atualizacoes_manager.verificar_atualizacao(
            "revista",
            "https://www.periodicos.ufc.br/index.php/geologia    ",
            criar_callback('revista')
        )

        self.atualizacoes_manager.verificar_atualizacao(
            "graduacao",
            "https://geologia.ufc.br/pt/graduacao/    ",
            criar_callback('graduacao')
        )

        self.atualizacoes_manager.verificar_atualizacao(
            "sobre_geologia",
            "https://geologia.ufc.br/pt/sobre-a-geologia/    ",
            criar_callback('sobre_geologia')
        )

        self.atualizacoes_manager.verificar_atualizacao(
            "sobre_departamento",
            "https://geologia.ufc.br/pt/sobre/    ",
            criar_callback('sobre_departamento')
        )

        self.atualizacoes_manager.verificar_atualizacao(
            "coordenacao",
            "https://geologia.ufc.br/pt/estrutura-organizacional-da-coordenacao-de-graduacao/    ",
            criar_callback('coordenacao')
        )

        self.atualizacoes_manager.verificar_atualizacao(
            "acessibilidade",
            "https://geologia.ufc.br/pt/acessibilidade/    ",
            criar_callback('acessibilidade')
        )

        self.atualizacoes_manager.verificar_atualizacao(
            "normas_ufc",
            "https://geologia.ufc.br/pt/estatuto-regimento-e-normas-da-ufc/    ",
            criar_callback('normas_ufc')
        )

        return True  # Continua o agendamento

    def _atualizar_badge(self, chave, tem_atualizacao):
        """Atualiza um badge específico com otimização de desempenho"""
        # Nota: O código original tentava acessar self.badges[chave].children[0]
        # Isso pode falhar se 'badges' não estiver sendo preenchido corretamente
        # ou se a estrutura dos widgets for diferente.
        # Esta é uma correção genérica. Você pode precisar adaptar
        # com base na implementação real da interface (que não está completa aqui).
        # Por exemplo, se você tiver labels específicas para badges, armazene-as
        # em um dicionário como self.badge_labels[chave] e atualize-as aqui.

        # Placeholder para atualização de badge - substitua pela lógica real
        logger.debug(f"Atualizando badge {chave}: {'Tem atualização' if tem_atualizacao else 'Sem atualização'}")
        # Exemplo (substitua 'nome_do_widget_badge' pelo nome real):
        # if hasattr(self, 'badge_noticias') and chave == 'noticias':
        #     if tem_atualizacao:
        #         self.badge_noticias.text = "1"
        #         self.badge_noticias.color = [1, 0, 0, 1] # Vermelho
        #     else:
        #         self.badge_noticias.text = ""
        #         self.badge_noticias.color = [1, 1, 1, 1] # Branco ou transparente
