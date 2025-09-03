# screens/professor_visualizar_aula.py
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

class ProfessorVisualizarAulasScreen(Screen):
    """
    Tela que lista as aulas criadas pelo professor logado.
    """
    def __init__(self, **kwargs):
        super(ProfessorVisualizarAulasScreen, self).__init__(**kwargs)
        self.name = "professor_visualizar_aulas"
        self.aulas_manager = AulasManager(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
        self.nome_professor = ""  # Deve ser preenchido pela tela de login/home
        self.aulas_layout = None
        logger.debug("ProfessorVisualizarAulasScreen inicializada.")

    def on_enter(self, *args):
        """Método chamado quando a tela é exibida"""
        logger.info(f"Entrando na tela de visualização de aulas do professor: {self.nome_professor}") # <-- Adicionar este log
        Clock.schedule_once(self.construir_interface, 0)
        """Método chamado quando a tela é exibida"""
        logger.info("Entrando na tela de visualização de aulas do professor")
        Clock.schedule_once(self.construir_interface, 0)

    def construir_interface(self, dt=None):
        """Constrói a interface da tela de visualização de aulas"""
        logger.debug("Construindo interface de visualização de aulas")

        # Limpa qualquer conteúdo anterior
        self.clear_widgets()

        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=30)

        # Título
        titulo = Label(
            text="Minhas Aulas",
            font_size=24,
            bold=True,
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=0.1,
            halign='center'
        )
        main_layout.add_widget(titulo)

        # Espaço
        main_layout.add_widget(Widget(size_hint_y=0.05))

        # ScrollView para a lista de aulas
        scroll = ScrollView()
        self.aulas_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=15
        )
        self.aulas_layout.bind(minimum_height=self.aulas_layout.setter('height'))

        # Carrega e exibe as aulas
        self.carregar_aulas()

        scroll.add_widget(self.aulas_layout)
        main_layout.add_widget(scroll)

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

    def carregar_aulas(self):
        """Carrega e exibe as aulas do professor"""
        self.aulas_layout.clear_widgets()

        # Verificar se o nome do professor está definido
        if not self.nome_professor:
            logger.error("Nome do professor não definido em ProfessorVisualizarAulasScreen")
            self.aulas_layout.add_widget(Label(
                text="Erro: Nome do professor não encontrado.",
                color=[1, 0, 0, 1], # Vermelho
                size_hint_y=None,
                height=50
            ))
            return

        try:
            logger.debug(f"Carregando aulas para o professor: '{self.nome_professor}'")
            todas_aulas = self.aulas_manager.obter_aulas()
            # Filtra apenas as aulas do professor logado
            aulas = [a for a in todas_aulas if a.get("professor", "") == self.nome_professor]

            if not aulas:
                self.aulas_layout.add_widget(Label(
                    text="Você ainda não criou nenhuma aula.",
                    color=[0.5, 0.5, 0.5, 1],
                    size_hint_y=None,
                    height=50
                ))
                return

            for aula in aulas:
                # Layout para a aula
                aula_item_layout = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=120, # Ajustar altura conforme necessário
                    spacing=5
                )

                # Título da aula
                titulo_aula = Label(
                    text=aula["titulo"],
                    color=[0.05, 0.15, 0.35, 1],
                    size_hint_y=None,
                    height=30,
                    font_size=18,
                    bold=True,
                    halign='left'
                )
                titulo_aula.bind(size=titulo_aula.setter('text_size'))
                aula_item_layout.add_widget(titulo_aula)

                # Disciplina (se disponível)
                if aula.get("disciplina"):
                    disciplina = Label(
                        text=f"Disciplina: {aula['disciplina']}",
                        color=[0.3, 0.3, 0.3, 1],
                        size_hint_y=None,
                        height=20,
                        font_size=14,
                        halign='left'
                    )
                    disciplina.bind(size=disciplina.setter('text_size'))
                    aula_item_layout.add_widget(disciplina)

                # Layout para botões
                botoes_layout = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=40,
                    spacing=10
                )

                # Botão Editar
                btn_editar = Button(
                    text="Editar",
                    background_color=[0.05, 0.15, 0.35, 1],
                    color=[1, 1, 1, 1],
                    size_hint_x=0.5
                )
                # ✅ CORREÇÃO: Passar a aula inteira para o lambda
                btn_editar.bind(on_release=lambda instance, a=aula: self.editar_aula(a))
                botoes_layout.add_widget(btn_editar)

                # Botão Excluir
                btn_excluir = Button(
                    text="Excluir",
                    background_color=[0.8, 0.2, 0.2, 1], # Vermelho
                    color=[1, 1, 1, 1],
                    size_hint_x=0.5
                )
                # ✅ CORREÇÃO: Passar a aula inteira para o lambda
                btn_excluir.bind(on_release=lambda instance, a=aula: self.excluir_aula(a))
                botoes_layout.add_widget(btn_excluir)

                aula_item_layout.add_widget(botoes_layout)

                self.aulas_layout.add_widget(aula_item_layout)

        except Exception as e:
            logger.error(f"Erro ao carregar aulas: {e}", exc_info=True)
            self.aulas_layout.add_widget(Label(
                text="Erro ao carregar aulas.",
                color=[1, 0, 0, 1], # Vermelho
                size_hint_y=None,
                height=50
            ))

    # ✅ MÉTODO ADICIONADO: Editar aula
    def editar_aula(self, aula):
        """Abre a tela de criação/edição para a aula selecionada"""
        logger.info(f"Abrindo edição para aula ID: {aula.get('id')}")
        try:
            # Obter a instância da tela de criação
            screen = self.manager.get_screen('professor_criar_aula')
            if screen:
                # Passar os dados da aula para a tela de criação
                # Isso irá acionar o preencher_campos no on_enter da tela de criação
                screen.dados_aula_para_edicao = aula
                screen.modo = 'editar'
                screen.aula_id = aula.get('id')
                # Passar o nome do professor também, por garantia
                screen.nome_professor = self.nome_professor

                # Mudar para a tela de criação/edição
                self.manager.current = 'professor_criar_aula'
            else:
                logger.error("Tela 'professor_criar_aula' não encontrada.")
                self.mostrar_erro("Tela de edição não encontrada.")
        except Exception as e:
            logger.error(f"Erro ao iniciar edição da aula: {e}", exc_info=True)
            self.mostrar_erro(f"Erro ao abrir edição: {str(e)}")

    # ✅ MÉTODO ADICIONADO: Excluir aula
    def excluir_aula(self, aula):
        """Exclui a aula selecionada após confirmação"""
        logger.info(f"Solicitando exclusão da aula ID: {aula.get('id')}")
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout

        # Criar conteúdo do popup de confirmação
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=f"Tem certeza que deseja excluir a aula:\n'{aula.get('titulo', 'Sem título')}'?",
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
            self._confirmar_exclusao_aula(aula)
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

    def _confirmar_exclusao_aula(self, aula):
        """Executa a exclusão da aula após confirmação"""
        try:
            aula_id = aula.get('id')
            if aula_id is None:
                logger.error("ID da aula não encontrado para exclusão.")
                self.mostrar_erro("ID da aula não encontrado.")
                return

            sucesso, mensagem = self.aulas_manager.excluir_aula(aula_id)
            if sucesso:
                logger.info(f"Aula ID {aula_id} excluída com sucesso.")
                self.mostrar_sucesso("Aula excluída com sucesso.")
                # Recarregar a lista de aulas
                Clock.schedule_once(lambda dt: self.carregar_aulas(), 0.5)
            else:
                logger.error(f"Falha ao excluir aula ID {aula_id}: {mensagem}")
                self.mostrar_erro(mensagem)
        except Exception as e:
            logger.error(f"Erro ao excluir aula: {e}", exc_info=True)
            self.mostrar_erro(f"Erro ao excluir aula: {str(e)}")

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

    def voltar_para_home(self, instance):
        """Volta para a tela inicial do professor"""
        logger.info("Voltando para a tela inicial do professor")
        self.manager.current = 'professor_home'
