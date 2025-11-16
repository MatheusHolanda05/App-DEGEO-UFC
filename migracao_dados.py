# migracao_dados.py - VERSÃO SIMPLIFICADA
import os
import json
import hashlib
import logging
from datetime import datetime
import sys

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('migracao')

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from repositories.usuario_repository import UsuarioRepository
from repositories.aula_repository import AulaRepository

class MigracaoDados:
    def __init__(self):
        self.usuario_repo = UsuarioRepository()
        self.aula_repo = AulaRepository()
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
    
    def migrar_usuarios(self):
        """Migra usuários de usuarios.json para o banco"""
        try:
            usuarios_file = os.path.join(self.data_dir, "usuarios.json")
            
            if not os.path.exists(usuarios_file):
                logger.warning("Arquivo usuarios.json não encontrado")
                return 0
            
            with open(usuarios_file, 'r', encoding='utf-8') as f:
                usuarios = json.load(f)
            
            migrados = 0
            for usuario in usuarios:
                try:
                    # Verifica se o usuário já existe
                    sucesso, _ = self.usuario_repo.autenticar_usuario(
                        usuario['email'], 
                        "senha_temporaria"
                    )
                    
                    # Se autenticação falhar, o usuário não existe
                    if not sucesso:
                        # Cria o usuário
                        sucesso, mensagem = self.usuario_repo.criar_usuario(
                            nome=usuario['nome'],
                            email=usuario['email'],
                            senha="123456",  # Senha padrão para migração
                            tipo=usuario['tipo'],
                            genero=usuario.get('genero'),
                            disciplina=usuario.get('disciplina')
                        )
                        
                        if sucesso:
                            migrados += 1
                            logger.info(f"✅ Usuário migrado: {usuario['email']}")
                        else:
                            logger.warning(f"⚠️ Usuário não migrado {usuario['email']}: {mensagem}")
                    else:
                        logger.info(f"📝 Usuário já existe: {usuario['email']}")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao migrar usuário {usuario['email']}: {e}")
            
            logger.info(f"📊 Usuários migrados: {migrados}/{len(usuarios)}")
            return migrados
            
        except Exception as e:
            logger.error(f"❌ Erro na migração de usuários: {e}")
            return 0
    
    def migrar_professores(self):
        """Migra professores de professores.json para o banco"""
        try:
            professores_file = os.path.join(self.data_dir, "professores.json")
            
            if not os.path.exists(professores_file):
                logger.warning("Arquivo professores.json não encontrado")
                return 0
            
            with open(professores_file, 'r', encoding='utf-8') as f:
                professores = json.load(f)
            
            migrados = 0
            for professor in professores:
                try:
                    # Verifica se já existe
                    sucesso, _ = self.usuario_repo.autenticar_usuario(
                        professor['email'], 
                        "senha_temporaria"
                    )
                    
                    if not sucesso:
                        # Cria como professor
                        sucesso, mensagem = self.usuario_repo.criar_usuario(
                            nome=professor['nome'],
                            email=professor['email'],
                            senha="123456",  # Senha padrão
                            tipo="professor",
                            genero=professor.get('genero'),
                            disciplina=professor.get('disciplina')
                        )
                        
                        if sucesso:
                            migrados += 1
                            logger.info(f"✅ Professor migrado: {professor['email']}")
                        else:
                            logger.warning(f"⚠️ Professor não migrado {professor['email']}: {mensagem}")
                    else:
                        logger.info(f"📝 Professor já existe: {professor['email']}")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao migrar professor {professor['email']}: {e}")
            
            logger.info(f"📊 Professores migrados: {migrados}/{len(professores)}")
            return migrados
            
        except Exception as e:
            logger.error(f"❌ Erro na migração de professores: {e}")
            return 0
    
    def migrar_aulas(self):
        """Migra aulas de aulas.json para o banco - VERSÃO CORRIGIDA"""
        try:
            aulas_file = os.path.join(self.data_dir, "aulas.json")
            
            if not os.path.exists(aulas_file):
                logger.warning("Arquivo aulas.json não encontrado")
                return 0
            
            with open(aulas_file, 'r', encoding='utf-8') as f:
                dados_aulas = json.load(f)
            
            # Extrai a lista de aulas
            aulas = dados_aulas.get('aulas', []) if isinstance(dados_aulas, dict) else dados_aulas
            
            # Mapeamento de nomes de professores (do JSON para o banco)
            mapeamento_professores = {
                "Mateusim": "Matheus de Andrade Holanda",
                "Mateusão": "Matheus de Andrade Holanda", 
                "Mateus": "Matheus de Andrade Holanda",
                "Ana Maria": "Bia",
                "Ana beathiz": "Bia",
                "Ana Maria Cabral Holanda": "Bia",
                "": "Professor Exemplo"  # Para aulas sem professor
            }
            
            migrados = 0
            # Consulta títulos existentes uma vez para evitar chamadas repetidas
            aulas_existentes = self.aula_repo.obter_todas_aulas()
            titulos_existentes = set(a['titulo'] for a in aulas_existentes)
            
            for aula in aulas:
                try:
                    titulo = aula.get('titulo', '')
                    if titulo in titulos_existentes:
                        logger.info(f"📝 Aula já existe: {titulo}")
                        continue
                    
                    # Obtém o nome correto do professor do mapeamento
                    professor_json = aula.get('professor', '')
                    professor_banco = mapeamento_professores.get(professor_json, professor_json) or "Professor Exemplo"
                    
                    # Migra a aula
                    sucesso, resultado = self.aula_repo.criar_aula(
                        titulo=titulo,
                        disciplina=aula.get('disciplina', ''),
                        observacoes=aula.get('observacoes', ''),
                        arquivos=[],  # Arquivos físicos mantidos no sistema de arquivos
                        links=aula.get('links', []),
                        professor_nome=professor_banco
                    )
                    
                    if sucesso:
                        migrados += 1
                        titulos_existentes.add(titulo)
                        logger.info(f"✅ Aula migrada: {titulo} (Prof: {professor_banco})")
                        
                        # Migra comentários se houver
                        for comentario in aula.get('comentarios', []):
                            try:
                                self.aula_repo.adicionar_comentario(
                                    aula_id=resultado.id,
                                    nome_aluno=comentario.get('nome_aluno', ''),
                                    comentario=comentario.get('comentario', '')
                                )
                                logger.info(f"   💬 Comentário migrado para aula {titulo}")
                            except Exception as e:
                                logger.error(f"❌ Erro ao migrar comentário para {titulo}: {e}")
                    else:
                        logger.warning(f"⚠️ Aula não migrada {titulo}: {resultado}")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao migrar aula {aula.get('titulo', '')}: {e}")
            
            logger.info(f"📊 Aulas migradas: {migrados}/{len(aulas)}")
            return migrados
            
        except Exception as e:
            logger.error(f"❌ Erro na migração de aulas: {e}")
            return 0
    
    def executar_migracao_completa(self):
        """Executa toda a migração de dados"""
        print("🚀 INICIANDO MIGRAÇÃO DE DADOS PARA O BANCO...")
        print("=" * 50)
        
        total_usuarios = self.migrar_usuarios()
        total_professores = self.migrar_professores() 
        total_aulas = self.migrar_aulas()
        
        print("=" * 50)
        print("🎉 MIGRAÇÃO CONCLUÍDA!")
        print(f"📊 RESUMO:")
        print(f"   👥 Usuários migrados: {total_usuarios}")
        print(f"   👨‍🏫 Professores migrados: {total_professores}")
        print(f"   📚 Aulas migradas: {total_aulas}")
        print(f"💾 Dados migrados para: data/degeo_app.db")

if __name__ == "__main__":
    migracao = MigracaoDados()
    migracao.executar_migracao_completa()                    