// ============================================================
// USER DASHBOARD SCRIPT
// Fetch products and reservations from Flask backend
// ============================================================

// -----------------------------
// API ENDPOINTS
// -----------------------------
const PRODUCTS_API = "/api/products";
const RESERVATIONS_API = "/api/reservations";

// -----------------------------
// ELEMENTS
// -----------------------------
const productContainer = document.getElementById("productContainer");
const reservationContainer = document.getElementById("reservationContainer");

const searchBar = document.getElementById("searchBar");
const searchResBar = document.getElementById("searchResBar");

// ============================================================
// FETCH DATA FROM SERVER
// ============================================================
async function getProducts() {
  try {
    const res = await fetch(PRODUCTS_API);
    if (!res.ok) throw new Error("Failed to fetch products");
    return await res.json();
  } catch (err) {
    console.error(err);
    return [];
  }
}

async function getReservations() {
  try {
    const res = await fetch(RESERVATIONS_API);
    if (!res.ok) throw new Error("Failed to fetch reservations");
    return await res.json();
  } catch (err) {
    console.error(err);
    return [];
  }
}

// ============================================================
// DISPLAY PRODUCTS
// ============================================================
async function loadProducts() {
  if (!productContainer) return;

  const products = await getProducts();

  productContainer.innerHTML = "";

  products.forEach(p => {
    const card = document.createElement("div");
    card.className = "product-card view-only";

    card.innerHTML = `
      <img src="${p.image}">
      <h4>${p.name}</h4>
      <p>Price: ₱${p.price}</p>
      <p>Qty: ${p.qty}</p>
    `;

    productContainer.appendChild(card);
  });
}

// ============================================================
// DISPLAY RESERVATIONS
// ============================================================
async function loadReservations() {
  if (!reservationContainer) return;

  const reservations = await getReservations();

  reservationContainer.innerHTML = "";

  reservations.forEach(r => {
    const row = document.createElement("div");
    row.className = "reservation-card view-only";

    row.innerHTML = `
      <div class="res-info">
        <strong>${r.name}</strong> • ${r.number} • ${r.product} • Qty: ${r.qty} • ₱${r.price}
      </div>
      <div class="res-status">Status: ${r.status}</div>
    `;

    reservationContainer.appendChild(row);
  });
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
// RESERVATION SEARCH
// ============================================================
if (searchResBar) {
  searchResBar.addEventListener("input", () => {
    const query = searchResBar.value.toLowerCase();
    document.querySelectorAll(".reservation-card").forEach(row => {
      row.style.display = row.innerText.toLowerCase().includes(query) ? "flex" : "none";
    });
  });
}

// ============================================================
// AUTO REFRESH
// ============================================================
setInterval(() => {
  loadProducts();
  loadReservations();
}, 5000); // maybe 5s is enough

// ============================================================
// INITIAL LOAD
// ============================================================
loadProducts();
loadReservations();