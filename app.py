import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuración de la Aplicación ---
# Título principal del cuadro de mandos
st.header('Análisis de Vehículos Usados: Distribuciones')

# Mensaje introductorio
st.write("""
¡Bienvenido a tu aplicación de visualización de datos!
Utiliza las casillas de verificación para generar los diferentes gráficos interactivos.
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

# --- Filtrado de datos (se usa para ambos gráficos) ---
df_filtered_general = car_data[
    (car_data['price'] >= price_low) & (car_data['price'] <= price_high) &
    (car_data['odometer'] >= odometer_low) & (
        car_data['odometer'] <= odometer_high)
].copy()


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

# Crear un segundo checkbox para un diagrama de dispersión (este es el "otro botón" que solicitaste)
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
