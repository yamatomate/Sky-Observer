# Todas as cores e fontes do app ficam aqui
# Assim se quiser mudar uma cor, muda em um só lugar

LIGHT_COLORS = {
    # Fundos
    "bg_primary":   "#FFFFFF",
    "bg_secondary": "#F5F5F0",
    "bg_sidebar":   "#EFEFEA",

    # Textos
    "text_primary":   "#1A1A18",
    "text_secondary": "#6B6B65",
    "text_muted":     "#9B9B95",

    # Bordas
    "border": "#E0E0DA",

    # Verde (ótimo)
    "green":      "#22C55E",
    "green_bg":   "#DCFCE7",
    "green_text": "#166534",

    # Amarelo (razoável)
    "yellow":      "#F59E0B",
    "yellow_bg":   "#FEF9C3",
    "yellow_text": "#713F12",

    # Vermelho (ruim)
    "red":      "#EF4444",
    "red_bg":   "#FEE2E2",
    "red_text": "#991B1B",

    # Azul (destaque, item ativo)
    "blue":    "#2563EB",
    "blue_bg": "#EFF6FF",
}

DARK_COLORS = {
    "bg_primary":   "#121212",
    "bg_secondary": "#1E1E1E",
    "bg_sidebar":   "#0A0A0A",
    "text_primary":   "#F3F4F6",
    "text_secondary": "#9CA3AF",
    "text_muted":     "#6B7280",
    "border": "#374151",
    "green":      "#4ADE80",
    "green_bg":   "#064E3B",
    "green_text": "#A7F3D0",
    "yellow":      "#FDE047",
    "yellow_bg":   "#713F12",
    "yellow_text": "#FEF08A",
    "red":      "#FCA5A5",
    "red_bg":   "#7F1D1D",
    "red_text": "#FECACA",
    "blue":    "#60A5FA",
    "blue_bg": "#1E3A8A",
}

COLORS = LIGHT_COLORS.copy()
CURRENT_THEME = "light"

def toggle_theme():
    global CURRENT_THEME
    CURRENT_THEME = "dark" if CURRENT_THEME == "light" else "light"
    new_colors = DARK_COLORS if CURRENT_THEME == "dark" else LIGHT_COLORS
    COLORS.update(new_colors)

FONTS = {
    "logo":     ("Helvetica", 12, "bold italic"),
    "title":    ("Helvetica", 14, "bold"),
    "subtitle": ("Helvetica", 12),
    "body":     ("Helvetica", 11),
    "small":    ("Helvetica", 10),
    "metric":   ("Helvetica", 22, "bold"),
    "score":    ("Helvetica", 34, "bold"),
}