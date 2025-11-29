import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuración de la Aplicación ---
# Título principal del cuadro de mandos
st.header('Análisis de Vehículos Usados: Distribuciones')

# Mensaje introductorio
st.write("""
¡Bienvenido a tu aplicación de visualización de datos!
Utiliza las casillas de verificación y las opciones desplegables para generar los diferentes gráficos interactivos.
""")

# Carga de datos
# Streamlit usa caché para no recargar los datos cada vez que la app se actualiza


@st.cache_data
def load_data():
    # Asegúrate de que el nombre del archivo coincida con el subido
    df = pd.read_csv('vehicles_us.csv')
    return df


# Cargar el DataFrame
car_data = load_data()

# --- Definición de límites para Preprocesamiento (Filtrado de Outliers) ---
# Para evitar un histograma y diagrama de dispersión muy sesgados por outliers extremos,
# filtramos los datos, manteniendo solo los precios y kilometraje entre el percentil 1 y 99.
price_low = car_data['price'].quantile(0.01)
price_high = car_data['price'].quantile(0.99)
odometer_low = car_data['odometer'].quantile(0.01)
odometer_high = car_data['odometer'].quantile(0.99)

# --- Ingeniería de Características y Filtrado de datos (se usa para todos los gráficos) ---

# 1. Extraer el fabricante (manufacturer) de la columna model
car_data['manufacturer'] = car_data['model'].apply(
    lambda x: x.split(' ')[0].lower())

# 2. Filtrado general
# También filtramos los fabricantes con muy pocos anuncios para asegurar una buena visualización
manufacturer_counts_full = car_data['manufacturer'].value_counts()
# Filtrar fabricantes con al menos 50 anuncios
valid_manufacturers = manufacturer_counts_full[manufacturer_counts_full >= 50].index

df_filtered_general = car_data[
    (car_data['price'] >= price_low) & (car_data['price'] <= price_high) &
    (car_data['odometer'].notna()) &
    (car_data['odometer'] >= odometer_low) & (car_data['odometer'] <= odometer_high) &
    # Usar solo fabricantes con suficientes datos
    (car_data['manufacturer'].isin(valid_manufacturers))
].copy()

# Lista de fabricantes disponibles para los selectboxes
manufacturer_list = sorted(
    df_filtered_general['manufacturer'].unique().tolist())


# --- Opción 1: Histograma de Precios ---
st.subheader('1. Distribución de Precios')
# Crear un checkbox (casilla de verificación) que activa la visualización
build_histogram = st.checkbox(
    'Construir un histograma de la distribución de precios',
    key='hist_checkbox'
)

if build_histogram:
    # Mostrar un mensaje mientras se genera el gráfico
    st.write('Construyendo histograma de precios...')

    # --- Creación del Histograma con Plotly Express ---
    fig = px.histogram(
        df_filtered_general,
        x="price",
        nbins=50,  # Número de bins para mayor detalle
        title='Distribución de Precios de Vehículos (Outliers Filtrados)',
        labels={'price': 'Precio (USD)', 'count': 'Frecuencia'},
        color_discrete_sequence=['#4CAF50']  # Color verde amigable
    )

    # Añadir un layout más limpio y etiquetas
    fig.update_layout(
        xaxis_title='Precio (USD)',
        yaxis_title='Número de Anuncios',
        bargap=0.05,  # Espacio entre las barras
        template='plotly_white'
    )

    # Mostrar el gráfico en la aplicación web
    st.plotly_chart(fig, use_container_width=True)

    st.write('El histograma muestra que la mayoría de los precios se agrupan en el rango bajo, lo que es típico en el mercado de vehículos usados.')

# --- Separador ---
st.write('---')

# --- Opción 2: Diagrama de Dispersión (Scatter Plot) ---
st.subheader('2. Correlación: Precio vs. Kilometraje')

# Crear un segundo checkbox para un diagrama de dispersión
build_scatterplot = st.checkbox(
    'Construir un diagrama de dispersión: Precio vs. Kilometraje',
    key='scatter_checkbox'
)

if build_scatterplot:
    st.write('Construyendo diagrama de dispersión...')

    # Diagrama de dispersión: Precio vs. Odométro, coloreado por Condición
    fig_scatter = px.scatter(
        df_filtered_general,  # Usamos el DataFrame ya filtrado
        x="odometer",
        y="price",
        color="condition",  # Colorear por condición
        title='Precio vs. Kilometraje por Condición',
        labels={'odometer': 'Kilometraje (Millas)', 'price': 'Precio (USD)'},
        opacity=0.6,
        hover_data=['model', 'model_year']
    )

    # Mostrar el gráfico en la aplicación web
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.write('El diagrama de dispersión confirma la tendencia: a mayor kilometraje, menor precio. Además, la Condición del vehículo es un factor clave.')

