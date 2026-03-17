import streamlit as st
import pandas as pd
from extraccion import procesar_pdf_bytes, generar_excel_bytes, COLUMNAS

# ── Configuración de página ──────────────────────────────────────────
st.set_page_config(
    page_title="Extractor",
    page_icon="",
    layout="wide",
)

# ── Subida de archivos ──────────────────────────────────────────────
archivos = st.file_uploader(
    "Arrastra o selecciona archivos PDF",
    type=["pdf"],
    accept_multiple_files=True,
)

# ── Procesamiento ────────────────────────────────────────────────────
if archivos:
    todas_las_filas = []
    errores = []

    with st.spinner("Procesando PDFs..."):
        barra = st.progress(0, text="Iniciando procesamiento...")

        for idx, archivo in enumerate(archivos):
            barra.progress(
                (idx) / len(archivos),
                text=f"Procesando: {archivo.name} ({idx + 1}/{len(archivos)})"
            )
            try:
                filas = procesar_pdf_bytes(archivo.read(), archivo.name)
                todas_las_filas.extend(filas)
            except Exception as e:
                errores.append((archivo.name, str(e)))

        barra.progress(1.0, text="Procesamiento completado")

    # ── Errores ──────────────────────────────────────────────────────
    if errores:
        for nombre, error in errores:
            st.error(f"Error procesando **{nombre}**: {error}")

    # ── Resultados ───────────────────────────────────────────────────
    if todas_las_filas:
        df = pd.DataFrame(todas_las_filas, columns=COLUMNAS)

        # Métricas
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="number">{len(todas_las_filas)}</div>
                <div class="label">Participantes encontrados</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="number">{len(archivos)}</div>
                <div class="label">PDFs procesados</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            provincias_unicas = df["Provincia/Localidad de origen"].replace("", pd.NA).dropna().nunique()
            st.markdown(f"""
            <div class="metric-card">
                <div class="number">{provincias_unicas}</div>
                <div class="label">Provincias únicas</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")

        # Tabla de datos
        st.subheader("📋 Resultados")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=min(400, 40 + len(df) * 35),
        )

        # Botón de descarga
        st.markdown("")
        excel_bytes = generar_excel_bytes(todas_las_filas)
        st.download_button(
            label="📥 Descargar Excel",
            data=excel_bytes,
            file_name="participantes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    elif not errores:
        st.warning("⚠️ No se encontraron participantes en los PDFs proporcionados.")

else:
    # Estado vacío
    st.markdown("")
    # st.info("👆 Sube uno o varios archivos PDF para comenzar el análisis.")