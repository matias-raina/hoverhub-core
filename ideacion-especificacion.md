## **IDEACIÓN Y ESPECIFICACIÓN**

### **1\. Ideación y requerimientos del negocio**

#### **1.1. Descripción general del proyecto**

**HoverHub** es una plataforma web que conecta a personas o empresas que ofrecen servicios realizados con drones (filmación aérea, relevamiento topográfico, agricultura de precisión, inspección industrial, etc.) con clientes que los necesitan. El sistema actúa como intermediario digital, facilitando la publicación, búsqueda y contratación de estos servicios.

#### **1.2. Problema que resuelve**

La demanda de servicios con drones crece en sectores como la agricultura, la construcción, los eventos y la logística. Aunque existen algunas plataformas que intentan conectar operadores y clientes, el mercado aún carece de una solución profesional, visible y especializada. HoverHub busca cubrir este vacío, creando un entorno confiable y moderno para centralizar la oferta y demanda de servicios con drones.

#### **1.3. Valor del proyecto**

* Facilita la visibilidad y profesionalización de quienes ofrecen servicios con drones.

* Centraliza la búsqueda y contratación, optimizando tiempo y recursos.

* Promueve un ecosistema de confianza mediante reseñas, calificaciones y perfiles verificados.

* A futuro, puede incluir integración con pagos y seguimiento de proyectos.

---

### **2\. Análisis de mercado**

#### **2.1. Usuarios objetivos**

* **Proveedores de servicios con drones**: pilotos independientes, productoras audiovisuales, empresas agrícolas o de mantenimiento industrial.

* **Clientes**: particulares, pymes, productores agropecuarios, organizadores de eventos, estudios de arquitectura, etc.

#### **2.2. Alcance del mercado**

Inicialmente el enfoque será local o regional (Argentina), con posibilidad de escalar a un mercado latinoamericano. El producto puede adaptarse fácilmente a otros países mediante localización de idioma y medios de pago.

#### **2.3. Competencia**

* **Plataformas generales:**  
  Mercado Libre, Facebook Marketplace, Fiverr.  
  *Debilidad:* no están orientadas específicamente a servicios con drones, lo que dificulta la comparación de experiencia, reputación o disponibilidad.

* **Plataformas específicas:**  
  Existen algunas páginas dedicadas exclusivamente a servicios con drones, pero su alcance y usabilidad son limitados. Presentan una baja adopción, interfaces poco profesionales y escasa visibilidad en buscadores.

* **Empresas locales:**  
  Agencias de filmación, inspección o mantenimiento que operan con drones, pero sin un marketplace abierto al público.  
  *Ventaja de HoverHub:* Combina la especialización sectorial con una experiencia de usuario moderna y una red centralizada de operadores certificados.

#### **2.4. Viabilidad económica**

Modelo de negocio proyectado:

* **Fase inicial:** autofinanciado (hosting \+ dominio).

* **Fase de crecimiento:**

  * Comisión por contratación, y/o

  * Suscripción premium para proveedores destacados.  
    El mercado de servicios con drones está en expansión, por lo que se espera una buena relación costo-beneficio a mediano plazo.

### **3\. Análisis de requerimientos del usuario**

#### **3.1. Casos de uso principales**

1. **Registro y login de usuario.**

   * El usuario se registra como cliente o proveedor.

   * Puede iniciar sesión para acceder a su panel personal.

2. **Publicación de servicios (proveedor).**

   * El proveedor puede crear, editar y eliminar anuncios con información del servicio, ubicación y contacto.   
     *Nota*: tanto contratante como contratista pueden ser proveedores.

3. **Búsqueda de servicios (cliente).**

   * El cliente puede buscar proveedores filtrando por tipo de servicio, ubicación o precio.

4. **Contacto entre usuarios.**

   * El cliente puede contactar al proveedor mediante un formulario o correo.

---

### 

### **4\. User Stories**

| ID | Rol | Historia | Criterios de aceptación |
| :---- | :---- | :---- | :---- |
| US\_1 | Visitante | Quiero registrarme como cliente o proveedor | Se muestran campos según el tipo de usuario elegido |
| US\_2 | Proveedor | Quiero publicar mi servicio | El servicio aparece en el listado general |
| US\_3 | Cliente | Quiero buscar servicios por tipo o ubicación | La búsqueda devuelve resultados filtrados |
| US\_4 | Cliente | Quiero contactar a un proveedor | El mensaje se envía correctamente y queda registro |
| US\_5 | Proveedor | Quiero editar o eliminar mi servicio | El sistema actualiza la información sin errores |

## **DISEÑO**

### **1\. MVP**

#### **1.1. Funciones básicas e imprescindibles (API)**

* **Usuarios / perfil / autenticación:**

  * **Registro de usuario**  
  * **Login / autenticación**  
  * **Logout / invalidar sesión**  
  * **Obtener datos del perfil del usuario autenticado**  
  * **Editar / actualizar perfil (nombre, correo, bio, etc.)**  
  * **Obtener perfil público de otro usuario**

* **Trabajos / ofertas:**

  * **Listar trabajos (paginación, filtros, ordenamiento)**  
  * **Obtener detalle de oferta**  
  * **Crear oferta**  
  * **Editar oferta**  
  * **Eliminar oferta**  
  * **Listar trabajos del usuario (“Mis trabajos”) y estadísticas**  
  * **Marcar / desmarcar favoritos**  
  * **Listar favoritos**  
  * **Crear / administrar alertas de trabajo (para recibir notificaciones de nuevas ofertas según criterios)**  
  * **Listar alertas creadas**  
  * **Editar / eliminar alertas**  
  * **Aplicar / postularse a una oferta**  
  * **Eliminar una postulación**  
  * **Listar mis postulaciones**  
  * **Ver postulaciones de una oferta (para quien publicó)**

* **Notificaciones / alertas del sistema:**

  * **Obtener notificaciones del usuario**  
  * **Marcar notificación como leída / despejada**  
  * **Eliminar notificaciones**

* **Configuración / preferencias:**

  * **Obtener configuración de usuario**  
  * **Actualizar configuración**  
  * **Cambiar contraseña**  
  * **Opciones de privacidad / visibilidad del perfil**  
  * **Configuraciones de alertas / frecuencia de notificaciones por correo**

* **Ayuda / soporte:**

  * **Obtener FAQs / artículos de ayuda**  
  * **Enviar mensaje a soporte técnico**

#### **1.2. [UI simple](https://hoverhub-interface.vercel.app/jobs/listings)**

### **2\. Modelado**

#### **2.1. Interacción de componentes**

