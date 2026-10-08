# Proyecto 1: ITACA

Proyecto de **ingesta, procesamiento y análisis de datos académicos** a partir de ficheros XML exportados de la plataforma **ITACA**.

El flujo de datos comprende la extracción de información sobre **alumnado, cursos, módulos y calificaciones**, su transformación y modelado documental en **MongoDB**, y su posterior explotación mediante **Power BI** para la creación de un dashboard de análisis académico.

## Estructura del proyecto

- `ingesta/`: captura y extracción de datos desde los ficheros XML exportados de ITACA.
- `etl/`: transformación, limpieza y carga de los datos en MongoDB.
- `dashboard/`: visualización y análisis de los datos mediante Power BI.

## Flujo de datos

XML ITACA  →  INGESTA  →  ETL  →  MONGODB  →  POWER BI  →  DASHBOARD

## Cómo ejecutarlo

> 🚧 **Pendiente de completar.**
>
> Se documentará el proceso de ejecución mediante `docker-compose.yml`.

## Equipo

- Jorge Esteban García