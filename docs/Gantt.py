import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

# Configuración de datos del proyecto


def create_gantt_data():
    """Crear datos estructurados para el diagrama de Gantt"""

    # Fecha de inicio del proyecto
    start_date = datetime(2024, 1, 1)

    # Definir actividades principales con sus detalles
    activities = [
        # OBJETIVO 1: Adaptación del Modelo CGEM
        {
            'Task': 'OBJ1: Adaptación Modelo CGEM',
            'Type': 'Objetivo',
            'Start': start_date,
            'Duration': 8*4,  # 8 meses en semanas
            'Progress': 0,
            'Resource': 'Equipo Ingeniería Biomédica',
            'Priority': 'Alta',
            'Budget': 120000
        },
        {
            'Task': '1.1 Análisis Arquitectura CGEM',
            'Type': 'Actividad',
            'Start': start_date,
            'Duration': 8,  # 2 meses
            'Progress': 0,
            'Resource': 'PhD Ingeniería + Investigador Senior',
            'Priority': 'Alta',
            'Budget': 15000,
            'Parent': 'OBJ1: Adaptación Modelo CGEM'
        },
        {
            'Task': '1.1.1 Revisión código fuente CGEM',
            'Type': 'Tarea',
            'Start': start_date,
            'Duration': 2,
            'Progress': 0,
            'Resource': 'PhD Ingeniería Biomédica',
            'Priority': 'Alta',
            'Budget': 3000,
            'Parent': '1.1 Análisis Arquitectura CGEM'
        },
        {
            'Task': '1.1.2 Análisis ecuaciones perfusión',
            'Type': 'Tarea',
            'Start': start_date + timedelta(weeks=2),
            'Duration': 1,
            'Progress': 0,
            'Resource': 'Investigador Senior',
            'Priority': 'Alta',
            'Budget': 2000,
            'Parent': '1.1 Análisis Arquitectura CGEM'
        },
        {
            'Task': '1.1.3 Documentación limitaciones',
            'Type': 'Tarea',
            'Start': start_date + timedelta(weeks=3),
            'Duration': 1,
            'Progress': 0,
            'Resource': 'PhD Ingeniería Biomédica',
            'Priority': 'Media',
            'Budget': 2000,
            'Parent': '1.1 Análisis Arquitectura CGEM'
        },
        {
            'Task': '1.1.4 Identificación parámetros modificables',
            'Type': 'Tarea',
            'Start': start_date + timedelta(weeks=4),
            'Duration': 2,
            'Progress': 0,
            'Resource': 'Investigador Senior',
            'Priority': 'Alta',
            'Budget': 4000,
            'Parent': '1.1 Análisis Arquitectura CGEM'
        },
        {
            'Task': '1.1.5 Informe arquitectura técnica',
            'Type': 'Entregable',
            'Start': start_date + timedelta(weeks=6),
            'Duration': 2,
            'Progress': 0,
            'Resource': 'Equipo completo',
            'Priority': 'Alta',
            'Budget': 4000,
            'Parent': '1.1 Análisis Arquitectura CGEM'
        },
        {
            'Task': '1.2 Módulos Hemodinámicos Avanzados',
            'Type': 'Actividad',
            'Start': start_date + timedelta(weeks=8),
            'Duration': 16,  # 4 meses
            'Progress': 0,
            'Resource': '2 PhD + Desarrollador Senior',
            'Priority': 'Alta',
            'Budget': 45000,
            'Parent': 'OBJ1: Adaptación Modelo CGEM'
        },
        {
            'Task': '1.2.1 Algoritmos flujo cerebral dinámico',
            'Type': 'Tarea',
            'Start': start_date + timedelta(weeks=8),
            'Duration': 4,
            'Progress': 0,
            'Resource': 'PhD Ingeniería Biomédica',
            'Priority': 'Alta',
            'Budget': 12000,
            'Parent': '1.2 Módulos Hemodinámicos Avanzados'
        },
        {
            'Task': '1.2.2 Modelos resistencia vascular',
            'Type': 'Tarea',
            'Start': start_date + timedelta(weeks=12),
            'Duration': 3,
            'Progress': 0,
            'Resource': 'PhD Ingeniería Biomédica',
            'Priority': 'Alta',
            'Budget': 9000,
            'Parent': '1.2 Módulos Hemodinámicos Avanzados'
        },
        {
            'Task': '1.2.3 Perfusión retiniana mejorada',
            'Type': 'Tarea',
            'Start': start_date + timedelta(weeks=15),
            'Duration': 3,
            'Progress': 0,
            'Resource': 'Desarrollador Senior',
            'Priority': 'Media',
            'Budget': 9000,
            'Parent': '1.2 Módulos Hemodinámicos Avanzados'
        },
        {
            'Task': '1.2.4 Validación con datos referencia',
            'Type': 'Tarea',
            'Start': start_date + timedelta(weeks=18),
            'Duration': 4,
            'Progress': 0,
            'Resource': 'Equipo completo',
            'Priority': 'Alta',
            'Budget': 12000,
            'Parent': '1.2 Módulos Hemodinámicos Avanzados'
        },
        {
            'Task': '1.2.5 Optimización computacional',
            'Type': 'Tarea',
            'Start': start_date + timedelta(weeks=22),
            'Duration': 2,
            'Progress': 0,
            'Resource': 'Desarrollador Senior',
            'Priority': 'Media',
            'Budget': 3000,
            'Parent': '1.2 Módulos Hemodinámicos Avanzados'
        },

        # OBJETIVO 2: Validación Predictiva
        {
            'Task': 'OBJ2: Validación Predictiva',
            'Type': 'Objetivo',
            'Start': start_date + timedelta(weeks=12),
            'Duration': 32,  # 8 meses
            'Progress': 0,
            'Resource': 'Equipo Validación',
            'Priority': 'Alta',
            'Budget': 95000
        },
        {
            'Task': '2.1 Compilación Perfiles Referencia',
            'Type': 'Actividad',
            'Start': start_date + timedelta(weeks=12),
            'Duration': 12,
            'Progress': 0,
            'Resource': '2 Post-docs + Bibliotecario',
            'Priority': 'Alta',
            'Budget': 20000,
            'Parent': 'OBJ2: Validación Predictiva'
        },
        {
            'Task': '2.2 Validación Cruzada Histórica',
            'Type': 'Actividad',
            'Start': start_date + timedelta(weeks=24),
            'Duration': 16,
            'Progress': 0,
            'Resource': 'Estadístico + Especialista',
            'Priority': 'Alta',
            'Budget': 30000,
            'Parent': 'OBJ2: Validación Predictiva'
        },

        # OBJETIVO 3: Caracterización Pilotos
        {
            'Task': 'OBJ3: Caracterización Pilotos FAC',
            'Type': 'Objetivo',
            'Start': start_date + timedelta(weeks=40),
            'Duration': 24,  # 6 meses
            'Progress': 0,
            'Resource': 'Equipo Médico FAC',
            'Priority': 'Alta',
            'Budget': 100000
        },
        {
            'Task': '3.1 Reclutamiento Cohorte',
            'Type': 'Actividad',
            'Start': start_date + timedelta(weeks=40),
            'Duration': 8,
            'Progress': 0,
            'Resource': 'Coordinador + Admin FAC',
            'Priority': 'Alta',
            'Budget': 10000,
            'Parent': 'OBJ3: Caracterización Pilotos FAC'
        },
        {
            'Task': '3.2 Evaluación Fisiológica Basal',
            'Type': 'Actividad',
            'Start': start_date + timedelta(weeks=44),
            'Duration': 12,
            'Progress': 0,
            'Resource': '2 Médicos + 2 Técnicos',
            'Priority': 'Alta',
            'Budget': 40000,
            'Parent': 'OBJ3: Caracterización Pilotos FAC'
        },
        {
            'Task': '3.3 Simulaciones Individualizadas',
            'Type': 'Actividad',
            'Start': start_date + timedelta(weeks=48),
            'Duration': 16,
            'Progress': 0,
            'Resource': 'Ingeniero + Analista',
            'Priority': 'Alta',
            'Budget': 30000,
            'Parent': 'OBJ3: Caracterización Pilotos FAC'
        },

        # OBJETIVO 4: Protocolos Operacionales
        {
            'Task': 'OBJ4: Protocolos Operacionales',
            'Type': 'Objetivo',
            'Start': start_date + timedelta(weeks=60),
            'Duration': 12,  # 3 meses
            'Progress': 0,
            'Resource': 'Especialistas OTAN + FAC',
            'Priority': 'Alta',
            'Budget': 60000
        },

        # Hitos críticos
        {
            'Task': 'HITO: Modelo CGEM Validado',
            'Type': 'Hito',
            'Start': start_date + timedelta(weeks=36),
            'Duration': 0,
            'Progress': 0,
            'Resource': '-',
            'Priority': 'Crítica',
            'Budget': 0
        },
        {
            'Task': 'HITO: Pilotos Caracterizados',
            'Type': 'Hito',
            'Start': start_date + timedelta(weeks=62),
            'Duration': 0,
            'Progress': 0,
            'Resource': '-',
            'Priority': 'Crítica',
            'Budget': 0
        },
        {
            'Task': 'HITO: Proyecto Completado',
            'Type': 'Hito',
            'Start': start_date + timedelta(weeks=72),
            'Duration': 0,
            'Progress': 0,
            'Resource': '-',
            'Priority': 'Crítica',
            'Budget': 0
        }
    ]

    # Convertir a DataFrame
    df = pd.DataFrame(activities)

    # Calcular fechas finales
    df['End'] = df['Start'] + pd.to_timedelta(df['Duration'], unit='W')

    # Asignar colores por tipo
    color_map = {
        'Objetivo': '#1f77b4',      # Azul
        'Actividad': '#ff7f0e',     # Naranja
        'Tarea': '#2ca02c',         # Verde
        'Entregable': '#d62728',    # Rojo
        'Hito': '#9467bd'           # Púrpura
    }
    df['Color'] = df['Type'].map(color_map)

    return df


