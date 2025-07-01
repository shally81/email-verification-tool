require('dotenv').config();
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const multer = require('multer');
const csv = require('csv-parser');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

const upload = multer({ dest: 'uploads/' });

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function verifyEmailLocal(email) {
  return emailRegex.test(email) ? 'valid-ish (regex only)' : 'invalid';
}

if (!fs.existsSync('results')) {
  fs.mkdirSync('results');
}

app.post('/verify', (req, res) => {
  const { email } = req.body;
  if(!email){ return res.status(400).json({error: 'Email missing'}); }
  const status = verifyEmailLocal(email);
  res.json({ email, status });
});

app.post('/upload', upload.single('csvfile'), (req, res) => {
  const resultsArr = [];
  fs.createReadStream(req.file.path)
    .pipe(csv())
    .on('data', (data) => {
      // Assume email column is named 'email' or take first column
      const email = data.email || Object.values(data)[0];
      const status = verifyEmailLocal(email);
      resultsArr.push({ email, status });
    })
    .on('end', () => {
      // create CSV of results
      const filename = `result_${Date.now()}.csv`;
      const filepath = path.join(__dirname, 'results', filename);
      const header = 'email,status\n';
      const fileContent = header + resultsArr.map(r => `${r.email},${r.status}`).join('\n');
      fs.writeFileSync(filepath, fileContent);
      fs.unlinkSync(req.file.path); // cleanup upload
      res.json({ results: resultsArr, download: `/download/${filename}` });
    });
});

app.get('/download/:file', (req, res) => {
  const filePath = path.join(__dirname, 'results', req.params.file);
  res.download(filePath);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
