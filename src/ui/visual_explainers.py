"""
Visual Explainer SVG Diagrams

Generates inline SVG cross-section diagrams for design concepts.
All diagrams are ~200×120px, programmatically generated in Python.
"""

def pedestal_base_diagram() -> str:
    """
    Cross-section showing raised bump on compartment floor.
    Push down on one end → other end pops up for grabbing.
    """
    return """
    <svg width="200" height="120" xmlns="http://www.w3.org/2000/svg">
        <!-- Container box -->
        <rect x="20" y="30" width="160" height="70" fill="none" stroke="#333" stroke-width="2"/>

        <!-- Cards on pedestal -->
        <rect x="40" y="40" width="120" height="35" fill="#e0e0e0" stroke="#666" stroke-width="1.5"/>
        <line x1="50" y1="45" x2="50" y2="70" stroke="#999" stroke-width="1"/>
        <line x1="70" y1="45" x2="70" y2="70" stroke="#999" stroke-width="1"/>
        <line x1="90" y1="45" x2="90" y2="70" stroke="#999" stroke-width="1"/>
        <line x1="110" y1="45" x2="110" y2="70" stroke="#999" stroke-width="1"/>
        <line x1="130" y1="45" x2="130" y2="70" stroke="#999" stroke-width="1"/>
        <line x1="150" y1="45" x2="150" y2="70" stroke="#999" stroke-width="1"/>

        <!-- Pedestal bump -->
        <path d="M 60 75 L 60 85 L 140 85 L 140 75" fill="#ccc" stroke="#666" stroke-width="2"/>

        <!-- Floor -->
        <line x1="20" y1="100" x2="60" y2="100" stroke="#333" stroke-width="2"/>
        <line x1="140" y1="100" x2="180" y2="100" stroke="#333" stroke-width="2"/>

        <!-- Arrows and labels -->
        <text x="30" y="115" font-size="10" fill="#333">Push ↓</text>
        <text x="145" y="115" font-size="10" fill="#333">↑ Pops up</text>

        <!-- Label -->
        <text x="100" y="15" font-size="11" fill="#333" text-anchor="middle" font-weight="bold">Pedestal Base</text>
    </svg>
    """

def finger_cutout_diagram() -> str:
    """
    Front view showing scoop in compartment wall for finger access.
    """
    return """
    <svg width="200" height="120" xmlns="http://www.w3.org/2000/svg">
        <!-- Container box front view -->
        <line x1="30" y1="30" x2="30" y2="90" stroke="#333" stroke-width="2"/>
        <line x1="170" y1="30" x2="170" y2="90" stroke="#333" stroke-width="2"/>

        <!-- Left wall -->
        <line x1="30" y1="30" x2="50" y2="30" stroke="#333" stroke-width="2"/>
        <line x1="30" y1="90" x2="50" y2="90" stroke="#333" stroke-width="2"/>

        <!-- Cutout curve (left side) -->
        <path d="M 50 90 Q 60 85, 70 75 L 70 30" fill="none" stroke="#333" stroke-width="2"/>

        <!-- Cutout curve (right side) -->
        <path d="M 130 30 L 130 75 Q 140 85, 150 90" fill="none" stroke="#333" stroke-width="2"/>

        <!-- Right wall -->
        <line x1="150" y1="30" x2="170" y2="30" stroke="#333" stroke-width="2"/>
        <line x1="150" y1="90" x2="170" y2="90" stroke="#333" stroke-width="2"/>

        <!-- Floor -->
        <line x1="30" y1="90" x2="170" y2="90" stroke="#333" stroke-width="2"/>

        <!-- Interior shading to show depth -->
        <rect x="70" y="35" width="60" height="40" fill="#f0f0f0" opacity="0.5"/>

        <!-- Arrow and label -->
        <text x="100" y="55" font-size="10" fill="#666" text-anchor="middle">← Reach in →</text>
        <text x="100" y="110" font-size="10" fill="#333" text-anchor="middle">30mm wide cutout</text>

        <!-- Label -->
        <text x="100" y="15" font-size="11" fill="#333" text-anchor="middle" font-weight="bold">Finger Cutout</text>
    </svg>
    """

