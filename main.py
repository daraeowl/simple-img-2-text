from machine import Pin, ADC, PWM
import time

print("\n=== Configuración del Sistema de Automatización ===")

# Configuración de Pines
print("\nInicializando Sensores...")
# Sensores
temp_sensor = ADC(4)  # Sensor de temperatura interno
light_sensor_in = ADC(26)  # LDR interior
light_sensor_out = ADC(27)  # LDR exterior
pir_sensor = Pin(15, Pin.IN)  # Sensor de movimiento PIR
ultrasonic_trigger = Pin(17, Pin.OUT)
ultrasonic_echo = Pin(16, Pin.IN)
print("✓ Sensores inicializados")

print("\nInicializando Actuadores...")
# Actuadores
temp_led = Pin(0, Pin.OUT)  # LED de alerta de temperatura
light_led = Pin(1, Pin.OUT)  # LED de alerta de luz
interior_light = Pin(2, Pin.OUT)  # Control de luz interior
door_servo = PWM(Pin(3))  # Servomotor de puerta
curtain_servo = PWM(Pin(4))  # Servomotor de cortina
print("✓ Actuadores inicializados")

# Configurar PWM para servomotores
print("\nConfigurando servomotores...")
door_servo.freq(50)
curtain_servo.freq(50)
print("✓ Servomotores configurados")

# Constantes
print("\nParámetros del Sistema:")
TEMP_MIN = 20  # Temperatura mínima aceptable (°C)
TEMP_MAX = 25  # Temperatura máxima aceptable (°C)
LIGHT_THRESHOLD = 30000  # Umbral de luz para alertas
LIGHT_EXTERIOR_THRESHOLD = 40000  # Umbral de luz para control de cortinas
DISTANCE_THRESHOLD = 30  # Distancia en cm para activar la puerta

print(f"• Rango de temperatura: {TEMP_MIN}°C - {TEMP_MAX}°C")
print(f"• Umbral de luz interior: {LIGHT_THRESHOLD}")
print(f"• Umbral de luz exterior: {LIGHT_EXTERIOR_THRESHOLD} (Cerrar cortinas si es mayor)")
print(f"• Distancia de activación de puerta: {DISTANCE_THRESHOLD}cm")

# Almacenamiento de estado previo
class SystemState:
    def __init__(self):
        self.temperature = 0
        self.temp_alert = False
        self.interior_light = 0
        self.light_alert = False
        self.motion_detected = False
        self.exterior_light = 0
        self.curtains_closed = False
        self.door_open = False
        self.distance = 100

# Crear objeto de estado global
state = SystemState()

def get_temperature():
    """Leer temperatura del sensor interno"""
    adc_value = temp_sensor.read_u16()
    voltage = (adc_value * 3.3) / 65535
    temperature = 27 - (voltage - 0.706) / 0.001721
    return temperature

def get_light_level(sensor):
    """Leer nivel de luz del sensor LDR"""
    return 65535 - sensor.read_u16()  # Invertir la lectura

def measure_distance():
    """Medir distancia usando sensor ultrasónico"""
    ultrasonic_trigger.low()
    time.sleep_us(2)
    ultrasonic_trigger.high()
    time.sleep_us(5)
    ultrasonic_trigger.low()
    
    try:
        while ultrasonic_echo.value() == 0:
            signaloff = time.ticks_us()
        while ultrasonic_echo.value() == 1:
            signalon = time.ticks_us()
        
        timepassed = signalon - signaloff
        distance = (timepassed * 0.0343) / 2
        return distance
    except:
        print("⚠ Advertencia: Error en la lectura del sensor ultrasónico")
        return 100

def set_servo_position(servo, angle):
    """Establecer posición del servomotor (0-180 grados)"""
    duty = int(((angle / 180) * 8000) + 1000)
    servo.duty_u16(duty)

def control_temperature():
    """Monitorear y controlar temperatura"""
    temp = get_temperature()
    temp_alert = temp < TEMP_MIN or temp > TEMP_MAX
    
    # Verificar cambios
    if abs(temp - state.temperature) >= 0.5 or temp_alert != state.temp_alert:
        status = "🔴" if temp_alert else "🟢"
        print(f"\n[Control de Temperatura] {status}")
        print(f"├── Actual: {temp:.1f}°C")
        print(f"└── Estado: {status} {'ALERTA' if temp_alert else 'Normal'}")
        
        # Actualizar estado
        state.temperature = temp
        state.temp_alert = temp_alert
    
    if temp_alert:
        temp_led.on()
    else:
        temp_led.off()

