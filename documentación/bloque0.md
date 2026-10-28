
## ENTORNO
**Objetivo:** dejar preparado el entorno base del proyecto: repositorio Git independiente, estructura de carpetas, `.gitignore`, `docker-compose.yml` con MongoDB y README inicial.

**Pasos realizados:**

1. Creación del repositorio con `git init` y la rama `main`.
2. Creación de las carpetas `ingesta/`, `etl/` y `dashboard/` (con `.gitkeep` para que Git las conserve).
3. Configuración del `.gitignore`.
4. Creación del `docker-compose.yml` con el servicio MongoDB 7 (volumen persistente y red `bigdata-net`).
5. Arranque con `docker compose up -d` y comprobación con `docker compose ps`.
6. Primer commit y publicación en GitHub.

**Problemas encontrados y solución:**

- **Error al conectar con la API de Docker:** Docker Desktop no estaba en marcha. Se solucionó abriéndolo y esperando a que el motor estuviera activo antes de ejecutar `docker compose up -d`.
- **`README.html` incluido en el commit:** un archivo HTML generado a partir del README se coló en `git add .`. Se retiró con `git rm --cached README.html` y se añadió al `.gitignore`.
- **Aviso de `version` obsoleto en el compose:** es solo informativo, el atributo se ignora en las versiones recientes de Docker Compose.

**Resultado:** contenedor `bigdata-mongo` en ejecución.

![docker compose ps](docs/docker-compose-ps.png)

## Decisiones técnicas

| Decisión | Alternativa descartada | Motivo |
|---|---|---|
| MongoDB como almacenamiento | Base de datos relacional | Los XML de ITACA tienen estructura anidada, que encaja de forma natural en documentos |
| Docker Compose para el entorno | Instalación local de MongoDB | Entorno reproducible y aislado, sin instalar nada en el equipo |
