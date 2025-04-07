import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Hipoteca",
    page_icon="🏠",
    layout="wide"
)

# Título y descripción
st.title("Calculadora de Hipoteca")
st.markdown("""
Esta aplicación te permite calcular las cuotas mensuales de una hipoteca y analizar cómo 
diferentes factores afectan al coste total del préstamo. Ajusta los parámetros en la 
barra lateral para ver el impacto en tiempo real.
""")

# Barra lateral con los parámetros de entrada
st.sidebar.header("Parámetros de la Hipoteca")

# Parámetros de entrada
precio_inmueble = st.sidebar.slider(
    "Precio del inmueble (€)", 
    min_value=50000, 
    max_value=1000000, 
    value=200000, 
    step=10000
)

porcentaje_entrada = st.sidebar.slider(
    "Entrada (% del precio)", 
    min_value=0, 
    max_value=50, 
    value=20, 
    step=5
)

entrada = precio_inmueble * (porcentaje_entrada / 100)
importe_hipoteca = precio_inmueble - entrada

plazo_anios = st.sidebar.slider(
    "Plazo (años)", 
    min_value=5, 
    max_value=40, 
    value=25, 
    step=1
)

tasa_interes = st.sidebar.slider(
    "Tasa de interés anual (%)", 
    min_value=1.0, 
    max_value=10.0, 
    value=3.0, 
    step=0.1
)

st.sidebar.markdown("---")

# Gastos adicionales
mostrar_gastos = st.sidebar.checkbox("Mostrar gastos adicionales", value=True)

if mostrar_gastos:
    st.sidebar.subheader("Gastos adicionales")
    
    comision_apertura_porcentaje = st.sidebar.slider(
        "Comisión de apertura (%)",
        min_value=0.0,
        max_value=3.0,
        value=1.0,
        step=0.1
    )
    
    gastos_notaria = st.sidebar.slider(
        "Gastos de notaría (€)",
        min_value=0,
        max_value=3000,
        value=1000,
        step=100
    )
    
    gastos_registro = st.sidebar.slider(
        "Gastos de registro (€)",
        min_value=0,
        max_value=1500,
        value=500,
        step=50
    )
    
    gastos_tasacion = st.sidebar.slider(
        "Gastos de tasación (€)",
        min_value=0,
        max_value=1000,
        value=300,
        step=50
    )
    
    impuesto_actos_juridicos_porcentaje = st.sidebar.slider(
        "Impuesto Actos Jurídicos Documentados (%)",
        min_value=0.0,
        max_value=2.5,
        value=1.5,
        step=0.1
    )
    
    # Cálculo de los gastos adicionales
    comision_apertura = importe_hipoteca * (comision_apertura_porcentaje / 100)
    impuesto_actos_juridicos = importe_hipoteca * (impuesto_actos_juridicos_porcentaje / 100)
    
    total_gastos = comision_apertura + gastos_notaria + gastos_registro + gastos_tasacion + impuesto_actos_juridicos
else:
    total_gastos = 0

# Función para calcular la cuota mensual
def calcular_cuota_mensual(importe, tasa, plazo_meses):
    tasa_mensual = tasa / 100 / 12
    return importe * (tasa_mensual * (1 + tasa_mensual) ** plazo_meses) / ((1 + tasa_mensual) ** plazo_meses - 1)

# Función para generar tabla de amortización
def generar_tabla_amortizacion(importe, tasa, plazo_meses):
    tasa_mensual = tasa / 100 / 12
    cuota_mensual = calcular_cuota_mensual(importe, tasa, plazo_meses)
    
    saldo_restante = importe
    amortizacion_acumulada = 0
    intereses_acumulados = 0
    
    tabla = []
    
    for mes in range(1, plazo_meses + 1):
        interes_mensual = saldo_restante * tasa_mensual
        amortizacion = cuota_mensual - interes_mensual
        
        intereses_acumulados += interes_mensual
        amortizacion_acumulada += amortizacion
        saldo_restante -= amortizacion
        
        # Solo guardamos algunos meses para no sobrecargar la memoria
        if mes <= 12 or mes % 12 == 0 or mes == plazo_meses:
            tabla.append({
                'Mes': mes,
                'Cuota Mensual': cuota_mensual,
                'Pago Intereses': interes_mensual,
                'Amortización': amortizacion,
                'Saldo Restante': max(0, saldo_restante),
                'Intereses Acumulados': intereses_acumulados,
                'Capital Amortizado': amortizacion_acumulada
            })
    
    return pd.DataFrame(tabla)

