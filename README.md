# HoverHub

Plataforma Web API para conectar clientes y proveedores de servicios con drones.

---

## Descripción

**HoverHub** es una plataforma que conecta a personas o empresas que ofrecen servicios con drones (filmación aérea, agricultura de precisión, relevamientos topográficos, inspecciones industriales, entre otros) con clientes que los necesitan.

La aplicación actúa como un intermediario digital que permite la publicación, búsqueda y contratación de servicios, facilitando el encuentro entre la oferta y la demanda dentro de un entorno confiable y especializado.

---

## Objetivo

Crear un sistema que simplifique la conexión entre clientes y proveedores de servicios con drones, ofreciendo una alternativa profesional frente a redes sociales o plataformas generalistas.  
El objetivo del MVP es contar con una versión funcional que permita registrar usuarios, publicar y buscar servicios, y establecer contacto básico entre las partes.

---

## Problema que resuelve

El mercado de servicios con drones se encuentra en expansión, con creciente demanda en sectores como la agricultura, construcción, eventos y logística. Sin embargo:

- No existe una plataforma especializada para este tipo de servicios.
- Los proveedores dependen de redes sociales o contactos informales.
- Los clientes tienen dificultades para comparar opciones y verificar la reputación de los oferentes.

**HoverHub** busca resolver esta brecha ofreciendo una plataforma específica, confiable y de fácil uso.

---

## Alcance y mercado

En una primera etapa, el desarrollo estará orientado al mercado local (Argentina), con potencial de expansión a nivel latinoamericano.  
A futuro se podrán incluir nuevas funciones, como chat interno, pasarela de pagos y sistema de reseñas.

---

## Características principales (MVP)

- Registro y autenticación de usuarios.
- Roles diferenciados: cliente y proveedor.
- Publicación de servicios (con descripción, ubicación y contacto).
- Listado y búsqueda de servicios.
- Contacto básico entre usuarios (por formulario o correo electrónico).

---

## Casos de uso

- Un proveedor se registra, crea un perfil y publica un servicio de filmación aérea.
- Un cliente busca servicios en su área filtrando por tipo o ubicación.
- El cliente contacta al proveedor a través del formulario de la plataforma.
- El proveedor puede editar o eliminar sus publicaciones.

---

## Requerimientos funcionales

- API RESTful con endpoints para usuarios y servicios.
- CRUD completo de publicaciones.
- Filtros de búsqueda por tipo de servicio, ubicación o palabra clave.
- Autenticación y manejo de sesiones seguras.
- Validación de roles (cliente / proveedor).

---

## Requerimientos no funcionales

- **Escalabilidad:** arquitectura modular que permita agregar nuevas funcionalidades.
- **Mantenibilidad:** código documentado y versionado con GitHub.
- **Usabilidad:** interfaz clara y adaptable a distintos dispositivos.
- **Disponibilidad:** servidor estable con uptime superior al 95% durante la demo.

---

## Tecnologías

- **Backend:** Python
- **Base de datos:** PostgreSQL  
- **Frontend:** 
- **Control de versiones:** Git y GitHub  
- **Arquitectura:** 

---

## Roadmap

**Semanas 1 - 2:** configuración del proyecto, autenticación de usuarios y base de datos  
**Semanas 3 - 4:** implementación de roles y publicación de servicios  
**Semanas 5 - 6:** listado y búsqueda de servicios  
**Semanas 7 - 8:** contacto básico, pruebas y demo final


