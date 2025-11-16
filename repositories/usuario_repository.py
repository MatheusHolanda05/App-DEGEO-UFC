import hashlib
import logging
from models.database_manager import DatabaseManager
from models.database_models import Usuario

logger = logging.getLogger('degeo_app')

class UsuarioRepository:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def criar_usuario(self, nome, email, senha, tipo, genero=None, disciplina=None):
        """Cria um novo usuário no banco de dados"""
        session = self.db_manager.get_session()
        try:
            # Verifica se o email já existe
            usuario_existente = session.query(Usuario).filter(Usuario.email == email.lower()).first()
            if usuario_existente:
                return False, "Email já cadastrado"
            
            # Cria hash da senha
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            
            # Cria novo usuário
            novo_usuario = Usuario(
                nome=nome.strip(),
                email=email.lower().strip(),
                senha_hash=senha_hash,
                tipo=tipo,
                genero=genero,
                disciplina=disciplina
            )
            
            session.add(novo_usuario)
            session.commit()
            
            logger.info(f"Usuário criado: {email} ({tipo})")
            return True, "Usuário criado com sucesso!"
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao criar usuário: {e}")
            return False, f"Erro ao criar usuário: {str(e)}"
        finally:
            session.close()
    
    def autenticar_usuario(self, email, senha):
        """Autentica um usuário por email e senha"""
        session = self.db_manager.get_session()
        try:
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            
            usuario = session.query(Usuario).filter(
                Usuario.email == email.lower(),
                Usuario.senha_hash == senha_hash,
                Usuario.ativo == True
            ).first()
            
            if usuario:
                logger.info(f"Login bem-sucedido: {email}")
                return True, usuario
            else:
                return False, "Email ou senha incorretos"
                
        except Exception as e:
            logger.error(f"Erro na autenticação: {e}")
            return False, f"Erro na autenticação: {str(e)}"
        finally:
            session.close()
    
    def obter_professores(self):
        """Obtém todos os professores cadastrados"""
        session = self.db_manager.get_session()
        try:
            professores = session.query(Usuario).filter(
                Usuario.tipo == 'professor',
                Usuario.ativo == True
            ).all()
            
            return professores
            
        except Exception as e:
            logger.error(f"Erro ao obter professores: {e}")
            return []
        finally:
            session.close()
    
    def alterar_senha(self, email, nova_senha):
        """Altera a senha de um usuário"""
        session = self.db_manager.get_session()
        try:
            usuario = session.query(Usuario).filter(Usuario.email == email.lower()).first()
            
            if not usuario:
                return False, "Usuário não encontrado"
            
            nova_senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
            usuario.senha_hash = nova_senha_hash
            
            session.commit()
            logger.info(f"Senha alterada para: {email}")
            return True, "Senha alterada com sucesso!"
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao alterar senha: {e}")
            return False, f"Erro ao alterar senha: {str(e)}"
        finally:
            session.close()