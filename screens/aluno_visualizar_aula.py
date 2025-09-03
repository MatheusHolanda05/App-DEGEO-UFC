# screens/aluno_visualizar_aula.py
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

# Configuração de logs
logger = logging.getLogger('degeo_app')

class AlunoVisualizarAulaScreen(Screen):
    def __init__(self, **kwargs):
        super(AlunoVisualizarAulaScreen, self).__init__(**kwargs)
        self.name = "aluno_visualizar_aula"
        # ✅ ADIÇÃO: Atributo para armazenar a aula atual
        self.aula = None
        # ... outros atributos ...
        # Referências para widgets que serão preenchidos
        self.titulo_label = None
        self.observacoes_label = None
        self.arquivos_layout = None
        self.links_layout = None
        self.comentarios_layout = None
        logger.debug("AlunoVisualizarAulaScreen inicializada.")

    def on_enter(self, *args):
        """Método chamado quando a tela é exibida"""
        logger.debug("Construindo interface do aluno - MÉTODO PARA VISUALIZAR UMA AULA")
        Clock.schedule_once(self.construir_interface, 0)

    def carregar_aula(self, aula):
        """Carrega os dados da aula para visualização"""
        logger.debug(f"Carregando dados da aula: {aula.get('titulo', 'Sem título')}")
        self.aula = aula
        # Agenda a reconstrução da interface para usar os novos dados
        # Isso é importante se o método for chamado fora do on_enter
        Clock.schedule_once(self.construir_interface, 0)

    def construir_interface(self, dt=None):
        """Constrói a interface da tela de visualização da aula"""
        logger.debug("Construindo interface de visualização da aula")

        # Limpa qualquer conteúdo anterior
        self.clear_widgets()

        # ✅ VERIFICAÇÃO: Se não houver aula carregada, mostra erro e volta
        if not self.aula:
             self.mostrar_erro("Dados da aula não encontrados")
             # Agenda o retorno após um curto período
             Clock.schedule_once(lambda dt: self.voltar_para_lista_aulas(None), 2)
             return

        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=30)

        # Título da aula
        self.titulo_label = Label(
            text=self.aula.get("titulo", "Sem título"),
            font_size=24,
            bold=True,
            color=[0.05, 0.15, 0.35, 1],
            size_hint_y=0.1,
            halign='center'
        )
        main_layout.add_widget(self.titulo_label)

        # Espaço
        main_layout.add_widget(Widget(size_hint_y=0.02))

        # Observações
        if self.aula.get("observacoes", ""):
            label_observacoes = Label(
                text="Observações:",
                font_size=18,
                bold=True,
                color=[0.05, 0.15, 0.35, 1],
                size_hint_y=None,
                height=30,
                halign='left'
            )
            main_layout.add_widget(label_observacoes)

            self.observacoes_label = Label(
                text=self.aula["observacoes"],
                color=[0, 0, 0, 1],
                size_hint_y=None,
                height=80,
                halign='left',
                valign='top'
            )
            self.observacoes_label.bind(size=self.observacoes_label.setter('text_size'))
            main_layout.add_widget(self.observacoes_label)

        # Espaço
        main_layout.add_widget(Widget(size_hint_y=0.02))

        # Arquivos
        if self.aula.get("arquivos", []):
            label_arquivos = Label(
                text="Arquivos:",
                font_size=18,
                bold=True,
                color=[0.05, 0.15, 0.35, 1],
                size_hint_y=None,
                height=30,
                halign='left'
            )
            main_layout.add_widget(label_arquivos)

            # ScrollView para os arquivos
            scroll_arquivos = ScrollView()
            self.arquivos_layout = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                spacing=10
            )
            self.arquivos_layout.bind(minimum_height=self.arquivos_layout.setter('height'))

            for arquivo in self.aula["arquivos"]:
                # Caminho completo do arquivo (ajustar conforme a estrutura real)
                # CUIDADO: O caminho salvo em aulas.json é relativo a 'data'
                # Exemplo salvo: "arquivos/1/nome_arquivo.txt"
                # Caminho completo: C:\...\Aplicativo com python\data\arquivos\1\nome_arquivo.txt
                caminho_relativo = arquivo.get("caminho", "")
                if caminho_relativo:
                    # Construir caminho absoluto relativo ao diretório do script
                    caminho_completo = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", caminho_relativo))
                else:
                    caminho_completo = ""

                btn_arquivo = Button(
                    text=arquivo["nome"],
                    background_color=[0.9, 0.9, 0.9, 1],
                    color=[0, 0, 0, 1],
                    size_hint_y=None,
                    height="45dp"
                )
                # Vincula o clique à abertura do arquivo (implementar abrir_arquivo)
                # Passa o caminho completo
                btn_arquivo.bind(on_release=lambda instance, c=caminho_completo: self.abrir_arquivo(c))
                self.arquivos_layout.add_widget(btn_arquivo)

            scroll_arquivos.add_widget(self.arquivos_layout)
            main_layout.add_widget(scroll_arquivos)

        # Espaço
        main_layout.add_widget(Widget(size_hint_y=0.02))

        # Links
        if self.aula.get("links", []):
             label_links = Label(
                 text="Links:",
                 font_size=18,
                 bold=True,
                 color=[0.05, 0.15, 0.35, 1],
                 size_hint_y=None,
                 height=30,
                 halign='left'
             )
             main_layout.add_widget(label_links)

             # ScrollView para os links
             scroll_links = ScrollView()
             self.links_layout = BoxLayout(
                 orientation='vertical',
                 size_hint_y=None,
                 spacing=10
             )
             self.links_layout.bind(minimum_height=self.links_layout.setter('height'))

             for link_obj in self.aula["links"]: # Renomear 'link' para 'link_obj' para evitar conflito
                 titulo_link = link_obj.get("titulo", "Link sem título")
                 url_link = link_obj.get("url", "#")

                 btn_link = Button(
                     text=titulo_link,
                     background_color=[0.05, 0.15, 0.35, 1], # Azul UFC
                     color=[1, 1, 1, 1],
                     size_hint_y=None,
                     height="45dp"
                 )
                 # Vincula o clique à abertura do link (implementar abrir_link)
                 # Passa a URL
                 btn_link.bind(on_release=lambda instance, url=url_link: self.abrir_link(url))
                 self.links_layout.add_widget(btn_link)

             scroll_links.add_widget(self.links_layout)
             main_layout.add_widget(scroll_links)

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
        btn_voltar.bind(on_release=self.voltar_para_lista_aulas) # Voltar para a lista de aulas filtradas
        main_layout.add_widget(btn_voltar)

        self.add_widget(main_layout)

    def mostrar_erro(self, mensagem):
        """Mostra uma mensagem de erro"""
        from kivy.uix.popup import Popup
        popup = Popup(
            title='Erro',
            content=Label(text=mensagem),
            size_hint=(0.8, 0.3)
        )
        popup.open()

    def abrir_arquivo(self, caminho):
        """Abre o arquivo selecionado"""
        logger.info(f"Tentando abrir arquivo: {caminho}")
        if os.path.exists(caminho):
            try:
                # Tenta abrir o arquivo com o programa padrão
                os.startfile(caminho)  # Windows
                # Para outros sistemas, use subprocess.Popen(['xdg-open', caminho]) ou webbrowser.open(caminho)
            except Exception as e:
                logger.error(f"Erro ao abrir arquivo {caminho}: {e}")
                self.mostrar_erro("Erro ao abrir arquivo. Verifique se o aplicativo associado está instalado.")
        else:
             self.mostrar_erro("Arquivo não encontrado.")

    def abrir_link(self, url):
        """Abre o link selecionado"""
        logger.info(f"Tentando abrir link: {url}")
        import webbrowser
        try:
            webbrowser.open(url, autoraise=True)
        except Exception as e:
            logger.error(f"Erro ao abrir link {url}: {e}")
            self.mostrar_erro("Erro ao abrir link.")

    def voltar_para_lista_aulas(self, instance):
        """Volta para a tela de lista de aulas filtrada"""
        logger.info("Voltando para a tela de lista de aulas")
        self.manager.current = 'aluno_aulas' # Ou o nome correto da tela que lista as aulas filtradas

    def mostrar_sucesso(self, mensagem):
        """Mostra uma mensagem de sucesso"""
        from kivy.uix.popup import Popup
        popup = Popup(
            title='Sucesso',
            content=Label(text=mensagem),
            size_hint=(0.8, 0.3)
        )
        popup.open()