def bottom_hole_diagram() -> str:
    """
    Side cross-section showing hole in floor for pushing tokens up.
    """
    return """
    <svg width="200" height="120" xmlns="http://www.w3.org/2000/svg">
        <!-- Container box -->
        <rect x="20" y="30" width="160" height="60" fill="none" stroke="#333" stroke-width="2"/>

        <!-- Tokens (circles) -->
        <circle cx="50" cy="60" r="8" fill="#d0d0d0" stroke="#666" stroke-width="1"/>
        <circle cx="70" cy="60" r="8" fill="#d0d0d0" stroke="#666" stroke-width="1"/>
        <circle cx="90" cy="60" r="8" fill="#d0d0d0" stroke="#666" stroke-width="1"/>
        <circle cx="110" cy="60" r="8" fill="#d0d0d0" stroke="#666" stroke-width="1"/>
        <circle cx="130" cy="60" r="8" fill="#d0d0d0" stroke="#666" stroke-width="1"/>
        <circle cx="150" cy="60" r="8" fill="#d0d0d0" stroke="#666" stroke-width="1"/>

        <!-- Floor with hole -->
        <line x1="20" y1="90" x2="85" y2="90" stroke="#333" stroke-width="2"/>
        <line x1="115" y1="90" x2="180" y2="90" stroke="#333" stroke-width="2"/>

        <!-- Hole opening -->
        <ellipse cx="100" cy="90" rx="15" ry="3" fill="none" stroke="#333" stroke-width="2"/>

        <!-- Arrow showing push direction -->
        <line x1="100" y1="105" x2="100" y2="95" stroke="#1f77b4" stroke-width="2" marker-end="url(#arrowblue)"/>
        <text x="100" y="115" font-size="10" fill="#1f77b4" text-anchor="middle">Push up</text>

        <!-- Arrow marker -->
        <defs>
            <marker id="arrowblue" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#1f77b4"/>
            </marker>
        </defs>

        <!-- Label -->
        <text x="100" y="15" font-size="11" fill="#333" text-anchor="middle" font-weight="bold">Bottom Hole (Vacuum Release)</text>
    </svg>
    """

def lid_comparison_diagram() -> str:
    """
    Side-by-side comparison of inset lid vs cap lid.
    """
    return """
    <svg width="200" height="120" xmlns="http://www.w3.org/2000/svg">
        <!-- Inset lid (left) -->
        <g transform="translate(0, 0)">
            <text x="50" y="15" font-size="10" fill="#333" text-anchor="middle" font-weight="bold">Inset Lid</text>

            <!-- Container -->
            <rect x="20" y="25" width="60" height="50" fill="none" stroke="#333" stroke-width="2"/>

            <!-- Inset lid -->
            <rect x="25" y="25" width="50" height="8" fill="#b0b0b0" stroke="#666" stroke-width="2"/>

            <!-- Interior space -->
            <rect x="25" y="33" width="50" height="37" fill="#f5f5f5"/>

            <!-- Dimension arrow -->
            <line x1="85" y1="25" x2="85" y2="75" stroke="#999" stroke-width="1" stroke-dasharray="2,2"/>
            <text x="92" y="52" font-size="9" fill="#666">H</text>

            <text x="50" y="95" font-size="9" fill="#666" text-anchor="middle">No added height</text>
        </g>

        <!-- Cap lid (right) -->
        <g transform="translate(100, 0)">
            <text x="50" y="15" font-size="10" fill="#333" text-anchor="middle" font-weight="bold">Cap Lid</text>

            <!-- Container -->
            <rect x="20" y="33" width="60" height="50" fill="none" stroke="#333" stroke-width="2"/>

            <!-- Cap lid sitting on top -->
            <rect x="15" y="25" width="70" height="8" fill="#b0b0b0" stroke="#666" stroke-width="2"/>

            <!-- Interior space -->
            <rect x="25" y="38" width="50" height="40" fill="#f5f5f5"/>

            <!-- Dimension arrow -->
            <line x1="85" y1="25" x2="85" y2="83" stroke="#999" stroke-width="1" stroke-dasharray="2,2"/>
            <text x="92" y="56" font-size="9" fill="#666">H+</text>

            <text x="50" y="95" font-size="9" fill="#666" text-anchor="middle">Adds lid thickness</text>
        </g>
    </svg>
    """

