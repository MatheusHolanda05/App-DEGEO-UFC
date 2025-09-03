# screens/professor_recuperar_senha.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time
import logging
import random
import json

# Configurar logging
logger = logging.getLogger('degeo_app')

class ProfessorRecuperarSenhaScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfessorRecuperarSenhaScreen, self).__init__(**kwargs)
        self.name = "professor_recuperar_senha"
        self.email = ""
    
    def on_enter(self, *args):
        """Método chamado quando a tela é exibida"""
        logger.info("Entrando na tela de recuperação de senha")
        Clock.schedule_once(self.construir_interface, 0)
    
    def construir_interface(self, dt=None):
        """Constrói a interface da tela de recuperação de senha"""
        logger.debug("Construindo interface de recuperação de senha")
        
        # Limpa qualquer conteúdo anterior
        self.clear_widgets()
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=30)
        
        # Título
        titulo = Label(
            text="Recuperar Senha",
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
            text="Digite seu email cadastrado para recuperar sua senha.",
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=0.1,
            halign='center',
            valign='middle'
        )
        instrucoes.bind(size=instrucoes.setter('text_size'))
        main_layout.add_widget(instrucoes)
        
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
        
        # Espaço
        main_layout.add_widget(Widget(size_hint_y=0.07))
        
        # Botão Enviar Código
        btn_enviar = Button(
            text="ENVIAR CÓDIGO",
            background_color=[0.05, 0.15, 0.35, 1],
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height="50dp"
        )
        btn_enviar.bind(on_release=self.enviar_codigo)
        main_layout.add_widget(btn_enviar)
        
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
    
    def validar_email(self, email):
        """Valida o formato do email"""
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(regex, email) is not None
    
    def enviar_codigo(self, instance):
        """Envia o código de recuperação para o email"""
        self.email = self.input_email.text.strip().lower()
        
        if not self.email:
            self.mostrar_erro("O email não pode estar vazio")
            return
        
        if not self.validar_email(self.email):
            self.mostrar_erro("Formato de email inválido")
            return
        
        # Verifica se o arquivo existe antes de tentar carregar
        professores_file = os.path.join(os.path.dirname(__file__), "..", "data", "professores.json")
        logger.info(f"Verificando arquivo de professores em: {professores_file}")
        
        if not os.path.exists(professores_file):
            logger.error("Arquivo professores.json não encontrado")
            self.mostrar_erro("Sistema de recuperação indisponível. Contate o administrador.")
            return
        
        # Verifica se o email existe no sistema
        professores = self.carregar_professores()
        
        # Adicionando logs detalhados
        logger.info(f"Total de professores carregados: {len(professores)}")
        for professor in professores:
            logger.debug(f"Professor no sistema: {professor.get('email', '').lower()}")
        
        # Comparação case-insensitive
        professor = next((p for p in professores if p.get("email", "").lower() == self.email), None)
        
        if not professor:
            logger.warning(f"Email não encontrado no sistema: {self.email}")
            self.mostrar_erro("Email não encontrado no sistema")
            return
        
        # Enviar código de recuperação de forma real
        sucesso, mensagem = self.enviar_codigo_real(self.email)
        
        if sucesso:
            # Vai para a tela de código de recuperação
            screen = self.manager.get_screen('professor_codigo_recuperacao')
            screen.email = self.email
            self.manager.current = 'professor_codigo_recuperacao'
        else:
            self.mostrar_erro(mensagem)
    
    def enviar_codigo_real(self, email):
        """Envia o código de recuperação por email de forma real"""
        logger.info(f"Tentando enviar código de recuperação para {email}")
        
        try:
            # Gerar código de recuperação
            codigo = str(random.randint(100000, 999999))
            tempo_expiracao = time.time() + 600  # 10 minutos para expirar
            
            # ✅ CORREÇÃO: Configurações do email - ATENÇÃO: CONFIGURE ESTAS CREDENCIAIS
            # Substitua "seuemail@gmail.com" pelo seu email real
            # Substitua "suasenha" pela sua senha ou senha de app
            SMTP_SERVER = "smtp.gmail.com"
            SMTP_PORT = 587
            SMTP_USER = "seuemail@gmail.com"
            SMTP_PASSWORD = "suasenha"
            
            # ✅ CORREÇÃO: Verificar se as credenciais estão configuradas
            if SMTP_USER == "seuemail@gmail.com" or SMTP_PASSWORD == "suasenha":
                logger.error("Credenciais SMTP não configuradas. Configure seu email e senha.")
                return False, "Erro de configuração: Credenciais SMTP não configuradas"
            
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = email
            msg['Subject'] = "Código de Recuperação - DEGEO App"
            
            corpo = f"""
            Olá,
            
            Você solicitou a recuperação de senha para o DEGEO App.
            
            Seu código de recuperação é: {codigo}
            
            Este código expirará em 10 minutos.
            
            Se você não solicitou esta recuperação, ignore este email.
            
            Atenciosamente,
            Equipe DEGEO
            """
            
            msg.attach(MIMEText(corpo, 'plain'))
            
            # Enviar email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_USER, email, msg.as_string())
            
            logger.info(f"Código de recuperação enviado com sucesso para {email}")
            
            # Armazenar o código e tempo de expiração
            screen = self.manager.get_screen('professor_codigo_recuperacao')
            screen.codigo = codigo
            screen.tempo_expiracao = tempo_expiracao
            
            return True, "Código enviado com sucesso!"
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Erro de autenticação SMTP: {str(e)}")
            return False, "Erro de autenticação. Verifique as credenciais SMTP."
        except Exception as e:
            logger.error(f"Erro ao enviar código de recuperação: {str(e)}", exc_info=True)
            return False, f"Erro ao enviar código: {str(e)}"
    
    def carregar_professores(self):
        """Carrega a lista de professores do arquivo JSON"""
        try:
            professores_file = os.path.join(os.path.dirname(__file__), "..", "data", "professores.json")
            logger.debug(f"Tentando carregar professores de: {professores_file}")
            
            # Garante que o diretório existe
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
    
    def mostrar_erro(self, mensagem):
        """Mostra uma mensagem de erro"""
        logger.error(f"Mensagem de erro exibida: {mensagem}")
        from kivy.uix.popup import Popup
        popup = Popup(
            title='Erro',
            content=Label(text=mensagem),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def voltar_para_login(self, instance):
        """Volta para a tela de login"""
        logger.info("Voltando para a tela de login")
        self.manager.current = 'login'