def control_light():
    """Monitorear y controlar luz interior"""
    light_level = get_light_level(light_sensor_in)
    light_alert = light_level < LIGHT_THRESHOLD
    
    # Verificar cambios significativos (>5% cambio)
    if abs(light_level - state.interior_light) > (LIGHT_THRESHOLD * 0.05) or light_alert != state.light_alert:
        status = "🔴" if light_alert else "🟢"
        print(f"\n[Luz Interior] {status}")
        print(f"├── Nivel: {light_level}")
        print(f"└── Estado: {status} {'Luz Baja' if light_alert else 'Luz Adecuada'}")
        
        # Actualizar estado
        state.interior_light = light_level
        state.light_alert = light_alert
    
    if light_alert:
        light_led.on()
    else:
        light_led.off()

def control_interior_lighting():
    """Controlar iluminación interior basada en movimiento"""
    motion = pir_sensor.value()
    
    # Solo registrar cuando cambia el estado de movimiento
    if motion != state.motion_detected:
        status = "🟡" if motion else "⚪"
        print(f"\n[Sensor de Movimiento] {status}")
        print(f"├── Movimiento: {'Detectado' if motion else 'Ninguno'}")
        print(f"└── Luces: {'ENCENDIDAS' if motion else 'APAGADAS'}")
        
        # Actualizar estado
        state.motion_detected = motion
    
    if motion:
        interior_light.on()
    else:
        interior_light.off()

def control_curtains():
    """Controlar cortinas basado en luz exterior
    - Cerrar cortinas cuando hay mucha luz (proteger del calor)
    - Abrir cortinas cuando hay poca luz (permitir iluminación natural)"""
    exterior_light = get_light_level(light_sensor_out)
    should_close = exterior_light > LIGHT_EXTERIOR_THRESHOLD  # Cerrar con mucha luz
    
    # Verificar cambios significativos (>5% cambio)
    if abs(exterior_light - state.exterior_light) > (LIGHT_EXTERIOR_THRESHOLD * 0.05) or should_close != state.curtains_closed:
        status = "🌞" if should_close else "🌙"
        print(f"\n[Luz Exterior] {status}")
        print(f"├── Nivel: {exterior_light}")
        print(f"└── Cortinas: {'Cerrando (Proteger del calor)' if should_close else 'Abriendo (Permitir luz natural)'}")
        
        # Actualizar estado
        state.exterior_light = exterior_light
        state.curtains_closed = should_close
    
    if should_close:
        set_servo_position(curtain_servo, 180)  # Cerrar cortinas
    else:
        set_servo_position(curtain_servo, 0)    # Abrir cortinas

def control_door():
    """Controlar puerta basado en proximidad"""
    distance = measure_distance()
    should_open = distance < DISTANCE_THRESHOLD
    
    # Verificar cambios significativos (>5cm cambio)
    if abs(distance - state.distance) > 5 or should_open != state.door_open:
        status = "🚪" if should_open else "🔒"
        print(f"\n[Sensor de Proximidad] {status}")
        print(f"├── Distancia: {distance:.1f}cm")
        print(f"└── Puerta: {'Abriendo' if should_open else 'Cerrada'}")
        
        # Actualizar estado
        state.distance = distance
        state.door_open = should_open
    
    if should_open:
        set_servo_position(door_servo, 90)
    else:
        set_servo_position(door_servo, 0)

# Inicializar posición de servomotores
print("\nInicializando posición del sistema...")
set_servo_position(door_servo, 0)
print("✓ Puerta cerrada")
set_servo_position(curtain_servo, 0)
print("✓ Cortinas abiertas")
time.sleep(1)

# Bucle principal
print("\n=== Sistema de Automatización Iniciado ===")
print("El sistema solo registrará cambios significativos")
print("=" * 50)

while True:
    try:
        # Ejecutar todos los sistemas de control
        control_temperature()
        control_light()
        control_interior_lighting()
        control_curtains()
        control_door()
        
        time.sleep(0.1)  # Pequeña pausa entre verificaciones
        
    except Exception as e:
        print(f"\n⚠ Error:")
        print(f"└── {str(e)}")
        time.sleep(1) 