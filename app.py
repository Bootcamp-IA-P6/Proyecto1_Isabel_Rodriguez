import streamlit as st
import time 

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---

def init_session_state():
    """Inicializa las variables de estado si aún no existen."""
    if 'active' not in st.session_state:
        st.session_state.active = False
        st.session_state.state = 'stopped' # 'stopped', 'moving', o 'finished'
        st.session_state.stopped_time = 0.0
        st.session_state.moving_time = 0.0
        st.session_state.start_time = 0.0 # Marca de tiempo del último cambio de estado
        st.session_state.MIN_FARE = 5.00 
        
        # Variable para almacenar la tarifa final después de que el viaje concluye
        st.session_state.last_calculated_fare = 0.0 

# --- 2. FUNCIÓN DE CÁLCULO DE TARIFA (Lógica de main.py) ---

def calculate_fare(seconds_stopped, seconds_moving):
    """
    Calcula la tarifa total, aplicando la tarifa mínima (Issue #18).
    """
    # Tarifas base: 0.02 €/s detenido, 0.05 €/s movimiento
    fare = seconds_stopped * 0.02 + seconds_moving * 0.05
    
    # Lógica de la Tarifa Mínima Fija
    if fare < st.session_state.MIN_FARE:
        return st.session_state.MIN_FARE
    else:
        return fare

# --- 3. FUNCIONES DE LÓGICA DE TIEMPO Y ESTADO ---

def update_current_time_for_display():
    """Calcula el tiempo transcurrido en el estado actual para la visualización en vivo."""
    
    # Si el viaje no está activo o es el inicio, devolvemos los contadores base.
    if not st.session_state.active or st.session_state.start_time == 0.0:
        return st.session_state.stopped_time, st.session_state.moving_time
    
    # Si está activo, calculamos la duración en vivo
    duration_live = time.time() - st.session_state.start_time
    
    # Clonamos y sumamos la duración al contador temporal
    temp_stopped = st.session_state.stopped_time
    temp_moving = st.session_state.moving_time

    if st.session_state.state == 'stopped':
        temp_stopped += duration_live
    elif st.session_state.state == 'moving':
        temp_moving += duration_live
    
    return temp_stopped, temp_moving

# Función de Callback para Iniciar
def start_trip():
    if not st.session_state.active:
        st.session_state.active = True
        st.session_state.stopped_time = 0.0
        st.session_state.moving_time = 0.0
        st.session_state.state = 'stopped'
        st.session_state.start_time = time.time()

# Función de Callback para Mover o Detener
def update_time_and_state(new_state):
    if st.session_state.active:
        # 1. Calcular y ACUMULAR el tiempo transcurrido del estado ANTERIOR
        duration = time.time() - st.session_state.start_time
        
        if st.session_state.state == 'stopped':
            st.session_state.stopped_time += duration
        elif st.session_state.state == 'moving':
            st.session_state.moving_time += duration
            
        # 2. Cambiar al NUEVO estado y resetear el cronómetro
        st.session_state.state = new_state
        st.session_state.start_time = time.time()

# Función de Callback para Finalizar
def finish_trip():
    if st.session_state.active:
        # 1. Acumular el tiempo del último tramo (CRÍTICO)
        duration = time.time() - st.session_state.start_time
        
        if st.session_state.state == 'stopped':
            st.session_state.stopped_time += duration
        else:
            st.session_state.moving_time += duration
        
        # 2. Calcular la tarifa final
        final_fare = calculate_fare(st.session_state.stopped_time, st.session_state.moving_time)
        
        # 3. Mostrar resumen
        st.success(f"VIAJE FINALIZADO. Tarifa a pagar: €{final_fare:.2f}")

        # 4. Guardar la tarifa final y resetear variables de sesión
        st.session_state.last_calculated_fare = final_fare # Guardamos el resultado final
        st.session_state.active = False
        st.session_state.stopped_time = 0.0
        st.session_state.moving_time = 0.0
        st.session_state.start_time = 0.0
        st.session_state.state = 'finished' 
    else:
        st.warning("No hay viaje activo para finalizar.")


# --- 4. FUNCIÓN PRINCIPAL DE STREAMLIT (LAYOUT) ---

def taximeter_app():
    """Función principal que define el layout de la aplicación Streamlit."""
    
    st.title("🚕 Taxímetro Digital F5")
    init_session_state()

    # Calcular tiempos y tarifa para mostrar en la interfaz (en vivo o final)
    current_stopped_time, current_moving_time = update_current_time_for_display()
    
    # Determinar qué tarifa mostrar (la tarifa final si el viaje terminó, o el cálculo en vivo)
    if st.session_state.state == 'finished':
        current_fare = st.session_state.last_calculated_fare
    else:
        current_fare = calculate_fare(current_stopped_time, current_moving_time)
    
    # 2. Métricas (Visualización)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="TARIFA ACUMULADA", value=f"€{current_fare:.2f}")
    with col2:
        st.metric(
            label="ESTADO ACTUAL", 
            value=st.session_state.state.upper(),
            delta="VIAJE ACTIVO" if st.session_state.active else "INACTIVO"
        )
        
    # 3. Controles (Botones)
    st.subheader("Controles del Taxímetro")
    
    st.button("🔴 Iniciar Viaje", on_click=start_trip, disabled=st.session_state.active)
    
    col3, col4 = st.columns(2)
    with col3:
        st.button(
            "▶️ Moverse (Move)", 
            on_click=update_time_and_state, 
            args=['moving'], 
            disabled=(not st.session_state.active or st.session_state.state == 'moving')
        )
    with col4:
        st.button(
            "⏸ Detenerse (Stop)", 
            on_click=update_time_and_state, 
            args=['stopped'], 
            disabled=(not st.session_state.active or st.session_state.state == 'stopped')
        )

    st.button("✅ Finalizar Viaje", on_click=finish_trip, disabled=not st.session_state.active)
    
    # 4. Información de Debugging (Muestra los valores en vivo para verificar)
    if st.session_state.active:
        st.subheader("Tiempo en Vivo (Calculado por la UI)")
        st.write(f"Tiempo Parado (Total): {current_stopped_time:.3f}s")
        st.write(f"Tiempo Movimiento (Total): {current_moving_time:.3f}s")
    
    # 5. El Cronómetro (Permite la actualización de la tarifa en vivo cada 0.5s)
    if st.session_state.active:
        time.sleep(0.5)
        st.rerun()

# --- PUNTO DE ENTRADA ---
if __name__ == "__main__":
    taximeter_app()