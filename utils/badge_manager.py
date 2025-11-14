# ✅ NOVO ARQUIVO - Colocar na pasta 'utils/'
import logging

logger = logging.getLogger('degeo_app')

class BadgeManager:
    def __init__(self):
        self.context = None
        
    def inicializar(self, context):
        """Inicializa o gerenciador de badge"""
        self.context = context
        logger.info("BadgeManager inicializado")
        
    def atualizar_badge(self, contagem):
        """Atualiza o badge no ícone do app - VERSÃO SIMULADA"""
        try:
            # Por enquanto, apenas log para desenvolvimento
            logger.info(f"SIMULAÇÃO - Badge atualizado: {contagem}")
            
            # Em produção com Buildozer, descomente:
            """
            from jnius import autoclass
            ShortcutBadger = autoclass('me.leolin.shortcutbadger.ShortcutBadger')
            ShortcutBadger.applyCount(self.context, contagem)
            """
            
        except Exception as e:
            logger.warning(f"Erro ao atualizar badge: {e}")
            
    def atualizar_badge_ios(self, contagem):
        """Atualiza o badge no ícone do app (iOS)"""
        try:
            logger.info(f"SIMULAÇÃO iOS - Badge atualizado: {contagem}")
        except Exception as e:
            logger.warning(f"Erro ao atualizar badge iOS: {e}")