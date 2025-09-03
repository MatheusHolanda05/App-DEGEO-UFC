# screens/aluno_cadastro.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from utils.usuarios_manager import UsuariosManager
import os

class AlunoCadastroScreen(Screen):
    def __init__(self, **kwargs):
        super(AlunoCadastroScreen, self).__init__(**kwargs)
        self.name = "aluno_cadastro"
        self.usuarios_manager = UsuariosManager(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
    
    def on_enter(self, *args):
        """Método chamado quando a tela é exibida"""
        Clock.schedule_once(self.construir_interface, 0)
    
    def construir_interface(self, dt=None):
        """Constrói a interface da tela de cadastro do aluno"""
        # Limpa qualquer conteúdo anterior
        self.clear_widgets()
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=30)
        
        # Título
        titulo = Label(
            text="Cadastro de Aluno",
            font_size=24,
            bold=True,
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=0.1,
            halign='center'
        )
        main_layout.add_widget(titulo)
        
        # Espaço
        main_layout.add_widget(Widget(size_hint_y=0.07))
        
        # Campo Nome
        label_nome = Label(
            text="Nome",
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=None,
            height=30,
            halign='left'
        )
        main_layout.add_widget(label_nome)
        
        self.input_nome = TextInput(
            multiline=False,
            font_size=16,
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(self.input_nome)
        
        # Campo Email
        label_email = Label(
            text="Email",
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=None,
            height=30,
            halign='left'
        )
        main_layout.add_widget(label_email)
        
        self.input_email = TextInput(
            multiline=False,
            font_size=16,
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(self.input_email)
        
        # Campo Senha
        label_senha = Label(
            text="Senha",
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=None,
            height=30,
            halign='left'
        )
        main_layout.add_widget(label_senha)
        
        self.input_senha = TextInput(
            multiline=False,
            password=True,
            font_size=16,
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(self.input_senha)
        
        # Campo Confirmar Senha
        label_confirmar_senha = Label(
            text="Confirmar Senha",
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=None,
            height=30,
            halign='left'
        )
        main_layout.add_widget(label_confirmar_senha)
        
        self.input_confirmar_senha = TextInput(
            multiline=False,
            password=True,
            font_size=16,
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(self.input_confirmar_senha)
        
        # Espaço
        main_layout.add_widget(Widget(size_hint_y=0.07))
        
        # Botão Cadastrar
        btn_cadastrar = Button(
            text="CADASTRAR",
            background_color=[0.05, 0.15, 0.35, 1],
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height="50dp"
        )
        btn_cadastrar.bind(on_release=self.cadastrar)
        main_layout.add_widget(btn_cadastrar)
        
        # Botão Voltar
        btn_voltar = Button(
            text="Voltar",
            background_color=[0.7, 0.7, 0.7, 1],
            color=[0, 0, 0, 1],
            size_hint_y=None,
            height="50dp",
            pos_hint={'center_x': 0.5}
        )
        btn_voltar.bind(on_release=lambda x: self.voltar_para_login())
        main_layout.add_widget(btn_voltar)
        
        self.add_widget(main_layout)
    
    def cadastrar(self, instance):
        """Realiza o cadastro do aluno"""
        nome = self.input_nome.text
        email = self.input_email.text
        senha = self.input_senha.text
        confirmar_senha = self.input_confirmar_senha.text
        
        # Validação dos campos
        if not nome or not email or not senha or not confirmar_senha:
            self.mostrar_erro("Todos os campos são obrigatórios")
            return
        
        if senha != confirmar_senha:
            self.mostrar_erro("As senhas não coincidem")
            return
        
        # Cadastra o usuário
        sucesso, mensagem = self.usuarios_manager.cadastrar_usuario(
            nome, email, senha, "aluno"
        )
        
        if sucesso:
            self.mostrar_sucesso("Cadastro realizado com sucesso!", self.voltar_para_login)
        else:
            self.mostrar_erro(mensagem)
    
    def mostrar_erro(self, mensagem):
        """Mostra uma mensagem de erro"""
        from kivy.uix.popup import Popup
        popup = Popup(
            title='Erro',
            content=Label(text=mensagem),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def mostrar_sucesso(self, mensagem, callback=None):
        """Mostra uma mensagem de sucesso"""
        from kivy.uix.popup import Popup
        content = BoxLayout(orientation='vertical', padding=10)
        
        content.add_widget(Label(text=mensagem))
        
        btn_layout = BoxLayout(size_hint_y=None, height=40)
        btn_ok = Button(text="OK")
        
        if callback:
            btn_ok.bind(on_release=lambda x: (popup.dismiss(), callback()))
        else:
            btn_ok.bind(on_release=lambda x: popup.dismiss())
        
        btn_layout.add_widget(btn_ok)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Sucesso',
            content=content,
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def voltar_para_login(self):
        """Volta para a tela de login"""
        self.manager.current = 'login'