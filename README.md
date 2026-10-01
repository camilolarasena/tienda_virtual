# SportZone Flask

Aplicación web demostrativa para vender productos de tenis, golf y squash. La interfaz está separada en plantillas HTML, estilos CSS, JavaScript y un servidor Flask conectado a SQLite.

## Funciones incluidas

- Catálogo almacenado en SQLite.
- Registro e inicio de sesión con roles `admin` y `user`.
- Contraseñas protegidas con hash de Werkzeug.
- Carrito guardado en la sesión.
- Pago de prueba y descuento transaccional de stock.
- Panel administrativo para productos, usuarios y pedidos.
- Edición rápida de stock desde la tabla administrativa.
- Creación y edición completa de productos.
- Galería obligatoria de cuatro imágenes por producto.
- Imágenes mediante URL o carga de archivos JPG, PNG y WebP.
- Página individual al hacer clic en cada producto.
- Cuatro productos relacionados en la página de detalle.
- Protección CSRF básica y cookies `HttpOnly`/`SameSite=Lax`.

## Estructura

```text
sportzone_flask/
├── app.py
├── schema.sql
├── requirements.txt
├── instance/
│   └── sportzone.db
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── product_detail.html
│   ├── login.html
│   ├── register.html
│   ├── cart.html
│   ├── checkout.html
│   ├── orders.html
│   ├── error.html
│   └── admin/
│       ├── dashboard.html
│       └── product_form.html
└── static/
    ├── css/styles.css
    ├── js/app.js
    └── uploads/products/
```

## Instalación en Windows

```powershell
cd sportzone_flask
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Crear el administrador

```powershell
flask --app app create-admin
```

La contraseña debe tener al menos ocho caracteres y solamente se guarda su hash.

## Ejecutar

```powershell
flask --app app run --debug
```

Abre `http://127.0.0.1:5000`.

## Dónde se almacena la base de datos

```text
sportzone_flask/instance/sportzone.db
```

Las imágenes subidas por el administrador se guardan en:

```text
sportzone_flask/static/uploads/products/
```

Las rutas de las cuatro imágenes de cada producto se almacenan en la tabla SQLite `product_images`.

## Actualizar desde la versión anterior

Reemplaza los archivos del proyecto, pero conserva tu carpeta `instance/` para no perder usuarios, productos ni pedidos. Al iniciar la nueva versión, Flask crea automáticamente la tabla `product_images` y completa una galería inicial de cuatro imágenes para los productos existentes.

No elimines `instance/sportzone.db` cuando estés actualizando una tienda con información real.

## Uso del panel administrativo

1. Ingresa con una cuenta `admin`.
2. Abre **Administración**.
3. Cambia el número en **Stock rápido** y pulsa el botón verde.
4. Pulsa el lápiz para editar precio, descripción, estado y las cuatro imágenes.
5. En cada espacio de imagen puedes pegar una URL/ruta o subir un archivo.
6. La imagen 1 funciona como portada del catálogo.

El formulario admite hasta 8 MB en total por solicitud.

## Variables recomendadas

```powershell
$env:SPORTZONE_SECRET_KEY="una-clave-aleatoria-muy-larga"
```

También puedes crear el primer administrador mediante variables de entorno:

```powershell
$env:SPORTZONE_ADMIN_EMAIL="admin@ejemplo.com"
$env:SPORTZONE_ADMIN_PASSWORD="CambiaEstaClave123!"
flask --app app run
```

## Pago real

La versión entregada usa un pago de prueba. Para producción debes integrar una pasarela, confirmar el pago mediante webhook y aplicar una política de reserva o descuento definitivo de inventario.
