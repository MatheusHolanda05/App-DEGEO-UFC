import logging
from models.database_manager import DatabaseManager
from models.database_models import Notificacao, AtualizacaoSite, FCMToken
from datetime import datetime

logger = logging.getLogger('degeo_app')

class NotificacaoRepository:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def adicionar_notificacao(self, recurso, titulo, mensagem, dados=None):
        """Adiciona uma nova notificação"""
        session = self.db_manager.get_session()
        try:
            notificacao = Notificacao(
                recurso=recurso,
                titulo=titulo,
                mensagem=mensagem,
                dados=str(dados) if dados else None,
                data=datetime.now(),
                lida=False
            )
            
            session.add(notificacao)
            session.commit()
            
            logger.info(f"Notificação adicionada: {titulo}")
            return True, notificacao
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao adicionar notificação: {e}")
            return False, f"Erro ao adicionar notificação: {str(e)}"
        finally:
            session.close()
    
    def obter_notificacoes_nao_lidas(self, recurso=None):
        """Obtém notificações não lidas"""
        session = self.db_manager.get_session()
        try:
            query = session.query(Notificacao).filter(Notificacao.lida == False)
            
            if recurso:
                query = query.filter(Notificacao.recurso == recurso)
            
            notificacoes = query.order_by(Notificacao.data.desc()).all()
            
            return [
                {
                    "id": n.id,
                    "recurso": n.recurso,
                    "titulo": n.titulo,
                    "mensagem": n.mensagem,
                    "dados": n.dados,
                    "data": n.data.isoformat(),
                    "lida": n.lida
                } for n in notificacoes
            ]
            
        except Exception as e:
            logger.error(f"Erro ao obter notificações: {e}")
            return []
        finally:
            session.close()
    
    def marcar_como_lida(self, notificacao_id=None, recurso=None):
        """Marca notificações como lidas"""
        session = self.db_manager.get_session()
        try:
            query = session.query(Notificacao).filter(Notificacao.lida == False)
            
            if notificacao_id:
                query = query.filter(Notificacao.id == notificacao_id)
            elif recurso:
                query = query.filter(Notificacao.recurso == recurso)
            
            notificacoes = query.all()
            for notificacao in notificacoes:
                notificacao.lida = True
            
            session.commit()
            logger.info(f"Notificações marcadas como lidas: {len(notificacoes)}")
            return True, f"{len(notificacoes)} notificações marcadas como lidas"
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao marcar notificações como lidas: {e}")
            return False, f"Erro ao marcar notificações como lidas: {str(e)}"
        finally:
            session.close()