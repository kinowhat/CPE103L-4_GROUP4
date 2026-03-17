// ============================================================
// FRONTEND SCRIPT (ADMIN) - FLASK + SQL READY SANA
// ============================================================

// -----------------------------
// DATA
// -----------------------------
let useBackend = false;
let products = JSON.parse(localStorage.getItem("products") || "[]");
let reservations = JSON.parse(localStorage.getItem("reservations") || "[]");
let imageData = "";

// -----------------------------
// SAVE LOCAL DATA
// -----------------------------
function saveProducts() {
  localStorage.setItem("products", JSON.stringify(products));
}

function saveReservations() {
  localStorage.setItem("reservations", JSON.stringify(reservations));
}

// -----------------------------
// ELEMENTS
// -----------------------------
const productContainer = document.getElementById("productContainer");
const reservationContainer = document.getElementById("reservationContainer");

const searchBar = document.getElementById("searchBar");
const searchResBar = document.getElementById("searchResBar");

const addProductBtn = document.getElementById("addProductBtn");
const popup = document.getElementById("popup");
const cancelBtn = document.getElementById("cancelBtn");
const saveBtn = document.getElementById("saveBtn");

const productName = document.getElementById("productName");
const productPrice = document.getElementById("productPrice");
const productQty = document.getElementById("productQty");
const productImage = document.getElementById("productImage");

const addReserveBtn = document.getElementById("addReserveBtn");
const reservePopup = document.getElementById("reservePopup");
const cancelReserveBtn = document.getElementById("cancelReserveBtn");
const saveReserveBtn = document.getElementById("saveReserveBtn");

const studentName = document.getElementById("studentName");
const studentNumber = document.getElementById("studentNumber");
const reserveProduct = document.getElementById("reserveProduct");
const reserveQty = document.getElementById("reserveQty");
const reservePrice = document.getElementById("reservePrice");

const resDetailsPopup = document.getElementById("resDetailsPopup");
const resDetailsName = document.getElementById("resDetailsName");
const closeResDetails = document.getElementById("closeResDetails");

// -----------------------------
// CHECK BACKEND
// -----------------------------
async function checkBackend() {
  try {
    const res = await fetch("/api/products");
    useBackend = res.ok;
  } catch {
    useBackend = false;
  }
}

// ============================================================
// LOAD PRODUCTS
// ============================================================
async function loadProducts() {
  if (!productContainer) return;

  productContainer.innerHTML = "";

  if (useBackend) {
    try {
      const res = await fetch("/api/products");
      products = await res.json();
    } catch {
      useBackend = false;
    }
  }

  products.forEach((p, index) => {
    const card = document.createElement("div");
    card.className = "product-card";

    card.innerHTML = `
      <button class="delete-btn">×</button>
      <img src="${p.image}">
      <h4>${p.name}</h4>
      <p>Price: ₱${p.price}</p>
      <p>Qty: ${p.qty}</p>
    `;

    card.querySelector(".delete-btn").onclick = async () => {
      if (useBackend) {
        await fetch(`/api/products/${p.id}`, { method: "DELETE" });
      }
      products.splice(index, 1);
      saveProducts();
      loadProducts();
    };

    productContainer.appendChild(card);
  });
}

// ============================================================
// ADD PRODUCT
// ============================================================
if (addProductBtn) addProductBtn.onclick = () => popup.classList.remove("hidden");
if (cancelBtn) cancelBtn.onclick = () => popup.classList.add("hidden");

if (productImage) {
  productImage.addEventListener("change", function () {
    const reader = new FileReader();
    reader.onload = () => (imageData = reader.result);
    reader.readAsDataURL(this.files[0]);
  });
}

if (saveBtn) {
  saveBtn.onclick = async () => {
    const name = productName.value.trim();
    const price = Number(productPrice.value);
    const qty = Number(productQty.value);

    if (!name || !price || !qty || !imageData) return alert("Fill all fields.");

    if (useBackend) {
      await fetch("/api/products", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, price, qty, image: imageData }),
      });
    } else {
      products.push({ id: Date.now(), name, price, qty, image: imageData });
      saveProducts();
    }

    popup.classList.add("hidden");
    productName.value = productPrice.value = productQty.value = productImage.value = "";
    imageData = "";
    loadProducts();
  };
}