def nested_subtrays_diagram() -> str:
    """
    Top-down view showing removable sub-trays inside parent tray.
    """
    return """
    <svg width="200" height="120" xmlns="http://www.w3.org/2000/svg">
        <!-- Parent tray -->
        <rect x="10" y="20" width="180" height="80" fill="#f9f9f9" stroke="#333" stroke-width="2"/>

        <!-- Left sub-tray -->
        <rect x="20" y="30" width="75" height="60" fill="#e0f0ff" stroke="#1f77b4" stroke-width="2" stroke-dasharray="3,2"/>
        <text x="57" y="55" font-size="10" fill="#1f77b4" text-anchor="middle" font-weight="bold">Coins</text>
        <text x="57" y="67" font-size="9" fill="#1f77b4" text-anchor="middle">(Player 1-2)</text>
        <text x="57" y="85" font-size="8" fill="#1f77b4" text-anchor="middle">↑ Lift out</text>

        <!-- Right sub-tray -->
        <rect x="105" y="30" width="75" height="60" fill="#ffe0f0" stroke="#d62728" stroke-width="2" stroke-dasharray="3,2"/>
        <text x="142" y="55" font-size="10" fill="#d62728" text-anchor="middle" font-weight="bold">Coins</text>
        <text x="142" y="67" font-size="9" fill="#d62728" text-anchor="middle">(Player 3-4)</text>
        <text x="142" y="85" font-size="8" fill="#d62728" text-anchor="middle">↑ Lift out</text>

        <!-- Arrows showing table placement -->
        <line x1="30" y1="105" x2="10" y2="115" stroke="#666" stroke-width="1" marker-end="url(#arrow)"/>
        <text x="5" y="118" font-size="8" fill="#666">Table left</text>

        <line x1="170" y1="105" x2="190" y2="115" stroke="#666" stroke-width="1" marker-end="url(#arrow)"/>
        <text x="175" y="118" font-size="8" fill="#666">Table right</text>

        <!-- Arrow marker -->
        <defs>
            <marker id="arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
                <path d="M 0 0 L 8 4 L 0 8 z" fill="#666"/>
            </marker>
        </defs>

        <!-- Label -->
        <text x="100" y="12" font-size="11" fill="#333" text-anchor="middle" font-weight="bold">Nested Sub-Trays</text>
    </svg>
    """

