from pathlib import Path
import json
import pandas as pd

class SemanticFlowRuntime:
    def __init__(self, geometry_csv, output_dir):
        self.geometry_csv = Path(geometry_csv)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def execute(self):
        df = pd.read_csv(self.geometry_csv)

        df['flow_type'] = df['extracted_text'].fillna('').str.lower().apply(
            lambda x: 'SUPPLY' if 'supply' in x else ('RETURN' if 'return' in x else 'GENERAL')
        )

        edges = []

        for slide in sorted(df['slide_number'].unique()):
            sdf = df[df['slide_number'] == slide]

            for i in range(len(sdf) - 1):
                a = sdf.iloc[i]
                b = sdf.iloc[i + 1]

                direction = 'LEFT_TO_RIGHT' if a['left_mm'] < b['left_mm'] else 'RIGHT_TO_LEFT'

                edges.append({
                    'source': f"S{slide}_{a['shape_index']}",
                    'target': f"S{slide}_{b['shape_index']}",
                    'direction': direction,
                    'connector_anchored': bool(a['connector_like']),
                    'semantic_flow_type': a['flow_type']
                })

        edge_df = pd.DataFrame(edges)

        edge_csv = self.output_dir / 'semantic_flow_edges.csv'
        edge_df.to_csv(edge_csv, index=False)

        summary = {
            'edges': len(edge_df),
            'directional_graph': True,
            'connector_anchored_edges': int(edge_df['connector_anchored'].sum()) if not edge_df.empty else 0
        }

        summary_json = self.output_dir / 'semantic_flow_summary.json'
        summary_json.write_text(json.dumps(summary, indent=2), encoding='utf-8')

        return {
            'edges_csv': str(edge_csv),
            'summary_json': str(summary_json)
        }