def create_modern_gantt():
    """Crear diagrama de Gantt moderno e interactivo"""

    # Obtener datos
    df = create_gantt_data()

    # Crear figura base
    fig = go.Figure()

    # Añadir barras para cada actividad
    for i, row in df.iterrows():
        # Determinar altura y posición Y según tipo
        if row['Type'] == 'Objetivo':
            height = 0.8
            y_pos = i
        elif row['Type'] == 'Actividad':
            height = 0.6
            y_pos = i
        elif row['Type'] == 'Tarea':
            height = 0.4
            y_pos = i
        elif row['Type'] == 'Entregable':
            height = 0.5
            y_pos = i
        else:  # Hito
            height = 0.3
            y_pos = i

        # Barra principal
        fig.add_trace(go.Scatter(
            x=[row['Start'], row['End'], row['End'],
               row['Start'], row['Start']],
            y=[y_pos - height/2, y_pos - height/2,
               y_pos + height/2, y_pos + height/2, y_pos - height/2],
            fill='toself',
            fillcolor=row['Color'],
            line=dict(color=row['Color'], width=1),
            hovertemplate=(
                f"<b>{row['Task']}</b><br>" +
                f"Tipo: {row['Type']}<br>" +
                f"Inicio: {row['Start'].strftime('%Y-%m-%d')}<br>" +
                f"Fin: {row['End'].strftime('%Y-%m-%d')}<br>" +
                f"Duración: {row['Duration']} semanas<br>" +
                f"Recurso: {row['Resource']}<br>" +
                f"Presupuesto: ${row['Budget']:,}<br>" +
                f"Prioridad: {row['Priority']}<br>" +
                "<extra></extra>"
            ),
            name=row['Task'],
            showlegend=False
        ))

        # Barra de progreso (si existe)
        if row['Progress'] > 0:
            progress_days = row['Duration'] * 7 * row['Progress'] / 100
            progress_end = row['Start'] + timedelta(days=progress_days)
            fig.add_trace(go.Scatter(
                x=[row['Start'], progress_end, progress_end,
                   row['Start'], row['Start']],
                y=[y_pos - height/2, y_pos - height/2,
                   y_pos + height/2, y_pos + height/2, y_pos - height/2],
                fill='toself',
                fillcolor='rgba(0,100,0,0.3)',
                line=dict(color='darkgreen', width=1),
                name=f"Progreso {row['Progress']}%",
                showlegend=False
            ))

    # Añadir líneas de dependencia (ejemplo)
    dependencies = [
        (0, 1), (1, 5), (5, 13), (13, 18)  # Algunas dependencias clave
    ]

    for start_idx, end_idx in dependencies:
        start_task = df.iloc[start_idx]
        end_task = df.iloc[end_idx]

        fig.add_trace(go.Scatter(
            x=[start_task['End'], end_task['Start']],
            y=[start_idx, end_idx],
            mode='lines',
            line=dict(color='gray', width=2, dash='dash'),
            showlegend=False,
            hoverinfo='skip'
        ))

    # Personalización del layout
    fig.update_layout(
        title={
            'text': ('Cronograma Proyecto CGEM Extendido - '
                     'Modelo Computacional Hemodinámico G-LOC'),
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial Black'}
        },
        xaxis=dict(
            title="Cronología del Proyecto",
            showgrid=True,
            gridcolor='lightgray',
            tickformat='%Y-%m-%d',
            dtick='M1',  # Cada mes
            title_font={'size': 14}
        ),
        yaxis=dict(
            title="Actividades y Tareas",
            tickmode='array',
            tickvals=list(range(len(df))),
            ticktext=[f"{task[:50]}..." if len(task) > 50 else task
                      for task in df['Task']],
            showgrid=True,
            gridcolor='lightgray',
            title_font={'size': 14}
        ),
        height=max(800, len(df) * 40),
        width=1400,
        font=dict(size=10),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='closest',
        margin=dict(l=300, r=50, t=100, b=100)
    )

    # Añadir línea de fecha actual
    current_date = datetime.now()
    if current_date >= df['Start'].min() and current_date <= df['End'].max():
        fig.add_vline(
            x=current_date,
            line_width=3,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Hoy: {current_date.strftime('%Y-%m-%d')}",
            annotation_position="top"
        )

    return fig


