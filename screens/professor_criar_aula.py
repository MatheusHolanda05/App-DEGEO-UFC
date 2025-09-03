# screens/professor_criar_aula.py
import os
import logging
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

from utils.aulas_manager import AulasManager

# Configurar logging
logger = logging.getLogger('degeo_app')

class ProfessorCriarAulaScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfessorCriarAulaScreen, self).__init__(**kwargs)
        self.name = "professor_criar_aula"
        # Inicializa o aulas_manager o mais cedo possível
        self.aulas_manager = AulasManager(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
        self.modo = 'criar'  # 'criar' ou 'editar'
        self.aula_id = None
        self.arquivos_selecionados = []
        self.links_adicionados = []
        self.dados_aula_para_edicao = None
        self.nome_professor = ""
        self.popup_link = None
        self.popup_selecao = None # Referência para o popup de seleção de arquivos
        # Referências para layouts de listas
        self.arquivos_layout = None
        self.links_layout = None
        # Listas para botões de exclusão
        self.botoes_excluir_arquivo = []
        self.botoes_excluir_link = []
        # Referência para o FileChooser
        self.filechooser = None
        logger.debug("ProfessorCriarAulaScreen inicializada.")

    # ✅ CORREÇÃO: Resetar o estado da tela ao entrar
    def on_enter(self, *args):
        """Método chamado quando a tela é exibida"""
        logger.debug("Entrando na tela de criar/editar aula")
        # Resetar completamente o estado da tela para 'criar'
        self.modo = 'criar'
        self.aula_id = None
        self.arquivos_selecionados = []
        self.links_adicionados = []
        self.botoes_excluir_arquivo = []
        self.botoes_excluir_link = []
        self.popup_link = None
        self.popup_selecao = None

        # Obter o nome do professor da tela inicial, se necessário e não estiver definido
        # Esta parte pode variar dependendo de como você passa o nome
        # Exemplo robusto de tentativa de obter o nome:
        try:
            if not self.nome_professor:
                home_screen = self.manager.get_screen('professor_home')
                self.nome_professor = getattr(home_screen, 'nome_professor', "")
                logger.debug(f"Nome do professor obtido no on_enter: '{self.nome_professor}'")
        except Exception as e:
            logger.warning(f"Não foi possível obter o nome do professor no on_enter: {e}")
            # O nome do professor DEVE ser passado corretamente. Se não estiver aqui,
            # depende de ser passado antes de entrar na tela (por exemplo, na tela de visualização)
            # self.nome_professor = "" # Fallback - NÃO RECOMENDADO se for essencial

        # Agendar a construção da interface
        Clock.schedule_once(self.construir_interface, 0)

        # Preenche os campos se estivermos editando uma aula
        # Esta parte só deve ser executada se dados_aula_para_edicao estiver presente
        # e após a interface ser construída. on_enter é chamado antes de construir_interface terminar,
        # então é melhor agendar isso também ou fazer no final de construir_interface.
        # Vamos agendá-lo para depois da construção da interface.
        # Clock.schedule_once(lambda dt: self._tentar_preencher_campos(), 0.1)

    def _tentar_preencher_campos(self, dt=None):
        """Tenta preencher os campos após a interface ser construída"""
        if self.dados_aula_para_edicao:
            logger.debug("Dados de aula para edição encontrados em _tentar_preencher_campos.")
            # Verificar se os widgets de input básicos existem
            if hasattr(self, 'input_titulo') and self.input_titulo:
                 self.preencher_campos(self.dados_aula_para_edicao)
                 self.dados_aula_para_edicao = None # Limpar após usar
            else:
                 # Se ainda não existirem, tenta novamente em breve
                 Clock.schedule_once(self._tentar_preencher_campos, 0.1)


    def construir_interface(self, dt=None):
        """Constrói a interface da tela de criação/editar aula"""
        logger.debug(f"Construindo interface de {'edição' if self.modo == 'editar' else 'criação'} de aula")

        try:
            # Limpa qualquer conteúdo anterior
            self.clear_widgets()

            # Layout principal
            main_layout = BoxLayout(orientation='vertical', padding=30)

            # Título - Usar self.modo para determinar o texto
            titulo_texto = "Criar Nova Aula" if self.modo == 'criar' else "Editar Aula"
            titulo = Label(
                text=titulo_texto,
                font_size=24,
                bold=True,
                color=[0.05, 0.15, 0.35, 1],
                size_hint_y=0.1,
                halign='center'
            )
            main_layout.add_widget(titulo)

            # Espaço
            main_layout.add_widget(Widget(size_hint_y=0.05))

            # Campo Título (obrigatório)
            label_titulo = Label(
                text="Título*",
                color=[0.05, 0.15, 0.35, 1],
                size_hint_y=None,
                height=30,
                halign='left'
            )
            main_layout.add_widget(label_titulo)

            self.input_titulo = TextInput(
                multiline=False,
                font_size=16,
                size_hint_y=None,
                height=40
            )
            main_layout.add_widget(self.input_titulo)

            # Campo Disciplina
            label_disciplina = Label(
                text="Disciplina",
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

            # Campo Observações
            label_observacoes = Label(
                text="Observações",
                color=[0.05, 0.15, 0.35, 1],
                size_hint_y=None,
                height=30,
                halign='left'
            )
            main_layout.add_widget(label_observacoes)

            self.input_observacoes = TextInput(
                multiline=True,
                font_size=16,
                size_hint_y=None,
                height=100
            )
            main_layout.add_widget(self.input_observacoes)

            # Espaço
            main_layout.add_widget(Widget(size_hint_y=0.02))

            # Área para selecionar arquivos
            label_arquivos = Label(
                text="Adicionar Arquivos",
                font_size=18,
                bold=True,
                color=[0.05, 0.15, 0.35, 1],
                size_hint_y=None,
                height=30,
                halign='left'
            )
            main_layout.add_widget(label_arquivos)

            btn_adicionar_arquivo = Button(
                text="Adicionar Arquivo",
                background_color=[0.05, 0.15, 0.35, 1],
                color=[1, 1, 1, 1],
                size_hint_y=None,
                height="40dp"
            )
            btn_adicionar_arquivo.bind(on_release=self.abrir_selecao_arquivos)
            main_layout.add_widget(btn_adicionar_arquivo)

            # ✅ CORREÇÃO: Armazenar a referência do layout de arquivos
            self.arquivos_layout = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=100
            )
            main_layout.add_widget(self.arquivos_layout)

            # Espaço
            main_layout.add_widget(Widget(size_hint_y=0.02))

            # Área para adicionar links
            label_links = Label(
                text="Adicionar Links",
                font_size=18,
                bold=True,
                color=[0.05, 0.15, 0.35, 1],
                size_hint_y=None,
                height=30,
                halign='left'
            )
            main_layout.add_widget(label_links)

            btn_adicionar_link = Button(
                text="Adicionar Link",
                background_color=[0.05, 0.15, 0.35, 1],
                color=[1, 1, 1, 1],
                size_hint_y=None,
                height="40dp"
            )
            btn_adicionar_link.bind(on_release=self.abrir_adicao_link)
            main_layout.add_widget(btn_adicionar_link)

            # ✅ CORREÇÃO: Armazenar a referência do layout de links
            self.links_layout = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=100
            )
            main_layout.add_widget(self.links_layout)

            # Espaço
            main_layout.add_widget(Widget(size_hint_y=0.05))

            # Botão Salvar/Atualizar
            btn_texto = "CRIAR AULA" if self.modo == 'criar' else "ATUALIZAR AULA"
            btn_salvar = Button(
                text=btn_texto,
                background_color=[0.05, 0.15, 0.35, 1],
                color=[1, 1, 1, 1],
                size_hint_y=None,
                height="50dp"
            )
            btn_salvar.bind(on_release=self.salvar_aula)
            main_layout.add_widget(btn_salvar)

            # ✅ CORREÇÃO: Botão Voltar com vinculação correta
            btn_voltar = Button(
                text="Voltar",
                background_color=[0.7, 0.7, 0.7, 1],
                color=[0, 0, 0, 1],
                size_hint_y=None,
                height="50dp",
                pos_hint={'center_x': 0.5}
            )
            # ✅ CORREÇÃO: Vinculação direta para evitar problemas de escopo
            btn_voltar.bind(on_release=self.voltar_para_home)
            main_layout.add_widget(btn_voltar)

            self.add_widget(main_layout)
            
            # Atualizar listas após adicionar os layouts
            self.atualizar_lista_arquivos()
            self.atualizar_lista_links()

            # Preenche os campos se estivermos editando uma aula
            # Esta parte só deve ser executada se dados_aula_para_edicao estiver presente
            # Agora que a interface está construída, podemos tentar preencher
            if self.dados_aula_para_edicao:
                logger.debug("Dados de aula para edição encontrados, preenchendo...")
                # Agendamos para garantir que os widgets existam
                # Clock.schedule_once(lambda dt: self.preencher_campos(self.dados_aula_para_edicao), 0)
                # OU chamamos diretamente, pois os widgets básicos já devem existir
                # Verificar novamente por garantia
                if hasattr(self, 'input_titulo') and self.input_titulo:
                     self.preencher_campos(self.dados_aula_para_edicao)
                     self.dados_aula_para_edicao = None # Limpar após usar
                else:
                     # Se ainda não estiver pronto, tenta novamente
                     Clock.schedule_once(lambda dt: self.preencher_campos(self.dados_aula_para_edicao) if self.dados_aula_para_edicao else None, 0.1)
                     self.dados_aula_para_edicao = None # Limpar para evitar loop

            logger.debug("Interface construída com sucesso.")

        except Exception as e:
            logger.error(f"Erro crítico ao construir interface: {e}", exc_info=True)
            self.mostrar_erro(f"Erro ao construir a tela: {str(e)}")
            # Opcional: Voltar para uma tela segura
            # Clock.schedule_once(lambda dt: self.voltar_para_home(None), 1)


    # ✅ MÉTODO ADICIONADO: Voltar para a tela inicial do professor
    def voltar_para_home(self, instance):
        """Volta para a tela inicial do professor"""
        logger.info("Voltando para a tela inicial do professor")
        # Resetar estado ao voltar
        self.modo = 'criar'
        self.aula_id = None
        self.dados_aula_para_edicao = None
        self.manager.current = 'professor_home'


    # ✅ CORREÇÃO: Garantir que preencher_campos exista e funcione corretamente
    def preencher_campos(self, aula):
        """Preenche os campos com os dados da aula para edição"""
        logger.debug(f"Preenchendo campos para edição da aula ID: {aula.get('id')}")
        # Verificar se os widgets de input existem
        if not hasattr(self, 'input_titulo') or not self.input_titulo:
             logger.warning("Widgets de input não encontrados em preencher_campos.")
             # Não armazenar em dados_aula_para_edicao aqui, pois isso pode causar loop
             # Se os widgets não existirem, é porque a interface ainda não terminou de construir
             # Nesse caso, o on_enter ou o agendamento no construir_interface deve cuidar disso.
             return

        try:
            # Preencher campos de texto
            self.input_titulo.text = aula.get("titulo", "")
            self.input_disciplina.text = aula.get("disciplina", "")
            self.input_observacoes.text = aula.get("observacoes", "")
            
            # --- CORREÇÃO PARA EVITAR ARQUIVOS DUPLICADOS AO CARREGAR PARA EDIÇÃO ---
            # ✅ Processar arquivos
            # 1. Limpar a lista de arquivos selecionados desta sessão de edição
            self.arquivos_selecionados = []
            # 2. Usar um conjunto (set) para rastrear caminhos já adicionados e evitar duplicatas
            caminhos_adicionados = set()

            # 3. Iterar pelos arquivos salvos na aula
            for arquivo_info in aula.get("arquivos", []):
                caminho_relativo = arquivo_info.get("caminho", "")
                if caminho_relativo:
                    # 4. Construir o caminho absoluto completo para o arquivo no sistema de arquivos
                    #    Isso junta o diretório do projeto -> pasta 'data' -> caminho relativo salvo
                    #    NOTA: Usar self.aulas_manager.data_dir é mais robusto do que montar o caminho manualmente
                    caminho_completo = os.path.abspath(os.path.join(self.aulas_manager.data_dir, caminho_relativo))
                    
                    # 5. Verificar se o arquivo REALMENTE existe no disco
                    #    E se o caminho completo ainda não foi adicionado à lista desta sessão
                    #    Isso evita problemas se o arquivo foi deletado manualmente OU se está duplicado no JSON
                    if os.path.exists(caminho_completo) and caminho_completo not in caminhos_adicionados:
                        # 6. Adicionar o CAMINHO COMPLETO ABSOLUTO à lista desta sessão de edição
                        #    Este é o ponto CRÍTICO para garantir que operações de edição
                        #    (excluir, adicionar novos) trabalhem com a lista correta.
                        self.arquivos_selecionados.append(caminho_completo)
                        # 7. Registrar o caminho como adicionado no conjunto de controle
                        caminhos_adicionados.add(caminho_completo)
                        logger.debug(f"[Preencher campos - Edição ID {aula.get('id')}] Arquivo existente e ÚNICO adicionado: {caminho_completo}")
                    elif not os.path.exists(caminho_completo):
                        # Opcional: Logar arquivos ausentes
                        logger.warning(f"[Preencher campos - Edição ID {aula.get('id')}] Arquivo NÃO ENCONTRADO no disco: {caminho_completo}")
                    elif caminho_completo in caminhos_adicionados:
                         # Opcional: Logar arquivos duplicados ignorados
                         logger.info(f"[Preencher campos - Edição ID {aula.get('id')}] Arquivo IGNORADO (duplicado): {caminho_completo}")
            # --- FIM DA CORREÇÃO ---
            
            # ✅ Processar links (mantém a lógica existente)
            self.links_adicionados = aula.get("links", [])
            
            # Atualizar as listas na interface
            self.atualizar_lista_arquivos()
            self.atualizar_lista_links()
            
            # ✅ CORREÇÃO: Definir o modo e o ID para 'editar'
            self.modo = 'editar'
            self.aula_id = aula.get("id")
            # self.dados_aula_para_edicao = None # Limpar após usar - Feito no chamador
            logger.debug("Campos preenchidos com sucesso para edição.")
        except Exception as e:
             logger.error(f"Erro ao preencher campos para edição: {e}", exc_info=True)
             self.mostrar_erro(f"Erro ao carregar dados da aula: {str(e)}")


    # ... restante dos métodos ...
    def abrir_selecao_arquivos(self, instance):
        """Abre o seletor de arquivos"""
        content = BoxLayout(orientation='vertical')
        
        # FileChooser configurado corretamente
        self.filechooser = FileChooserListView(
            filters=['*.pdf', '*.pptx', '*.docx', '*.mp4', '*.jpg', '*.png', '*.txt', '*'], # Adicionado '*' para todos
            path=os.path.expanduser('~'),
            show_hidden=False
        )
        content.add_widget(self.filechooser)
        
        # Botões de ação
        btn_layout = BoxLayout(size_hint_y=None, height=50)
        
        btn_cancelar = Button(text="Cancelar")
        btn_cancelar.bind(on_release=lambda x: self.popup_selecao.dismiss() if self.popup_selecao else None)
        
        btn_selecionar = Button(text="Selecionar")
        btn_selecionar.bind(on_release=self.processar_selecao_arquivos)
        
        btn_layout.add_widget(btn_cancelar)
        btn_layout.add_widget(btn_selecionar)
        
        content.add_widget(btn_layout)
        
        # Cria e abre o popup
        self.popup_selecao = Popup(
            title='Selecionar Arquivos',
            content=content,
            size_hint=(0.9, 0.9)
        )
        self.popup_selecao.open()

    def processar_selecao_arquivos(self, instance):
        """Processa os arquivos selecionados"""
        if self.filechooser:
            selection = self.filechooser.selection
            if selection:
                # Adiciona apenas arquivos que ainda não estão na lista
                for arquivo in selection:
                    if arquivo not in self.arquivos_selecionados:
                        self.arquivos_selecionados.append(arquivo)
                self.atualizar_lista_arquivos()
        
        if self.popup_selecao:
            self.popup_selecao.dismiss()

    # ✅ CORREÇÃO: Atualizar atualizar_lista_arquivos para incluir botão de excluir
    def atualizar_lista_arquivos(self):
        """Atualiza a lista de arquivos selecionados"""
        # Limpar lista de botões de exclusão antigos
        self.botoes_excluir_arquivo = []
        
        if not self.arquivos_layout:
            logger.warning("Layout de arquivos não encontrado em atualizar_lista_arquivos")
            return
            
        self.arquivos_layout.clear_widgets()

        if not self.arquivos_selecionados:
            self.arquivos_layout.add_widget(Label(
                text="Nenhum arquivo selecionado",
                color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None,
                height=50
            ))
            return

        for i, arquivo in enumerate(self.arquivos_selecionados):
            item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
            
            nome_arquivo = os.path.basename(arquivo)
            label_arquivo = Label(
                text=nome_arquivo,
                color=[0.05, 0.15, 0.35, 1],
                size_hint_x=0.8,
                halign='left',
                valign='middle',
                text_size=(None, None)
            )
            item_layout.add_widget(label_arquivo)
            
            # Botão de excluir (ícone vermelho - usando texto 'X' por simplicidade)
            btn_excluir = Button(
                text='X', # Ícone de lixeira simples
                font_size=14,
                background_color=[0.8, 0.2, 0.2, 1], # Vermelho
                color=[1, 1, 1, 1],
                size_hint_x=0.2
            )
            # Passar o índice 'i' usando lambda default argument
            btn_excluir.bind(on_release=lambda instance, index=i: self.excluir_arquivo(index))
            item_layout.add_widget(btn_excluir)
            self.botoes_excluir_arquivo.append(btn_excluir) # Armazenar referência
            
            self.arquivos_layout.add_widget(item_layout)

    def abrir_adicao_link(self, instance):
        """Abre o popup para adicionar um link"""
        content = BoxLayout(orientation='vertical', padding=10)
        
        label = Label(
            text="Digite o título e a URL do link:",
            size_hint_y=None,
            height=30
        )
        content.add_widget(label)
        
        self.input_titulo_link = TextInput(
            hint_text="Título do link",
            multiline=False,
            font_size=16,
            size_hint_y=None,
            height=40
        )
        content.add_widget(self.input_titulo_link)
        
        self.input_url_link = TextInput(
            hint_text="URL (ex: https://example.com  )",
            multiline=False,
            font_size=16,
            size_hint_y=None,
            height=40
        )
        content.add_widget(self.input_url_link)
        
        buttons = BoxLayout(size_hint_y=None, height=50)
        
        btn_cancelar = Button(text="Cancelar")
        btn_cancelar.bind(on_release=lambda x: self.popup_link.dismiss() if self.popup_link else None)
        
        btn_adicionar = Button(text="Adicionar", background_color=[0.05, 0.15, 0.35, 1], color=[1, 1, 1, 1])
        btn_adicionar.bind(on_release=self.processar_link_adicionado)
        
        buttons.add_widget(btn_cancelar)
        buttons.add_widget(btn_adicionar)
        
        content.add_widget(buttons)
        
        self.popup_link = Popup(
            title="Adicionar Link",
            content=content,
            size_hint=(0.8, 0.4)
        )
        self.popup_link.open()

    def processar_link_adicionado(self, instance):
        """Processa o link adicionado"""
        titulo = self.input_titulo_link.text.strip() if self.input_titulo_link else ""
        url = self.input_url_link.text.strip() if self.input_url_link else ""
        
        if not titulo or not url:
            self.mostrar_erro("Título e URL são obrigatórios")
            return
        
        # Validar URL básica
        if not url.startswith("http://") and not url.startswith("https://"):
            self.mostrar_erro("URL inválida. Deve começar com http:// ou https://")
            return
        
        self.links_adicionados.append({"titulo": titulo, "url": url})
        self.atualizar_lista_links()
        if self.popup_link:
            self.popup_link.dismiss()  # Usa a referência armazenada

    # ✅ CORREÇÃO: Atualizar atualizar_lista_links para incluir botão de excluir
    def atualizar_lista_links(self):
        """Atualiza a lista de links adicionados"""
        # Limpar lista de botões de exclusão antigos
        self.botoes_excluir_link = []

        if not self.links_layout:
            logger.warning("Layout de links não encontrado em atualizar_lista_links")
            return

        self.links_layout.clear_widgets()

        if not self.links_adicionados:
            self.links_layout.add_widget(Label(
                text="Nenhum link adicionado",
                color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None,
                height=50
            ))
            return

        for i, link in enumerate(self.links_adicionados):
            item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
            
            label_link = Label(
                text=link.get("titulo", "Link sem título"),
                color=[0.05, 0.15, 0.35, 1],
                size_hint_x=0.8,
                halign='left',
                valign='middle',
                text_size=(None, None)
            )
            item_layout.add_widget(label_link)
            
            # Botão de excluir (ícone vermelho)
            btn_excluir = Button(
                text='X',
                font_size=14,
                background_color=[0.8, 0.2, 0.2, 1], # Vermelho
                color=[1, 1, 1, 1],
                size_hint_x=0.2
            )
            # Passar o índice 'i' usando lambda default argument
            btn_excluir.bind(on_release=lambda instance, index=i: self.excluir_link(index))
            item_layout.add_widget(btn_excluir)
            self.botoes_excluir_link.append(btn_excluir) # Armazenar referência
            
            self.links_layout.add_widget(item_layout)

    # ✅ CORREÇÃO: Adicionar métodos para excluir arquivos e links
    def excluir_arquivo(self, indice):
        """Exclui um arquivo da lista pelo índice"""
        logger.debug(f"[EXCLUIR_ARQUIVO] Solicitada exclusão do índice: {indice}")
        logger.debug(f"[EXCLUIR_ARQUIVO] Estado atual de self.arquivos_selecionados ANTES da exclusão: {self.arquivos_selecionados}")
        logger.debug(f"[EXCLUIR_ARQUIVO] Tamanho da lista ANTES: {len(self.arquivos_selecionados)}")

        # Verifica se o índice é válido
        if 0 <= indice < len(self.arquivos_selecionados):
            arquivo_removido = self.arquivos_selecionados[indice]
            logger.debug(f"[EXCLUIR_ARQUIVO] Arquivo a ser removido: {arquivo_removido}")
            # Remove o item da lista
            del self.arquivos_selecionados[indice]
            logger.debug(f"[EXCLUIR_ARQUIVO] Arquivo REMOVIDO com sucesso.")
        else:
            logger.error(f"[EXCLUIR_ARQUIVO] ÍNDICE INVÁLIDO: {indice}. Tamanho da lista: {len(self.arquivos_selecionados)}")
            self.mostrar_erro(f"Erro interno ao excluir arquivo (índice {indice}).")
            return # Sai da função se o índice for inválido

        logger.debug(f"[EXCLUIR_ARQUIVO] Estado de self.arquivos_selecionados APÓS a exclusão: {self.arquivos_selecionados}")
        logger.debug(f"[EXCLUIR_ARQUIVO] Tamanho da lista APÓS: {len(self.arquivos_selecionados)}")
        # Recria a lista visual (isso remove o botão)
        self.atualizar_lista_arquivos()
        logger.debug(f"[EXCLUIR_ARQUIVO] Lista visual de arquivos atualizada.")

    def excluir_link(self, indice):
        """Exclui um link da lista pelo índice"""
        if 0 <= indice < len(self.links_adicionados):
            logger.debug(f"Excluindo link no índice {indice}")
            del self.links_adicionados[indice]
            self.atualizar_lista_links() # Recria a lista, removendo o botão
        else:
            logger.warning(f"Índice de link inválido para exclusão: {indice}")

    def salvar_aula(self, instance):
        """Salva uma nova aula ou atualiza uma existente"""
        # Coleta os dados dos campos de input
        titulo = self.input_titulo.text.strip() if self.input_titulo else ""
        disciplina = self.input_disciplina.text.strip() if self.input_disciplina else ""
        observacoes = self.input_observacoes.text.strip() if self.input_observacoes else ""

        # Validações básicas
        if not titulo:
            self.mostrar_erro("O título é obrigatório")
            return

        # Determina se é criação ou edição e chama o método apropriado no aulas_manager
        if self.modo == 'criar':
            logger.info(f"Tentando CRIAR nova aula. Professor: '{self.nome_professor}'")
            sucesso, mensagem = self.aulas_manager.criar_aula(
                titulo=titulo,
                disciplina=disciplina,
                observacoes=observacoes,
                arquivos=self.arquivos_selecionados, # Passa a lista de caminhos de arquivos
                links=self.links_adicionados,       # Passa a lista de dicionários de links
                professor=self.nome_professor       # ✅ Passa o nome do professor logado
            )
        else: # self.modo == 'editar'
            logger.info(f"Tentando ATUALIZAR aula ID {self.aula_id}. Professor: '{self.nome_professor}'")
            # >>>>>>>>> LOG DE DEPURAÇÃO <<<<<<<<<
            logger.debug(f"[SALVAR_AULA - EDITAR] Estado FINAL de self.arquivos_selecionados ANTES de chamar atualizar_aula: {self.arquivos_selecionados}")
            logger.debug(f"[SALVAR_AULA - EDITAR] Tamanho da lista ANTES: {len(self.arquivos_selecionados)}")
            # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            sucesso, mensagem = self.aulas_manager.atualizar_aula(
                aula_id=self.aula_id,
                titulo=titulo,
                disciplina=disciplina,
                observacoes=observacoes,
                arquivos=self.arquivos_selecionados, # Passa os arquivos atuais (novos + mantidos)
                links=self.links_adicionados,       # Passa os links atuais (novos + mantidos)
                professor=self.nome_professor       # Passa o nome do professor logado (deve ser o mesmo)
            )
            logger.info(f"Tentando ATUALIZAR aula ID {self.aula_id}. Professor: '{self.nome_professor}'")
            sucesso, mensagem = self.aulas_manager.atualizar_aula(
                aula_id=self.aula_id,
                titulo=titulo,
                disciplina=disciplina,
                observacoes=observacoes,
                arquivos=self.arquivos_selecionados, # Passa os arquivos atuais (novos + mantidos)
                links=self.links_adicionados,       # Passa os links atuais (novos + mantidos)
                professor=self.nome_professor       # ✅ Passa o nome do professor logado (deve ser o mesmo)
            )

        # Trata o resultado da operação
        if sucesso:
            self.mostrar_sucesso("Aula salva com sucesso!")
            # ✅ CHAMADA AO MÉTODO QUE SERÁ DEFINIDO
            if self.modo == 'criar':
                self.limpar_campos() # Limpa os campos apenas após criação

            # Volta para a tela de visualização de aulas após salvar
            try:
                # Certifique-se de que o nome do professor está definido na tela de visualização
                visualizar_screen = self.manager.get_screen('professor_visualizar_aulas')
                # ✅ Garante que o nome do professor correto seja passado
                visualizar_screen.nome_professor = self.nome_professor
                self.manager.current = 'professor_visualizar_aulas'
            except Exception as e:
                logger.error(f"Erro ao voltar para a tela de visualização: {e}")
                # Fallback: Voltar para a tela inicial do professor
                self.voltar_para_home(instance)

        else:
            self.mostrar_erro(mensagem)

        """Salva uma nova aula ou atualiza uma existente"""
        # Coleta os dados dos campos de input
        titulo = self.input_titulo.text.strip() if self.input_titulo else ""
        disciplina = self.input_disciplina.text.strip() if self.input_disciplina else ""
        observacoes = self.input_observacoes.text.strip() if self.input_observacoes else ""

        # Validações básicas
        if not titulo:
            self.mostrar_erro("O título é obrigatório")
            return

        # Determina se é criação ou edição e chama o método apropriado no aulas_manager
        if self.modo == 'criar':
            logger.info(f"Tentando CRIAR nova aula. Professor: '{self.nome_professor}'")
            sucesso, mensagem = self.aulas_manager.criar_aula(
                titulo=titulo,
                disciplina=disciplina,
                observacoes=observacoes,
                arquivos=self.arquivos_selecionados, # Passa a lista de caminhos de arquivos
                links=self.links_adicionados,       # Passa a lista de dicionários de links
                professor=self.nome_professor       # Passa o nome do professor logado
            )
        else: # self.modo == 'editar'
            logger.info(f"Tentando ATUALIZAR aula ID {self.aula_id}. Professor: '{self.nome_professor}'")
            sucesso, mensagem = self.aulas_manager.atualizar_aula(
                aula_id=self.aula_id,
                titulo=titulo,
                disciplina=disciplina,
                observacoes=observacoes,
                arquivos=self.arquivos_selecionados, # Passa os arquivos atuais (novos + mantidos)
                links=self.links_adicionados,       # Passa os links atuais (novos + mantidos)
                professor=self.nome_professor       # Passa o nome do professor logado (deve ser o mesmo)
            )

        # Trata o resultado da operação
        if sucesso:
            self.mostrar_sucesso("Aula salva com sucesso!")
            # --- LINHA REMOVIDA: self.limpar_campos() ---
            # Se quiser limpar os campos manualmente aqui, faça-o diretamente, por exemplo:
            # if self.modo == 'criar':
            #     if self.input_titulo: self.input_titulo.text = ""
            #     if self.input_disciplina: self.input_disciplina.text = ""
            #     if self.input_observacoes: self.input_observacoes.text = ""
            #     self.arquivos_selecionados = []
            #     self.links_adicionados = []
            #     self.atualizar_lista_arquivos()
            #     self.atualizar_lista_links()

            # Volta para a tela de visualização de aulas após salvar
            try:
                # Certifique-se de que o nome do professor está definido na tela de visualização
                visualizar_screen = self.manager.get_screen('professor_visualizar_aulas')
                # Passa o nome do professor novamente, por garantia
                visualizar_screen.nome_professor = self.nome_professor
                self.manager.current = 'professor_visualizar_aulas'
            except Exception as e:
                logger.error(f"Erro ao voltar para a tela de visualização: {e}")
                # Fallback: Voltar para a tela inicial do professor
                self.voltar_para_home(instance)

        else:
            self.mostrar_erro(mensagem)

        """Salva uma nova aula ou atualiza uma existente"""
        # Coleta os dados dos campos de input
        titulo = self.input_titulo.text.strip() if self.input_titulo else ""
        disciplina = self.input_disciplina.text.strip() if self.input_disciplina else ""
        observacoes = self.input_observacoes.text.strip() if self.input_observacoes else ""

        # Validações básicas
        if not titulo:
            self.mostrar_erro("O título é obrigatório")
            return

        # Determina se é criação ou edição e chama o método apropriado no aulas_manager
        if self.modo == 'criar':
            logger.info(f"Tentando CRIAR nova aula. Professor: '{self.nome_professor}'")
            sucesso, mensagem = self.aulas_manager.criar_aula(
                titulo=titulo,
                disciplina=disciplina,
                observacoes=observacoes,
                arquivos=self.arquivos_selecionados, # Passa a lista de caminhos de arquivos
                links=self.links_adicionados,       # Passa a lista de dicionários de links
                professor=self.nome_professor       # ✅ Passa o nome do professor logado
            )
        else: # self.modo == 'editar'
            logger.info(f"Tentando ATUALIZAR aula ID {self.aula_id}. Professor: '{self.nome_professor}'")
            sucesso, mensagem = self.aulas_manager.atualizar_aula(
                aula_id=self.aula_id,
                titulo=titulo,
                disciplina=disciplina,
                observacoes=observacoes,
                arquivos=self.arquivos_selecionados, # Passa os arquivos atuais (novos + mantidos)
                links=self.links_adicionados,       # Passa os links atuais (novos + mantidos)
                professor=self.nome_professor       # ✅ Passa o nome do professor logado (deve ser o mesmo)
            )

        # Trata o resultado da operação
        if sucesso:
            self.mostrar_sucesso("Aula salva com sucesso!")
            # Limpa os campos se foi uma criação
            if self.modo == 'criar':
                self.limpar_campos()
                # Opcional: Atualizar a tela de visualização se estiver aberta
                # try:
                #     visualizar_screen = self.manager.get_screen('professor_visualizar_aulas')
                #     visualizar_screen.carregar_aulas() # Recarrega a lista
                # except Exception as e:
                #     logger.warning(f"Não foi possível atualizar a tela de visualização: {e}")

            # Volta para a tela de visualização de aulas após salvar
            try:
                # Certifique-se de que o nome do professor está definido na tela de visualização
                visualizar_screen = self.manager.get_screen('professor_visualizar_aulas')
                # Passa o nome do professor novamente, por garantia
                visualizar_screen.nome_professor = self.nome_professor
                self.manager.current = 'professor_visualizar_aulas'
            except Exception as e:
                logger.error(f"Erro ao voltar para a tela de visualização: {e}")
                # Fallback: Voltar para a tela inicial do professor
                self.voltar_para_home(instance)

        else:
            self.mostrar_erro(mensagem)

        """Salva uma nova aula ou atualiza uma existente"""
        titulo = self.input_titulo.text.strip() if self.input_titulo else ""
        disciplina = self.input_disciplina.text.strip() if self.input_disciplina else ""
        observacoes = self.input_observacoes.text.strip() if self.input_observacoes else ""
        
        # Validações
        if not titulo:
            self.mostrar_erro("O título é obrigatório")
            return
        
        # Verifica se estamos editando uma aula existente
        if self.modo == 'criar':
            sucesso, mensagem = self.aulas_manager.criar_aula(
                titulo=titulo,
                disciplina=disciplina,
                observacoes=observacoes,
                arquivos=self.arquivos_selecionados,
                links=self.links_adicionados,
                professor=self.nome_professor
            )
        else:
            sucesso, mensagem = self.aulas_manager.atualizar_aula(
                aula_id=self.aula_id,
                titulo=titulo,
                disciplina=disciplina,
                observacoes=observacoes,
                arquivos=self.arquivos_selecionados, # Passa os arquivos atuais
                links=self.links_adicionados,       # Passa os links atuais
                professor=self.nome_professor
            )
        
        if sucesso:
            self.mostrar_sucesso("Aula salva com sucesso!")
            # Limpa os campos para uma nova criação (a menos que estejamos editando)
            if self.modo == 'criar':
                self.input_titulo.text = ""
                self.input_disciplina.text = ""
                self.input_observacoes.text = ""
                self.arquivos_selecionados = []
                self.links_adicionados = []
                self.atualizar_lista_arquivos()
                self.atualizar_lista_links()
                # Opcionalmente, atualizar a tela de visualização
                try:
                    visualizar_screen = self.manager.get_screen('professor_visualizar_aulas')
                    # Se você quiser forçar uma atualização na tela de visualização
                    # Clock.schedule_once(lambda dt: setattr(visualizar_screen, 'nome_professor', self.nome_professor) or visualizar_screen.carregar_aulas(), 0.1)
                except Exception as e:
                    logger.warning(f"Não foi possível atualizar a tela de visualização após criação: {e}")
            else:
                # Volta para a tela de visualização após edição
                # Certifique-se de que o nome_professor está definido na tela de visualização
                try:
                    visualizar_screen = self.manager.get_screen('professor_visualizar_aulas')
                    # Atualizar o nome do professor na tela de visualização, se necessário
                    # visualizar_screen.nome_professor = self.nome_professor # Se não estiver definido
                    # Voltar para a tela de visualização
                    self.manager.current = 'professor_visualizar_aulas'
                except Exception as e:
                   logger.error(f"Erro ao voltar para a tela de visualização: {e}")
                   self.voltar_para_home(instance) # Fallback
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
    
    def mostrar_sucesso(self, mensagem):
        """Mostra uma mensagem de sucesso"""
        from kivy.uix.popup import Popup
        popup = Popup(
            title='Sucesso',
            content=Label(text=mensagem),
            size_hint=(0.8, 0.3)
        )
        popup.open()

    def limpar_campos(self):
        """Limpa todos os campos de entrada e listas da tela"""
        logger.debug("Limpando campos da tela de criação/edição de aula")
        try:
            # Limpa os TextInput
            if self.input_titulo:
                self.input_titulo.text = ""
            if self.input_disciplina:
                self.input_disciplina.text = ""
            if self.input_observacoes:
                self.input_observacoes.text = ""

            # Limpa as listas internas
            self.arquivos_selecionados = []
            self.links_adicionados = []

            # Atualiza as listas visuais na tela
            self.atualizar_lista_arquivos()
            self.atualizar_lista_links()

            logger.debug("Campos limpos com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao limpar campos: {e}", exc_info=True)
