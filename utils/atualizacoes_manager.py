# utils/atualizacoes_manager.py
import json
import os
import requests
from datetime import datetime
import logging
import time
import threading
from queue import Queue

# Configurar logging
logger = logging.getLogger('degeo_app')

class AtualizacoesManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.atualizacoes_file = os.path.join(data_dir, "atualizacoes.json")
        
        # Cria diretório de dados se não existir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Inicializa arquivo de atualizações se não existir
        if not os.path.exists(self.atualizacoes_file):
            self._salvar_atualizacoes({})
        
        # Cache para evitar verificações excessivas
        self.cache_verificacao = {}
        # Tempo mínimo entre verificações (5 minutos)
        self.tempo_minimo_entre_verificacoes = 300
        # Timeout reduzido para respostas
        self.timeout = 2.0
        # Fila para operações assíncronas
        self.verificacao_queue = Queue()
        # Thread para processar a fila
        self.verificacao_thread = threading.Thread(target=self._processar_fila, daemon=True)
        self.verificacao_thread.start()
    
    def _processar_fila(self):
        """Processa a fila de verificações em uma thread separada"""
        while True:
            try:
                chave, url, callback = self.verificacao_queue.get()
                resultado = self._verificar_atualizacao_real(chave, url)
                if callback:
                    # Executar callback na thread principal
                    from kivy.clock import Clock
                    Clock.schedule_once(lambda dt, r=resultado, c=callback: c(r), 0)
                self.verificacao_queue.task_done()
            except Exception as e:
                logger.error(f"Erro ao processar fila de verificações: {e}")
    
    def _carregar_atualizacoes(self):
        try:
            with open(self.atualizacoes_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _salvar_atualizacoes(self, atualizacoes):
        try:
            with open(self.atualizacoes_file, "w") as f:
                json.dump(atualizacoes, f, default=str, indent=2)
            logger.debug(f"Atualizações salvas: {atualizacoes}")
        except Exception as e:
            logger.error(f"Erro ao salvar atualizações: {e}")
    
    def verificar_atualizacao(self, chave, url, callback=None):
        """Verifica atualização de forma assíncrona"""
        # Adiciona à fila para processamento em segundo plano
        self.verificacao_queue.put((chave, url, callback))
        # Retorna o valor do cache se existir, para não deixar a interface sem resposta
        if chave in self.cache_verificacao:
            return self.cache_verificacao[chave][1]
        return 0
    
    def _verificar_atualizacao_real(self, chave, url):
        """Verifica atualização sem bloquear a interface"""
        logger.debug(f"Verificando atualização para {chave} em {url}")
        
        # Verifica se já verificamos recentemente
        agora = time.time()
        if chave in self.cache_verificacao:
            ultima_verificacao, resultado = self.cache_verificacao[chave]
            # Se verificamos há menos de 5 minutos, retorna o resultado cacheado
            if agora - ultima_verificacao < self.tempo_minimo_entre_verificacoes:
                logger.debug(f"Usando cache para {chave}")
                return resultado
        
        # Carrega o estado atual das atualizações
        atualizacoes = self._carregar_atualizacoes()
        
        # Obtém a última data de verificação
        info = atualizacoes.get(chave, {})
        ultima_verificacao = info.get('ultima_verificacao')
        ultima_atualizacao = info.get('ultima_atualizacao')
        ultima_lida = info.get('ultima_lida')
        
        # Se já verificamos recentemente, não verificamos novamente
        if ultima_verificacao:
            try:
                tempo_passado = datetime.now() - datetime.fromisoformat(ultima_verificacao)
                if tempo_passado.total_seconds() < self.tempo_minimo_entre_verificacoes:
                    logger.debug(f"Verificação recente para {chave}, não verificando novamente")
                    # Retorna a quantidade de atualizações não lidas
                    quantidade = info.get('quantidade_nao_lida', 0)
                    # Armazena no cache
                    self.cache_verificacao[chave] = (time.time(), quantidade)
                    return quantidade
            except:
                pass
        
        # Verifica a atualização no site
        quantidade_novas = self._verificar_quantidade_atualizacoes(url, ultima_lida)
        
        # Atualiza o estado
        agora_iso = datetime.now().isoformat()
        if chave not in atualizacoes:
            atualizacoes[chave] = {}
        
        atualizacoes[chave]['ultima_verificacao'] = agora_iso
        atualizacoes[chave]['quantidade_nao_lida'] = quantidade_novas
        
        # Salva as atualizações
        self._salvar_atualizacoes(atualizacoes)
        
        # Armazena no cache
        self.cache_verificacao[chave] = (time.time(), quantidade_novas)
        
        # Retorna a quantidade de atualizações não lidas
        return quantidade_novas
    
    def _verificar_quantidade_atualizacoes(self, url, ultima_lida):
        """Verifica quantas atualizações existem desde a última leitura"""
        logger.debug(f"Verificando quantidade de atualizações para: {url}")
        
        try:
            # Timeout reduzido para evitar travamentos
            response = requests.get(url, timeout=self.timeout)
            logger.debug(f"Resposta do site ({url}): {response.status_code}")
            
            if response.status_code == 200:
                # Verifica se é JSON (API WordPress)
                try:
                    data = response.json()
                    if isinstance(data, list):
                        # Converte a data da última leitura para datetime se existir
                        data_ultima_lida = None
                        if ultima_lida:
                            try:
                                data_ultima_lida = datetime.fromisoformat(ultima_lida)
                            except:
                                pass
                        
                        # Conta quantos itens são mais recentes que a última leitura
                        count = 0
                        for item in data:
                            if 'date' in item:
                                try:
                                    item_date = datetime.strptime(item['date'], "%Y-%m-%dT%H:%M:%S")
                                    if not data_ultima_lida or item_date > data_ultima_lida:
                                        count += 1
                                except:
                                    continue
                        return count
                except:
                    # Se não for JSON, usa scraping básico
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    # Tenta encontrar elementos de conteúdo recente
                    # Para WordPress: posts, articles, etc.
                    elementos_recentes = soup.select("article, .post, .entry, .news-item")
                    
                    # Se encontrou elementos, retorna a quantidade
                    if elementos_recentes:
                        return len(elementos_recentes)
                    
                    # Fallback: conta headings como indicador de conteúdo
                    headings = soup.find_all(["h1", "h2", "h3", "h4"])
                    return min(len(headings), 5)  # Limita a 5 para não exagerar
                    
        except Exception as e:
            logger.error(f"Erro ao verificar quantidade de atualizações: {e}")
        
        return 0
    
    def marcar_como_lido(self, chave):
        """Marca uma seção como lida com cache atualizado"""
        logger.info(f"Marcando {chave} como lido")
        
        # Remove do cache para forçar nova verificação na próxima vez
        if chave in self.cache_verificacao:
            del self.cache_verificacao[chave]
        
        # Carrega o estado atual das atualizações
        atualizacoes = self._carregar_atualizacoes()
        
        # Atualiza a última data lida e zera a quantidade não lida
        agora = datetime.now().isoformat()
        if chave not in atualizacoes:
            atualizacoes[chave] = {}
        
        atualizacoes[chave]['ultima_lida'] = agora
        atualizacoes[chave]['quantidade_nao_lida'] = 0
        
        # Salva as atualizações
        self._salvar_atualizacoes(atualizacoes)
        
        return True
    
    def forcar_verificacao(self, chave, url, callback=None):
        """Força uma nova verificação removendo do cache"""
        if chave in self.cache_verificacao:
            del self.cache_verificacao[chave]
        self.verificar_atualizacao(chave, url, callback)