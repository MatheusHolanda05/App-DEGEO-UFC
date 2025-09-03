# screens/professor_cadastro.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock
import os
import json
import hashlib
import logging
import re

# Configurar logging
logger = logging.getLogger('degeo_app')

class ProfessorCadastroScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfessorCadastroScreen, self).__init__(**kwargs)
        self.name = "professor_cadastro"
        self.usuarios_manager = None
        self.genero_selecionado = None  # Para armazenar o gênero selecionado
        # Referências para os checkboxes e retângulos de fundo
        self.chk_feminino = None
        self.chk_masculino = None
        self.chk_outros = None
        self.feminino_bg_rect = None
        self.masculino_bg_rect = None
        self.outros_bg_rect = None

    def on_enter(self, *args):
        """Método chamado quando a tela é exibida"""
        Clock.schedule_once(self.construir_interface, 0)

    def construir_interface(self, dt=None):
        """Constrói a interface da tela de cadastro do professor"""
        # Limpa qualquer conteúdo anterior
        self.clear_widgets()

        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=30)

        # Título
        titulo = Label(
            text="Cadastro de Professor",
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
            text="Nome*",
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
            text="Email*",
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

        # Campo Disciplina
        label_disciplina = Label(
            text="Disciplina*", # Texto obrigatório
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=None,
            height=30,
            halign='left'
        )
        main_layout.add_widget(label_disciplina)

        self.input_disciplina = TextInput(
            multiline=False,
            font_size=16,
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(self.input_disciplina)

        # Campo Senha
        label_senha = Label(
            text="Senha*",
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
        label_confirmar = Label(
            text="Confirmar Senha*",
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=None,
            height=30,
            halign='left'
        )
        main_layout.add_widget(label_confirmar)

        self.input_confirmar = TextInput(
            multiline=False,
            password=True,
            font_size=16,
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(self.input_confirmar)

        # ✅ CORREÇÃO: Adicionando as opções de gênero abaixo do campo "Confirmar Senha"
        # ✅ COM FUNDO PARA OS CHECKBOXES - IMPLEMENTAÇÃO CORRETA
        label_genero = Label(
            text="Gênero*",
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=None,
            height=30,
            halign='left'
        )
        main_layout.add_widget(label_genero)

        # Layout para as opções de gênero
        genero_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=10
        )

        # --- Opção Feminino ---
        feminino_layout = BoxLayout(
            orientation='horizontal',
            size_hint_x=0.33
        )
        # Criar o retângulo de fundo
        with feminino_layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.9, 0.9, 0.9, 1) # Cinza claro
            self.feminino_bg_rect = Rectangle(size=feminino_layout.size, pos=feminino_layout.pos)

        # Vincular a atualização do retângulo às mudanças de tamanho/posição
        def _update_feminino_bg(instance, value):
            if self.feminino_bg_rect:
                self.feminino_bg_rect.pos = instance.pos
                self.feminino_bg_rect.size = instance.size
        feminino_layout.bind(size=_update_feminino_bg, pos=_update_feminino_bg)

        self.chk_feminino = CheckBox(
            size_hint_x=None,
            width=30
        )
        self.chk_feminino.bind(active=self.selecionar_genero)
        feminino_layout.add_widget(self.chk_feminino)
        feminino_layout.add_widget(Label(
            text="Feminino",
            color=[0, 0, 0, 1],
            size_hint_x=0.7
        ))
        genero_layout.add_widget(feminino_layout)

        # --- Opção Masculino ---
        masculino_layout = BoxLayout(
            orientation='horizontal',
            size_hint_x=0.33
        )
        with masculino_layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.9, 0.9, 0.9, 1) # Cinza claro
            self.masculino_bg_rect = Rectangle(size=masculino_layout.size, pos=masculino_layout.pos)

        def _update_masculino_bg(instance, value):
            if self.masculino_bg_rect:
                self.masculino_bg_rect.pos = instance.pos
                self.masculino_bg_rect.size = instance.size
        masculino_layout.bind(size=_update_masculino_bg, pos=_update_masculino_bg)

        self.chk_masculino = CheckBox(
            size_hint_x=None,
            width=30
        )
        self.chk_masculino.bind(active=self.selecionar_genero)
        masculino_layout.add_widget(self.chk_masculino)
        masculino_layout.add_widget(Label(
            text="Masculino",
            color=[0, 0, 0, 1],
            size_hint_x=0.7
        ))
        genero_layout.add_widget(masculino_layout)

        # --- Opção Outros ---
        outros_layout = BoxLayout(
            orientation='horizontal',
            size_hint_x=0.33
        )
        with outros_layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.9, 0.9, 0.9, 1) # Cinza claro
            self.outros_bg_rect = Rectangle(size=outros_layout.size, pos=outros_layout.pos)

        def _update_outros_bg(instance, value):
            if self.outros_bg_rect:
                self.outros_bg_rect.pos = instance.pos
                self.outros_bg_rect.size = instance.size
        outros_layout.bind(size=_update_outros_bg, pos=_update_outros_bg)

        self.chk_outros = CheckBox(
            size_hint_x=None,
            width=30
        )
        self.chk_outros.bind(active=self.selecionar_genero)
        outros_layout.add_widget(self.chk_outros)
        outros_layout.add_widget(Label(
            text="Outros",
            color=[0, 0, 0, 1],
            size_hint_x=0.7
        ))
        genero_layout.add_widget(outros_layout)

        main_layout.add_widget(genero_layout)

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
        btn_cadastrar.bind(on_release=self.realizar_cadastro)
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

    # ✅ CORREÇÃO: Função de seleção simplificada sem 'group'
    def selecionar_genero(self, checkbox, value):
        """Seleciona o gênero do professor, garantindo que apenas um esteja marcado"""
        if value:  # Se o checkbox foi marcado
            # Desmarcar os outros
            if checkbox != self.chk_feminino:
                self.chk_feminino.active = False
            if checkbox != self.chk_masculino:
                self.chk_masculino.active = False
            if checkbox != self.chk_outros:
                self.chk_outros.active = False

            # Atualizar o gênero selecionado com base no checkbox
            if checkbox == self.chk_feminino:
                self.genero_selecionado = "Feminino"
            elif checkbox == self.chk_masculino:
                self.genero_selecionado = "Masculino"
            elif checkbox == self.chk_outros:
                self.genero_selecionado = "Outros"

    def validar_email(self, email):
        """Valida o formato do email"""
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(regex, email) is not None

    def carregar_professores(self):
        """Carrega a lista de professores do arquivo JSON"""
        professores_file = os.path.join(os.path.dirname(__file__), "..", "data", "professores.json")
        try:
            if os.path.exists(professores_file):
                with open(professores_file, 'r') as f:
                    return json.load(f)
            else:
                return []
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

    def realizar_cadastro(self, instance):
        """Realiza o cadastro do professor"""
        nome = self.input_nome.text.strip()
        email = self.input_email.text.strip().lower()
        # ✅ ADIÇÃO: Obter o valor do campo disciplina
        disciplina = self.input_disciplina.text.strip() # ✅ NOVO
        senha = self.input_senha.text.strip()
        confirmar = self.input_confirmar.text.strip()
        
        # Validações básicas
        if not nome:
            self.mostrar_erro("O nome é obrigatório")
            return
            
        if not self.validar_email(email):
            self.mostrar_erro("Email inválido")
            return
            
        # ✅ ADIÇÃO: Validação da disciplina
        if not disciplina:
            self.mostrar_erro("A disciplina é obrigatória")
            return
            
        if not senha:
            self.mostrar_erro("A senha é obrigatória")
            return
            
        if senha != confirmar:
            self.mostrar_erro("As senhas não coincidem")
            return
            
        if not self.genero_selecionado:
            self.mostrar_erro("Selecione um gênero")
            return

        # Cria o hash da senha
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()

        # Adiciona o novo professor
        novo_professor = {
            "id": str(hashlib.md5(email.encode()).hexdigest()),  # ID único baseado no email
            "nome": nome,
            "email": email,
            "senha_hash": senha_hash,
            # ✅ ADIÇÃO: Adicionar a disciplina aos dados do professor
            "disciplina": disciplina, # ✅ NOVO
            "genero": self.genero_selecionado,
            "tipo": "professor"
        }

        # Carrega professores existentes
        professores = self.carregar_professores()
        
        # Verifica se o email já existe
        if any(p["email"] == email for p in professores):
            self.mostrar_erro("Este email já está cadastrado")
            return
            
        # Adiciona o novo professor à lista
        professores.append(novo_professor)
        self.salvar_professores(professores)

        self.mostrar_sucesso("Cadastro realizado com sucesso!")
        self.voltar_para_login(instance)

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