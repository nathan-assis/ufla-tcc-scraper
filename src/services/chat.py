"""Serviço de chat para conversação com grafos usando GRetriever."""
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class ChatService:
    """Serviço centralizado para chat com grafo usando GRetriever ou fallback por embeddings."""
    
    def __init__(self, summaries: List[str], titles: List[str], embedder, sim_matrix, graph, 
                 llm_model_name: str = "meta-llama/Llama-2-7b-chat-hf", 
                 use_lora: bool = False, 
                 mlp_out_channels: int = 4096,
                 max_out_tokens: int = 128):
        """
        Inicializa o serviço de chat.
        
        Args:
            summaries: Lista de resumos dos projetos
            titles: Lista de títulos dos projetos
            embedder: Serviço de embeddings
            sim_matrix: Matriz de similaridade
            graph: Grafo NetworkX construído
            llm_model_name: Nome do modelo LLM
            use_lora: Se deve usar LoRA
            mlp_out_channels: Canais de saída do MLP
            max_out_tokens: Máximo de tokens de saída
        """
        self.summaries = summaries
        self.titles = titles
        self.embedder = embedder
        self.sim_matrix = sim_matrix
        self.graph = graph
        self.max_out_tokens = max_out_tokens
        
        self.model = None
        self.use_gretriever = False
        self.x = None
        self.edge_index = None
        self.batch = None
        
        # Tenta inicializar GRetriever
        self._initialize_gretriever(llm_model_name, use_lora, mlp_out_channels)
    
    def _initialize_gretriever(self, llm_model_name: str, use_lora: bool, mlp_out_channels: int):
        """Tenta inicializar GRetriever com LLM e GNN."""
        try:
            from torch_geometric.nn.models import GRetriever
            import torch
            
            logger.info("Inicializando GRetriever...")
            
            # Construir tensores do grafo
            import numpy as np
            embeddings = self.embedder.encode(self.summaries)
            self.x = torch.tensor(embeddings, dtype=torch.float)
            self.edge_index = self._networkx_to_edge_index(self.graph, self.titles)
            self.batch = torch.zeros(self.x.size(0), dtype=torch.long)
            
            # Construir GNN
            gnn = self._build_gnn(self.x.size(1))
            
            # Construir LLM
            llm = self._build_llm(llm_model_name)
            
            # Construir GRetriever
            self.model = GRetriever(
                llm=llm,
                gnn=gnn,
                use_lora=use_lora,
                mlp_out_channels=mlp_out_channels,
            )
            self.use_gretriever = True
            logger.info("GRetriever inicializado com sucesso.")
        except Exception as exc:
            logger.warning(f"GRetriever não está disponível: {exc}. Usando fallback por embeddings.")
    
    def _build_gnn(self, in_channels: int):
        """Constrói o GNN (GCN ou Identity fallback)."""
        try:
            import torch
            from torch_geometric.nn import GCNConv
            
            class SimpleGNN(torch.nn.Module):
                def __init__(self, in_channels, out_channels=128):
                    super().__init__()
                    self.conv1 = GCNConv(in_channels, out_channels)
                
                def forward(self, x, edge_index):
                    return self.conv1(x, edge_index)
            
            return SimpleGNN(in_channels)
        except Exception as gnn_exc:
            logger.debug(f"Falha ao carregar GCNConv, usando IdentityGNN: {gnn_exc}")
            import torch
            
            class IdentityGNN(torch.nn.Module):
                def forward(self, x, edge_index):
                    return x
            
            return IdentityGNN()
    
    def _build_llm(self, model_name: str):
        """Constrói o wrapper de LLM usando transformers."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Carregando modelo {model_name} no device: {device}")
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            )
            model.to(device)
            model.eval()
            
            # Wrapper compatível com GRetriever
            class LLMWrapper(torch.nn.Module):
                def __init__(self, model, tokenizer, device):
                    super().__init__()
                    self.model = model
                    self.tokenizer = tokenizer
                    self.device = device
                
                def forward(self, input_ids, attention_mask=None, **kwargs):
                    with torch.no_grad():
                        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                    return outputs.logits
                
                def __call__(self, input_ids, attention_mask=None, **kwargs):
                    return self.forward(input_ids, attention_mask, **kwargs)
            
            return LLMWrapper(model, tokenizer, device)
        except Exception as e:
            logger.error(f"Falha ao carregar LLM {model_name}: {e}")
            raise
    
    def _networkx_to_edge_index(self, G, node_order: List[str]):
        """Converte NetworkX Graph para edge_index tensor."""
        try:
            import torch
        except Exception:
            raise RuntimeError("PyTorch is required to convert to edge_index")
        
        edges = []
        index_map = {node: i for i, node in enumerate(node_order)}
        for u, v in G.edges():
            if u in index_map and v in index_map:
                edges.append((index_map[u], index_map[v]))
                edges.append((index_map[v], index_map[u]))
        
        if not edges:
            return torch.empty((2, 0), dtype=torch.long)
        
        edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
        return edge_index
    
    def infer(self, query: str) -> str:
        """Executa inferência com GRetriever ou fallback."""
        if self.use_gretriever and self.model is not None:
            try:
                result = self.model.inference(
                    [query],
                    self.x,
                    self.edge_index,
                    self.batch,
                    additional_text_context=self.summaries,
                    max_out_tokens=self.max_out_tokens,
                )
                return result
            except Exception as e:
                logger.warning(f"Erro durante inferência com GRetriever: {e}. Usando fallback.")
        
        # Fallback: retrieval por embeddings
        return self._fallback_retrieval(query)
    
    def _fallback_retrieval(self, query: str, top_k: int = 5) -> str:
        """Recuperação simples por similaridade de embeddings."""
        q_emb = self.embedder.encode(query)
        emb = self.embedder.encode(self.summaries)
        sims = (emb @ q_emb.T).flatten()
        idxs = sims.argsort()[::-1][:top_k]
        results = []
        for i in idxs:
            results.append(f"- {self.titles[i]}: {self.summaries[i][:300]}{'...' if len(self.summaries[i]) > 300 else ''}")
        
        answer = "Encontrei os seguintes projetos relacionados:\n" + "\n".join(results)
        return answer
