# utils/notificacoes_manager.py - CRIAR ESTE ARQUIVO COMPLETO
import json
import os
import logging
from datetime import datetime
from kivy.app import App
from kivy.clock import Clock
import threading
import time

logger = logging.getLogger('degeo_app')

class NotificacoesManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.notificacoes_file = os.path.join(data_dir, "notificacoes.json")
        self.config_file = os.path.join(data_dir, "notificacoes_config.json")
        self.tokens_file = os.path.join(data_dir, "fcm_tokens.json")
        
        # Serviços
        self.fcm_service = None
        self.badge_manager = None
        self.notificacao_service = None
        
        # Inicializar arquivos
        self._inicializar_arquivos()
        
        # Configurações
        self.notificacoes_ativas = True
        self.verificacao_automatica = True
        
    def _inicializar_arquivos(self):
        """Inicializa os arquivos necessários"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        if not os.path.exists(self.notificacoes_file):
            self._salvar_notificacoes({})
        
        if not os.path.exists(self.config_file):
            self._salvar_config({
                "intervalo_verificacao": 300,
                "ultima_verificacao": None,
                "notificacoes_ativas": True,
                "badge_ativo": True
            })
            
        if not os.path.exists(self.tokens_file):
            self._salvar_tokens({})
    
    def inicializar_servicos(self):
        """Inicializa todos os serviços de notificação"""
        try:
            # Inicializar FCM
            from services.fcm_service import FCMService
            self.fcm_service = FCMService()
            
            # Inicializar Badge Manager
            from utils.badge_manager import BadgeManager
            self.badge_manager = BadgeManager()
            
            # Inicializar Serviço de Notificação
            from services.notificacao_service import NotificacaoService
            self.notificacao_service = NotificacaoService()
            
            # Registrar dispositivo no FCM
            self._registrar_dispositivo()
            
            logger.info("Serviços de notificação inicializados")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar serviços: {e}")
    
    def _registrar_dispositivo(self):
        """Registra o dispositivo no FCM"""
        try:
            # Obter token FCM (em uma app real, isso viria do Firebase)
            token = self._obter_fcm_token()
            
            if token:
                tokens = self._carregar_tokens()
                tokens[token] = {
                    "data_registro": datetime.now().isoformat(),
                    "plataforma": "android",
                    "ativo": True
                }
                self._salvar_tokens(tokens)
                logger.info("Dispositivo registrado no FCM")
                
        except Exception as e:
            logger.error(f"Erro ao registrar dispositivo: {e}")
    
    def _obter_fcm_token(self):
        """Obtém o token FCM do dispositivo (simulação)"""
        # Em uma implementação real, isso obteria o token real do Firebase
        return "fcm_token_simulado_" + str(int(time.time()))
    
    def adicionar_notificacao(self, recurso, titulo, mensagem, dados=None):
        """Adiciona uma nova notificação com todos os serviços"""
        # Salvar notificação localmente
        notificacao_salva = self._salvar_notificacao_local(recurso, titulo, mensagem, dados)
        
        # Enviar notificação push via FCM
        if self.fcm_service:
            self._enviar_notificacao_fcm(recurso, titulo, mensagem, dados)
        
        # Atualizar badge
        self._atualizar_badge_global()
        
        # Mostrar notificação local
        self._mostrar_notificacao_local(titulo, mensagem)
        
        return notificacao_salva
    
    def _salvar_notificacao_local(self, recurso, titulo, mensagem, dados):
        """Salva notificação localmente"""
        notificacoes = self._carregar_notificacoes()
        
        if recurso not in notificacoes:
            notificacoes[recurso] = []
        
        nova_notificacao = {
            "id": int(time.time() * 1000),
            "titulo": titulo,
            "mensagem": mensagem,
            "data": datetime.now().isoformat(),
            "lida": False,
            "dados": dados or {}
        }
        
        notificacoes[recurso].insert(0, nova_notificacao)
        notificacoes[recurso] = notificacoes[recurso][:50]  # Limite de 50
        
        self._salvar_notificacoes(notificacoes)
        return nova_notificacao
    
    def _enviar_notificacao_fcm(self, recurso, titulo, mensagem, dados):
        """Envia notificação via FCM para todos os dispositivos"""
        try:
            tokens = self._carregar_tokens()
            
            for token, info in tokens.items():
                if info.get("ativo", True):
                    dados_completos = {
                        "recurso": recurso,
                        "tipo": "atualizacao_site",
                        "url": dados.get("url", "") if dados else "",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    self.fcm_service.enviar_notificacao_push(
                        token, titulo, mensagem, dados_completos
                    )
                    
        except Exception as e:
            logger.error(f"Erro ao enviar notificação FCM: {e}")
    
    def _atualizar_badge_global(self):
        """Atualiza o badge do app com o total de notificações não lidas"""
        try:
            total_nao_lidas = self.obter_total_nao_lidas()
            
            if self.badge_manager:
                self.badge_manager.atualizar_badge(total_nao_lidas)
                
        except Exception as e:
            logger.error(f"Erro ao atualizar badge: {e}")
    
    def _mostrar_notificacao_local(self, titulo, mensagem):
        """Mostra notificação local usando plyer"""
        try:
            from plyer import notification
            
            notification.notify(
                title=titulo,
                message=mensagem,
                timeout=10,
                app_name="DEGEO UFC"
            )
            
        except Exception as e:
            logger.warning(f"Erro ao mostrar notificação local: {e}")
    
    def obter_total_nao_lidas(self):
        """Retorna o total de notificações não lidas"""
        notificacoes = self._carregar_notificacoes()
        total = 0
        
        for recurso, lista in notificacoes.items():
            for notificacao in lista:
                if not notificacao.get("lida", False):
                    total += 1
                    
        return total
    
    def obter_notificacoes_nao_lidas(self, recurso=None):
        """Obtém notificações não lidas para um recurso específico ou todos"""
        notificacoes = self._carregar_notificacoes()
        
        if recurso:
            if recurso not in notificacoes:
                return []
            return [n for n in notificacoes[recurso] if not n.get("lida", False)]
        else:
            # Retorna contagem total de não lidas por recurso
            resultado = {}
            for recurso, lista in notificacoes.items():
                nao_lidas = [n for n in lista if not n.get("lida", False)]
                resultado[recurso] = len(nao_lidas)
            return resultado
    
    def marcar_como_lida(self, recurso, notificacao_id=None):
        """Marca notificações como lidas e atualiza badge"""
        notificacoes = self._carregar_notificacoes()
        
        if recurso not in notificacoes:
            return False
        
        if notificacao_id:
            # Marca uma notificação específica
            for notificacao in notificacoes[recurso]:
                if notificacao["id"] == notificacao_id:
                    notificacao["lida"] = True
                    break
        else:
            # Marca todas as notificações do recurso
            for notificacao in notificacoes[recurso]:
                notificacao["lida"] = True
        
        self._salvar_notificacoes(notificacoes)
        
        # Atualizar badge após marcar como lida
        self._atualizar_badge_global()
        
        return True
    
    # Métodos de carregamento/salvamento
    def _carregar_notificacoes(self):
        try:
            with open(self.notificacoes_file, "r", encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _salvar_notificacoes(self, notificacoes):
        try:
            with open(self.notificacoes_file, "w", encoding='utf-8') as f:
                json.dump(notificacoes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar notificações: {e}")
    
    def _carregar_config(self):
        try:
            with open(self.config_file, "r", encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _salvar_config(self, config):
        try:
            with open(self.config_file, "w", encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
    
    def _carregar_tokens(self):
        try:
            with open(self.tokens_file, "r", encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _salvar_tokens(self, tokens):
        try:
            with open(self.tokens_file, "w", encoding='utf-8') as f:
                json.dump(tokens, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar tokens: {e}")