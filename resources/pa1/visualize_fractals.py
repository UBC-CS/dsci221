"""
DSCI 221 - PA1 Fractal Visualizer
=================================

This script visualizes the fractals you create in PA1!

Instructions:
1. Copy your lsystem_expand() and turtle_interpret() functions below
2. Run this script: python visualize_fractals.py
3. A window will open showing your fractals

Requirements:
    pip install matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.collections as mc
import math

# =============================================================================
# PASTE YOUR FUNCTIONS HERE
# =============================================================================

def lsystem_expand(axiom, rules, n):
    """
    YOUR IMPLEMENTATION FROM PART 1
    Expand an L-system string n times using the given rules.
    """
    # Example implementation (replace with yours):
    if n == 0:
        return axiom
    def expand_once(s):
        return "".join(rules.get(c, c) for c in s)
    return lsystem_expand(expand_once(axiom), rules, n - 1)


def turtle_interpret(commands, step, angle, draw_chars="F"):
    """
    YOUR IMPLEMENTATION FROM PART 2
    Interpret an L-system string as turtle graphics commands.

    Note: This version supports multiple draw characters via draw_chars parameter.
    For the basic version, you can ignore draw_chars and just draw on 'F'.
    """
    # Example implementation (replace with yours):
    segments = []
    x, y = 0, 0
    heading = 0
    for cmd in commands:
        if cmd in draw_chars:
            rad = math.radians(heading)
            new_x = x + step * math.cos(rad)
            new_y = y + step * math.sin(rad)
            segments.append(((x, y), (new_x, new_y)))
            x, y = new_x, new_y
        elif cmd == '+':
            heading += angle
        elif cmd == '-':
            heading -= angle
    return segments


# =============================================================================
# FRACTAL DEFINITIONS - These use your functions!
# =============================================================================

def koch_curve(n, step=5):
    """Koch quadratic curve"""
    axiom = "F"
    rules = {"F": "F+F-F-F+F"}
    commands = lsystem_expand(axiom, rules, n)
    return turtle_interpret(commands, step, 90)


def koch_snowflake(n, step=5):
    """Classic Koch snowflake (triangle variant)"""
    axiom = "F--F--F"
    rules = {"F": "F+F--F+F"}
    commands = lsystem_expand(axiom, rules, n)
    return turtle_interpret(commands, step, 60)


def sierpinski(n, step=10):
    """Sierpinski triangle"""
    axiom = "F-G-G"
    rules = {"F": "F-G+F+G-F", "G": "GG"}
    commands = lsystem_expand(axiom, rules, n)
    return turtle_interpret(commands, step, 120, draw_chars="FG")


def dragon(n, step=10):
    """Dragon curve (Heighway dragon)"""
    axiom = "X"
    rules = {"X": "X+YF+", "Y": "-FX-Y"}
    commands = lsystem_expand(axiom, rules, n)
    return turtle_interpret(commands, step, 90, draw_chars="F")


def plant(n, step=5):
    """Fractal plant with branching"""
    # This one requires bracket support in turtle_interpret!
    axiom = "X"
    rules = {"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"}
    commands = lsystem_expand(axiom, rules, n)
    # Note: This needs bracket handling which is a bonus challenge
    return turtle_interpret(commands, step, 25, draw_chars="F")


def hilbert(n, step=10):
    """Hilbert space-filling curve"""
    axiom = "A"
    rules = {"A": "-BF+AFA+FB-", "B": "+AF-BFB-FA+"}
    commands = lsystem_expand(axiom, rules, n)
    return turtle_interpret(commands, step, 90, draw_chars="F")


# =============================================================================
# VISUALIZATION CODE
# =============================================================================

def draw_fractal(segments, ax, color='#2E86AB', linewidth=0.5, title=""):
    """Draw a fractal on a matplotlib axis."""
    if not segments:
        ax.text(0.5, 0.5, "No segments to draw!\nCheck your implementation.",
                ha='center', va='center', transform=ax.transAxes)
        ax.set_title(title)
        return

    lc = mc.LineCollection(segments, colors=[color], linewidths=linewidth)
    ax.add_collection(lc)
    ax.autoscale()
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=12, fontweight='bold')


def create_gallery():
    """Create a gallery of fractals."""
    print("Generating fractals... (this may take a moment for higher iterations)")

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle("DSCI 221 - Recursive Art Gallery", fontsize=16, fontweight='bold')

    # Koch Curve
    print("  Drawing Koch Curve...")
    draw_fractal(koch_curve(3, step=3), axes[0, 0],
                 color='#E63946', title="Koch Quadratic (n=3)")

    # Koch Snowflake
    print("  Drawing Koch Snowflake...")
    draw_fractal(koch_snowflake(4, step=2), axes[0, 1],
                 color='#457B9D', title="Koch Snowflake (n=4)")

    # Sierpinski Triangle
    print("  Drawing Sierpinski Triangle...")
    draw_fractal(sierpinski(5, step=3), axes[0, 2],
                 color='#2A9D8F', title="Sierpinski Triangle (n=5)")

    # Dragon Curve
    print("  Drawing Dragon Curve...")
    draw_fractal(dragon(12, step=3), axes[1, 0],
                 color='#E76F51', title="Dragon Curve (n=12)")

    # Hilbert Curve
    print("  Drawing Hilbert Curve...")
    draw_fractal(hilbert(5, step=3), axes[1, 1],
                 color='#9B5DE5', title="Hilbert Curve (n=5)")

    # Empty slot for student's custom fractal
    axes[1, 2].text(0.5, 0.5, "Your Custom Fractal Here!\n\nDefine your own L-system\nand add it to the gallery.",
                    ha='center', va='center', fontsize=11,
                    bbox=dict(boxstyle='round', facecolor='#F1FAEE', edgecolor='#A8DADC'))
    axes[1, 2].axis('off')
    axes[1, 2].set_title("??? (Your Creation)", fontsize=12, fontweight='bold')

    plt.tight_layout()
    print("\nOpening gallery window...")
    plt.show()


def single_fractal_demo():
    """Demo a single fractal with progressive iterations."""
    print("Showing Dragon Curve evolution...")

    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    fig.suptitle("Dragon Curve: Iteration by Iteration", fontsize=16, fontweight='bold')

    iterations = [1, 2, 3, 4, 6, 8, 10, 12]

    for idx, n in enumerate(iterations):
        row, col = idx // 4, idx % 4
        segments = dragon(n, step=5)
        draw_fractal(segments, axes[row, col],
                     color='#E76F51', linewidth=max(0.3, 2-n*0.15),
                     title=f"n={n} ({len(segments)} segments)")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    print("=" * 60)
    print("DSCI 221 - PA1 Fractal Visualizer")
    print("=" * 60)
    print()
    print("Make sure you've pasted your lsystem_expand() and")
    print("turtle_interpret() functions at the top of this file!")
    print()

    # Create the gallery
    create_gallery()

    # Optionally show the single fractal demo
    # single_fractal_demo()