# --- Separador ---
st.write('---')

# --- Opción 3: Tipos de Vehículos por Fabricante ---
st.subheader('3. Distribución de Tipos de Vehículo por Fabricante')

# Crear el checkbox para el nuevo histograma
build_manufacturer_type_histogram = st.checkbox(
    'Construir histograma de Tipos de Vehículo por Fabricante',
    key='manufacturer_type_hist_checkbox'
)

if build_manufacturer_type_histogram:
    st.write('Construyendo histograma de tipos de vehículo por fabricante...')

    # Contar la cantidad de anuncios por fabricante
    manufacturer_counts = df_filtered_general['manufacturer'].value_counts()

    # Limitar a los 10 principales fabricantes para una mejor visualización
    top_manufacturers = manufacturer_counts.head(10).index
    df_top_manufacturers = df_filtered_general[
        df_filtered_general['manufacturer'].isin(top_manufacturers)
    ]

    # Histograma apilado: Eje X = Tipo, Color = Fabricante
    fig_manufacturer = px.histogram(
        df_top_manufacturers,
        x="type",
        color="manufacturer",  # Usar el fabricante como color para apilar
        title='Tipos de Vehículos por Fabricante (Top 10 Fabricantes)',
        labels={'type': 'Tipo de Vehículo',
                'count': 'Número de Anuncios', 'manufacturer': 'Fabricante'},
        template='plotly_white',
        category_orders={"manufacturer": top_manufacturers.tolist()},
        height=500
    )

    fig_manufacturer.update_layout(
        xaxis_title='Tipo de Vehículo',
        yaxis_title='Frecuencia',
        barmode='stack',
    )

    # Mostrar el gráfico
    st.plotly_chart(fig_manufacturer, use_container_width=True)

    st.write('Este gráfico muestra la distribución de tipos de vehículos anunciados para los 10 principales fabricantes, ayudando a identificar las especialidades de cada marca.')

# --- Separador ---
st.write('---')

# --- Opción 4: Comparación de Distribución de Precios entre Fabricantes (NUEVO) ---
st.subheader('4. Comparación de Distribución de Precios por Fabricante')

st.write('Selecciona dos fabricantes para comparar la distribución de precios:')

# Dividir el espacio en dos columnas para las listas desplegables
col1, col2 = st.columns(2)

with col1:
    manufacturer_1 = st.selectbox(
        'Selecciona el primer fabricante:',
        manufacturer_list,
        index=manufacturer_list.index(
            'ford') if 'ford' in manufacturer_list else 0,
        key='manufacturer_1_select'
    )

with col2:
    manufacturer_2 = st.selectbox(
        'Selecciona el segundo fabricante:',
        manufacturer_list,
        index=manufacturer_list.index(
            'chevrolet') if 'chevrolet' in manufacturer_list else 1,
        key='manufacturer_2_select'
    )

# Solo mostrar el gráfico si los dos fabricantes son diferentes
if manufacturer_1 and manufacturer_2 and manufacturer_1 != manufacturer_2:
    # 1. Filtrar los datos solo para los dos fabricantes seleccionados
    df_compare = df_filtered_general[
        df_filtered_general['manufacturer'].isin(
            [manufacturer_1, manufacturer_2])
    ]

    # 2. Crear el Box Plot (Diagrama de Caja) para la comparación de precios
    fig_compare = px.violin(
        df_compare,
        x="manufacturer",
        y="price",
        color="manufacturer",
        box=True,  # Mostrar también el diagrama de caja dentro del violín
        title=f'Comparación de Distribución de Precios (Diagrama de Violín): {manufacturer_1.upper()} vs {manufacturer_2.upper()}',
        labels={'manufacturer': 'Fabricante', 'price': 'Precio (USD)'},
        template='plotly_white',
        height=500
    )

    # Mostrar la línea de la media para mayor claridad
    fig_compare.update_traces(meanline_visible=True)

    # 3. Mostrar el gráfico
    st.plotly_chart(fig_compare, use_container_width=True)

    st.write(
        f'El **Diagrama de Violín** muestra la densidad de la distribución de precios. La parte más ancha '
        f'indica dónde se concentran la mayoría de los precios, y la línea central es el Diagrama de Caja, '
        f'mostrando la mediana (línea central) y cuartiles. Esto permite una mejor comprensión de cómo se '
        f'distribuyen los precios para {manufacturer_1.upper()} y {manufacturer_2.upper()}.'
    )
elif manufacturer_1 == manufacturer_2:
    st.warning(
        "Por favor, selecciona dos fabricantes diferentes para la comparación.")
