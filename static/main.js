// Helper to build Bootstrap alert
function showAlert(elementId, type, message) {
  const el = document.getElementById(elementId);
  el.innerHTML = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>`;
}

// Single email verification
document.getElementById("singleForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = e.target.email.value.trim();
  if (!email) return;
  const res = await fetch("/verify", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ email })
  });
  const data = await res.json();
  showAlert("singleAlert", data.status ? "success" : "danger", data.message);
});

// Bulk verification
document.getElementById("bulkForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const res = await fetch("/bulk", { method: "POST", body: form });
  const data = await res.json();

  const table = document.getElementById("bulkTable");
  const tbody = table.querySelector("tbody");
  tbody.innerHTML = "";

  (data.results || []).forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${row.email}</td><td>${row.status ? "✅" : "❌"}</td><td>${row.message}</td>`;
    tbody.appendChild(tr);
  });

  table.classList.remove("d-none");
});