import os
import logging
from models.database_manager import DatabaseManager
from models.database_models import Aula, ArquivoAula, LinkAula, ComentarioAula
from datetime import datetime

logger = logging.getLogger('degeo_app')

class AulaRepository:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    def criar_aula(self, titulo, disciplina, observacoes, arquivos, links, professor_nome):
        """Cria uma nova aula no banco de dados"""
        session = self.db_manager.get_session()
        try:
            # Primeiro, busca o professor pelo nome
            from models.database_models import Usuario
            professor = session.query(Usuario).filter(
                Usuario.nome == professor_nome,
                Usuario.tipo == 'professor'
            ).first()
            
            if not professor:
                return False, "Professor não encontrado"
            
            # Cria a aula
            nova_aula = Aula(
                titulo=titulo.strip(),
                disciplina=disciplina.strip(),
                observacoes=observacoes.strip(),
                professor_id=professor.id,
                data_criacao=datetime.now()
            )
            
            session.add(nova_aula)
            session.flush()  # Para obter o ID da aula
            
            # Processa arquivos
            for arquivo_path in arquivos:
                if os.path.exists(arquivo_path):
                    nome_arquivo = os.path.basename(arquivo_path)
                    aula_dir = os.path.join(self.data_dir, "arquivos", str(nova_aula.id))
                    os.makedirs(aula_dir, exist_ok=True)
                    
                    destino = os.path.join(aula_dir, nome_arquivo)
                    import shutil
                    shutil.copy2(arquivo_path, destino)
                    
                    arquivo_aula = ArquivoAula(
                        aula_id=nova_aula.id,
                        nome=nome_arquivo,
                        caminho=os.path.join("arquivos", str(nova_aula.id), nome_arquivo)
                    )
                    session.add(arquivo_aula)
            
            # Processa links
            for link in links:
                link_aula = LinkAula(
                    aula_id=nova_aula.id,
                    titulo=link.get("titulo", "").strip(),
                    url=link.get("url", "").strip()
                )
                session.add(link_aula)
            
            session.commit()
            logger.info(f"Aula criada: {titulo} (ID: {nova_aula.id})")
            return True, nova_aula
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao criar aula: {e}")
            return False, f"Erro ao criar aula: {str(e)}"
        finally:
            session.close()
    
    def obter_aulas_por_professor(self, professor_nome):
        """Obtém todas as aulas de um professor específico"""
        session = self.db_manager.get_session()
        try:
            from models.database_models import Usuario
            
            aulas = session.query(Aula).join(Usuario).filter(
                Usuario.nome == professor_nome
            ).order_by(Aula.data_criacao.desc()).all()
            
            return self._aulas_para_dict(aulas)
            
        except Exception as e:
            logger.error(f"Erro ao obter aulas do professor: {e}")
            return []
        finally:
            session.close()
    
    def obter_todas_aulas(self):
        """Obtém todas as aulas (para alunos)"""
        session = self.db_manager.get_session()
        try:
            aulas = session.query(Aula).order_by(Aula.data_criacao.desc()).all()
            return self._aulas_para_dict(aulas)
            
        except Exception as e:
            logger.error(f"Erro ao obter todas as aulas: {e}")
            return []
        finally:
            session.close()
    
    def atualizar_aula(self, aula_id, titulo, disciplina, observacoes, arquivos, links, professor_nome):
        """Atualiza uma aula existente"""
        session = self.db_manager.get_session()
        try:
            aula = session.query(Aula).filter(Aula.id == aula_id).first()
            
            if not aula:
                return False, "Aula não encontrada"
            
            # Atualiza dados básicos
            aula.titulo = titulo.strip()
            aula.disciplina = disciplina.strip()
            aula.observacoes = observacoes.strip()
            
            # Processa novos arquivos
            for arquivo_path in arquivos:
                if os.path.exists(arquivo_path):
                    nome_arquivo = os.path.basename(arquivo_path)
                    aula_dir = os.path.join(self.data_dir, "arquivos", str(aula_id))
                    os.makedirs(aula_dir, exist_ok=True)
                    
                    destino = os.path.join(aula_dir, nome_arquivo)
                    import shutil
                    shutil.copy2(arquivo_path, destino)
                    
                    arquivo_aula = ArquivoAula(
                        aula_id=aula_id,
                        nome=nome_arquivo,
                        caminho=os.path.join("arquivos", str(aula_id), nome_arquivo)
                    )
                    session.add(arquivo_aula)
            
            # Remove links existentes e adiciona novos
            session.query(LinkAula).filter(LinkAula.aula_id == aula_id).delete()
            
            for link in links:
                link_aula = LinkAula(
                    aula_id=aula_id,
                    titulo=link.get("titulo", "").strip(),
                    url=link.get("url", "").strip()
                )
                session.add(link_aula)
            
            session.commit()
            logger.info(f"Aula atualizada: {titulo} (ID: {aula_id})")
            return True, aula
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao atualizar aula: {e}")
            return False, f"Erro ao atualizar aula: {str(e)}"
        finally:
            session.close()
    
    def excluir_aula(self, aula_id):
        """Exclui uma aula e seus arquivos/links"""
        session = self.db_manager.get_session()
        try:
            aula = session.query(Aula).filter(Aula.id == aula_id).first()
            
            if not aula:
                return False, "Aula não encontrada"
            
            # Exclui arquivos físicos
            aula_dir = os.path.join(self.data_dir, "arquivos", str(aula_id))
            if os.path.exists(aula_dir):
                import shutil
                shutil.rmtree(aula_dir)
            
            # Exclui do banco
            session.delete(aula)
            session.commit()
            
            logger.info(f"Aula excluída: ID {aula_id}")
            return True, "Aula excluída com sucesso"
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao excluir aula: {e}")
            return False, f"Erro ao excluir aula: {str(e)}"
        finally:
            session.close()
    
    def adicionar_comentario(self, aula_id, nome_aluno, comentario):
        """Adiciona um comentário a uma aula"""
        session = self.db_manager.get_session()
        try:
            novo_comentario = ComentarioAula(
                aula_id=aula_id,
                nome_aluno=nome_aluno.strip(),
                comentario=comentario.strip(),
                data=datetime.now()
            )
            
            session.add(novo_comentario)
            session.commit()
            
            logger.info(f"Comentário adicionado à aula {aula_id}")
            return True, "Comentário adicionado com sucesso"
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao adicionar comentário: {e}")
            return False, f"Erro ao adicionar comentário: {str(e)}"
        finally:
            session.close()
    
    def _aulas_para_dict(self, aulas):
        """Converte objetos Aula para dicionários (compatibilidade)"""
        resultado = []
        for aula in aulas:
            aula_dict = {
                "id": aula.id,
                "titulo": aula.titulo,
                "disciplina": aula.disciplina,
                "observacoes": aula.observacoes,
                "professor": aula.professor.nome if aula.professor else "",
                "data_criacao": aula.data_criacao.isoformat(),
                "arquivos": [{"nome": a.nome, "caminho": a.caminho} for a in aula.arquivos],
                "links": [{"titulo": l.titulo, "url": l.url} for l in aula.links],
                "comentarios": [
                    {
                        "nome_aluno": c.nome_aluno,
                        "comentario": c.comentario,
                        "data": c.data.isoformat()
                    } for c in aula.comentarios
                ]
            }
            resultado.append(aula_dict)
        
        return resultado