from flask import Flask, render_template_string, request, jsonify
import requests, json, re, time, random, base64, hashlib, subprocess, os, threading
from urllib.parse import urlparse

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Leak Scanner - Domain Credential Finder</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0a;font-family:'Courier New',monospace;color:#0f0;padding:20px}
.container{max-width:1400px;margin:0 auto}
.header{border-bottom:2px solid #0f0;padding:15px;margin-bottom:20px;text-align:center}
.header h1{font-size:24px}
.ascii{text-align:center;font-size:9px;margin-bottom:20px;color:#0a3}
.card{background:#0f0f0f;border:1px solid #0f0;border-radius:8px;padding:20px;margin-bottom:20px}
input{background:#0a0a0a;border:1px solid #0f0;color:#0f0;padding:12px;width:100%;font-family:monospace;font-size:14px}
button{background:#0a0a0a;border:1px solid #0f0;color:#0f0;padding:12px 24px;cursor:pointer;font-family:monospace;font-weight:bold;margin-top:10px}
button:hover{background:#0f0;color:#0a0a0a}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.result-item{background:#0a0a0a;border:1px solid #0a3;padding:10px;margin:8px 0;font-size:12px;word-break:break-all}
.result-item a{color:#0f0}
.status{color:#ff0;font-size:11px;margin-top:10px}
table{width:100%;border-collapse:collapse;font-size:11px}
th,td{border:1px solid #0f0;padding:8px;text-align:left}
th{background:#1a1a1a}
.footer{text-align:center;font-size:11px;margin-top:20px;padding-top:15px;border-top:1px solid #1a3a1a}
.blink{animation:blink 1s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}
.tab{display:flex;gap:5px;margin-bottom:20px;border-bottom:1px solid #0f0;flex-wrap:wrap}
.tab-btn{background:#0a0a0a;border:none;padding:10px 20px;cursor:pointer}
.tab-btn.active{background:#0f0;color:#0a0a0a}
.tab-content{display:none}
.tab-content.active{display:block}
.progress-bar{width:100%;background:#1a1a1a;height:20px;border-radius:10px;overflow:hidden;margin:10px 0}
.progress{background:#0f0;height:100%;width:0%;transition:width 0.3s}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>🔍 LEAK SCANNER - DOMAIN CREDENTIAL FINDER</h1>
</div>
<div class="ascii">
╔══════════════════════════════════════════════════════════════════════════════╗<br>
║   SIFIR API KEY - TAMAMEN UCRETSIZ - TUM KAYNAKLARI TARAR                    ║<br>
║   GitHub Leaks | Pastebin | Public Breaches | Google Dorks | Telegram       ║<br>
╚══════════════════════════════════════════════════════════════════════════════╝
</div>

<div class="tab">
<button class="tab-btn active" data-tab="scan">🎯 SCAN</button>
<button class="tab-btn" data-tab="results">📁 RESULTS</button>
</div>

<div id="scan" class="tab-content active">
<div class="card">
<h3>🌐 DOMAIN GIR</h3>
<input type="text" id="domain" placeholder="ornek.com" value="">
<div class="grid-2" style="margin-top:15px">
<div>
<h4>📡 AKTIF KAYNAKLAR:</h4>
<label><input type="checkbox" id="source_github" checked> GitHub Leaks</label><br>
<label><input type="checkbox" id="source_pastebin" checked> Pastebin</label><br>
<label><input type="checkbox" id="source_public" checked> Public Breaches</label><br>
<label><input type="checkbox" id="source_google" checked> Google Dorks</label><br>
<label><input type="checkbox" id="source_telegram" checked> Telegram Channels</label><br>
<label><input type="checkbox" id="source_gitrepo" checked> Git Repo Search</label><br>
</div>
<div>
<h4>⚙️ AYARLAR:</h4>
<label>Derin Tarama: <input type="checkbox" id="deepscan"></label><br>
<label>Timeout (saniye): <input type="number" id="timeout" value="30" style="width:80px"></label><br>
</div>
</div>
<button onclick="startScan()" style="width:100%">🔍 TARAMAYI BASLAT</button>
<div id="scanStatus" class="status"></div>
<div id="progressBar" class="progress-bar" style="display:none"><div id="progressFill" class="progress"></div></div>
</div>
</div>

<div id="results" class="tab-content">
<div class="card">
<h3>📁 BULUNAN LEAKLER</h3>
<button onclick="exportResults()">📤 JSON DISA AKTAR</button>
<button onclick="clearResults()" style="margin-left:10px">🗑️ TEMIZLE</button>
<div id="resultsCount" class="status" style="margin-top:10px"></div>
<div id="resultsList"></div>
</div>
</div>

<div class="footer">
<span class="blink">●</span> LEAK SCANNER v3.0 | 0 API KEY | TUM KAYNAKLAR UCRETSIZ
</div>
</div>

<script>
let results = [];
let scanning = false;

// Tab
document.querySelectorAll('.tab-btn').forEach(btn => {
btn.addEventListener('click', () => {
document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
btn.classList.add('active');
document.getElementById(btn.dataset.tab).classList.add('active');
if (btn.dataset.tab === 'results') displayResults();
});
});

async function startScan() {
if (scanning) { alert('Zaten tarama yapiliyor!'); return; }
const domain = document.getElementById('domain').value.trim();
if (!domain) { alert('Domain girin!'); return; }

scanning = true;
results = [];
document.getElementById('scanStatus').innerHTML = '⏳ Tarama baslatiliyor...';
document.getElementById('progressBar').style.display = 'block';
updateProgress(0);

const sources = [];
if (document.getElementById('source_github').checked) sources.push('github');
if (document.getElementById('source_pastebin').checked) sources.push('pastebin');
if (document.getElementById('source_public').checked) sources.push('public');
if (document.getElementById('source_google').checked) sources.push('google');
if (document.getElementById('source_telegram').checked) sources.push('telegram');
if (document.getElementById('source_gitrepo').checked) sources.push('gitrepo');

const timeout = document.getElementById('timeout').value;
let completed = 0;

for (let i = 0; i < sources.length; i++) {
const source = sources[i];
updateProgress((i / sources.length) * 100);
document.getElementById('scanStatus').innerHTML = `⏳ Taraniyor: ${source.toUpperCase()} (${i+1}/${sources.length})`;

try {
let response;
if (source === 'github') response = await scanGitHub(domain, timeout);
else if (source === 'pastebin') response = await scanPastebin(domain, timeout);
else if (source === 'public') response = await scanPublicBreaches(domain, timeout);
else if (source === 'google') response = await scanGoogle(domain, timeout);
else if (source === 'telegram') response = await scanTelegram(domain, timeout);
else if (source === 'gitrepo') response = await scanGitRepo(domain, timeout);

if (response && response.results) {
results.push(...response.results);
}
} catch(e) { console.error(source + ' error:', e); }
completed++;
}

updateProgress(100);
document.getElementById('scanStatus').innerHTML = `✅ Tarama tamamlandi! Toplam ${results.length} leak bulundu.`;
displayResults();
scanning = false;
setTimeout(() => { document.getElementById('progressBar').style.display = 'none'; }, 2000);
}

function updateProgress(percent) {
document.getElementById('progressFill').style.width = percent + '%';
}

// ==================== KAYNAK TARAYICILAR ====================

async function scanGitHub(domain, timeout) {
const results = [];
try {
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), timeout * 1000);
const response = await fetch(`https://api.github.com/search/code?q=${domain}+password`, {
signal: controller.signal,
headers: { 'Accept': 'application/vnd.github.v3+json' }
});
clearTimeout(timeoutId);
if (response.ok) {
const data = await response.json();
if (data.items) {
for (const item of data.items.slice(0, 20)) {
results.push({
source: 'GitHub',
type: 'Code Leak',
data: `Repository: ${item.repository.full_name}<br>File: ${item.path}<br>URL: <a href="${item.html_url}" target="_blank">Link</a>`,
raw: `${item.repository.full_name}/${item.path}`
});
}
}
}
} catch(e) {}
return { results: results };
}

async function scanPastebin(domain, timeout) {
const results = [];
try {
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), timeout * 1000);
const response = await fetch(`https://psbdmp.ws/api/search/${domain}`, {
signal: controller.signal
});
clearTimeout(timeoutId);
if (response.ok) {
const data = await response.json();
if (Array.isArray(data)) {
for (const item of data.slice(0, 30)) {
results.push({
source: 'Pastebin',
type: 'Paste Leak',
data: `ID: ${item.id}<br>Title: ${item.title || 'No title'}<br>URL: <a href="https://pastebin.com/${item.id}" target="_blank">Link</a>`,
raw: item.id
});
}
}
}
} catch(e) {}
return { results: results };
}

async function scanPublicBreaches(domain, timeout) {
const results = [];
const services = [
`https://leak-lookup.com/api/search?query=${domain}`,
`https://leakcheck.net/api/public?query=${domain}`,
`https://breachdirectory.org/trespass?domain=${domain}`
];
for (const service of services) {
try {
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 5000);
const response = await fetch(service, { signal: controller.signal });
clearTimeout(timeoutId);
if (response.ok) {
const data = await response.json();
results.push({
source: 'Public Breach',
type: 'Credential',
data: JSON.stringify(data).substring(0, 500),
raw: JSON.stringify(data)
});
}
} catch(e) {}
}
return { results: results };
}

async function scanGoogle(domain, timeout) {
const results = [];
const dorks = [
`site:${domain} filetype:env`,
`site:${domain} filetype:sql`,
`site:${domain} password`,
`site:${domain} api_key`,
`site:${domain} secret_key`,
`site:${domain} wp-config`,
`site:${domain} .git/config`,
`intitle:index.of ${domain}`,
`site:${domain} inurl:admin`,
`site:${domain} inurl:api`
];
for (const dork of dorks) {
const googleUrl = `https://www.google.com/search?q=${encodeURIComponent(dork)}`;
results.push({
source: 'Google Dork',
type: 'Search Query',
data: `${dork}<br><a href="${googleUrl}" target="_blank">Google\'da Ara</a>`,
raw: dork
});
await new Promise(r => setTimeout(r, 200));
}
return { results: results };
}

async function scanTelegram(domain, timeout) {
const results = [];
const telegramChannels = [
'https://raw.githubusercontent.com/TelegramLeaks/leaks/main/leaks.json',
'https://raw.githubusercontent.com/xHak9x/TelegramScraper/main/data.json'
];
for (const channel of telegramChannels) {
try {
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 8000);
const response = await fetch(channel, { signal: controller.signal });
clearTimeout(timeoutId);
if (response.ok) {
const data = await response.text();
if (data.toLowerCase().includes(domain.toLowerCase())) {
results.push({
source: 'Telegram',
type: 'Channel Leak',
data: `Leak found in: ${channel}<br>Contains domain: ${domain}`,
raw: channel
});
}
}
} catch(e) {}
}
return { results: results };
}

async function scanGitRepo(domain, timeout) {
const results = [];
try {
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), timeout * 1000);
const response = await fetch(`https://api.github.com/search/repositories?q=${domain}`, {
signal: controller.signal,
headers: { 'Accept': 'application/vnd.github.v3+json' }
});
clearTimeout(timeoutId);
if (response.ok) {
const data = await response.json();
if (data.items) {
for (const item of data.items.slice(0, 15)) {
results.push({
source: 'Git Repo',
type: 'Repository',
data: `Repo: <a href="${item.html_url}" target="_blank">${item.full_name}</a><br>Stars: ${item.stargazers_count}<br>Description: ${item.description || 'No description'}`,
raw: item.full_name
});
}
}
}
} catch(e) {}
return { results: results };
}

function displayResults() {
const container = document.getElementById('resultsList');
const countSpan = document.getElementById('resultsCount');
countSpan.innerHTML = `Toplam ${results.length} leak bulundu`;

if (results.length === 0) {
container.innerHTML = '<div class="status">Henüz leak bulunamadi. Tarama yapin.</div>';
return;
}

let html = '<table><thead><tr><th>Kaynak</th><th>Tip</th><th>Veri</th></tr></thead><tbody>';
results.forEach(r => {
html += `<tr>
<td style="color:#0f0">${r.source}</td>
<td style="color:#ff0">${r.type}</td>
<td>${r.data}</td>
</tr>`;
});
html += '</tbody></table>';
container.innerHTML = html;
}

function exportResults() {
const dataStr = JSON.stringify(results, null, 2);
const blob = new Blob([dataStr], {type: 'application/json'});
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = `leak_scan_${Date.now()}.json`;
a.click();
URL.revokeObjectURL(url);
}

function clearResults() {
results = [];
displayResults();
}
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)
