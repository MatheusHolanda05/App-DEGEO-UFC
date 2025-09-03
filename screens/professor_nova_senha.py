# screens/professor_nova_senha.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from utils.usuarios_manager import UsuariosManager
import os

class ProfessorNovaSenhaScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfessorNovaSenhaScreen, self).__init__(**kwargs)
        self.name = "professor_nova_senha"
        self.usuarios_manager = UsuariosManager(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
        self.email = ""
    
    def on_enter(self, *args):
        """Método chamado quando a tela é exibida"""
        Clock.schedule_once(self.construir_interface, 0)
    
    def construir_interface(self, dt=None):
        """Constrói a interface da tela de nova senha"""
        # Limpa qualquer conteúdo anterior
        self.clear_widgets()
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=30)
        
        # Título
        titulo = Label(
            text="Nova Senha",
            font_size=24,
            bold=True,
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=0.1,
            halign='center'
        )
        main_layout.add_widget(titulo)
        
        # Espaço
        main_layout.add_widget(Widget(size_hint_y=0.07))
        
        # Instruções
        instrucoes = Label(
            text="Digite sua nova senha abaixo.",
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=0.1,
            halign='center',
            valign='middle'
        )
        instrucoes.bind(size=instrucoes.setter('text_size'))
        main_layout.add_widget(instrucoes)
        
        # Campo Nova Senha
        label_nova_senha = Label(
            text="Nova Senha",
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=None,
            height=30,
            halign='left'
        )
        main_layout.add_widget(label_nova_senha)
        
        self.input_nova_senha = TextInput(
            multiline=False,
            password=True,
            font_size=16,
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(self.input_nova_senha)
        
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
        
        # Botão Alterar Senha
        btn_alterar = Button(
            text="ALTERAR SENHA",
            background_color=[0.05, 0.15, 0.35, 1],
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height="50dp"
        )
        btn_alterar.bind(on_release=self.alterar_senha)
        main_layout.add_widget(btn_alterar)
        
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
    
    def alterar_senha(self, instance):
        """Altera a senha do professor"""
        nova_senha = self.input_nova_senha.text
        confirmar_senha = self.input_confirmar_senha.text
        
        # Validação
        if not nova_senha or not confirmar_senha:
            self.mostrar_erro("Todos os campos são obrigatórios")
            return
        
        if nova_senha != confirmar_senha:
            self.mostrar_erro("As senhas não coincidem")
            return
        
        if len(nova_senha) < 6:
            self.mostrar_erro("A senha deve ter pelo menos 6 caracteres")
            return
        
        # Altera a senha
        sucesso, mensagem = self.usuarios_manager.alterar_senha(self.email, nova_senha)
        
        if sucesso:
            self.mostrar_sucesso(
                "Senha alterada com sucesso!",
                self.voltar_para_login
            )
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
        self.manager.current = 'professor_login'