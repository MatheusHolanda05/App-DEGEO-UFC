# screens/recentes.py
import requests
from datetime import datetime
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
import json
import os
import webbrowser
from plyer import notification
import logging

# Configurar logging para diagnóstico
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('degeo_app')

# Caminho do arquivo de logs
ARQUIVO_LOG = "logs_atualizacoes.json"

def carregar_logs():
    if os.path.exists(ARQUIVO_LOG):
        try:
            with open(ARQUIVO_LOG, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar logs: {e}")
    return {}

def salvar_logs(logs):
    try:
        with open(ARQUIVO_LOG, "w") as f:
            json.dump(logs, f, default=str)
        logger.debug(f"Logs salvos: {logs}")
    except Exception as e:
        logger.error(f"Erro ao salvar logs: {e}")

def verificar_atualizacao_site(url, seletor_data=None):
    """Verifica atualização em sites com API ou scraping."""
    logger.debug(f"Verificando atualização para: {url}")
    try:
        # Primeiro, tenta verificar se é uma URL de API do WordPress
        if "wp-json" in url:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 0:  # ✅ CORREÇÃO: Condição completa
                    # Ajuste para o formato de data do WordPress (ISO 8601)
                    return datetime.strptime(data[0]['date'], "%Y-%m-%dT%H:%M:%S")
        
        # Se não for API ou falhar, usa scraping
        response = requests.get(url, timeout=5)
        logger.debug(f"Resposta do site ({url}): {response.status_code}")
        
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Tenta encontrar data em vários formatos possíveis
            data_elemento = None
            if seletor_data:
                data_elemento = soup.select_one(seletor_data)
            
            # Se não encontrou com seletor, tenta padrões comuns
            if not data_elemento:
                # Padrões comuns para data em sites WordPress
                data_elemento = soup.select_one("time.entry-date, .post-date, .date, .entry-meta time")
            
            if data_elemento:
                data_texto = data_elemento.get('datetime', data_elemento.text).strip()
                logger.debug(f"Data encontrada no scraping: {data_texto}")
                
                # Tenta vários formatos de data
                for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%dT%H:%M:%S", "%B %d, %Y"]:
                    try:
                        return datetime.strptime(data_texto, fmt)
                    except ValueError:
                        continue
    except Exception as e:
        logger.error(f"Erro ao verificar atualização: {e}")
    return None

class RecentesScreen(Screen):
    # IDs dos badges (DEVEM corresponder EXATAMENTE aos IDs no KV)
    badge_noticias = ObjectProperty(None)
    badge_graduacao = ObjectProperty(None)
    badge_sobre_geologia = ObjectProperty(None)
    badge_sobre_departamento = ObjectProperty(None)
    badge_coordenacao = ObjectProperty(None)
    badge_acessibilidade = ObjectProperty(None)
    badge_normas_ufc = ObjectProperty(None)
    
    # ✅ CORREÇÃO: Inicialização explícita ANTES do __init__
    badges = {
        'noticias': None,
        'graduacao': None,
        'sobre_geologia': None,
        'sobre_departamento': None,
        'coordenacao': None,
        'acessibilidade': None,
        'normas_ufc': None
    }
    
    def __init__(self, **kwargs):
        # ✅ CORREÇÃO: Primeiro inicializa o dicionário
        self.badges = {
            'noticias': None,
            'graduacao': None,
            'sobre_geologia': None,
            'sobre_departamento': None,
            'coordenacao': None,
            'acessibilidade': None,
            'normas_ufc': None
        }
        logger.debug("Dicionário badges inicializado no __init__")
        
        super(RecentesScreen, self).__init__(**kwargs)
        logger.debug("RecentesScreen inicializado")
    
    def on_kv_post(self, base_widget):
        """Chamado após o KV ser carregado"""
        logger.debug("on_kv_post chamado - widgets do KV estão disponíveis")
        
        # ✅ CORREÇÃO: Verifica se o dicionário já existe
        if not hasattr(self, 'badges'):
            self.badges = {
                'noticias': None,
                'graduacao': None,
                'sobre_geologia': None,
                'sobre_departamento': None,
                'coordenacao': None,
                'acessibilidade': None,
                'normas_ufc': None
            }
        
        # Associa os badges aos IDs do KV
        try:
            self.badges['noticias'] = self.ids.badge_noticias
            self.badges['graduacao'] = self.ids.badge_graduacao
            self.badges['sobre_geologia'] = self.ids.badge_sobre_geologia
            self.badges['sobre_departamento'] = self.ids.badge_sobre_departamento
            self.badges['coordenacao'] = self.ids.badge_coordenacao
            self.badges['acessibilidade'] = self.ids.badge_acessibilidade
            self.badges['normas_ufc'] = self.ids.badge_normas_ufc
            
            logger.debug("Badges vinculados com sucesso aos IDs do KV")
            
            # Agora que os widgets estão prontos, atualiza os badges
            Clock.schedule_once(self._delayed_update, 0.2)
        except Exception as e:
            logger.error(f"Erro ao vincular badges: {e}")
    
    def _delayed_update(self, dt):
        try:
            logger.debug("Iniciando atualização de badges...")
            self.atualizar_badges()
            logger.debug("Atualização de badges concluída")
        except Exception as e:
            logger.error(f"Erro ao atualizar badges: {e}")
    
    def atualizar_badges(self):
        logs = carregar_logs()
        logger.debug(f"Logs carregados: {logs}")
        
        # Verifica atualizações para cada seção
        self._atualizar_badge(
            "noticias", 
            "https://geologia.ufc.br/wp-json/wp/v2/posts",  # URL corrigida
            logs
        )
        self._atualizar_badge(
            "graduacao", 
            "https://geologia.ufc.br/pt/graduacao/", 
            logs,
            seletor_data="time.entry-date"
        )
        self._atualizar_badge(
            "sobre_geologia", 
            "https://geologia.ufc.br/pt/sobre-a-geologia/", 
            logs,
            seletor_data="time.entry-date"
        )
        self._atualizar_badge(
            "sobre_departamento", 
            "https://geologia.ufc.br/pt/sobre/", 
            logs,
            seletor_data="time.entry-date"
        )
        self._atualizar_badge(
            "coordenacao", 
            "https://geologia.ufc.br/pt/estrutura-organizacional-da-coordenacao-de-graduacao/", 
            logs,
            seletor_data="time.entry-date"
        )
        self._atualizar_badge(
            "acessibilidade", 
            "https://geologia.ufc.br/pt/acessibilidade/", 
            logs,
            seletor_data="time.entry-date"
        )
        self._atualizar_badge(
            "normas_ufc", 
            "https://geologia.ufc.br/pt/estatuto-regimento-e-normas-da-ufc/", 
            logs,
            seletor_data="time.entry-date"
        )

    def _atualizar_badge(self, chave, url, logs, seletor_data=None):
        logger.debug(f"Verificando atualização para {chave} em {url}")
        
        # Verifica se o badge está disponível
        badge_widget = self.badges.get(chave)
        if not badge_widget:
            logger.warning(f"Badge não encontrado para {chave}")
            return
            
        ultima_atualizacao = verificar_atualizacao_site(url, seletor_data)
        if ultima_atualizacao:
            # Converte a última leitura para datetime
            ultima_lida_str = logs.get(chave, "2000-01-01")
            try:
                ultima_lida = datetime.strptime(ultima_lida_str, "%Y-%m-%d")
            except:
                ultima_lida = datetime(2000, 1, 1)
                logger.warning(f"Formato de data inválido para {chave}: {ultima_lida_str}")
                
            logger.debug(f"Última atualização: {ultima_atualizacao}, Última lida: {ultima_lida}")
            
            if ultima_atualizacao > ultima_lida:
                badge_widget.text = "1"
                logger.info(f"Nova atualização detectada para {chave}")
                
                # Notificação push (opcional)
                try:
                    notification.notify(
                        title="Atualização DEGEO", 
                        message=f"Nova informação em {chave.replace('_', ' ')}",
                        app_name="DEGEO App"
                    )
                    logger.debug("Notificação push enviada")
                except Exception as e:
                    logger.error(f"Erro ao enviar notificação: {e}")
                return
        badge_widget.text = ""
        logger.debug(f"Nenhuma atualização para {chave}")

    def marcar_como_lido(self, chave):
        logger.info(f"Marcando {chave} como lido")
        logs = carregar_logs()
        logs[chave] = datetime.now().strftime("%Y-%m-%d")
        salvar_logs(logs)

    # Métodos para cada botão
    def abrir_noticias(self, instance):
        logger.info("Abrindo notícias")
        self._abrir_link("noticias", "https://geologia.ufc.br/pt/category/noticias/")
    
    def abrir_graduacao(self, instance):
        logger.info("Abrindo graduação")
        self._abrir_link("graduacao", "https://geologia.ufc.br/pt/graduacao/")
    
    def abrir_sobre_geologia(self, instance):
        logger.info("Abrindo sobre geologia")
        self._abrir_link("sobre_geologia", "https://geologia.ufc.br/pt/sobre-a-geologia/")
    
    def abrir_sobre_departamento(self, instance):
        logger.info("Abrindo sobre departamento")
        self._abrir_link("sobre_departamento", "https://geologia.ufc.br/pt/sobre/")
    
    def abrir_coordenacao(self, instance):
        logger.info("Abrindo coordenação")
        self._abrir_link("coordenacao", "https://geologia.ufc.br/pt/estrutura-organizacional-da-coordenacao-de-graduacao/")
    
    def abrir_acessibilidade(self, instance):
        logger.info("Abrindo acessibilidade")
        self._abrir_link("acessibilidade", "https://geologia.ufc.br/pt/acessibilidade/")
    
    def abrir_normas_ufc(self, instance):
        logger.info("Abrindo normas UFC")
        self._abrir_link("normas_ufc", "https://geologia.ufc.br/pt/estatuto-regimento-e-normas-da-ufc/")
    
    def _abrir_link(self, chave, url):
        # Marca como lido
        badge_widget = self.badges.get(chave)
        if badge_widget:
            self.marcar_como_lido(chave)
            badge_widget.text = ""
            logger.info(f"Marcando {chave} como lido e removendo badge")
        
        # Abre o link
        webbrowser.open(url, autoraise=True)
        logger.debug(f"Link aberto: {url}")