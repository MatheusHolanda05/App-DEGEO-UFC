# screens/professor.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
# ✅ CORREÇÃO: Adicione esta importação
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from utils.aulas_manager import AulasManager
import os

class ProfessorHomeScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfessorHomeScreen, self).__init__(**kwargs)
        self.aulas_manager = AulasManager(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
        # Armazena o nome do professor
        self.nome_professor = ""
    
    def on_enter(self):
        self.construir_interface()
    
    def construir_interface(self):
        # Limpa qualquer conteúdo anterior
        self.clear_widgets()
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=30)
        
        # Espaço para saudação (será preenchido posteriormente)
        saudacao_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=80
        )
        # ✅ CORREÇÃO: Adiciona a saudação com o nome do professor
        saudacao_layout.add_widget(Label(
            text=f"Olá, {self.nome_professor}!",
            font_size=18,
            bold=True,
            color=[0.05, 0.15, 0.35, 1],
            halign='center'
        ))
        main_layout.add_widget(saudacao_layout)
        
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
        
        # ✅ CORREÇÃO: Widget já está importado
        # Espaço
        main_layout.add_widget(Widget(size_hint_y=0.05))
        
        # Título da lista de aulas
        titulo_lista = Label(
            text="Minhas Aulas",
            font_size=20,
            bold=True,
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=None,
            height="40dp",
            halign='left'
        )
        main_layout.add_widget(titulo_lista)
        
        # ScrollView para a lista de aulas
        scroll = ScrollView()
        self.aulas_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10
        )
        self.aulas_layout.bind(minimum_height=self.aulas_layout.setter('height'))
        
        # Carrega e exibe as aulas
        self.carregar_aulas()
        
        scroll.add_widget(self.aulas_layout)
        main_layout.add_widget(scroll)
        
        # Botão de logout
        btn_logout = Button(
            text="Sair",
            background_color=[0.7, 0.7, 0.7, 1],
            color=[0, 0, 0, 1],
            size_hint_y=None,
            height="50dp",
            pos_hint={'center_x': 0.5}
        )
        btn_logout.bind(on_release=self.logout)
        main_layout.add_widget(btn_logout)
        
        self.add_widget(main_layout)
    
    def carregar_aulas(self):
        """Carrega e exibe as aulas do professor"""
        self.aulas_layout.clear_widgets()
        
        aulas = self.aulas_manager.obter_aulas()
        if not aulas:
            self.aulas_layout.add_widget(Label(
                text="Nenhuma aula criada ainda",
                color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None,
                height=50
            ))
            return
        
        for aula in aulas:
            # Layout para a aula (com botões de ação)
            aula_layout = BoxLayout(
                size_hint_y=None,
                height=70,
                spacing=10
            )
            
            # Botão com o título da aula
            btn_aula = Button(
                text=aula["titulo"],
                background_color=[0.9, 0.9, 0.9, 1],
                color=[0, 0, 0, 1],
                halign='left',
                valign='middle',
                text_size=(None, None)
            )
            btn_aula.bind(on_release=lambda instance, a=aula: self.abrir_aula(a))
            aula_layout.add_widget(btn_aula)
            
            # Layout para os botões de ação (Editar e Excluir)
            botoes_layout = BoxLayout(
                size_hint_x=None,
                width=150,
                spacing=5
            )
            
            # Botão Editar
            btn_editar = Button(
                text="EDITAR",
                background_color=[0.05, 0.15, 0.35, 1],
                color=[1, 1, 1, 1],
                size_hint_x=None,
                width=70
            )
            btn_editar.bind(on_release=lambda instance, a=aula: self.abrir_editar_aula(a))
            botoes_layout.add_widget(btn_editar)
            
            # Botão Excluir
            btn_excluir = Button(
                text="EXCLUIR",
                background_color=[0.8, 0.2, 0.2, 1],
                color=[1, 1, 1, 1],
                size_hint_x=None,
                width=70
            )
            btn_excluir.bind(on_release=lambda instance, a=aula: self.confirmar_exclusao(a))
            botoes_layout.add_widget(btn_excluir)
            
            aula_layout.add_widget(botoes_layout)
            self.aulas_layout.add_widget(aula_layout)
    
    def abrir_criar_aula(self, instance):
        """Abre a tela para criar uma nova aula"""
        screen = self.manager.get_screen('professor_criar_aula')
        screen.modo = 'criar'
        screen.aula_id = None
        # ✅ CORREÇÃO: Passa o nome do professor para a tela de criação de aula
        screen.nome_professor = self.nome_professor
        self.manager.current = 'professor_criar_aula'
    
    def abrir_editar_aula(self, aula):
        """Abre a tela para editar uma aula existente"""
        screen = self.manager.get_screen('professor_criar_aula')
        screen.modo = 'editar'
        screen.aula_id = aula['id']
        screen.nome_professor = self.nome_professor
        screen.preencher_campos(aula)
        self.manager.current = 'professor_criar_aula'
    
    def abrir_aula(self, aula):
        """Abre a tela para visualizar uma aula"""
        screen = self.manager.get_screen('professor_visualizar_aula')
        screen.carregar_aula(aula)
        self.manager.current = 'professor_visualizar_aula'
    
    def confirmar_exclusao(self, aula):
        """Confirma a exclusão de uma aula"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=f"Tem certeza que deseja excluir a aula '{aula['titulo']}'?",
            halign='center'
        ))
        
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        
        btn_cancelar = Button(text="Cancelar", size_hint_x=0.5)
        btn_cancelar.bind(on_release=lambda x: popup.dismiss())
        
        btn_confirmar = Button(text="Excluir", size_hint_x=0.5, background_color=[0.8, 0.2, 0.2, 1])
        btn_confirmar.bind(on_release=lambda x: self.excluir_aula(aula, popup))
        
        btn_layout.add_widget(btn_cancelar)
        btn_layout.add_widget(btn_confirmar)
        
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Confirmar Exclusão',
            content=content,
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def excluir_aula(self, aula, popup):
        """Exclui uma aula"""
        popup.dismiss()
        sucesso, mensagem = self.aulas_manager.excluir_aula(aula['id'])
        
        if sucesso:
            # Mostra mensagem de sucesso
            sucesso_popup = Popup(
                title='Sucesso',
                content=Label(text=mensagem),
                size_hint=(0.8, 0.3)
            )
            sucesso_popup.open()
            
            # Recarrega a lista de aulas
            self.carregar_aulas()
        else:
            # Mostra mensagem de erro
            erro_popup = Popup(
                title='Erro',
                content=Label(text=mensagem),
                size_hint=(0.8, 0.3)
            )
            erro_popup.open()
    
    def logout(self, instance):
        """Volta para a tela de login"""
        self.manager.current = 'login'