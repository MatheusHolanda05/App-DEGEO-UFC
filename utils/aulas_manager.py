# utils/aulas_manager.py
import json
import os
import uuid
import shutil
import tempfile
from datetime import datetime
import logging
import time

# Configurar logging
logger = logging.getLogger('degeo_app')

class AulasManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.aulas_file = os.path.join(data_dir, "aulas.json")
        self.arquivos_dir = os.path.join(data_dir, "arquivos")
        
        # Cria diretório de dados se não existir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Cria diretório de arquivos se não existir
        if not os.path.exists(self.arquivos_dir):
            os.makedirs(self.arquivos_dir)
        
        # Inicializa arquivo de aulas se não existir
        if not os.path.exists(self.aulas_file):
            self._salvar_aulas([])
    
    def _carregar_aulas(self):
        try:
            with open(self.aulas_file, "r") as f:
                data = json.load(f)
                # Garante que é um dicionário com chave "aulas"
                if isinstance(data, dict) and "aulas" in data:
                    return data["aulas"]
                # Se for uma lista direta, converte para o formato correto
                elif isinstance(data, list):
                    return data
                # Se for outro formato, retorna lista vazia
                else:
                    return []
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _salvar_aulas(self, aulas):
        """Salva as aulas no arquivo, garantindo o formato correto."""
        # Garante que 'aulas' seja uma lista
        if not isinstance(aulas, list):
            # Se for um dicionário com a chave 'aulas', extrai a lista
            if isinstance(aulas, dict) and "aulas" in aulas:
                aulas_para_salvar = aulas["aulas"]
            else:
                # Se for outro formato inesperado, salva como lista vazia
                logger.warning(f"Formato inesperado para aulas ao salvar: {type(aulas)}. Salvando lista vazia.")
                aulas_para_salvar = []
        else:
            # Já é uma lista, usa diretamente
            aulas_para_salvar = aulas

        dados_para_salvar = {"aulas": aulas_para_salvar}

        with open(self.aulas_file, "w") as f:
            # Salva no formato correto com chave "aulas"
            json.dump(dados_para_salvar, f, default=str, indent=2)
    
    def criar_aula(self, titulo, disciplina, observacoes="", arquivos=None, links=None, professor=""):
        """Cria uma nova aula"""
        if not titulo:
            return False, "Título é obrigatório"
        
        aulas = self._carregar_aulas()
        
        # ✅ CORREÇÃO: Garantir que o ID seja um inteiro
        aula_id = 1
        if aulas:
            # Converte os IDs para int antes de calcular o max
            try:
                aula_id = max(int(aula["id"]) for aula in aulas if "id" in aula and isinstance(aula["id"], (int, str)) and str(aula["id"]).isdigit()) + 1
            except ValueError:
                # Se houver algum problema na conversão, usa 1 como fallback
                aula_id = 1
                logger.warning("Erro ao calcular o próximo ID de aula. Usando ID 1.")
        
        # Cria diretório para a aula
        aula_dir = os.path.join(self.arquivos_dir, str(aula_id))
        os.makedirs(aula_dir, exist_ok=True)
        
        # Processa arquivos (CORREÇÃO: indentação corrigida aqui)
        arquivos_info = []
        if arquivos:
            for arquivo in arquivos:
                # Verifica se o arquivo existe
                if os.path.exists(arquivo):
                    nome_arquivo = os.path.basename(arquivo)
                    destino = os.path.join(aula_dir, nome_arquivo)

                    # Copia o arquivo para o diretório da aula
                    shutil.copy2(arquivo, destino)

                    arquivos_info.append({
                        "nome": nome_arquivo,
                        "caminho": os.path.join("arquivos", str(aula_id), nome_arquivo)
                    })
                else:
                    logger.warning(f"Arquivo não encontrado: {arquivo}")

        
        # Processa links
        links_info = []
        if links:
            for link in links:
                links_info.append(link)
        
        # Cria nova aula
        nova_aula = {
            "id": aula_id,
            "titulo": titulo,
            "disciplina": disciplina,
            "observacoes": observacoes,
            "arquivos": arquivos_info,
            "links": links_info,
            "comentarios": [],  # Inicializa com lista vazia de comentários
            "data_criacao": datetime.now().isoformat(),
            "professor": professor
        }
        
        aulas.insert(0, nova_aula)  # Insere no início (mais recente primeiro)
        self._salvar_aulas(aulas)
        
        return True, nova_aula
    
    def obter_aulas(self):
        """Obtém todas as aulas"""
        return self._carregar_aulas()
    
    def atualizar_aula(self, aula_id, titulo, disciplina, observacoes="", arquivos=None, links=None, professor=""):
            """Atualiza uma aula existente"""
            if not titulo:
                return False, "Título é obrigatório"

            aulas = self._carregar_aulas()
            aula_idx = next((i for i, aula in enumerate(aulas) if aula["id"] == aula_id), None)

            if aula_idx is None:
                return False, "Aula não encontrada"

            # Processa novos arquivos
            arquivos_info = aulas[aula_idx]["arquivos"] # Mantém os arquivos existentes
            if arquivos:
                aula_dir = os.path.join(self.arquivos_dir, str(aula_id))
                os.makedirs(aula_dir, exist_ok=True)

                for arquivo in arquivos:
                    # Verifica se o arquivo existe
                    if os.path.exists(arquivo):
                        nome_arquivo = os.path.basename(arquivo)
                        destino_original = os.path.join(aula_dir, nome_arquivo)
                        # Cria um nome temporário para a cópia
                        destino_temp = destino_original + f".tmp_{int(time.time() * 1000)}"

                        try:
                            # 1. Copia para o nome temporário
                            logger.debug(f"Tentando copiar '{arquivo}' para '{destino_temp}'")
                            shutil.copy2(arquivo, destino_temp)
                            logger.debug(f"Cópia temporária bem-sucedida para '{destino_temp}'")

                            # 2. Substitui o arquivo original pelo temporário (operação atômica em muitos sistemas)
                            # os.replace é preferido em sistemas modernos por ser mais atômico
                            logger.debug(f"Tentando substituir '{destino_original}' por '{destino_temp}'")
                            os.replace(destino_temp, destino_original)
                            logger.debug(f"Substituição bem-sucedida de '{destino_original}'")

                            # Adiciona o arquivo à lista de informações da aula
                            caminho_relativo = os.path.relpath(destino_original, self.data_dir)
                            arquivos_info.append({
                                "nome": nome_arquivo,
                                "caminho": caminho_relativo
                            })
                            logger.info(f"Arquivo '{nome_arquivo}' atualizado com sucesso.")

                        except PermissionError as e:
                            # Se falhar, tenta remover o temp e reporta o erro
                            logger.error(f"Permissão negada ao atualizar o arquivo '{nome_arquivo}': {e}")
                            try:
                                if os.path.exists(destino_temp):
                                    os.remove(destino_temp)
                                    logger.debug(f"Arquivo temporário '{destino_temp}' removido após falha.")
                            except OSError:
                                pass # Ignora erro ao remover temp
                            return False, f"Erro de permissão ao atualizar o arquivo '{nome_arquivo}'. Verifique se ele está aberto em outro programa."
                        except Exception as e:
                            # Se falhar por outro motivo, tenta remover o temp e reporta o erro
                            logger.error(f"Erro ao atualizar o arquivo '{nome_arquivo}': {e}", exc_info=True)
                            try:
                                if os.path.exists(destino_temp):
                                    os.remove(destino_temp)
                                    logger.debug(f"Arquivo temporário '{destino_temp}' removido após falha.")
                            except OSError:
                                pass # Ignora erro ao remover temp
                            return False, f"Erro ao atualizar o arquivo '{nome_arquivo}': {str(e)}"
                    else:
                        logger.warning(f"Arquivo não encontrado para atualização: {arquivo}")

            # Processa links (substitui completamente os links existentes, como no código original)
            # Se você quiser adicionar ao invés de substituir, precisa modificar esta lógica.
            links_info = []
            if links is not None: # Permite passar uma lista vazia para limpar
                links_info = links
            else:
                # Se links for None, mantém os links existentes
                links_info = aulas[aula_idx]["links"]

            # Atualiza aula
            aulas[aula_idx].update({
                "titulo": titulo,
                "disciplina": disciplina,
                "observacoes": observacoes,
                "arquivos": arquivos_info, # Usa a lista atualizada
                "links": links_info,       # Usa a lista de links (nova ou mantida)
                "professor": professor
            })

            self._salvar_aulas(aulas)
            logger.info(f"Aula ID {aula_id} atualizada com sucesso.")
            return True, aulas[aula_idx]

    
    def excluir_aula(self, aula_id):
        """Exclui uma aula"""
        aulas = self._carregar_aulas()
        aula_idx = next((i for i, aula in enumerate(aulas) if aula["id"] == aula_id), None)
        
        if aula_idx is None:
            return False, "Aula não encontrada"
        
        # Remove diretório da aula
        aula_dir = os.path.join(self.arquivos_dir, str(aula_id))
        if os.path.exists(aula_dir):
            shutil.rmtree(aula_dir)
        
        # Remove aula da lista
        aulas.pop(aula_idx)
        self._salvar_aulas(aulas)
        
        return True, "Aula excluída com sucesso"
    
    # ✅ CORREÇÃO: Implementação robusta do método adicionar_comentario
    def adicionar_comentario(self, aula_id, nome_aluno, comentario):
        """Adiciona um comentário a uma aula"""
        try:
            # Carrega as aulas existentes
            aulas = self._carregar_aulas()
            
            # Encontra a aula
            aula_idx = next((i for i, aula in enumerate(aulas) if aula["id"] == aula_id), None)
            
            if aula_idx is None:
                return False, "Aula não encontrada"
            
            # Garante que comentarios seja uma lista
            if "comentarios" not in aulas[aula_idx] or not isinstance(aulas[aula_idx]["comentarios"], list):
                aulas[aula_idx]["comentarios"] = []
            
            # Adiciona o comentário
            aulas[aula_idx]["comentarios"].append({
                "nome_aluno": nome_aluno,
                "comentario": comentario,
                "data": datetime.now().isoformat()
            })
            
            # Salva as aulas
            self._salvar_aulas(aulas)
            
            return True, "Comentário adicionado com sucesso"
        except Exception as e:
            logger.error(f"Erro ao adicionar comentário: {str(e)}", exc_info=True)
            return False, f"Erro ao adicionar comentário: {str(e)}" 