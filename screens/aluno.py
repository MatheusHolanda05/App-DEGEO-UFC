# screens/aluno.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import webbrowser
import os
import time
import threading
from utils.aulas_manager import AulasManager
from utils.atualizacoes_manager import AtualizacoesManager
import logging

# Configurar logging
logger = logging.getLogger('degeo_app')

class AlunoHomeScreen(Screen):
    def __init__(self, **kwargs):
        super(AlunoHomeScreen, self).__init__(**kwargs)
        self.name = "aluno_home"
        self.aulas_manager = AulasManager(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
        self.atualizacoes_manager = AtualizacoesManager(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
        
        # Mapeamento de botões para URLs e recursos
        self.botoes_info = {
            "noticias": {
                "nome": "Notícias", 
                "url": "https://geologia.ufc.br/pt/category/noticias/",
                "descricao": "Verifique as últimas notícias do departamento",
                "recurso": "noticias"
            },
            "calendario_academico": {
                "nome": "Calendário Acadêmico", 
                "url": "https://www.ufc.br/calendario-universitario/2025",
                "descricao": "Consulte o calendário universitário",
                "recurso": "calendario"
            },
            "revista": {
                "nome": "Revista", 
                "url": "https://www.periodicos.ufc.br/index.php/geologia",
                "descricao": "Acesse a revista do departamento",
                "recurso": "revista"
            },
            "graduacao": {
                "nome": "Graduação", 
                "url": "https://geologia.ufc.br/pt/graduacao/",
                "descricao": "Informações sobre o curso de graduação",
                "recurso": "graduacao"
            },
            "sobre_a_geologia": {
                "nome": "Sobre a Geologia", 
                "url": "https://geologia.ufc.br/pt/sobre-a-geologia/",
                "descricao": "Conheça mais sobre a geologia",
                "recurso": "sobre_geologia"
            },
            "sobre_o_departamento": {
                "nome": "Sobre o Departamento", 
                "url": "https://geologia.ufc.br/pt/sobre/",
                "descricao": "Saiba mais sobre nosso departamento",
                "recurso": "sobre_departamento"
            },
            "coordenacao": {
                "nome": "Coordenação", 
                "url": "https://geologia.ufc.br/pt/estrutura-organizacional-da-coordenacao-de-graduacao/",
                "descricao": "Contato com a coordenação de graduação",
                "recurso": "coordenacao"
            },
            "acessibilidade": {
                "nome": "Acessibilidade", 
                "url": "https://geologia.ufc.br/pt/acessibilidade/",
                "descricao": "Recursos de acessibilidade",
                "recurso": "acessibilidade"
            },
            "normas_ufc": {
                "nome": "Normas UFC", 
                "url": "https://geologia.ufc.br/pt/estatuto-regimento-e-normas-da-ufc/",
                "descricao": "Consulte as normas da UFC",
                "recurso": "normas_ufc"
            }
        }
        
        # Dicionário para armazenar os botões e seus indicadores
        self.botoes = {}
        self.indicadores = {}
        
        # Cache para evitar verificações excessivas
        self.ultima_verificacao = 0
        self.intervalo_minimo_verificacao = 300  # 5 minutos

    def on_enter(self, *args):
        """Método chamado quando a tela é exibida"""
        logger.debug("Construindo interface do aluno")
        Clock.schedule_once(self.construir_interface, 0)
        # Iniciar verificação periódica de atualizações
        Clock.schedule_interval(self.verificar_atualizacoes, self.intervalo_minimo_verificacao)

    def on_leave(self, *args):
        """Método chamado quando a tela é deixada"""
        # Cancelar verificações periódicas
        Clock.unschedule(self.verificar_atualizacoes)

    def construir_interface(self, dt=None):
        """Constrói a interface da tela inicial do aluno"""
        logger.debug("Interface do aluno construída com sucesso")

        # Limpa qualquer conteúdo anterior
        self.clear_widgets()

        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=30)

        # Título
        titulo = Label(
            text="Bem-vindo(a), Aluno(a)!",
            font_size=24,
            bold=True,
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=0.1,
            halign='center'
        )
        main_layout.add_widget(titulo)

        # Espaço após o título
        main_layout.add_widget(Widget(size_hint_y=0.05))

        # ScrollView para os botões
        scroll = ScrollView()
        botoes_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10
        )
        botoes_layout.bind(minimum_height=botoes_layout.setter('height'))

        # Botão de Aulas (especial - não tem URL)
        aulas_layout = BoxLayout(
            orientation='vertical',
            spacing=5,
            size_hint_y=None,
            height="70dp"
        )
        
        btn_aulas = Button(
            text="Aulas",
            background_color=[0.05, 0.15, 0.35, 1],
            color=[1, 1, 1, 1],
            size_hint_x=0.9
        )
        btn_aulas.bind(on_release=self.abrir_aulas)
        aulas_layout.add_widget(btn_aulas)
        
        descricao_label = Label(
            text="Acesse as aulas criadas pelos professores",
            color=[0.5, 0.5, 0.5, 1],
            size_hint_y=None,
            height=20,
            font_size=12,
            halign='center'
        )
        descricao_label.bind(size=descricao_label.setter('text_size'))
        aulas_layout.add_widget(descricao_label)
        
        # Indicador vazio para o botão de Aulas
        indicador_vazio = Label(
            text="",
            size_hint_y=None,
            height=20,
            opacity=0
        )
        aulas_layout.add_widget(indicador_vazio)
        
        botoes_layout.add_widget(aulas_layout)

        # Criar os botões para cada recurso com URL
        for chave, info in self.botoes_info.items():
            # Layout para o botão e descrição
            botao_layout = BoxLayout(
                orientation='vertical',
                spacing=5,
                size_hint_y=None,
                height="70dp"
            )

            # Botão principal
            btn = Button(
                text=info["nome"],
                background_color=[0.05, 0.15, 0.35, 1],
                color=[1, 1, 1, 1],
                size_hint_x=0.9
            )
            
            # Vincular a ação do botão
            btn.bind(on_release=lambda instance, c=chave: self.abrir_site(c))
            
            # Armazenar referência ao botão
            self.botoes[chave] = btn
            botao_layout.add_widget(btn)

            # Descrição do botão
            descricao_label = Label(
                text=info["descricao"],
                color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None,
                height=20,
                font_size=12,
                halign='center'
            )
            descricao_label.bind(size=descricao_label.setter('text_size'))
            botao_layout.add_widget(descricao_label)

            # Indicador de atualização (inicialmente oculto)
            indicador = Label(
                text="",
                color=[1, 1, 1, 1],
                size_hint_y=None,
                height=20,
                font_size=12,
                bold=True,
                opacity=0
            )
            botao_layout.add_widget(indicador)
            
            # Armazenar referência ao indicador
            self.indicadores[chave] = indicador

            botoes_layout.add_widget(botao_layout)

        # Calcular altura total para o layout dos botões
        altura_total = len(self.botoes_info) * 70 + 70  # +70 para o botão de Aulas
        botoes_layout.height = altura_total

        scroll.add_widget(botoes_layout)
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
        btn_voltar.bind(on_release=self.voltar_para_login)
        main_layout.add_widget(btn_voltar)

        self.add_widget(main_layout)

        # Iniciar verificação de atualizações
        self.verificar_atualizacoes()

    def verificar_atualizacoes(self, dt=None):
        """Verifica atualizações para todos os recursos"""
        logger.debug("Verificando atualizações")
        
        for chave, info in self.botoes_info.items():
            recurso = info["recurso"]
            url = info["url"]
            
            # Verificar se há atualizações
            def criar_callback(chave_recurso):
                def callback(quantidade):
                    self._atualizar_indicador(chave_recurso, quantidade)
                return callback
            
            self.atualizacoes_manager.verificar_atualizacao(
                recurso, 
                url, 
                criar_callback(chave)
            )

    def _atualizar_indicador(self, chave, quantidade):
        """Atualiza o indicador de notificação para um recurso específico"""
        if quantidade > 0 and chave in self.indicadores:
            indicador = self.indicadores[chave]
            indicador.text = str(quantidade)
            indicador.background_color = [1, 0, 0, 1]  # Fundo vermelho
            indicador.opacity = 1  # Torna visível
            logger.debug(f"Atualizações encontradas para {chave}: {quantidade}")
        elif chave in self.indicadores:
            self.indicadores[chave].opacity = 0  # Oculta o indicador

    def abrir_aulas(self, instance):
        """Abre a tela para selecionar professor/disciplina"""
        logger.info("Abrindo tela de seleção de professor/disciplina")
        self.manager.current = 'aluno_lista_professores'

    def abrir_site(self, chave):
        """Abre o site correspondente e marca como lido"""
        if chave in self.botoes_info:
            info = self.botoes_info[chave]
            logger.info(f"Abrindo {info['nome']}")
            
            # Marcar como lido
            if self.atualizacoes_manager.marcar_como_lido(info["recurso"]):
                # Atualizar indicador
                if chave in self.indicadores:
                    self.indicadores[chave].opacity = 0
            
            # Abrir site de forma assíncrona para evitar travamentos
            threading.Thread(
                target=lambda: webbrowser.open(info["url"], autoraise=True),
                daemon=True
            ).start()
        else:
            logger.warning(f"Chave não encontrada: {chave}")

    def voltar_para_login(self, instance):
        """Volta para a tela de login"""
        logger.info("Voltando para a tela de login")
        self.manager.current = 'login'