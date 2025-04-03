"""
Diálogo de progreso para mostrar el avance de las operaciones de respaldo
con curiosidades sobre Minecraft que cambian automáticamente.
"""

import random
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from app.utils.styles import (
    get_dialog_style, get_progress_bar_style, get_button_style,
    get_operation_title_style, get_facts_frame_style, get_fact_title_style,
    get_fact_content_style, get_fact_counter_style, get_success_status_style
)


class BackupProgressDialog(QDialog):
    """
    Diálogo personalizado que muestra el progreso de las operaciones de respaldo
    mientras entretiene al usuario con curiosidades sobre Minecraft.
    """

    def __init__(self, parent=None, operation_type="respaldo"):
        """
        Inicializa el diálogo de progreso.

        Args:
            parent: Widget padre (normalmente la ventana principal)
            operation_type: Tipo de operación ("respaldo" o "restauración")
        """
        super().__init__(parent)
        self.operation_type = operation_type
        self.curiosity_index = -1  # Iniciar en -1 para que el primer incremento sea 0
        self.operation_completed = False

        # Colección de curiosidades sobre Minecraft
        self.minecraft_facts = [
            "Minecraft fue creado originalmente por Markus 'Notch' Persson en 2009.",
            "El nombre de los Creepers surgió de un error de programación en los cerdos.",
            "El Enderman fue inspirado por el personaje de terror Slenderman.",
            "El bloque 'Far Lands' era un error de generación en las versiones antiguas de Minecraft que creaba terrenos extraños.",
            "La música de Minecraft fue compuesta por Daniel 'C418' Rosenfeld.",
            "Un día en Minecraft dura exactamente 20 minutos en tiempo real.",
            "El sonido de los Ghasts está basado en el maullido del gato de un desarrollador.",
            "El mundo de Minecraft es técnicamente 'infinito', pero tiene limitaciones técnicas después de cierta distancia.",
            "El nombre original de Minecraft era 'Cave Game'.",
            "Cada oveja en Minecraft puede dar de 1 a 3 bloques de lana al ser esquilada.",
            "El bloque de diamante requiere 9 diamantes para ser creado, lo que lo convierte en uno de los bloques más caros del juego.",
            "Los Endermans solo se volvieron hostiles cuando los miras directamente a los ojos.",
            "El Nether es en realidad 8 veces más pequeño que el mundo normal, por lo que viajar 1 bloque en el Nether equivale a 8 en el mundo normal.",
            "La probabilidad de que un zombie recoja un objeto es del 10% en dificultad fácil, 50% en normal y 55% en difícil.",
            "Los conejos tienen una pequeña probabilidad de aparecer como el conejo asesino de Monty Python.",
            "El sonido de apertura de puertas es en realidad un sonido de una lata de refresco abriéndose, pero ralentizado.",
            "Los Creepers tienen miedo a los ocelotes y los gatos, y huirán activamente de ellos.",
            "La semilla '404' en las versiones antiguas generaba un mundo con un notable hueco en el suelo cerca del punto de generación.",
            "Los calamares pueden generar lluvia de tinta cuando son atacados.",
            "El sonido de caminar sobre arena es en realidad alguien caminando sobre sal en la vida real.",
            "Los aldeanos pueden intercambiar sus profesiones si pierden acceso a su bloque de trabajo.",
            "Los bloques de obsidiana tardan 9,4 segundos en ser minados con un pico de diamante y 4,5 con uno de netherita.",
            "Si un rayo golpea a un cerdo, este se transformará en un cerdo zombie (piglin).",
            "El rango de visión de un Enderman es más corto cuando está lloviendo.",
            "Antes de la versión 1.14, los aldeanos no tenían profesiones específicas y todos comerciaban los mismos objetos.",
            "Las coordenadas 0,0 en el mapa son conocidas como 'spawn chunks' y siempre están cargadas mientras juegas.",
            "El libro encantado más raro posible en Minecraft tiene una probabilidad de generarse de aproximadamente 1 en 403 millones.",
            "Los pandas tienen personalidades diferentes: pueden ser juguetones, agresivos, perezosos o tímidos.",
            "Si nombras a una oveja 'jeb_' con una etiqueta de nombre, su lana cambiará continuamente de color.",
            "El sonido de los bloques de piedra rompiéndose es en realidad alguien golpeando cartón en la vida real."
        ]

        self.init_ui()

        # Mostrar la primera curiosidad inmediatamente
        self.change_fact()

        # Iniciar temporizador para cambiar las curiosidades
        self.fact_timer = QTimer(self)
        self.fact_timer.timeout.connect(self.change_fact)
        self.fact_timer.start(10000)  # Cambiar cada 10 segundos

    def init_ui(self):
        """Configura la interfaz de usuario del diálogo."""
        # Configurar la ventana
        self.setWindowTitle(f"Progreso de {self.operation_type}")
        self.setFixedSize(600, 400)
        self.setModal(True)

        # Usar estilos consistentes con la aplicación
        self.setStyleSheet(get_dialog_style())

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # Título de la operación
        title_label = QLabel(f"Realizando {self.operation_type} de mundos")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(get_operation_title_style())
        main_layout.addWidget(title_label)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet(get_progress_bar_style())
        main_layout.addWidget(self.progress_bar)

        # Etiqueta de estado
        self.status_label = QLabel("Preparando operación...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        # Marco para las curiosidades
        facts_frame = QFrame()
        facts_frame.setStyleSheet(get_facts_frame_style())
        facts_layout = QVBoxLayout(facts_frame)

        # Título "¿Sabías que...?"
        did_you_know_label = QLabel("¿Sabías que...?")
        did_you_know_label.setStyleSheet(get_fact_title_style())
        did_you_know_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        facts_layout.addWidget(did_you_know_label)

        # Contenido de la curiosidad
        self.fact_label = QLabel("Inicializando curiosidades...")
        self.fact_label.setWordWrap(True)
        self.fact_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fact_label.setStyleSheet(get_fact_content_style())
        self.fact_label.setMinimumHeight(100)
        facts_layout.addWidget(self.fact_label)

        # Indicador de curiosidad actual
        self.fact_counter = QLabel("Curiosidad 0/30")
        self.fact_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fact_counter.setStyleSheet(get_fact_counter_style())
        facts_layout.addWidget(self.fact_counter)

        main_layout.addWidget(facts_frame)

        # Añadir espacio flexible
        main_layout.addStretch(1)

        # Botón de cierre (inicialmente deshabilitado)
        button_layout = QHBoxLayout()
        self.close_button = QPushButton("Cerrar")
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

    def update_progress(self, value, message):
        """
        Actualiza el progreso de la operación.

        Args:
            value: Porcentaje de progreso (0-100)
            message: Mensaje descriptivo del estado actual
        """
        self.progress_bar.setValue(value)
        self.status_label.setText(message)

        # Si alcanzamos el 100%, activar el botón de cierre
        if value >= 100:
            self.complete_operation()

    def complete_operation(self):
        """Marca la operación como completada y habilita el botón de cierre."""
        if self.operation_completed:
            return

        self.operation_completed = True
        self.close_button.setEnabled(True)

        # NO detenemos el temporizador para que las curiosidades sigan cambiando

        # Mostrar mensaje de éxito
        self.status_label.setText(f"¡{self.operation_type.capitalize()} completado con éxito!")
        self.status_label.setStyleSheet(get_success_status_style())

        # Animar la barra de progreso con el nuevo color verde #05C17C
        self.animate_completion()

    def change_fact(self):
        """Cambia a la siguiente curiosidad."""
        # Actualizar el índice para la próxima curiosidad
        self.curiosity_index = (self.curiosity_index + 1) % len(self.minecraft_facts)

        # Obtener y mostrar la nueva curiosidad directamente (sin animaciones)
        new_fact = self.minecraft_facts[self.curiosity_index]
        self.fact_label.setText(new_fact)

        # Actualizar contador
        self.fact_counter.setText(f"Curiosidad {self.curiosity_index + 1}/{len(self.minecraft_facts)}")

    def animate_completion(self):
        """Realiza una animación visual para indicar que el proceso ha terminado."""
        # Animar cambio de color en la barra de progreso - Verde #05C17C
        self.progress_bar.setStyleSheet(get_progress_bar_style(success=True))

        # Hacer que el botón se destaque usando colores consistentes
        self.close_button.setStyleSheet(get_button_style())