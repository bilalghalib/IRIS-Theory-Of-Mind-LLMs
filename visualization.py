import yaml
from typing import Any

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

def generate_tom_visualization(tom: Any) -> str:
    """
    Generate a simple ASCII visualization of the Theory of Mind.
    """
    visualization = "Theory of Mind Visualization:\n"
    visualization += "=" * 40 + "\n"

    for category, elements in tom.frame.items():
        visualization += f"{category.capitalize()}:\n"
        for element in elements:
            confidence_bar = "█" * int(element.confidence * 10)
            visualization += f"  [{confidence_bar:<10}] {element.content}...\n"
        visualization += "\n"

    visualization += "Blindspots:\n"
    if isinstance(tom.blindspots, list):
        for blindspot in tom.blindspots[:3]:  # Show top 3 blindspots
            visualization += f"  - {str(blindspot)}...\n"
    else:
        visualization += "  (No blindspots identified yet)\n"

    visualization += "\nNext Steps:\n"
    if isinstance(tom.next_steps, list):
        for step in tom.next_steps[:3]:  # Show top 3 next steps
            visualization += f"  - {str(step)}...\n"
    else:
        visualization += "  (No next steps identified yet)\n"

    return visualization

# For future implementation: More advanced visualization methods
def generate_graphical_visualization(tom: Any) -> None:
    """
    Generate a graphical visualization of the Theory of Mind using a library like Plotly or Matplotlib.
    
    This is a placeholder for future implementation.
    """
    # Implement graphical visualization here
    pass