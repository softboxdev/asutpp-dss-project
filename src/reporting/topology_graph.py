"""Граф топологии архитектуры."""
import networkx as nx
from pathlib import Path
from typing import Dict, Optional
from loguru import logger
from .base import ReportSection


class TopologyGraphBuilder(ReportSection):
    """Строит и экспортирует граф архитектуры."""
    
    name = "topology"
    title = "Граф топологии архитектуры"
    order = 10
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        """Построить граф из архитектуры."""
        if not pipeline_result.architectures:
            logger.warning("Нет архитектур для построения графа")
            return {'error': 'no_architectures'}
        
        arch = pipeline_result.architectures[0]
        G = self._build_graph(arch)
        metrics = self._compute_metrics(G)
        
        # Экспорт
        files = self._export_all(G)
        
        return {
            'graph': {
                'nodes': [
                    {'id': n, **G.nodes[n]}
                    for n in G.nodes()
                ],
                'edges': [
                    {'source': u, 'target': v, **G.edges[u, v]}
                    for u, v in G.edges()
                ],
            },
            'metrics': metrics,
            'files': {k: str(v) for k, v in files.items() if v},
            'mermaid': self._to_mermaid(G),
        }
    
    def _build_graph(self, architecture: Dict) -> nx.DiGraph:
        """Построить граф."""
        G = nx.DiGraph()
        
        for comp in architecture.get('components', []):
            G.add_node(
                comp['id'],
                type=comp.get('type', 'unknown'),
                capacity=comp.get('capacity', 1),
                latency=comp.get('latency', 10),
                cost=comp.get('cost', 0),
                label=self._format_label(comp['id']),
            )
        
        # Типичные связи для АСУ ТП
        connections = [
            ('sensor_adapter', 'controller', 'data_flow'),
            ('controller', 'historian', 'data_flow'),
            ('controller', 'business_logic', 'control_flow'),
            ('historian', 'hmi', 'data_flow'),
            ('business_logic', 'historian', 'data_flow'),
            ('sensor_adapter', 'event_bus', 'event'),
            ('controller', 'event_bus', 'event'),
            ('event_bus', 'historian', 'event'),
        ]
        
        for src, dst, etype in connections:
            if src in G.nodes() and dst in G.nodes():
                G.add_edge(src, dst, type=etype, bandwidth=100)
        
        return G
    
    def _format_label(self, comp_id: str) -> str:
        """Форматирование метки."""
        return comp_id.replace('_', ' ').title()
    
    def _compute_metrics(self, G: nx.DiGraph) -> Dict:
        """Метрики графа."""
        if G.number_of_nodes() == 0:
            return {}
        
        metrics = {
            'num_nodes': G.number_of_nodes(),
            'num_edges': G.number_of_edges(),
            'density': round(nx.density(G), 4),
            'is_connected': nx.is_weakly_connected(G) 
                if G.number_of_nodes() > 0 else False,
        }
        
        if G.number_of_nodes() > 1:
            degree_c = nx.degree_centrality(G)
            betweenness = nx.betweenness_centrality(G)
            
            metrics['critical_nodes'] = [
                {'node': n, 'degree': round(c, 4)}
                for n, c in sorted(degree_c.items(), 
                                   key=lambda x: x[1], reverse=True)[:3]
            ]
            
            metrics['bottlenecks'] = [
                {'node': n, 'betweenness': round(b, 4)}
                for n, b in sorted(betweenness.items(),
                                   key=lambda x: x[1], reverse=True)[:3]
            ]
        
        return metrics
    
    def _to_mermaid(self, G: nx.DiGraph) -> str:
        """Mermaid-диаграмма."""
        lines = ["graph TD"]
        
        for n in G.nodes():
            label = G.nodes[n].get('label', n)
            lines.append(f'    {n}["{label}"]')
        
        for u, v in G.edges():
            etype = G.edges[u, v].get('type', '')
            lines.append(f'    {u} -->|{etype}| {v}')
        
        return '\n'.join(lines)
    
    def _export_all(self, G: nx.DiGraph) -> Dict:
        """Экспорт во все форматы."""
        return {
            'json': self._export_json(G),
            'graphml': self._export_graphml(G),
            'mermaid': self._export_mermaid(G),
            'png': self._export_png(G),
        }
    
    def _export_json(self, G: nx.DiGraph) -> Path:
        path = self.output_dir / "topology.json"
        import json
        data = {
            'nodes': [{'id': n, **G.nodes[n]} for n in G.nodes()],
            'edges': [
                {'source': u, 'target': v, **G.edges[u, v]}
                for u, v in G.edges()
            ],
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        return path
    
    def _export_graphml(self, G: nx.DiGraph) -> Path:
        path = self.output_dir / "topology.graphml"
        nx.write_graphml(G, path)
        return path
    
    def _export_mermaid(self, G: nx.DiGraph) -> Path:
        path = self.output_dir / "topology.mmd"
        path.write_text(self._to_mermaid(G), encoding='utf-8')
        return path
    
    def _export_png(self, G: nx.DiGraph) -> Optional[Path]:
        try:
            import matplotlib.pyplot as plt
            
            plt.figure(figsize=(14, 10))
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
            
            color_map = {
                'sensor_adapter': '#4fc3f7',
                'controller': '#81c784',
                'historian': '#fff176',
                'hmi': '#ff8a65',
                'business_logic': '#ba68c8',
                'event_bus': '#f06292',
            }
            colors = [
                color_map.get(G.nodes[n].get('type', 'unknown'), '#bdbdbd')
                for n in G.nodes()
            ]
            
            nx.draw_networkx_nodes(G, pos, node_size=3000,
                                   node_color=colors, edgecolors='black',
                                   linewidths=2)
            nx.draw_networkx_edges(G, pos, edge_color='gray',
                                   arrows=True, arrowsize=20, width=2)
            
            labels = {n: G.nodes[n].get('label', n)[:15] for n in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels, font_size=10,
                                    font_weight='bold')
            
            plt.title('Топология архитектуры АСУ ТП', 
                      fontsize=16, fontweight='bold')
            plt.axis('off')
            plt.tight_layout()
            
            path = self.output_dir / "topology.png"
            plt.savefig(path, dpi=150, bbox_inches='tight')
            plt.close()
            return path
        except ImportError:
            logger.warning("matplotlib не установлен")
            return None