def create_resource_timeline():
    """Crear cronograma de recursos"""
    df = create_gantt_data()

    # Extraer recursos únicos
    resources = df['Resource'].unique()

    fig = go.Figure()

    resource_colors = px.colors.qualitative.Set3[:len(resources)]

    for i, resource in enumerate(resources):
        resource_tasks = df[df['Resource'] == resource]

        for _, task in resource_tasks.iterrows():
            fig.add_trace(go.Scatter(
                x=[task['Start'], task['End']],
                y=[i, i],
                mode='lines',
                line=dict(color=resource_colors[i], width=10),
                name=resource,
                hovertemplate=(
                    f"<b>{resource}</b><br>" +
                    f"Tarea: {task['Task']}<br>" +
                    f"Presupuesto: ${task['Budget']:,}<br>" +
                    "<extra></extra>"
                ),
                # Solo mostrar leyenda una vez por recurso
                showlegend=(task.name == resource_tasks.index[0])
            ))

    fig.update_layout(
        title="Cronograma de Recursos Humanos - Proyecto CGEM",
        xaxis_title="Cronología",
        yaxis=dict(
            title="Recursos",
            tickmode='array',
            tickvals=list(range(len(resources))),
            ticktext=[resource[:40] + "..." if len(resource) > 40
                      else resource for resource in resources]
        ),
        height=400,
        width=1200
    )

    return fig


