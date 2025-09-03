# screens/aluno_aulas.py
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

class AlunoAulasScreen(Screen):
    def __init__(self, **kwargs):
        super(AlunoAulasScreen, self).__init__(**kwargs)
        self.name = "aluno_aulas"
        self.aulas_manager = AulasManager(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
        self.aulas_layout = None
        # ✅ ADIÇÃO: Atributos para filtragem
        self.filtrar_por_professor = None
        self.filtrar_por_disciplina = None
        self.titulo_personalizado = None # Para exibir um título específico
        logger.debug("AlunoAulasScreen inicializada.")
        
    
    def on_enter(self, *args):
        """Método chamado quando a tela é exibida"""
        logger.debug("Entrando na tela de aulas do aluno")
        # ✅ CORREÇÃO: Não limpar os filtros automaticamente a cada entrada
        # Eles devem persistir enquanto o aluno navega entre essa tela e a de visualização
        # self.filtrar_por_professor = None
        # self.filtrar_por_disciplina = None
        # self.titulo_personalizado = None
        Clock.schedule_once(self.construir_interface, 0)

    def construir_interface(self, dt=None):
        """Constrói a interface da tela de aulas do aluno"""
        logger.debug("Construindo interface da tela de aulas do aluno")

        # Limpa qualquer conteúdo anterior
        self.clear_widgets()

        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=30)

        # ✅ CORREÇÃO: Usar título personalizado se disponível
        titulo_texto = self.titulo_personalizado if self.titulo_personalizado else "Minhas Aulas"
        titulo = Label(
            text=titulo_texto,
            font_size=24,
            bold=True,
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=0.1,
            halign='center'
        )
        main_layout.add_widget(titulo)

        # Espaço
        main_layout.add_widget(Widget(size_hint_y=0.05))

        # ✅ CORREÇÃO: ScrollView para a lista de aulas
        scroll = ScrollView()
        self.aulas_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10
        )
        # ✅ CORREÇÃO: Bind para altura mínima
        self.aulas_layout.bind(minimum_height=self.aulas_layout.setter('height'))

        # ✅ CORREÇÃO: Carrega e exibe as aulas (com filtros)
        self.carregar_aulas()

        scroll.add_widget(self.aulas_layout)
        main_layout.add_widget(scroll)
        # ✅ FIM DA CORREÇÃO: ScrollView

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
        btn_voltar.bind(on_release=self.voltar_para_lista_professores) # ✅ CORREÇÃO: Voltar para a nova tela
        main_layout.add_widget(btn_voltar)

        self.add_widget(main_layout)

        
    def carregar_aulas(self):
        """Carrega e exibe as aulas disponíveis, filtradas apenas por professor"""
        self.aulas_layout.clear_widgets()

        # ✅ VERIFICAÇÃO: Se não houver filtro de professor, mostra erro e volta
        if not self.filtrar_por_professor:
            logger.error("Filtro de professor não definido em AlunoAulasScreen")
            self.aulas_layout.add_widget(Label(
                text="Erro: Professor não selecionado.",
                color=[1, 0, 0, 1], # Vermelho
                size_hint_y=None,
                height=50
            ))
            # Agenda o retorno após um curto período
            Clock.schedule_once(lambda dt: self.voltar_para_lista_professores(None), 2)
            return

        try:
            logger.debug(f"Carregando aulas para o professor: '{self.filtrar_por_professor}'")
            todas_aulas = self.aulas_manager.obter_aulas()
            logger.debug(f"Total de aulas carregadas: {len(todas_aulas)}")

            # ✅ CORREÇÃO: Aplicar filtro APENAS por professor
            # A lógica agora é: MOSTRAR TODAS AS AULAS que pertencem AO PROFESSOR selecionado
            aulas_filtradas = [a for a in todas_aulas if a.get("professor", "") == self.filtrar_por_professor]
            logger.debug(f"Aulas após filtro de professor '{self.filtrar_por_professor}': {len(aulas_filtradas)}")

            aulas = aulas_filtradas

            if not aulas:
                self.aulas_layout.add_widget(Label(
                    text="Nenhuma aula encontrada para este professor.",
                    color=[0.5, 0.5, 0.5, 1],
                    size_hint_y=None,
                    height=50
                ))
                return

            # Ordenar as aulas pela data de criação (mais recente primeiro)
            # Supondo que 'data_criacao' seja uma string ISO 8601
            try:
                aulas.sort(key=lambda a: a.get("data_criacao", ""), reverse=True)
            except Exception as e:
                logger.warning(f"Erro ao ordenar aulas por data_criacao: {e}")

            # Para cada aula filtrada, criar um botão para visualizá-la
            for aula in aulas:
                # Layout para a aula
                aula_layout = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=70, # Ajustar altura conforme necessário
                    spacing=5
                )

                # Botão com o título da aula
                btn_aula = Button(
                    text=aula["titulo"],
                    background_color=[0.05, 0.15, 0.35, 1],
                    color=[1, 1, 1, 1],
                    size_hint_y=None,
                    height=50,
                    halign='left',
                    valign='middle',
                    text_size=(None, None)
                )
                # ✅ CORREÇÃO: Vincula o clique à visualização da aula
                # Passa a aula inteira para o lambda
                btn_aula.bind(on_release=lambda instance, a=aula: self.abrir_aula(a))
                aula_layout.add_widget(btn_aula)

                # Informações da disciplina (se disponível)
                # (Este bloco pode ser removido se a informação já estiver implícita pelo filtro)
                # if "disciplina" in aula and aula["disciplina"]:
                #     disciplina = Label(
                #         text=f"Disciplina: {aula['disciplina']}",
                #         color=[0.5, 0.5, 0.5, 1],
                #         size_hint_y=None,
                #         height=20,
                #         font_size=12,
                #         halign='left'
                #     )
                #     disciplina.bind(size=disciplina.setter('text_size'))
                #     aula_layout.add_widget(disciplina)

                self.aulas_layout.add_widget(aula_layout)

        except Exception as e:
            logger.error(f"Erro ao carregar aulas: {e}", exc_info=True)
            self.aulas_layout.add_widget(Label(
                text="Erro ao carregar aulas.",
                color=[1, 0, 0, 1], # Vermelho
                size_hint_y=None,
                height=50
            ))

    # ✅ ADIÇÃO: Novo método para voltar à tela de seleção
    def voltar_para_lista_professores(self, instance):
        """Volta para a tela de seleção de professor/disciplina"""
        logger.info("Voltando para a tela de seleção de professor/disciplina")
        self.manager.current = 'aluno_lista_professores' # ✅ MODIFICAÇÃO: Nome da nova tela

    # Certifique-se de que o método abrir_aula(aula) exista e funcione corretamente
    # Exemplo básico (substitua pela sua lógica real):

    def abrir_aula(self, aula):
        """Abre a tela de visualização da aula selecionada"""
        logger.info(f"[Abrindo aula] {aula['titulo']}")
        try:
            # Obter a instância da tela de visualização
            # ✅ CORREÇÃO: Certifique-se de usar o nome correto da tela e do método
            screen = self.manager.get_screen('aluno_visualizar_aula') # Nome da tela no ScreenManager
            if screen:
                # ✅ CORREÇÃO: Chamar o método correto para carregar UMA aula
                # Isso requer que o método 'carregar_aula' exista em AlunoVisualizarAulaScreen
                screen.carregar_aula(aula) # Passa a aula específica

                # Mudar para a tela de visualização
                self.manager.current = 'aluno_visualizar_aula' # Nome da tela no ScreenManager
            else:
                logger.error("Tela 'aluno_visualizar_aula' não encontrada.")
                self.mostrar_erro("Tela de visualização não encontrada.") # ✅ CORREÇÃO: Usar mostrar_erro
        except Exception as e:
            logger.error(f"[Erro ao abrir aula] {e}", exc_info=True)
            self.mostrar_erro(f"Erro ao abrir aula: {str(e)}") # ✅ CORREÇÃO: Usar mostrar_erro

    def voltar_para_lista_professores(self, instance):
        """Volta para a tela de seleção de professor/disciplina"""
        logger.info("Voltando para a tela de seleção de professor/disciplina")
        self.manager.current = 'aluno_lista_professores' # ✅ CORREÇÃO: Nome da nova tela

    def mostrar_erro(self, mensagem):
        """Mostra uma mensagem de erro"""
        from kivy.uix.popup import Popup
        popup = Popup(
            title='Erro',
            content=Label(text=mensagem),
            size_hint=(0.8, 0.3)
        )
        popup.open()

    
    def voltar_para_home(self, instance):
        """Volta para a tela inicial do aluno"""
        logger.info("Voltando para a tela inicial do aluno")
        self.manager.current = 'aluno_lista_professores'