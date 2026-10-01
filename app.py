from __future__ import annotations

import os
import secrets
import sqlite3
from functools import wraps
from pathlib import Path
from typing import Any, Callable, TypeVar

import click
from flask import (
    Flask,
    abort,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "instance" / "sportzone.db"
UPLOAD_DIR = BASE_DIR / "static" / "uploads" / "products"
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
F = TypeVar("F", bound=Callable[..., Any])

SEED_PRODUCTS = [
    (
        "Wilson Pro Staff 97 V14 Profesional",
        "Wilson",
        "tenis",
        "Raqueta profesional",
        "adulto",
        "Raqueta de control y precisión para jugadores avanzados.",
        1299900,
        8,
        "https://images.unsplash.com/photo-1617083934555-ac7d4d58ce51?w=900&q=80",
    ),
    (
        "Wilson Clash 100 V3",
        "Wilson",
        "tenis",
        "Raqueta normal",
        "adulto",
        "Raqueta versátil, cómoda y estable para nivel intermedio.",
        899900,
        14,
        "https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?w=900&q=80",
    ),
    (
        "Babolat Pure Drive Team",
        "Babolat",
        "tenis",
        "Raqueta normal",
        "adulto",
        "Potencia accesible con peso ligero para juego recreativo y competitivo.",
        829900,
        10,
        "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=900&q=80",
    ),
    (
        "Wilson Junior 26 3/4",
        "Wilson",
        "tenis",
        "Raqueta infantil 3/4",
        "niños",
        "Tamaño 3/4 recomendado para niños en proceso de iniciación.",
        249900,
        18,
        "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=900&q=80",
    ),
    (
        "Pelotas US Open x3",
        "Wilson",
        "tenis",
        "Pelotas",
        "todos",
        "Tubo de tres pelotas para entrenamiento y competencia.",
        39900,
        40,
        "https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=900&q=80",
    ),
    (
        "Driver Qi10 Max",
        "TaylorMade",
        "golf",
        "Driver",
        "adulto",
        "Driver de alta estabilidad y tolerancia para mejorar la salida.",
        2399900,
        6,
        "https://images.unsplash.com/photo-1535131749006-b7f58c99034b?w=900&q=80",
    ),
    (
        "Hierro 5 Paradym AI Smoke",
        "Callaway",
        "golf",
        "Hierro 5",
        "adulto",
        "Hierro individual con diseño orientado a distancia y control.",
        719900,
        7,
        "https://images.unsplash.com/photo-1587174486073-ae5e5cff23aa?w=900&q=80",
    ),
    (
        "Hierro 6 G430",
        "PING",
        "golf",
        "Hierro 6",
        "adulto",
        "Hierro individual con buena tolerancia y trayectoria consistente.",
        759900,
        8,
        "https://images.unsplash.com/photo-1587174486073-ae5e5cff23aa?w=900&q=80",
    ),
    (
        "Hierro 7 Darkspeed",
        "Cobra",
        "golf",
        "Hierro 7",
        "adulto",
        "Hierro equilibrado para precisión en golpes de aproximación.",
        689900,
        9,
        "https://images.unsplash.com/photo-1592919505780-303950717480?w=900&q=80",
    ),
    (
        "Hierro 8 Dynapower",
        "Wilson Staff",
        "golf",
        "Hierro 8",
        "adulto",
        "Hierro de control para golpes cortos y aproximaciones al green.",
        599900,
        11,
        "https://images.unsplash.com/photo-1593111774240-d529f12cf4bb?w=900&q=80",
    ),
    (
        "Putter White Hot Versa",
        "Odyssey",
        "golf",
        "Putter",
        "adulto",
        "Putter con alineación visual y sensación suave en el impacto.",
        1099900,
        5,
        "https://images.unsplash.com/photo-1591491653056-4d2f82d9bd66?w=900&q=80",
    ),
    (
        "Pelotas Pro V1 x12",
        "Titleist",
        "golf",
        "Pelotas",
        "todos",
        "Docena de pelotas premium con control y rendimiento integral.",
        249900,
        24,
        "https://images.unsplash.com/photo-1587174486073-ae5e5cff23aa?w=900&q=80",
    ),
    (
        "Sonic Core Revelation Pro",
        "Dunlop",
        "squash",
        "Raqueta profesional",
        "adulto",
        "Raqueta profesional de precisión y respuesta rápida.",
        649900,
        9,
        "https://images.unsplash.com/photo-1657704358775-ed705c7388d2?w=900&q=80",
    ),
    (
        "Graphene 360 Speed 135",
        "HEAD",
        "squash",
        "Raqueta normal",
        "adulto",
        "Raqueta balanceada para jugadores intermedios.",
        469900,
        13,
        "https://images.unsplash.com/photo-1657704358775-ed705c7388d2?w=900&q=80",
    ),
    (
        "Carboflex 125 X-Top",
        "Tecnifibre",
        "squash",
        "Raqueta profesional",
        "adulto",
        "Raqueta ligera para velocidad de preparación y potencia.",
        799900,
        7,
        "https://images.unsplash.com/photo-1657704358775-ed705c7388d2?w=900&q=80",
    ),
    (
        "Pelotas Pro Doble Punto x3",
        "Dunlop",
        "squash",
        "Pelotas",
        "todos",
        "Pack de pelotas para jugadores avanzados y competencia.",
        54900,
        32,
        "https://images.unsplash.com/photo-1599474924187-334a4ae5bd3c?w=900&q=80",
    ),
    (
        "Gafas Protectoras Impulse",
        "HEAD",
        "squash",
        "Protección ocular",
        "todos",
        "Protección liviana para entrenamiento y competencia de squash.",
        119900,
        16,
        "https://images.unsplash.com/photo-1577803645773-f96470509666?w=900&q=80",
    ),
]

DEFAULT_GALLERY_IMAGES = {
    "tenis": [
        "https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?w=1200&q=85",
        "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=1200&q=85",
        "https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=1200&q=85",
        "https://images.unsplash.com/photo-1617083934555-ac7d4d58ce51?w=1200&q=85",
    ],
    "golf": [
        "https://images.unsplash.com/photo-1535131749006-b7f58c99034b?w=1200&q=85",
        "https://images.unsplash.com/photo-1587174486073-ae5e5cff23aa?w=1200&q=85",
        "https://images.unsplash.com/photo-1592919505780-303950717480?w=1200&q=85",
        "https://images.unsplash.com/photo-1593111774240-d529f12cf4bb?w=1200&q=85",
    ],
    "squash": [
        "https://images.unsplash.com/photo-1657704358775-ed705c7388d2?w=1200&q=85",
        "https://images.unsplash.com/photo-1599474924187-334a4ae5bd3c?w=1200&q=85",
        "https://images.unsplash.com/photo-1577803645773-f96470509666?w=1200&q=85",
        "https://images.unsplash.com/photo-1544287757-a8ab80d90b60?w=1200&q=85",
    ],
}


def build_default_gallery(sport: str, primary_image: str) -> list[str]:
    images: list[str] = []
    for candidate in [primary_image, *DEFAULT_GALLERY_IMAGES.get(sport, [])]:
        candidate = (candidate or "").strip()
        if candidate and candidate not in images:
            images.append(candidate)
        if len(images) == 4:
            break
    while len(images) < 4:
        images.append("https://placehold.co/1200x900?text=SportZone")
    return images


def allowed_image_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SPORTZONE_SECRET_KEY", "dev-change-this-secret"),
        DATABASE=str(DATABASE),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("SPORTZONE_COOKIE_SECURE", "0") == "1",
        MAX_CONTENT_LENGTH=8 * 1024 * 1024,
    )

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    def get_db() -> sqlite3.Connection:
        if "db" not in g:
            connection = sqlite3.connect(app.config["DATABASE"])
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            g.db = connection
        return g.db

    def close_db(_: BaseException | None = None) -> None:
        db = g.pop("db", None)
        if db is not None:
            db.close()

    app.teardown_appcontext(close_db)

    def init_db(seed: bool = True) -> None:
        db = get_db()
        db.executescript((BASE_DIR / "schema.sql").read_text(encoding="utf-8"))
        if seed and db.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
            db.executemany(
                """
                INSERT INTO products
                    (name, brand, sport, product_type, audience, description, price, stock, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                SEED_PRODUCTS,
            )

        # Migración no destructiva: crea una galería mínima de cuatro imágenes
        # para productos existentes y nuevos sin borrar usuarios, pedidos o inventario.
        products_without_gallery = db.execute(
            """
            SELECT products.*
            FROM products
            LEFT JOIN product_images ON product_images.product_id = products.id
            GROUP BY products.id
            HAVING COUNT(product_images.id) < 4
            """
        ).fetchall()
        for product in products_without_gallery:
            existing = db.execute(
                "SELECT image_url FROM product_images WHERE product_id = ? ORDER BY position, id",
                (product["id"],),
            ).fetchall()
            images = [row["image_url"] for row in existing]
            defaults = build_default_gallery(product["sport"], product["image_url"])
            for candidate in defaults:
                if candidate not in images:
                    images.append(candidate)
                if len(images) == 4:
                    break
            db.execute("DELETE FROM product_images WHERE product_id = ?", (product["id"],))
            db.executemany(
                "INSERT INTO product_images (product_id, image_url, position) VALUES (?, ?, ?)",
                [(product["id"], image_url, position) for position, image_url in enumerate(images[:4], 1)],
            )
            db.execute(
                "UPDATE products SET image_url = ? WHERE id = ?",
                (images[0], product["id"]),
            )
        db.commit()

    app.get_db = get_db  # type: ignore[attr-defined]
    app.init_db = init_db  # type: ignore[attr-defined]

    @app.cli.command("init-db")
    def init_db_command() -> None:
        """Crea la base de datos y carga el catálogo inicial."""
        init_db(seed=True)
        click.echo("Base de datos inicializada.")

    @app.cli.command("create-admin")
    @click.option("--name", prompt="Nombre del administrador")
    @click.option("--email", prompt="Correo del administrador")
    @click.password_option(confirmation_prompt=True)
    def create_admin_command(name: str, email: str, password: str) -> None:
        """Crea o actualiza una cuenta con rol administrador."""
        email = email.strip().lower()
        if len(password) < 8:
            raise click.ClickException("La contraseña debe tener al menos 8 caracteres.")
        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        password_hash = generate_password_hash(password)
        if existing:
            db.execute(
                "UPDATE users SET name = ?, password_hash = ?, role = 'admin' WHERE id = ?",
                (name.strip(), password_hash, existing["id"]),
            )
        else:
            db.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'admin')",
                (name.strip(), email, password_hash),
            )
        db.commit()
        click.echo(f"Administrador listo: {email}")

    def login_required(view: F) -> F:
        @wraps(view)
        def wrapped_view(*args: Any, **kwargs: Any) -> Any:
            if g.user is None:
                flash("Debes iniciar sesión para continuar.", "warning")
                return redirect(url_for("login", next=request.path))
            return view(*args, **kwargs)

        return wrapped_view  # type: ignore[return-value]

    def admin_required(view: F) -> F:
        @wraps(view)
        @login_required
        def wrapped_view(*args: Any, **kwargs: Any) -> Any:
            if g.user["role"] != "admin":
                abort(403)
            return view(*args, **kwargs)

        return wrapped_view  # type: ignore[return-value]

    def csrf_token() -> str:
        token = session.get("_csrf_token")
        if not token:
            token = secrets.token_urlsafe(32)
            session["_csrf_token"] = token
        return token

    @app.before_request
    def load_logged_in_user_and_validate_csrf() -> None:
        user_id = session.get("user_id")
        g.user = (
            get_db().execute(
                "SELECT id, name, email, role, created_at FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if user_id
            else None
        )

        if request.method == "POST":
            supplied = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
            if not supplied or not secrets.compare_digest(supplied, csrf_token()):
                abort(400, "Token CSRF inválido o ausente.")

    @app.after_request
    def set_security_headers(response: Any) -> Any:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    @app.context_processor
    def inject_helpers() -> dict[str, Any]:
        return {"csrf_token": csrf_token, "format_cop": format_cop}

    @app.route("/")
    def index() -> str:
        sport = request.args.get("sport", "").strip().lower()
        query = request.args.get("q", "").strip()
        sql = "SELECT * FROM products WHERE active = 1"
        params: list[Any] = []
        if sport in {"tenis", "golf", "squash"}:
            sql += " AND sport = ?"
            params.append(sport)
        if query:
            sql += " AND (name LIKE ? OR brand LIKE ? OR product_type LIKE ?)"
            term = f"%{query}%"
            params.extend([term, term, term])
        sql += " ORDER BY sport, id"
        products = get_db().execute(sql, params).fetchall()
        return render_template("index.html", products=products, selected_sport=sport, query=query)

    @app.route("/productos/<int:product_id>")
    def product_detail(product_id: int) -> str:
        db = get_db()
        if g.user and g.user["role"] == "admin":
            product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        else:
            product = db.execute(
                "SELECT * FROM products WHERE id = ? AND active = 1", (product_id,)
            ).fetchone()
        if product is None:
            abort(404)
        images = db.execute(
            "SELECT image_url, position FROM product_images WHERE product_id = ? ORDER BY position, id",
            (product_id,),
        ).fetchall()
        related = db.execute(
            """
            SELECT * FROM products
            WHERE sport = ? AND id <> ? AND active = 1
            ORDER BY id DESC LIMIT 4
            """,
            (product["sport"], product_id),
        ).fetchall()
        return render_template(
            "product_detail.html", product=product, images=images, related=related
        )

    @app.route("/registro", methods=("GET", "POST"))
    def register() -> str | Any:
        if g.user:
            return redirect(url_for("index"))
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            password_confirm = request.form.get("password_confirm", "")
            error = None
            if len(name) < 2:
                error = "Escribe un nombre válido."
            elif "@" not in email or "." not in email.rsplit("@", 1)[-1]:
                error = "Escribe un correo electrónico válido."
            elif len(password) < 8:
                error = "La contraseña debe tener al menos 8 caracteres."
            elif password != password_confirm:
                error = "Las contraseñas no coinciden."

            if error is None:
                try:
                    db = get_db()
                    db.execute(
                        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'user')",
                        (name, email, generate_password_hash(password)),
                    )
                    db.commit()
                except sqlite3.IntegrityError:
                    error = "Ya existe una cuenta con ese correo."
                else:
                    flash("Cuenta creada. Ya puedes iniciar sesión.", "success")
                    return redirect(url_for("login"))
            flash(error, "danger")
        return render_template("register.html")

    @app.route("/ingresar", methods=("GET", "POST"))
    def login() -> str | Any:
        if g.user:
            return redirect(url_for("index"))
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            user = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if user is None or not check_password_hash(user["password_hash"], password):
                flash("Correo o contraseña incorrectos.", "danger")
            else:
                session.clear()
                session["user_id"] = user["id"]
                csrf_token()
                flash(f"Bienvenido, {user['name']}.", "success")
                target = request.args.get("next")
                return redirect(target if target and target.startswith("/") else url_for("index"))
        return render_template("login.html")

    @app.post("/salir")
    def logout() -> Any:
        session.clear()
        flash("Sesión cerrada correctamente.", "info")
        return redirect(url_for("index"))

    def get_cart() -> dict[str, int]:
        raw = session.get("cart", {})
        return {str(k): max(0, int(v)) for k, v in raw.items() if int(v) > 0}

    def cart_details() -> tuple[list[dict[str, Any]], int, int, int]:
        cart = get_cart()
        if not cart:
            return [], 0, 0, 0
        ids = [int(product_id) for product_id in cart]
        placeholders = ",".join("?" for _ in ids)
        rows = get_db().execute(
            f"SELECT * FROM products WHERE id IN ({placeholders})", ids
        ).fetchall()
        items: list[dict[str, Any]] = []
        subtotal = 0
        for row in rows:
            quantity = cart.get(str(row["id"]), 0)
            line_total = row["price"] * quantity
            subtotal += line_total
            items.append({"product": row, "quantity": quantity, "line_total": line_total})
        shipping = 0 if subtotal == 0 or subtotal >= 250000 else 18000
        return items, subtotal, shipping, subtotal + shipping

    @app.route("/carrito")
    def cart_page() -> str:
        items, subtotal, shipping, total = cart_details()
        return render_template(
            "cart.html", items=items, subtotal=subtotal, shipping=shipping, total=total
        )

    @app.post("/api/carrito/agregar")
    def cart_add() -> Any:
        data = request.get_json(silent=True) or {}
        try:
            product_id = int(data.get("product_id", 0))
            quantity = max(1, min(20, int(data.get("quantity", 1))))
        except (TypeError, ValueError):
            return jsonify(ok=False, message="Datos inválidos."), 400
        product = get_db().execute(
            "SELECT id, name, stock, active FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        if product is None or not product["active"]:
            return jsonify(ok=False, message="Producto no disponible."), 404
        cart = get_cart()
        new_quantity = cart.get(str(product_id), 0) + quantity
        if new_quantity > product["stock"]:
            return jsonify(ok=False, message="No hay suficiente inventario."), 409
        cart[str(product_id)] = new_quantity
        session["cart"] = cart
        session.modified = True
        return jsonify(
            ok=True,
            message=f"{product['name']} fue añadido al carrito.",
            cart_count=sum(cart.values()),
        )

    @app.post("/api/carrito/actualizar")
    def cart_update() -> Any:
        data = request.get_json(silent=True) or {}
        try:
            product_id = int(data.get("product_id", 0))
            quantity = max(0, min(20, int(data.get("quantity", 0))))
        except (TypeError, ValueError):
            return jsonify(ok=False, message="Datos inválidos."), 400
        product = get_db().execute(
            "SELECT id, stock FROM products WHERE id = ? AND active = 1", (product_id,)
        ).fetchone()
        if product is None:
            return jsonify(ok=False, message="Producto no disponible."), 404
        if quantity > product["stock"]:
            return jsonify(ok=False, message="La cantidad supera el inventario."), 409
        cart = get_cart()
        if quantity == 0:
            cart.pop(str(product_id), None)
        else:
            cart[str(product_id)] = quantity
        session["cart"] = cart
        session.modified = True
        return jsonify(ok=True, cart_count=sum(cart.values()))

    @app.route("/pagar", methods=("GET", "POST"))
    @login_required
    def checkout() -> str | Any:
        items, subtotal, shipping, total = cart_details()
        if not items:
            flash("El carrito está vacío.", "warning")
            return redirect(url_for("cart_page"))

        if request.method == "POST":
            db = get_db()
            try:
                db.execute("BEGIN IMMEDIATE")
                cart = get_cart()
                validated_items: list[tuple[sqlite3.Row, int]] = []
                product_subtotal = 0
                for product_id, quantity in cart.items():
                    product = db.execute(
                        "SELECT * FROM products WHERE id = ? AND active = 1", (int(product_id),)
                    ).fetchone()
                    if product is None:
                        raise ValueError("Uno de los productos ya no está disponible.")
                    if quantity > product["stock"]:
                        raise ValueError(
                            f"Stock insuficiente para {product['name']}. Disponible: {product['stock']}."
                        )
                    validated_items.append((product, quantity))
                    product_subtotal += product["price"] * quantity

                final_shipping = 0 if product_subtotal >= 250000 else 18000
                final_total = product_subtotal + final_shipping
                cursor = db.execute(
                    "INSERT INTO orders (user_id, total, status) VALUES (?, ?, 'pagado_prueba')",
                    (g.user["id"], final_total),
                )
                order_id = cursor.lastrowid

                for product, quantity in validated_items:
                    updated = db.execute(
                        "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?",
                        (quantity, product["id"], quantity),
                    )
                    if updated.rowcount != 1:
                        raise ValueError(f"El inventario de {product['name']} cambió. Intenta nuevamente.")
                    db.execute(
                        """
                        INSERT INTO order_items
                            (order_id, product_id, product_name, unit_price, quantity)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (order_id, product["id"], product["name"], product["price"], quantity),
                    )
                db.commit()
            except (sqlite3.Error, ValueError) as exc:
                db.rollback()
                flash(str(exc), "danger")
                return redirect(url_for("cart_page"))

            session["cart"] = {}
            flash(f"Pago de prueba aprobado. Pedido #{order_id} creado.", "success")
            return redirect(url_for("orders"))

        return render_template(
            "checkout.html", items=items, subtotal=subtotal, shipping=shipping, total=total
        )

    @app.route("/mis-pedidos")
    @login_required
    def orders() -> str:
        db = get_db()
        order_rows = db.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (g.user["id"],)
        ).fetchall()
        order_data = []
        for order in order_rows:
            lines = db.execute(
                "SELECT * FROM order_items WHERE order_id = ? ORDER BY id", (order["id"],)
            ).fetchall()
            order_data.append({"order": order, "items": lines})
        return render_template("orders.html", orders=order_data)

    @app.route("/admin")
    @admin_required
    def admin_dashboard() -> str:
        db = get_db()
        products = db.execute("SELECT * FROM products ORDER BY sport, name").fetchall()
        users = db.execute(
            "SELECT id, name, email, role, created_at FROM users ORDER BY id DESC"
        ).fetchall()
        orders_rows = db.execute(
            """
            SELECT orders.*, users.name AS customer_name, users.email AS customer_email
            FROM orders JOIN users ON users.id = orders.user_id
            ORDER BY orders.id DESC LIMIT 30
            """
        ).fetchall()
        stats = {
            "products": db.execute("SELECT COUNT(*) FROM products").fetchone()[0],
            "users": db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "orders": db.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
            "sales": db.execute("SELECT COALESCE(SUM(total), 0) FROM orders").fetchone()[0],
        }
        return render_template(
            "admin/dashboard.html",
            products=products,
            users=users,
            orders=orders_rows,
            stats=stats,
        )

    def save_uploaded_product_image(file_storage: Any) -> tuple[str | None, str | None]:
        if not file_storage or not file_storage.filename:
            return None, None
        if not allowed_image_file(file_storage.filename):
            return None, "Las imágenes deben ser JPG, JPEG, PNG o WebP."
        original = secure_filename(file_storage.filename)
        extension = original.rsplit(".", 1)[1].lower()
        filename = f"{secrets.token_hex(12)}.{extension}"
        file_storage.save(UPLOAD_DIR / filename)
        return url_for("static", filename=f"uploads/products/{filename}"), None

    def collect_product_images(existing_images: list[str] | None = None) -> tuple[list[str] | None, str | None]:
        existing_images = existing_images or []
        resolved: list[str] = []
        for position in range(1, 5):
            upload = request.files.get(f"image_file_{position}")
            typed_url = request.form.get(f"image_url_{position}", "").strip()
            current = existing_images[position - 1] if position <= len(existing_images) else ""
            if upload and upload.filename:
                saved_url, error = save_uploaded_product_image(upload)
                if error:
                    return None, error
                image_url = saved_url or ""
            elif typed_url:
                image_url = typed_url
            else:
                image_url = current
            if not image_url:
                return None, "Cada producto debe tener cuatro imágenes. Completa los cuatro espacios."
            resolved.append(image_url)
        return resolved, None

    def replace_product_images(db: sqlite3.Connection, product_id: int, images: list[str]) -> None:
        db.execute("DELETE FROM product_images WHERE product_id = ?", (product_id,))
        db.executemany(
            "INSERT INTO product_images (product_id, image_url, position) VALUES (?, ?, ?)",
            [(product_id, image_url, position) for position, image_url in enumerate(images, 1)],
        )
        db.execute("UPDATE products SET image_url = ? WHERE id = ?", (images[0], product_id))

    @app.route("/admin/productos/nuevo", methods=("GET", "POST"))
    @admin_required
    def admin_product_new() -> str | Any:
        if request.method == "POST":
            product_data, error = validate_product_form(request.form)
            images, image_error = collect_product_images()
            error = error or image_error
            if error:
                flash(error, "danger")
            else:
                db = get_db()
                cursor = db.execute(
                    """
                    INSERT INTO products
                        (name, brand, sport, product_type, audience, description, price, stock, image_url, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (*product_data[:-1], images[0], product_data[-1]),
                )
                replace_product_images(db, int(cursor.lastrowid), images)
                db.commit()
                flash("Producto creado correctamente con cuatro imágenes.", "success")
                return redirect(url_for("admin_dashboard"))
        return render_template("admin/product_form.html", product=None, product_images=[])

    @app.route("/admin/productos/<int:product_id>/editar", methods=("GET", "POST"))
    @admin_required
    def admin_product_edit(product_id: int) -> str | Any:
        db = get_db()
        product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        if product is None:
            abort(404)
        image_rows = db.execute(
            "SELECT image_url FROM product_images WHERE product_id = ? ORDER BY position, id",
            (product_id,),
        ).fetchall()
        existing_images = [row["image_url"] for row in image_rows]
        if request.method == "POST":
            product_data, error = validate_product_form(request.form)
            images, image_error = collect_product_images(existing_images)
            error = error or image_error
            if error:
                flash(error, "danger")
            else:
                db.execute(
                    """
                    UPDATE products SET
                        name = ?, brand = ?, sport = ?, product_type = ?, audience = ?,
                        description = ?, price = ?, stock = ?, image_url = ?, active = ?
                    WHERE id = ?
                    """,
                    (*product_data[:-1], images[0], product_data[-1], product_id),
                )
                replace_product_images(db, product_id, images)
                db.commit()
                flash("Producto, stock e imágenes actualizados.", "success")
                return redirect(url_for("admin_dashboard"))
        return render_template(
            "admin/product_form.html", product=product, product_images=existing_images
        )

    @app.post("/admin/productos/<int:product_id>/stock")
    @admin_required
    def admin_product_stock(product_id: int) -> Any:
        try:
            stock = int(request.form.get("stock", ""))
        except ValueError:
            flash("El stock debe ser un número entero.", "danger")
            return redirect(url_for("admin_dashboard"))
        if stock < 0:
            flash("El stock no puede ser negativo.", "danger")
            return redirect(url_for("admin_dashboard"))
        db = get_db()
        updated = db.execute("UPDATE products SET stock = ? WHERE id = ?", (stock, product_id))
        if updated.rowcount != 1:
            abort(404)
        db.commit()
        flash(f"Stock del producto #{product_id} actualizado a {stock} unidades.", "success")
        return redirect(url_for("admin_dashboard"))

    def validate_product_form(form: Any) -> tuple[tuple[Any, ...] | None, str | None]:
        name = form.get("name", "").strip()
        brand = form.get("brand", "").strip()
        sport = form.get("sport", "").strip().lower()
        product_type = form.get("product_type", "").strip()
        audience = form.get("audience", "adulto").strip()
        description = form.get("description", "").strip()
        active = 1 if form.get("active") == "1" else 0
        try:
            price = int(form.get("price", "0"))
            stock = int(form.get("stock", "0"))
        except ValueError:
            return None, "Precio y stock deben ser números enteros."
        if not all((name, brand, product_type)):
            return None, "Nombre, marca y tipo son obligatorios."
        if sport not in {"tenis", "golf", "squash"}:
            return None, "Selecciona un deporte válido."
        if price < 0 or stock < 0:
            return None, "Precio y stock no pueden ser negativos."
        return (
            name,
            brand,
            sport,
            product_type,
            audience,
            description,
            price,
            stock,
            active,
        ), None

    @app.errorhandler(400)
    def bad_request(error: Any) -> tuple[str, int]:
        return render_template("error.html", code=400, message=str(error.description)), 400

    @app.errorhandler(403)
    def forbidden(_: Any) -> tuple[str, int]:
        return render_template("error.html", code=403, message="No tienes permiso para acceder."), 403

    @app.errorhandler(404)
    def not_found(_: Any) -> tuple[str, int]:
        return render_template("error.html", code=404, message="La página solicitada no existe."), 404

    with app.app_context():
        init_db(seed=True)
        admin_email = os.getenv("SPORTZONE_ADMIN_EMAIL", "").strip().lower()
        admin_password = os.getenv("SPORTZONE_ADMIN_PASSWORD", "")
        if admin_email and admin_password and len(admin_password) >= 8:
            db = get_db()
            existing = db.execute("SELECT id FROM users WHERE email = ?", (admin_email,)).fetchone()
            if not existing:
                db.execute(
                    "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'admin')",
                    ("Administrador", admin_email, generate_password_hash(admin_password)),
                )
                db.commit()

    return app


def format_cop(value: int) -> str:
    return "$" + f"{int(value):,}".replace(",", ".")


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
