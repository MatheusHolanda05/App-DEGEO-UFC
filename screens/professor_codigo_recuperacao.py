# screens/professor_codigo_recuperacao.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
import time
import random  # ✅ CORREÇÃO: Importação necessária
import logging
import json  # Adicionado para carregar professores
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configurar logging
logger = logging.getLogger('degeo_app')

class ProfessorCodigoRecuperacaoScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfessorCodigoRecuperacaoScreen, self).__init__(**kwargs)
        self.name = "professor_codigo_recuperacao"
        self.email = ""
        self.codigo = ""
        self.tempo_expiracao = 0
    
    def on_enter(self, *args):
        """Método chamado quando a tela é exibida"""
        Clock.schedule_once(self.construir_interface, 0)
    
    def construir_interface(self, dt=None):
        """Constrói a interface da tela de código de recuperação"""
        # Limpa qualquer conteúdo anterior
        self.clear_widgets()
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=30)
        
        # Título
        titulo = Label(
            text="Código de Recuperação",
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
        tempo_restante = max(0, int(self.tempo_expiracao - time.time()))
        minutos = tempo_restante // 60
        segundos = tempo_restante % 60
        
        self.instrucoes = Label(  # ✅ CORREÇÃO: Armazenar referência para atualização
            text=f"Digite o código de 6 dígitos enviado para seu email. Tempo restante: {minutos:02d}:{segundos:02d}",
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=0.1,
            halign='center',
            valign='middle'
        )
        self.instrucoes.bind(size=self.instrucoes.setter('text_size'))
        main_layout.add_widget(self.instrucoes)
        
        # Campo Código
        label_codigo = Label(
            text="Código",
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=None,
            height=30,
            halign='left'
        )
        main_layout.add_widget(label_codigo)
        
        # ✅ CORREÇÃO: Removido o input_filter='int'
        self.input_codigo = TextInput(
            multiline=False,
            font_size=16,
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(self.input_codigo)
        
        # Espaço
        main_layout.add_widget(Widget(size_hint_y=0.07))
        
        # Botão Verificar
        btn_verificar = Button(
            text="VERIFICAR CÓDIGO",
            background_color=[0.05, 0.15, 0.35, 1],
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height="50dp"
        )
        btn_verificar.bind(on_release=self.verificar_codigo)
        main_layout.add_widget(btn_verificar)
        
        # Botão Reenviar Código
        btn_reenviar = Button(
            text="REENVIAR CÓDIGO",
            background_color=[0.9, 0.9, 0.9, 1],
            color=[0, 0, 0, 1],
            size_hint_y=None,
            height="50dp"
        )
        btn_reenviar.bind(on_release=self.reenviar_codigo)
        main_layout.add_widget(btn_reenviar)
        
        # Botão Voltar
        btn_voltar = Button(
            text="Voltar",
            background_color=[0.7, 0.7, 0.7, 1],
            color=[0, 0, 0, 1],
            size_hint_y=None,
            height="50dp",
            pos_hint={'center_x': 0.5}
        )
        btn_voltar.bind(on_release=self.voltar_para_recuperar_senha)
        main_layout.add_widget(btn_voltar)
        
        self.add_widget(main_layout)
        
        # Atualiza o contador de tempo
        Clock.schedule_interval(self.atualizar_tempo, 1)
    
    def atualizar_tempo(self, dt):
        """Atualiza o contador de tempo restante"""
        tempo_restante = max(0, int(self.tempo_expiracao - time.time()))
        
        if tempo_restante <= 0:
            # O tempo expirou
            self.mostrar_erro("O código expirou. Por favor, solicite um novo código.")
            Clock.unschedule(self.atualizar_tempo)
            return
        
        minutos = tempo_restante // 60
        segundos = tempo_restante % 60
        
        if hasattr(self, 'instrucoes'):
            self.instrucoes.text = f"Digite o código de 6 dígitos enviado para seu email. Tempo restante: {minutos:02d}:{segundos:02d}"
    
    def verificar_codigo(self, instance):
        """Verifica se o código digitado está correto"""
        codigo_digitado = self.input_codigo.text
        
        if time.time() > self.tempo_expiracao:
            self.mostrar_erro("O código expirou. Por favor, solicite um novo código.")
            return
        
        if codigo_digitado == self.codigo:
            # Código correto
            self.ir_para_nova_senha()
        else:
            self.mostrar_erro("Código incorreto. Tente novamente.")
    
    def reenviar_codigo(self, instance):
        """Reenvia o código de recuperação"""
        # ✅ CORREÇÃO: random já está importado
        self.codigo = str(random.randint(100000, 999999))
        self.tempo_expiracao = time.time() + 600  # 10 minutos para expirar
        
        # ✅ CORREÇÃO: Enviar código de forma real
        sucesso, mensagem = self.enviar_codigo_real(self.email)
        
        if sucesso:
            self.mostrar_sucesso(f"Novo código enviado para {self.email}.")
        else:
            self.mostrar_erro(mensagem)
    
    def enviar_codigo_real(self, email):
        """Envia o código de recuperação por email de forma real"""
        logger.info(f"Tentando reenviar código de recuperação para {email}")
        
        try:
            # Configurações do email
            SMTP_SERVER = "smtp.gmail.com"
            SMTP_PORT = 587
            SMTP_USER = "seuemail@gmail.com"
            SMTP_PASSWORD = "suasenha"
            
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = email
            msg['Subject'] = "Código de Recuperação - DEGEO App"
            
            corpo = f"""
            Olá,
            
            Você solicitou a recuperação de senha para o DEGEO App.
            
            Seu código de recuperação é: {self.codigo}
            
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
            
            logger.info(f"Novo código de recuperação enviado com sucesso para {email}")
            return True, "Novo código enviado com sucesso!"
        except Exception as e:
            logger.error(f"Erro ao enviar novo código de recuperação: {str(e)}", exc_info=True)
            return False, f"Erro ao enviar código: {str(e)}"
    
    def ir_para_nova_senha(self):
        """Vai para a tela de nova senha"""
        screen = self.manager.get_screen('professor_nova_senha')
        screen.email = self.email
        self.manager.current = 'professor_nova_senha'
    
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
    
    def voltar_para_recuperar_senha(self, instance):
        """Volta para a tela de recuperação de senha"""
        self.manager.current = 'professor_recuperar_senha'