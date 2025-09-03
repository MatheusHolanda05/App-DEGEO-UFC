# screens/professor_login.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
import os
import json
import hashlib
import logging

# Configurar logging
logger = logging.getLogger('degeo_app')

class ProfessorLoginScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfessorLoginScreen, self).__init__(**kwargs)
        self.name = "professor_login"
    
    def on_enter(self, *args):
        """Método chamado quando a tela é exibida"""
        Clock.schedule_once(self.construir_interface, 0)
    
    def construir_interface(self, dt=None):
        """Constrói a interface da tela de login do professor"""
        # Limpa qualquer conteúdo anterior
        self.clear_widgets()
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=30)
        
        # Título
        titulo = Label(
            text="Área do Professor",
            font_size=24,
            bold=True,
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=0.1,
            halign='center'
        )
        main_layout.add_widget(titulo)
        
        # Espaço
        main_layout.add_widget(Widget(size_hint_y=0.07))
        
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
        
        # Espaço
        main_layout.add_widget(Widget(size_hint_y=0.07))
        
        # Botão Login
        btn_login = Button(
            text="LOGIN",
            background_color=[0.05, 0.15, 0.35, 1],
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height="50dp"
        )
        btn_login.bind(on_release=self.fazer_login)
        main_layout.add_widget(btn_login)
        
        # Botão Esqueci minha senha
        btn_esqueci = Button(
            text="Esqueci minha senha",
            background_color=[0.9, 0.9, 0.9, 1],
            color=[0, 0, 0, 1],
            size_hint_y=None,
            height="40dp"
        )
        btn_esqueci.bind(on_release=self.ir_para_recuperar_senha)
        main_layout.add_widget(btn_esqueci)
        
        # ✅ CORREÇÃO: Botão Cadastrar (adicionado novamente)
        btn_cadastrar = Button(
            text="CADASTRAR",
            background_color=[0.9, 0.9, 0.9, 1],
            color=[0, 0, 0, 1],
            size_hint_y=None,
            height="40dp"
        )
        btn_cadastrar.bind(on_release=self.ir_para_cadastro)
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
        btn_voltar.bind(on_release=self.voltar_para_login)
        main_layout.add_widget(btn_voltar)
        
        self.add_widget(main_layout)
    
    def fazer_login(self, instance):
        """Realiza o login do professor"""
        email = self.input_email.text.strip().lower()
        senha = self.input_senha.text.strip()
        
        if not email or not senha:
            self.mostrar_erro("Email e senha são obrigatórios")
            return
        
        professores = self.carregar_professores()
        
        # Verifica se há professores cadastrados
        if not professores:
            # ✅ CORREÇÃO: Cria o arquivo se não existir com um professor de exemplo
            logger.warning("Nenhum professor encontrado. Criando arquivo com professor de exemplo.")
            senha_hash = hashlib.sha256("123456".encode()).hexdigest()
            professores = [{
                "nome": "Professor Exemplo",
                "email": "professor@ufc.br",
                "senha_hash": senha_hash
            }]
            self.salvar_professores(professores)
        
        # Comparação case-insensitive
        professor = next((p for p in professores if p.get("email", "").lower() == email), None)
        
        if not professor:
            self.mostrar_erro("Email ou senha incorretos")
            return
        
        # Verifica a senha (comparação segura)
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        if senha_hash != professor["senha_hash"]:
            self.mostrar_erro("Email ou senha incorretos")
            return
        
        logger.info(f"Login bem-sucedido para professor: {professor['nome']}")
        
        # Armazena o nome do professor para uso posterior
        home_screen = self.manager.get_screen('professor_home')
        home_screen.nome_professor = professor['nome']
        
        # Vai para a tela inicial do professor
        self.manager.current = 'professor_home'
    
    def ir_para_recuperar_senha(self, instance):
        """Vai para a tela de recuperação de senha"""
        self.manager.current = 'professor_recuperar_senha'
    
    # ✅ CORREÇÃO: Método adicionado para ir para a tela de cadastro
    def ir_para_cadastro(self, instance):
        """Vai para a tela de cadastro de professor"""
        self.manager.current = 'professor_cadastro'
    
    def voltar_para_login(self, instance):
        """Volta para a tela de login"""
        self.manager.current = 'login'
    
    def carregar_professores(self):
        """Carrega a lista de professores do arquivo JSON"""
        try:
            professores_file = os.path.join(os.path.dirname(__file__), "..", "data", "professores.json")
            logger.debug(f"Tentando carregar professores de: {professores_file}")
            
            # ✅ CORREÇÃO: Garante que o diretório existe
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
            if not os.path.exists(data_dir):
                logger.info(f"Criando diretório de dados: {data_dir}")
                os.makedirs(data_dir, exist_ok=True)
            
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
            
            # ✅ CORREÇÃO: Garante que o diretório existe
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
            if not os.path.exists(data_dir):
                logger.info(f"Criando diretório de dados: {data_dir}")
                os.makedirs(data_dir, exist_ok=True)
            
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