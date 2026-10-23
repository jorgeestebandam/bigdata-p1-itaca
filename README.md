# Proyecto 1 · ITACA

> Análisis de datos académicos a partir de ficheros XML exportados de ITACA, con MongoDB y Power BI.

## Descripción y objetivo

Proyecto de **ingesta, procesamiento y análisis de datos académicos** a partir de ficheros XML exportados de la plataforma **ITACA**.

El flujo de datos comprende la extracción de información sobre **alumnado, cursos, módulos y calificaciones**, su transformación y modelado documental en **MongoDB**, y su posterior explotación mediante **Power BI** para la creación de un dashboard de análisis académico.

> [!NOTE]
> Los datos de alumnado deben estar siempre anonimizados.

## Arquitectura

*Diagrama provisional del Bloque 0. Se actualizará al terminar cada bloque.*

```mermaid
graph LR
    A[XML ITACA] --> B[Ingesta]
    B --> C[ETL]
    C --> D[(MongoDB)]
    D --> E[Power BI]
    E --> F[Dashboard]
```
## Fuentes de datos

| Fuente | URL / origen | Formato | Frecuencia de actualización | Licencia | Última ingesta |
|---|---|---|---|---|---|
| Exportación de ITACA | Plataforma ITACA | XML | Pendiente | Pendiente | Pendiente |

## Estructura del repositorio

| Carpeta | Contenido |
|---|---|
| `ingesta/` | Captura y extracción de datos desde los ficheros XML exportados de ITACA |
| `etl/` | Transformación, limpieza y carga de los datos en MongoDB |
| `dashboard/` | Visualización y análisis de los datos mediante Power BI |
| `docker-compose.yml` | Definición del servicio MongoDB |

## Cómo desplegar el entorno

**Requisitos:** Docker Desktop (con Docker Compose) y Git.

1. Clona el repositorio:

```bash
git clone https://github.com/jorgeestebandam/bigdata-p1-itaca.git
cd bigdata-p1-itaca
```

2. Levanta los servicios en segundo plano:

```bash
docker compose up -d
```

3. Comprueba que MongoDB está en marcha:

```bash
docker compose ps
```

Debe aparecer el contenedor `bigdata-mongo` con estado `Up` y el puerto `27017`.

**Acceso a MongoDB**

- Host: `localhost`
- Puerto: `27017`
- Cadena de conexión: `mongodb://localhost:27017`

**Detener los servicios**

```bash
docker compose down
```

> [!WARNING]
> `docker compose down -v` elimina también el volumen `mongo-data` y, con él, todos los datos.

## Bitácora de prácticas


### [Bloque 0 · Entorno ](./documentación/bloque0.md)
### [Bloque 1 · Ingesta de datos ](./documentación/bloque1.md)

## Equipo

- Jorge Esteban García