// ============================================================
// PRODUCT SEARCH
// ============================================================
if (searchBar) {
  searchBar.addEventListener("input", () => {
    const query = searchBar.value.toLowerCase();
    document.querySelectorAll(".product-card").forEach(card => {
      const name = card.querySelector("h4").textContent.toLowerCase();
      card.style.display = name.includes(query) ? "flex" : "none";
    });
  });
}

// ============================================================
// ADD RESERVATION
// ============================================================
if (addReserveBtn) addReserveBtn.onclick = () => reservePopup.classList.remove("hidden");
if (cancelReserveBtn) cancelReserveBtn.onclick = () => reservePopup.classList.add("hidden");

if (saveReserveBtn) {
  saveReserveBtn.onclick = async () => {
    const name = studentName.value.trim();
    const number = studentNumber.value.trim();
    const productNameValue = reserveProduct.value.trim();
    const qty = Number(reserveQty.value);
    const price = Number(reservePrice.value);

    if (!name || !number || !productNameValue || !qty || !price)
      return alert("Fill all fields.");

    const product = products.find(p => p.name.toLowerCase() === productNameValue.toLowerCase());
    if (!product) return alert("Product not found!");
    if (product.qty < qty) return alert("Not enough stock!");

    product.qty -= qty;

    if (useBackend) {
      await fetch("/api/reservations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, number, product: productNameValue, qty, price, status: "ongoing" }),
      });
      await fetch(`/api/products/${product.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ qty: product.qty }),
      });
    } else {
      reservations.push({ id: Date.now(), name, number, product: productNameValue, qty, price, status: "ongoing" });
      saveReservations();
    }

    saveProducts();
    reservePopup.classList.add("hidden");
    studentName.value = studentNumber.value = reserveProduct.value = reserveQty.value = reservePrice.value = "";
    loadProducts();
    loadReservations();
  };
}

// ============================================================
// LOAD RESERVATIONS
// ============================================================
async function loadReservations() {
  if (!reservationContainer) return;
  reservationContainer.innerHTML = "";

  if (useBackend) {
    try {
      const res = await fetch("/api/reservations");
      reservations = await res.json();
    } catch {
      useBackend = false;
    }
  }

  reservations.forEach((r, index) => {
    const row = document.createElement("div");
    row.className = "reservation-card";

    row.innerHTML = `
      <div class="res-info">
        <strong>${r.name}</strong> • ${r.number} • ${r.product} • Qty: ${r.qty} • ₱${r.price}
      </div>
      <div class="res-status">Status: ${r.status}</div>
      <button class="delete-res-btn">×</button>
    `;

    row.querySelector(".delete-res-btn").onclick = async e => {
      e.stopPropagation();
      if (useBackend) await fetch(`/api/reservations/${r.id}`, { method: "DELETE" });
      reservations.splice(index, 1);
      saveReservations();
      loadReservations();
    };

    row.onclick = () => openStatusPopup(r);
    reservationContainer.appendChild(row);
  });
}

// ============================================================
// STATUS POPUP
// ============================================================
function openStatusPopup(r) {
  resDetailsName.textContent = r.name;
  resDetailsPopup.classList.remove("hidden");

  document.querySelectorAll(".status-btn").forEach(btn => {
    btn.onclick = async () => {
      r.status = btn.dataset.status;
      if (useBackend) {
        await fetch(`/api/reservations/${r.id}/status`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status: r.status }),
        });
      }
      saveReservations();
      resDetailsPopup.classList.add("hidden");
      loadReservations();
    };
  });
}

if (closeResDetails) closeResDetails.onclick = () => resDetailsPopup.classList.add("hidden");

function showSection(section) {

  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.classList.remove("active");
  });

  if (section === "products") {
    document.querySelector(".nav-btn:nth-child(1)").classList.add("active");
  } else {
    document.querySelector(".nav-btn:nth-child(2)").classList.add("active");
  }

  document.getElementById("products-section").classList.add("hidden");
  document.getElementById("reservations-section").classList.add("hidden");

  document.getElementById(section + "-section").classList.remove("hidden");
}


// ============================================================
// INITIAL LOAD
// ============================================================
checkBackend().then(() => {
  loadProducts();
  loadReservations();
});