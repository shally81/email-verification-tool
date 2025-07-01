function showAlert(elementId, type, message) {
  const el = document.getElementById(elementId);
  el.innerHTML = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>`;
}

// Single email verification
async function postJSON(url, data) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return await res.json();
}

document.getElementById("singleForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = e.target.email.value.trim();
  if (!email) return;
  const result = await postJSON("/verify", { email });
  showAlert("singleAlert", result.status ? "success" : "danger", result.message);
});

// Bulk verification
document.getElementById("bulkForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = e.target.file.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch("/bulk", {
    method: "POST",
    body: formData,
  });
  const data = await res.json();
  const table = document.getElementById("bulkTable");
  const tbody = table.querySelector("tbody");
  tbody.innerHTML = "";
  if (data.results) {
    table.classList.remove("d-none");
    data.results.forEach(row => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${row.email}</td><td>${row.status}</td><td>${row.message}</td>`;
      tbody.appendChild(tr);
    });
  }
});