# screens/login.py
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.clock import Clock
import webbrowser
import os

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.name = "login"
    
    def on_enter(self, *args):
        """Método chamado quando a tela é exibida"""
        Clock.schedule_once(self.construir_interface, 0)
    
    def construir_interface(self, dt=None):
        """Constrói a interface da tela de login conforme a versão original"""
        # Limpa qualquer conteúdo anterior
        self.clear_widgets()
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=20)
        
        # Layout para a logo (no topo)
        logo_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=0.3,
            spacing=10
        )
        
        # ✅ CORREÇÃO: Nome correto do arquivo da logo
        logo_filename = "logo_ufc.png"  # Nome correto do arquivo
        
        # Tentativa de carregar a logo da UFC
        try:
            # Caminho relativo à localização atual do arquivo
            logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", logo_filename)
            
            # Verifica se o arquivo existe
            if os.path.exists(logo_path):
                logo = Image(
                    source=logo_path,
                    size_hint_y=None,
                    height="100dp",
                    allow_stretch=True
                )
                logo_layout.add_widget(logo)
            else:
                # Tenta caminho alternativo (caso o app esteja rodando de outro diretório)
                logo_path = os.path.join("assets", logo_filename)
                if os.path.exists(logo_path):
                    logo = Image(
                        source=logo_path,
                        size_hint_y=None,
                        height="100dp",
                        allow_stretch=True
                    )
                    logo_layout.add_widget(logo)
                else:
                    raise FileNotFoundError(f"Arquivo não encontrado: {logo_path}")
        except Exception as e:
            # Se não conseguir carregar a imagem, mostra um texto explicativo
            logo_layout.add_widget(Label(
                text="Logo da UFC",
                color=[0.05, 0.15, 0.35, 1],
                size_hint_y=None,
                height="30dp",
                halign='center'
            ))
            print(f"Erro ao carregar logo: {e}")
        
        main_layout.add_widget(logo_layout)
        
        # Título do app (no meio)
        titulo = Label(
            text="DEGEO App",
            font_size=24,
            bold=True,
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=0.1,
            halign='center'
        )
        main_layout.add_widget(titulo)
        
        # Espaço entre o título e os botões
        main_layout.add_widget(Widget(size_hint_y=0.15))
        
        # Botão Aluno
        btn_aluno = Button(
            text="Área do Aluno",
            background_color=[0.05, 0.15, 0.35, 1],
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height="50dp"
        )
        btn_aluno.bind(on_release=self.ir_para_aluno)
        main_layout.add_widget(btn_aluno)
        
        # Espaçamento
        main_layout.add_widget(Widget(size_hint_y=0.02))
        
        # Botão Professor
        btn_professor = Button(
            text="Área do Professor",
            background_color=[0.05, 0.15, 0.35, 1],
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height="50dp"
        )
        btn_professor.bind(on_release=self.ir_para_professor)
        main_layout.add_widget(btn_professor)
        
        # Espaçamento antes do crédito
        main_layout.add_widget(Widget(size_hint_y=0.05))
        
        # Créditos do desenvolvedor (atualizado conforme solicitado)
        credito_texto = "O aplicativo DEGEO App foi desenvolvido por Matheus de Andrade Holanda, ex aluno do curso de Geologia da UFC (Matrícula 512224). Quer contribuir ou sugerir melhorias?"
        
        credito = Label(
            text=credito_texto,
            font_size=10,
            color=[0.6, 0.6, 0.6, 1],
            size_hint_y=None,
            height="30dp",
            halign='center',
            text_size=(320, None)
        )
        credito.bind(size=credito.setter('text_size'))
        main_layout.add_widget(credito)
        
        # Botão clicável para o repositório GitHub
        btn_github = Button(
            text="Acessar Repositório no GitHub",
            font_size=11,
            background_color=[0.3, 0.3, 0.3, 0.8],
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height="30dp"
        )
        btn_github.bind(on_release=self.abrir_github)
        main_layout.add_widget(btn_github)
        
        self.add_widget(main_layout)
    
    def ir_para_aluno(self, instance):
        """Vai para a tela do aluno"""
        self.manager.current = 'aluno_home'
    
    def ir_para_professor(self, instance):
        """Vai para a tela de login do professor"""
        self.manager.current = 'professor_login'
    
    def abrir_github(self, instance):
        """Abre o repositório no GitHub"""
        webbrowser.open("https://github.com/MatheusHolanda05/App-DEGEO-UFC")