def angled_card_well_diagram() -> str:
    """
    Side view showing tilted compartment for thumbing through cards.
    """
    return """
    <svg width="200" height="120" xmlns="http://www.w3.org/2000/svg">
        <!-- Container -->
        <rect x="20" y="30" width="160" height="70" fill="none" stroke="#333" stroke-width="2"/>

        <!-- Angled floor -->
        <line x1="20" y1="100" x2="120" y2="65" stroke="#333" stroke-width="2"/>

        <!-- Back wall -->
        <line x1="120" y1="30" x2="120" y2="65" stroke="#333" stroke-width="2"/>

        <!-- Cards on angle -->
        <g transform="rotate(-15, 70, 82)">
            <rect x="40" y="55" width="60" height="55" fill="#e0e0e0" stroke="#666" stroke-width="1.5"/>
            <line x1="45" y1="60" x2="45" y2="105" stroke="#999" stroke-width="1"/>
            <line x1="55" y1="60" x2="55" y2="105" stroke="#999" stroke-width="1"/>
            <line x1="65" y1="60" x2="65" y2="105" stroke="#999" stroke-width="1"/>
            <line x1="75" y1="60" x2="75" y2="105" stroke="#999" stroke-width="1"/>
            <line x1="85" y1="60" x2="85" y2="105" stroke="#999" stroke-width="1"/>
            <line x1="95" y1="60" x2="95" y2="105" stroke="#999" stroke-width="1"/>
        </g>

        <!-- Angle indicator -->
        <path d="M 20 100 L 40 100 A 20 20 0 0 1 48 92" fill="none" stroke="#1f77b4" stroke-width="1"/>
        <text x="50" y="98" font-size="9" fill="#1f77b4">15°</text>

        <!-- Hand/thumb indicator -->
        <text x="140" y="75" font-size="10" fill="#666">← Thumb</text>
        <text x="140" y="87" font-size="10" fill="#666">through</text>

        <!-- Label -->
        <text x="100" y="15" font-size="11" fill="#333" text-anchor="middle" font-weight="bold">Angled Card Well</text>
    </svg>
    """

def wall_thickness_diagram() -> str:
    """
    Zoomed cross-section showing perimeter lines in wall.
    """
    return """
    <svg width="200" height="120" xmlns="http://www.w3.org/2000/svg">
        <!-- Wall cross-section (zoomed) -->
        <g transform="translate(50, 30)">
            <!-- Three perimeter lines -->
            <line x1="0" y1="0" x2="0" y2="60" stroke="#ff7f0e" stroke-width="3"/>
            <line x1="8" y1="0" x2="8" y2="60" stroke="#ff7f0e" stroke-width="3"/>
            <line x1="16" y1="0" x2="16" y2="60" stroke="#ff7f0e" stroke-width="3"/>

            <!-- Dimension arrows -->
            <line x1="0" y1="70" x2="8" y2="70" stroke="#333" stroke-width="1" marker-start="url(#arrowleft)" marker-end="url(#arrowright)"/>
            <text x="4" y="82" font-size="9" fill="#333" text-anchor="middle">0.4mm</text>

            <line x1="0" y1="-10" x2="16" y2="-10" stroke="#1f77b4" stroke-width="1.5" marker-start="url(#arrowleftblue)" marker-end="url(#arrowrightblue)"/>
            <text x="8" y="-13" font-size="10" fill="#1f77b4" text-anchor="middle" font-weight="bold">1.2mm total</text>
        </g>

        <!-- Labels -->
        <text x="100" y="15" font-size="11" fill="#333" text-anchor="middle" font-weight="bold">Wall Thickness (3 Perimeters)</text>
        <text x="100" y="110" font-size="9" fill="#666" text-anchor="middle">0.4mm nozzle × 3 = 1.2mm wall</text>

        <!-- Arrow markers -->
        <defs>
            <marker id="arrowleft" markerWidth="8" markerHeight="8" refX="0" refY="4" orient="auto">
                <path d="M 8 0 L 0 4 L 8 8 z" fill="#333"/>
            </marker>
            <marker id="arrowright" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto">
                <path d="M 0 0 L 8 4 L 0 8 z" fill="#333"/>
            </marker>
            <marker id="arrowleftblue" markerWidth="8" markerHeight="8" refX="0" refY="4" orient="auto">
                <path d="M 8 0 L 0 4 L 8 8 z" fill="#1f77b4"/>
            </marker>
            <marker id="arrowrightblue" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto">
                <path d="M 0 0 L 8 4 L 0 8 z" fill="#1f77b4"/>
            </marker>
        </defs>
    </svg>
    """

