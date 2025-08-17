from __future__ import annotations

import streamlit as st


# Supported languages
LANGS = {"en": "English", "es": "Español"}


# Central translation dictionary. Extend over time.
TRANSLATIONS = {
    "en": {
        # Generic
        "Español": "Español",
        "English": "English",
        "Language": "Language",
        "Profile": "Profile",
        "Prediction (CGEM)": "Prediction (CGEM)",
        "All Profiles (Batch)": "All Profiles (Batch)",
        "Select aerobatic manoeuvre": "Select aerobatic manoeuvre",
        "Description": "Description",
        "Duration": "Duration",
        "Max +G": "Max +G",
        "Max -G": "Max -G",
        "Weighted mean G": "Weighted mean G",
        "G-Force": "G-Force",

        # App titles
        "G-Effects Model": "G-Effects Model",
        "Aerobatic G-Profile – CGEM Prediction Demo": "Aerobatic G-Profile – CGEM Prediction Demo",

        # Sidebar
        "Configuration ⚙️": "Configuration ⚙️",
        "Pilot Profile 👨‍✈️": "Pilot Profile 👨‍✈️",
        "Visualization Options 📊": "Visualization Options 📊",
        "2D Physiological Plots": "2D Physiological Plots",
        "3D Trajectory Plot": "3D Trajectory Plot",
        "Animated Timeline": "Animated Timeline",
        "Parameter Heatmap": "Parameter Heatmap",
        "Cardiovascular Response": "Cardiovascular Response",

        # Sections / labels
        "Pilot configuration": "Pilot configuration",
        "Sex": "Sex",
        "Male": "Male",
        "Female": "Female",
        "Run mode": "Run mode",
        "Select simulation mode": "Select simulation mode",
        "Custom EGP (aerobatic profile)": "Custom EGP (aerobatic profile)",
        "Internal centrifuge experiment": "Internal centrifuge experiment",
        "Run CGEM Physiological Simulation": "Run CGEM Physiological Simulation",
        "Run CGEM Prediction": "Run CGEM Prediction",
        "Run Batch Analysis": "Run Batch Analysis",
        "G-Force Profile: {profile}": "G-Force Profile: {profile}",
        "Detailed Analysis: {profile}": "Detailed Analysis: {profile}",
        "Comparative Analysis Across All Maneuvers": "Comparative Analysis Across All Maneuvers",
        "ECharts Scientific Dashboard": "ECharts Scientific Dashboard",
        "Layout": "Layout",
        "Grid (all charts)": "Grid (all charts)",
        "Single (one chart)": "Single (one chart)",
        "Chart": "Chart",
        "Lines": "Lines",
        "Heatmap": "Heatmap",
        "Histogram": "Histogram",
        "Radar": "Radar",
        "Scatter": "Scatter",
        "Durations": "Durations",
        "Flows": "Flows",
        "Banks": "Banks",
        "HLAP": "HLAP",
        "3D (ECharts)": "3D (ECharts)",
        "Pilot Survey": "Pilot Survey",
        "Administrative": "Administrative",
        "Pilot Demographics & Experience": "Pilot Demographics & Experience",
        "G-Force Experience History": "G-Force Experience History",
        "Sleep & Fatigue Assessment": "Sleep & Fatigue Assessment",
        "Physical Health & Fitness": "Physical Health & Fitness",
        "Physiological Status (Day of Survey)": "Physiological Status (Day of Survey)",
        "Environmental & Operational Factors": "Environmental & Operational Factors",
        "Lifestyle & Behavioral Factors": "Lifestyle & Behavioral Factors",
        "Performance & Symptoms": "Performance & Symptoms",
        "Training & Countermeasures": "Training & Countermeasures",
        "Psychological Factors": "Psychological Factors",
        "Flight Surgeon Objective Data (optional)": "Flight Surgeon Objective Data (optional)",
        "Attach RR Files (optional)": "Attach RR Files (optional)",
        "Database": "Database",
        "Search Pilot by ID and view files": "Search Pilot by ID and view files",
        "Export": "Export",
        "Delete records": "Delete records",
        "Educational Resources": "Educational Resources",

        # Messages
        "Run the physiological simulation first to populate the ECharts dashboard.": "Run the physiological simulation first to populate the ECharts dashboard.",
        "Simulation failed: {error}": "Simulation failed: {error}",
        "Unable to render ECharts dashboard: {error}": "Unable to render ECharts dashboard: {error}",
        "Run the physiological simulation first to see detailed analysis.": "Run the physiological simulation first to see detailed analysis.",
    },
    "es": {
        "Español": "Español",
        "English": "Inglés",
        "Language": "Idioma",
        "Profile": "Perfil",
        "Prediction (CGEM)": "Predicción (CGEM)",
        "All Profiles (Batch)": "Todos los perfiles (lote)",
        "Select aerobatic manoeuvre": "Selecciona maniobra acrobática",
        "Description": "Descripción",
        "Duration": "Duración",
        "Max +G": "+G máximo",
        "Max -G": "-G máximo",
        "Weighted mean G": "Media ponderada de G",
        "G-Force": "Fuerza G",

        # App titles
        "G-Effects Model": "Modelo de Efectos G",
        "Aerobatic G-Profile – CGEM Prediction Demo": "Perfil G acrobático – Demostración de predicción CGEM",

        # Sidebar
        "Configuration ⚙️": "Configuración ⚙️",
        "Pilot Profile 👨‍✈️": "Perfil del Piloto 👨‍✈️",
        "Visualization Options 📊": "Opciones de visualización 📊",
        "2D Physiological Plots": "Gráficas fisiológicas 2D",
        "3D Trajectory Plot": "Trayectoria 3D",
        "Animated Timeline": "Línea de tiempo animada",
        "Parameter Heatmap": "Mapa de calor de parámetros",
        "Cardiovascular Response": "Respuesta cardiovascular",

        # Sections / labels
        "Pilot configuration": "Configuración del piloto",
        "Sex": "Sexo",
        "Male": "Masculino",
        "Female": "Femenino",
        "Run mode": "Modo de ejecución",
        "Select simulation mode": "Selecciona el modo de simulación",
        "Custom EGP (aerobatic profile)": "EGP personalizado (perfil acrobático)",
        "Internal centrifuge experiment": "Experimento de centrifugado interno",
        "Run CGEM Physiological Simulation": "Ejecutar simulación fisiológica CGEM",
        "Run CGEM Prediction": "Ejecutar predicción CGEM",
        "Run Batch Analysis": "Ejecutar análisis por lotes",
        "G-Force Profile: {profile}": "Perfil de fuerza G: {profile}",
        "Detailed Analysis: {profile}": "Análisis detallado: {profile}",
        "Comparative Analysis Across All Maneuvers": "Análisis comparativo entre todas las maniobras",
        "ECharts Scientific Dashboard": "Panel científico ECharts",
        "Layout": "Disposición",
        "Grid (all charts)": "Cuadrícula (todos los gráficos)",
        "Single (one chart)": "Único (un gráfico)",
        "Chart": "Gráfico",
        "Lines": "Líneas",
        "Heatmap": "Mapa de calor",
        "Histogram": "Histograma",
        "Radar": "Radar",
        "Scatter": "Dispersión",
        "Durations": "Duraciones",
        "Flows": "Flujos",
        "Banks": "Inclinaciones",
        "HLAP": "HLAP",
        "3D (ECharts)": "3D (ECharts)",
        "Pilot Survey": "Encuesta de piloto",
        "Administrative": "Administrativo",
        "Pilot Demographics & Experience": "Demografía y experiencia del piloto",
        "G-Force Experience History": "Historial de experiencia con fuerzas G",
        "Sleep & Fatigue Assessment": "Evaluación del sueño y la fatiga",
        "Physical Health & Fitness": "Salud física y estado físico",
        "Physiological Status (Day of Survey)": "Estado fisiológico (día de la encuesta)",
        "Environmental & Operational Factors": "Factores ambientales y operacionales",
        "Lifestyle & Behavioral Factors": "Estilo de vida y factores conductuales",
        "Performance & Symptoms": "Rendimiento y síntomas",
        "Training & Countermeasures": "Entrenamiento y contramedidas",
        "Psychological Factors": "Factores psicológicos",
        "Flight Surgeon Objective Data (optional)": "Datos objetivos del médico de vuelo (opcional)",
        "Attach RR Files (optional)": "Adjuntar archivos RR (opcional)",
        "Database": "Base de datos",
        "Search Pilot by ID and view files": "Buscar piloto por ID y ver archivos",
        "Export": "Exportar",
        "Delete records": "Eliminar registros",
        "Educational Resources": "Recursos educativos",

        # Messages
        "Run the physiological simulation first to populate the ECharts dashboard.": "Ejecute primero la simulación fisiológica para llenar el panel de ECharts.",
        "Simulation failed: {error}": "La simulación falló: {error}",
        "Unable to render ECharts dashboard: {error}": "No se pudo renderizar el panel de ECharts: {error}",
        "Run the physiological simulation first to see detailed analysis.": "Ejecute primero la simulación fisiológica para ver el análisis detallado.",
    },
}


def get_locale() -> str:
    """Return the current UI language code."""
    return st.session_state.get("lang", "en")


def set_locale(lang: str):
    """Set the current UI language code."""
    st.session_state["lang"] = "es" if lang == "es" else "en"


def _(key: str, **kwargs) -> str:
    """Translate a string key; fallback to English and then the key itself.

    Use Python str.format with kwargs for placeholders.
    """
    lang = get_locale()
    text = TRANSLATIONS.get(lang, {}).get(key) or TRANSLATIONS["en"].get(key) or key
    try:
        return text.format(**kwargs) if kwargs else text
    except Exception:
        # If formatting fails, return untranslated text to avoid breaking UX
        return text


def use_lang_selector():
    """Render a single-toggle language selector in the sidebar.

    One-click toggle labeled 'Español'. When on -> es, off -> en.
    """
    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"
    # Support older Streamlit versions without toggle()
    try:
        es_on = st.sidebar.toggle("Español", value=(st.session_state["lang"] == "es"))
    except Exception:
        es_on = st.sidebar.checkbox("Español", value=(st.session_state["lang"] == "es"))
    set_locale("es" if es_on else "en")
    return get_locale()


