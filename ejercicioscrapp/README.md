#  Fauna Marina de Galápagos — App interactiva

Visualiza y explora las listas de especies de **Peces** y **Aves** de Galápagos
obtenidas directamente desde la Fundación Charles Darwin.

## Instalación y uso

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar la app
python app.py

# 3. Abrir en el navegador
# → http://localhost:5000
```

## ¿Qué hace la app?

1. **Scraping automático**: descarga los CSV más recientes de peces y aves desde
   `datazone.darwinfoundation.org/es/checklist/checklists-archive`

2. **Limpieza de datos**:
   - Elimina filas y columnas completamente vacías
   - Limpia espacios en blanco en celdas de texto
   - Reemplaza strings vacíos por valores nulos
   - Elimina filas sin nombre de especie

3. **Interfaz interactiva**:
   - Estadísticas (total de especies, endémicas, familias, órdenes)
   - Buscador en tiempo real
   - Filtro por orden/familia
   - Ordenamiento por cualquier columna
   - Paginación de 50 filas por página
   - Etiquetas de estado (Nativa / Endémica / Introducida)
