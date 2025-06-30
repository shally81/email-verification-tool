async function postJSON(url = "", data = {}) {
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return resp.json();
}

document.getElementById("singleForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = e.target.email.value;
  const res = await postJSON("/verify", { email });
  document.getElementById("singleResult").innerText = JSON.stringify(res, null, 2);
});

document.getElementById("bulkForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fileInput = e.target.file;
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  const resp = await fetch("/bulk", { method: "POST", body: formData });
  const data = await resp.json();
  document.getElementById("bulkResult").innerText = JSON.stringify(data, null, 2);
});