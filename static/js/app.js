"use strict";

const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || "";

function showToast(message, type = "success") {
  const container = document.getElementById("toastContainer");
  if (!container) return;
  const toastElement = document.createElement("div");
  toastElement.className = `toast align-items-center text-bg-${type} border-0`;
  toastElement.setAttribute("role", "alert");
  toastElement.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${escapeHtml(message)}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>`;
  container.appendChild(toastElement);
  const toast = new bootstrap.Toast(toastElement, { delay: 2800 });
  toastElement.addEventListener("hidden.bs.toast", () => toastElement.remove());
  toast.show();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrfToken,
      "X-Requested-With": "XMLHttpRequest",
    },
    body: JSON.stringify(payload),
  });
  const data = await response.json().catch(() => ({ ok: false, message: "Respuesta inválida del servidor." }));
  if (!response.ok || !data.ok) throw new Error(data.message || "No fue posible completar la operación.");
  return data;
}

function updateCartCount(count) {
  const badge = document.getElementById("cartCount");
  if (badge) badge.textContent = String(count);
}

document.querySelectorAll(".add-cart-btn").forEach((button) => {
  button.addEventListener("click", async () => {
    const productId = Number(button.dataset.productId);
    const original = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    try {
      const data = await postJson("/api/carrito/agregar", { product_id: productId, quantity: 1 });
      updateCartCount(data.cart_count);
      button.innerHTML = '<i class="fa-solid fa-check"></i>';
      showToast(data.message);
    } catch (error) {
      showToast(error.message, "danger");
      button.innerHTML = original;
    } finally {
      window.setTimeout(() => {
        button.disabled = false;
        button.innerHTML = original;
      }, 900);
    }
  });
});

document.querySelectorAll(".quantity-btn").forEach((button) => {
  button.addEventListener("click", async () => {
    const row = button.closest("tr");
    const input = row?.querySelector(".quantity-input");
    if (!row || !input) return;
    const current = Number(input.value);
    const isIncrease = button.dataset.action === "increase";
    const stock = Number(button.dataset.stock || 9999);
    const next = isIncrease ? Math.min(current + 1, stock) : Math.max(current - 1, 0);
    try {
      const data = await postJson("/api/carrito/actualizar", {
        product_id: Number(button.dataset.productId),
        quantity: next,
      });
      updateCartCount(data.cart_count);
      window.location.reload();
    } catch (error) {
      showToast(error.message, "danger");
    }
  });
});

document.querySelectorAll(".remove-cart-btn").forEach((button) => {
  button.addEventListener("click", async () => {
    try {
      const data = await postJson("/api/carrito/actualizar", {
        product_id: Number(button.dataset.productId),
        quantity: 0,
      });
      updateCartCount(data.cart_count);
      window.location.reload();
    } catch (error) {
      showToast(error.message, "danger");
    }
  });
});

document.querySelectorAll(".password-toggle").forEach((button) => {
  button.addEventListener("click", () => {
    const input = document.getElementById(button.dataset.target);
    const icon = button.querySelector("i");
    if (!input || !icon) return;
    const reveal = input.type === "password";
    input.type = reveal ? "text" : "password";
    icon.className = reveal ? "fa-solid fa-eye-slash" : "fa-solid fa-eye";
  });
});

// Galería pública del producto.
document.querySelectorAll(".gallery-thumb").forEach((button) => {
  button.addEventListener("click", () => {
    const mainImage = document.getElementById("productMainImage");
    const nextImage = button.dataset.galleryImage;
    if (!mainImage || !nextImage) return;
    mainImage.src = nextImage;
    document.querySelectorAll(".gallery-thumb").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
  });
});

// Vista previa de URL en el formulario administrativo.
document.querySelectorAll(".image-url-input").forEach((input) => {
  input.addEventListener("input", () => {
    const preview = document.getElementById(input.dataset.preview);
    if (preview && input.value.trim()) preview.src = input.value.trim();
  });
});

// Vista previa de archivos locales antes de guardar.
document.querySelectorAll(".image-file-input").forEach((input) => {
  input.addEventListener("change", () => {
    const file = input.files?.[0];
    const preview = document.getElementById(input.dataset.preview);
    if (!file || !preview) return;
    if (!file.type.startsWith("image/")) {
      showToast("Selecciona un archivo de imagen válido.", "danger");
      input.value = "";
      return;
    }
    const reader = new FileReader();
    reader.addEventListener("load", () => { preview.src = String(reader.result); });
    reader.readAsDataURL(file);
  });
});
