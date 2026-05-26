from pathlib import Path

backends = ['Fallback','NIST','CoolProp','REFPROP','HEPAK']

residuals = [
    [0.0,0.12,0.34,0.48,0.57],
    [0.12,0.0,0.18,0.31,0.41],
    [0.34,0.18,0.0,0.16,0.28],
    [0.48,0.31,0.16,0.0,0.19],
    [0.57,0.41,0.28,0.19,0.0],
]

def build_backend_residual_heatmap():
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise SystemExit(
            'Plotly is required to generate backend residual heatmap. Install it with: pip install plotly'
        ) from exc

    fig = go.Figure(
        data=go.Heatmap(
            z=residuals,
            x=backends,
            y=backends,
        )
    )
    fig.update_layout(
        title='Backend Residual Heatmap (A9 Scaffold)',
    )
    return fig


def main():
    output_path = Path('outputs/backend_residual_heatmap.html')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig = build_backend_residual_heatmap()
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


if __name__ == '__main__':
    main()