def clearance_zones_diagram() -> str:
    """
    Top view showing component outline with clearance boundary.
    """
    return """
    <svg width="200" height="120" xmlns="http://www.w3.org/2000/svg">
        <!-- Component (card outline) -->
        <rect x="70" y="35" width="60" height="50" fill="#e0e0e0" stroke="#333" stroke-width="2"/>
        <text x="100" y="63" font-size="10" fill="#333" text-anchor="middle">Card</text>

        <!-- Clearance zone (dashed) -->
        <rect x="60" y="25" width="80" height="70" fill="none" stroke="#1f77b4" stroke-width="2" stroke-dasharray="4,2"/>

        <!-- Dimension arrows -->
        <!-- Left side -->
        <line x1="60" y1="60" x2="70" y2="60" stroke="#1f77b4" stroke-width="1" marker-start="url(#arrowleftblue2)" marker-end="url(#arrowrightblue2)"/>
        <text x="65" y="56" font-size="8" fill="#1f77b4" text-anchor="middle">+2mm</text>

        <!-- Top side -->
        <line x1="100" y1="25" x2="100" y2="35" stroke="#1f77b4" stroke-width="1" marker-start="url(#arrowupblue)" marker-end="url(#arrowdownblue)"/>
        <text x="115" y="31" font-size="8" fill="#1f77b4">+5mm</text>

        <!-- Labels -->
        <text x="100" y="15" font-size="11" fill="#333" text-anchor="middle" font-weight="bold">Clearance Zones</text>
        <text x="100" y="110" font-size="9" fill="#666" text-anchor="middle">Cards: +2mm sides, +5mm top for finger access</text>

        <!-- Arrow markers -->
        <defs>
            <marker id="arrowleftblue2" markerWidth="6" markerHeight="6" refX="0" refY="3" orient="auto">
                <path d="M 6 0 L 0 3 L 6 6 z" fill="#1f77b4"/>
            </marker>
            <marker id="arrowrightblue2" markerWidth="6" markerHeight="6" refX="6" refY="3" orient="auto">
                <path d="M 0 0 L 6 3 L 0 6 z" fill="#1f77b4"/>
            </marker>
            <marker id="arrowupblue" markerWidth="6" markerHeight="6" refX="3" refY="0" orient="auto">
                <path d="M 0 6 L 3 0 L 6 6 z" fill="#1f77b4"/>
            </marker>
            <marker id="arrowdownblue" markerWidth="6" markerHeight="6" refX="3" refY="6" orient="auto">
                <path d="M 0 0 L 3 6 L 6 0 z" fill="#1f77b4"/>
            </marker>
        </defs>
    </svg>
    """


# Dictionary mapping concept names to diagram functions
DIAGRAMS = {
    'pedestal_base': pedestal_base_diagram,
    'finger_cutout': finger_cutout_diagram,
    'bottom_hole': bottom_hole_diagram,
    'lid_comparison': lid_comparison_diagram,
    'nested_subtrays': nested_subtrays_diagram,
    'angled_card_well': angled_card_well_diagram,
    'wall_thickness': wall_thickness_diagram,
    'clearance_zones': clearance_zones_diagram,
}


def get_diagram(concept: str) -> str:
    """
    Get SVG diagram for a design concept.

    Args:
        concept: Name of the concept (e.g., 'pedestal_base', 'finger_cutout')

    Returns:
        SVG string ready for st.markdown with unsafe_allow_html=True
    """
    if concept in DIAGRAMS:
        return DIAGRAMS[concept]()
    return f"<p>Diagram for '{concept}' not found</p>"


def show_diagram(concept: str, description: str = None):
    """
    Display a diagram with optional description in Streamlit.

    Args:
        concept: Name of the concept
        description: Optional text description to show below diagram
    """
    import streamlit as st

    svg = get_diagram(concept)
    st.markdown(svg, unsafe_allow_html=True)

    if description:
        st.caption(description)