def create_budget_timeline():
    """Crear cronograma de presupuesto acumulado"""
    df = create_gantt_data()

    # Crear series temporal de gastos
    date_range = pd.date_range(start=df['Start'].min(),
                               end=df['End'].max(), freq='W')
    cumulative_budget = []

    for date in date_range:
        spent_to_date = 0
        for _, task in df.iterrows():
            if task['Start'] <= date <= task['End']:
                # Distribuir presupuesto proporcionalmente durante la duración
                weeks_elapsed = max(1, (date - task['Start']).days / 7)
                weeks_total = max(1, task['Duration'])
                proportion = min(1.0, weeks_elapsed / weeks_total)
                spent_to_date += task['Budget'] * proportion

        cumulative_budget.append(spent_to_date)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=date_range,
        y=cumulative_budget,
        mode='lines',
        fill='tonexty',
        line=dict(color='green', width=3),
        name='Presupuesto Acumulado',
        hovertemplate="Fecha: %{x}<br>Presupuesto: $%{y:,.0f}<extra></extra>"
    ))

    # Añadir presupuesto total como línea horizontal
    total_budget = df['Budget'].sum()
    fig.add_hline(
        y=total_budget,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Presupuesto Total: ${total_budget:,}"
    )

    fig.update_layout(
        title="Ejecución Presupuestaria del Proyecto",
        xaxis_title="Fecha",
        yaxis_title="Presupuesto Acumulado (USD)",
        height=400,
        width=1200,
        yaxis_tickformat="$,.0f"
    )

    return fig


# Ejecutar y mostrar los gráficos
if __name__ == "__main__":
    # Crear los gráficos
    gantt_fig = create_modern_gantt()
    resource_fig = create_resource_timeline()
    budget_fig = create_budget_timeline()

    # Mostrar (en Streamlit sería st.plotly_chart())
    gantt_fig.show()
    resource_fig.show()
    budget_fig.show()

    # Opcional: Guardar como HTML
    gantt_fig.write_html("cronograma_cgem_gantt.html")
    resource_fig.write_html("cronograma_cgem_recursos.html")
    budget_fig.write_html("cronograma_cgem_presupuesto.html")

    print("Diagramas de Gantt creados exitosamente!")
    print("\nResumen del Proyecto:")
    print("=" * 50)

    df = create_gantt_data()

    print(f"Total de actividades: {len(df)}")
    print(f"Duración total: {(df['End'].max() - df['Start'].min()).days} días")
    print(f"Presupuesto total: ${df['Budget'].sum():,} USD")
    print(f"Fecha inicio: {df['Start'].min().strftime('%Y-%m-%d')}")
    print(f"Fecha fin: {df['End'].max().strftime('%Y-%m-%d')}")

    # Mostrar recursos únicos
    print(f"\nRecursos involucrados: {len(df['Resource'].unique())}")
    for resource in df['Resource'].unique():
        resource_budget = df[df['Resource'] == resource]['Budget'].sum()
        print(f"  - {resource}: ${resource_budget:,}")
