document.getElementById('verifyBtn').addEventListener('click', async () => {
  const email = document.getElementById('singleEmail').value.trim();
  if (!email) return alert('Please enter email');
  const res = await fetch('/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  const data = await res.json();
  document.getElementById('singleResult').innerText = `${data.email} → ${data.status}`;
});

document.getElementById('uploadBtn').addEventListener('click', async () => {
  const fileInput = document.getElementById('csvfile');
  if (!fileInput.files.length) return alert('Choose CSV file first!');
  const formData = new FormData();
  formData.append('csvfile', fileInput.files[0]);
  document.getElementById('bulkStatus').innerText = 'Uploading & verifying...';
  const res = await fetch('/upload', {
    method: 'POST',
    body: formData
  });
  const data = await res.json();
  document.getElementById('bulkStatus').innerHTML = `Done! <a href="${data.download}">Download results CSV</a>`;
  const tbody = document.querySelector('#bulkTable tbody');
  tbody.innerHTML = '';
  data.results.forEach(r => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${r.email}</td><td>${r.status}</td>`;
    tbody.appendChild(tr);
  });
});