# Cálculos principales
plazo_meses = plazo_anios * 12
cuota_mensual = calcular_cuota_mensual(importe_hipoteca, tasa_interes, plazo_meses)
coste_total = cuota_mensual * plazo_meses
total_intereses = coste_total - importe_hipoteca

# Tabla de amortización
tabla_amortizacion = generar_tabla_amortizacion(importe_hipoteca, tasa_interes, plazo_meses)

# Dashboard principal
col1, col2 = st.columns(2)

with col1:
    st.subheader("Resumen de la Hipoteca")
    
    # Diseño de tarjetas para los datos principales
    st.markdown("""
    <style>
    .metric-card {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: #f0f2f6;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1E88E5;
    }
    .metric-label {
        font-size: 14px;
        color: #424242;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Información del préstamo
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{importe_hipoteca:,.2f} €</div>
        <div class="metric-label">Importe de la hipoteca</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{cuota_mensual:,.2f} €</div>
        <div class="metric-label">Cuota mensual</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{coste_total:,.2f} €</div>
        <div class="metric-label">Coste total (capital + intereses)</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{total_intereses:,.2f} €</div>
        <div class="metric-label">Total intereses pagados</div>
    </div>
    """, unsafe_allow_html=True)
    
    if mostrar_gastos:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_gastos:,.2f} €</div>
            <div class="metric-label">Total gastos iniciales</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{entrada + total_gastos:,.2f} €</div>
            <div class="metric-label">Desembolso inicial (entrada + gastos)</div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.subheader("Distribución del Pago")
    
    # Gráfico de distribución del pago total
    fig, ax = plt.subplots(figsize=(10, 6))
    etiquetas = ['Capital', 'Intereses']
    valores = [importe_hipoteca, total_intereses]
    colores = ['#1E88E5', '#FFC107']
    
    # Añadir porcentajes
    def autopct_format(values):
        def my_format(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return '{:.1f}%\n({:,.0f} €)'.format(pct, val)
        return my_format
    
    ax.pie(valores, labels=etiquetas, colors=colores, autopct=autopct_format(valores),
           startangle=90, shadow=False, explode=(0, 0.1))
    ax.axis('equal')
    st.pyplot(fig)
    
    # Añadir información sobre el ratio préstamo/valor
    ltv = (importe_hipoteca / precio_inmueble) * 100
    st.markdown(f"**Ratio préstamo/valor (LTV):** {ltv:.1f}%")
    
    # Indicador de esfuerzo financiero
    st.subheader("Indicador de Esfuerzo Financiero")
    ingresos_mensuales = st.slider(
        "Ingresos mensuales netos (€)",
        min_value=1000,
        max_value=10000,
        value=2500,
        step=100
    )
    
    esfuerzo = (cuota_mensual / ingresos_mensuales) * 100
    
    # Determinar el color basado en el nivel de esfuerzo
    if esfuerzo <= 30:
        color_esfuerzo = "green"
        mensaje_esfuerzo = "Nivel de esfuerzo adecuado (por debajo del 30% recomendado)"
    elif esfuerzo <= 40:
        color_esfuerzo = "orange"
        mensaje_esfuerzo = "Nivel de esfuerzo elevado (entre 30-40%)"
    else:
        color_esfuerzo = "red"
        mensaje_esfuerzo = "Nivel de esfuerzo excesivo (por encima del 40%)"
    
    st.markdown(f"""
    <div style="background-color: {color_esfuerzo}25; padding: 15px; border-radius: 10px; margin-top: 10px;">
        <h3 style="color: {color_esfuerzo}; margin: 0;">Esfuerzo financiero: {esfuerzo:.1f}%</h3>
        <p>{mensaje_esfuerzo}</p>
    </div>
    """, unsafe_allow_html=True)

# Visualización de la evolución del préstamo
st.subheader("Evolución del Préstamo")

# Pestañas para diferentes visualizaciones
tab1, tab2, tab3 = st.tabs(["Tabla de Amortización", "Gráfico de Evolución", "Comparativa de Plazos"])

with tab1:
    # Formatear las columnas monetarias
    formato = {col: '{:,.2f} €' for col in tabla_amortizacion.columns if col != 'Mes'}
    
    # Mostrar la tabla con formato
    st.dataframe(tabla_amortizacion.style.format(formato))

with tab2:
    # Gráfico de evolución del préstamo
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(tabla_amortizacion['Mes'], tabla_amortizacion['Intereses Acumulados'], 
            label='Intereses Pagados', color='#FFC107', linewidth=3)
    ax.plot(tabla_amortizacion['Mes'], tabla_amortizacion['Capital Amortizado'], 
            label='Capital Amortizado', color='#1E88E5', linewidth=3)
    ax.plot(tabla_amortizacion['Mes'], tabla_amortizacion['Saldo Restante'], 
            label='Saldo Pendiente', color='#F44336', linewidth=3, linestyle='--')
    
    ax.set_xlabel('Meses')
    ax.set_ylabel('Euros (€)')
    ax.set_title('Evolución del Préstamo a lo Largo del Tiempo')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    st.pyplot(fig)

    # Explicación del gráfico
    st.markdown("""
    **¿Qué muestra este gráfico?**
    - **Intereses Pagados (amarillo)**: Muestra cómo se acumulan los intereses pagados a lo largo del tiempo.
    - **Capital Amortizado (azul)**: Muestra cómo se va amortizando el capital del préstamo.
    - **Saldo Pendiente (rojo)**: Muestra la evolución del saldo pendiente del préstamo.
    
    *Observa cómo al principio del préstamo se pagan más intereses y se amortiza menos capital, mientras que al final ocurre lo contrario.*
    """)

with tab3:
    st.subheader("¿Cómo afecta el plazo a tu hipoteca?")
    
    # Crear datos para diferentes plazos
    plazos_comparativa = [10, 15, 20, 25, 30, 35, 40]
    cuotas = []
    total_pagado = []
    total_intereses_lista = []
    
    for p in plazos_comparativa:
        meses = p * 12
        c = calcular_cuota_mensual(importe_hipoteca, tasa_interes, meses)
        t_pagado = c * meses
        t_intereses = t_pagado - importe_hipoteca
        
        cuotas.append(c)
        total_pagado.append(t_pagado)
        total_intereses_lista.append(t_intereses)
    
    # Crear DataFrame para la comparativa
    comparativa_df = pd.DataFrame({
        'Plazo (años)': plazos_comparativa,
        'Cuota Mensual': cuotas,
        'Total Pagado': total_pagado,
        'Total Intereses': total_intereses_lista
    })
    
    # Gráficos de comparativa
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de cuotas mensuales
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(comparativa_df['Plazo (años)'].astype(str), comparativa_df['Cuota Mensual'], color='#1E88E5')
        
        # Resaltar el plazo seleccionado
        idx_seleccionado = plazos_comparativa.index(plazo_anios) if plazo_anios in plazos_comparativa else -1
        if idx_seleccionado >= 0:
            ax.bar(str(plazos_comparativa[idx_seleccionado]), comparativa_df['Cuota Mensual'][idx_seleccionado], color='#4CAF50')
        
        ax.set_xlabel('Plazo (años)')
        ax.set_ylabel('Cuota Mensual (€)')
        ax.set_title('Cuota Mensual según Plazo')
        
        # Añadir etiquetas de valor
        for i, v in enumerate(comparativa_df['Cuota Mensual']):
            ax.text(i, v + 20, f'{v:,.2f} €', ha='center', fontsize=9)
        
        st.pyplot(fig)
    
    with col2:
        # Gráfico de intereses totales
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(comparativa_df['Plazo (años)'].astype(str), comparativa_df['Total Intereses'], color='#FFC107')
        
        # Resaltar el plazo seleccionado
        if idx_seleccionado >= 0:
            ax.bar(str(plazos_comparativa[idx_seleccionado]), comparativa_df['Total Intereses'][idx_seleccionado], color='#F44336')
        
        ax.set_xlabel('Plazo (años)')
        ax.set_ylabel('Total Intereses (€)')
        ax.set_title('Total de Intereses según Plazo')
        
        # Añadir etiquetas de valor
        for i, v in enumerate(comparativa_df['Total Intereses']):
            ax.text(i, v + 1000, f'{v:,.0f} €', ha='center', fontsize=9)
        
        st.pyplot(fig)
    
    # Tabla comparativa
    st.markdown("### Tabla comparativa por plazos")
    
    # Formatear las columnas monetarias
    formato_comparativa = {
        'Cuota Mensual': '{:,.2f} €',
        'Total Pagado': '{:,.2f} €',
        'Total Intereses': '{:,.2f} €'
    }
    
    # Mostrar la tabla con formato
    st.dataframe(comparativa_df.style.format(formato_comparativa))
    
    # Análisis de la comparativa
    st.markdown("""
    **Observaciones importantes:**
    - A mayor plazo, **menor cuota mensual** pero **mayor coste total** del préstamo.
    - A menor plazo, **mayor cuota mensual** pero **menor coste total** del préstamo.
    - Los intereses pueden llegar a duplicar el coste en los plazos más largos.
    
    *Encontrar el equilibrio entre una cuota mensual asumible y un coste total razonable es la clave para una buena decisión hipotecaria.*
    """)

# Sección educativa
with st.expander("Conceptos Clave para Entender tu Hipoteca"):
    st.markdown("""
    ### Conceptos Básicos
    
    - **Capital**: La cantidad de dinero que se solicita prestada.
    - **Plazo**: El tiempo durante el cual se devolverá el préstamo.
    - **Tasa de interés**: El precio que se paga por el dinero prestado, expresado como porcentaje anual.
    - **Cuota**: La cantidad que se paga periódicamente (normalmente mensual) para devolver el préstamo.
    
    ### Indicadores Importantes
    
    - **TAE (Tasa Anual Equivalente)**: Incluye el interés nominal y los gastos asociados al préstamo.
    - **LTV (Loan-to-Value)**: Relación entre el importe del préstamo y el valor del inmueble.
    - **Esfuerzo financiero**: Porcentaje de los ingresos destinados a pagar la hipoteca (recomendable no superar el 30-35%).
    
    ### Tipos de Hipotecas
    
    - **Fija**: La tasa de interés permanece constante durante toda la vida del préstamo.
    - **Variable**: La tasa de interés se actualiza periódicamente según un índice de referencia (generalmente Euribor).
    - **Mixta**: Combina un período inicial a tipo fijo seguido de un período a tipo variable.
    
    ### Consejos para Negociar una Hipoteca
    
    1. **Comparar ofertas** de diferentes entidades financieras.
    2. **Negociar las comisiones** (apertura, amortización anticipada, etc.).
    3. **Evaluar productos vinculados** (seguros, nóminas, tarjetas) y su coste real.
    4. **Considerar la posibilidad de amortización anticipada** sin penalizaciones.
    5. **Analizar el momento económico** (tendencias de tipos de interés, situación del mercado).
    """)

# Información sobre el uso de la aplicación
with st.expander("¿Cómo usar esta calculadora?"):
    st.markdown("""
    ### Instrucciones de Uso
    
    1. **Ajusta los parámetros** en la barra lateral:
       - Precio del inmueble
       - Porcentaje de entrada
       - Plazo del préstamo
       - Tasa de interés
       - Gastos adicionales (opcional)
       
    2. **Explora los resultados** en el panel principal:
       - Resumen de la hipoteca (cuota mensual, coste total, etc.)
       - Distribución del pago (capital vs. intereses)
       - Indicador de esfuerzo financiero
       
    3. **Analiza la evolución** del préstamo:
       - Tabla de amortización
       - Gráfico de evolución
       - Comparativa por plazos
       
    4. **Aprende conceptos clave** en la sección educativa.
    
    ### Actividades Didácticas
    
    1. **Análisis de escenarios**: Prueba diferentes combinaciones de parámetros y analiza su impacto.
    2. **Caso práctico**: Plantea un caso real y busca la mejor solución.
    3. **Debate**: Discute las ventajas e inconvenientes de diferentes estrategias (plazo corto vs. largo, tipo fijo vs. variable).
    """)

# Pie de página
st.markdown("---")
st.markdown("### Calculadora de Hipoteca | Herramienta Educativa")
st.caption("Nota: Esta herramienta tiene fines educativos. Las cifras son aproximadas y pueden variar según las condiciones específicas de cada entidad financiera.")
