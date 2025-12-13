import time
import logging

# ----------------------------------------------------
# [ISSUE #17] CONFIGURACIÓN DEL LOGGING
# ----------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("taximetro.log"), 
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('TaximetroDigital')

# [ISSUE #18] DEFINICIÓN DE LA TARIFA MÍNIMA
MIN_FARE = 5.00 # <-- Nuevo: Tarifa mínima fija

# --- FUNCIONES DE CÁLCULO ---

def calculate_fare(seconds_stopped, seconds_moving):
    """
    [ISSUE #18] Calcula la tarifa total en euros y aplica la tarifa mínima.
    """
    # Tarifas base: 0.02 €/s detenido, 0.05 €/s movimiento
    fare = seconds_stopped * 0.02 + seconds_moving * 0.05
    
    # [ISSUE #18] Lógica para aplicar la Tarifa Mínima Fija
    if fare < MIN_FARE:
        # [ISSUE #17] Usamos el logger para registrar cuando se aplica la regla de negocio
        logger.info(f"APLICANDO TARIFA MÍNIMA: Tarifa calculada (€{fare:.2f}) < Tarifa Mínima (€{MIN_FARE:.2f})")
        return MIN_FARE # Devolvemos 5.00€
    else:
        return fare # Devolvemos la tarifa calculada original

# --- FUNCIÓN DE FEEDBACK PARA VISUALIZACIÓN (ISSUE #15) ---

def display_fare_status(current_stopped, current_moving, current_state):
    """ 
    [ISSUE #15] Muestra el estado actual y la tarifa acumulada para el usuario.
    """
    # Llama a la función calculate_fare (que ahora aplica la regla del mínimo)
    current_fare = calculate_fare(current_stopped, current_moving)
    print("=" * 45)
    print(f"ESTADO ACTUAL: {current_state.upper()} ⏱️")
    print(f"TIEMPO TOTAL MOVIMIENTO: {current_moving:.1f}s | TIEMPO TOTAL DETENIDO: {current_stopped:.1f}s")
    print(f"💰 TARIFA ACUMULADA: €{current_fare:.2f}")
    print("=" * 45)

# --- FUNCIÓN PRINCIPAL (El resto permanece igual) ---

def taximeter():
    logger.info("APLICACIÓN INICIADA: Welcome to the F5 Taximeter!")
    print("Available commands: 'start', 'stop', 'move', 'finish', 'exit'\n")

    trip_active = False
    stopped_time = 0
    moving_time = 0
    state = None 
    state_start_time = 0

    while True:
        if trip_active and state is not None:
            display_fare_status(stopped_time, moving_time, state)

        command = input("> ").strip().lower()

        if command == "start":
            if trip_active:
                logger.warning("Intento de iniciar viaje cuando ya estaba activo.")
                print("Error: A trip is already in progress.")
                continue

            trip_active = True
            stopped_time = 0
            moving_time = 0
            state = 'stopped'
            state_start_time = time.time()
            logger.info("EVENTO: Carrera iniciada. Estado inicial: 'stopped'.")
            print("Trip started. Initial state: 'stopped'.") 

        elif command in ("stop", "move"):
            if not trip_active:
                logger.warning("Error: No se puede cambiar de estado sin un viaje activo.")
                print("Error: No active trip. Please start first.")
                continue
            
            old_state = state
            duration = time.time() - state_start_time

            if state == 'stopped':
                stopped_time += duration
            elif state == 'moving':
                moving_time += duration

            state = 'stopped' if command == "stop" else 'moving'
            state_start_time = time.time()
            
            logger.info(f"CAMBIO DE ESTADO: De '{old_state}' a '{state}'. Tiempo acumulado en '{old_state}': {duration:.1f}s")
            print(f"State changed to '{state}'.")

        elif command == "finish":
            if not trip_active:
                logger.warning("Error: Intento de finalizar viaje cuando no hay uno activo.")
                print("Error: No active trip to finish.")
                continue

            duration = time.time() - state_start_time
            if state == 'stopped':
                stopped_time += duration
            else:
                moving_time += duration
            
            # Llama a la función modificada que aplica la tarifa mínima
            final_fare = calculate_fare(stopped_time, moving_time)

            display_fare_status(stopped_time, moving_time, "FINALIZADO")
            
            logger.info(f"VIAJE FINALIZADO. Tiempo total (Mov: {moving_time:.1f}s | Det: {stopped_time:.1f}s). Tarifa final: €{final_fare:.2f}")

            trip_active = False
            state = None

        elif command == "exit":
            logger.info("APLICACIÓN FINALIZADA. El usuario ha salido.")
            print("Exiting the program. Goodbye!")
            break

        else:
            print("Unknown command. Use: start, stop, move, finish, or exit.")

if __name__ == "__main__":
    taximeter()