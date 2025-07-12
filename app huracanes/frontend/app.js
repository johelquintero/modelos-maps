// --- Inicialización del Mapa ---

// Coordenadas para centrar el mapa (ej. Caribe) y nivel de zoom
const mapCenter = [15, -70];
const zoomLevel = 4;

// Crear el objeto de mapa
const map = L.map('map').setView(mapCenter, zoomLevel);

// --- Capa Base del Mapa ---

// Añadir una capa de teselas (tiles) de OpenStreetMap
// Se pueden usar otros proveedores como CartoDB, Stamen, etc.
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// --- Carga de Datos de Viento ---

// Ruta al archivo JSON generado por nuestro script de Python
const windDataUrl = 'data/wind.json';

// Usar la función fetch para cargar los datos
fetch(windDataUrl)
    .then(response => {
        // Verificar si la respuesta de la red fue exitosa
        if (!response.ok) {
            throw new Error(`Error de red - ${response.statusText}`);
        }
        return response.json(); // Convertir la respuesta a JSON
    })
    .then(data => {
        console.log("Datos de viento cargados exitosamente:", data);

        // --- Creación de la Capa de Velocidad ---

        const velocityLayer = L.velocityLayer({
            displayValues: true,
            displayOptions: {
                velocityType: 'Wind',
                position: 'bottomleft',
                emptyString: 'No wind data',
                angleConvention: 'bearingCCW',
                speedUnit: 'm/s'
            },
            data: data, // Los datos JSON cargados
            
            // Opciones de visualización de las partículas
            minVelocity: 0,      // Velocidad mínima para mostrar una partícula
            maxVelocity: 15,     // Velocidad máxima (afecta el color)
            velocityScale: 0.01, // Escala para la longitud de las partículas
            particleMultiplier: 1 / 300, // Cantidad de partículas
            lineWidth: 2,        // Ancho de la línea de la partícula
            frameRate: 15,       // Fotogramas por segundo para la animación
            colorScale: [        // Escala de colores
                "rgb(255,255,255)", // Blanco para velocidades bajas
                "rgb(100,200,255)", // Azul claro
                "rgb(0,100,255)",   // Azul oscuro
                "rgb(255,255,0)",   // Amarillo
                "rgb(255,100,0)",   // Naranja
                "rgb(255,0,0)"      // Rojo para velocidades altas
            ]
        });

        // Añadir la capa de velocidad al mapa
        velocityLayer.addTo(map);
        console.log("Capa de viento añadida al mapa.");

    })
    .catch(error => {
        // Manejo de errores (ej. si el archivo no se encuentra)
        console.error('Error al cargar o procesar los datos de viento:', error);
        // Mostrar un mensaje al usuario en el mapa
        L.control.attribution({
            prefix: `<span style="color:red;">Error: No se pudieron cargar los datos de viento. Ejecuta los scripts del backend.</span>`
        }).addTo(map);
    });