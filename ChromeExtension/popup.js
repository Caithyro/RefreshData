const JSON_URL = ""; // URL to fetch JSON data
const PRIVATE_TOKEN = ""; // Private token for authentication

let data = [];

async function loadData() {
  try {
    const response = await fetch(JSON_URL, {
      headers: {
        "PRIVATE-TOKEN": PRIVATE_TOKEN
      }
    });
    if (!response.ok) throw new Error("HTTP " + response.status);

    const rawText = await response.text();
    data = JSON.parse(rawText);
  } catch (err) {
    console.error("Error loading data:", err);
    document.getElementById("result").textContent = "Помилка завантаження даних";
    document.getElementById("status").textContent = "";
  }
}

function searchDevices(term) {
  return data.filter(
    item => item.deviceId === term || item.controllerId === term
  );
}

document.getElementById("searchBtn").addEventListener("click", () => {
  const term = document.getElementById("searchInput").value.trim();
  const resultDiv = document.getElementById("result");
  const statusDiv = document.getElementById("status");

  resultDiv.innerHTML = "";
  statusDiv.textContent = "";

  if (!term) {
    resultDiv.textContent = "Введіть ID";
    return;
  }

  const matches = searchDevices(term);

  if (matches.length > 0) {
    matches.forEach((item, index) => {
      const container = document.createElement("div");
      container.style.marginBottom = "10px";
      container.style.borderBottom = "1px solid var(--border-color)";
      container.style.paddingBottom = "8px";

      const uuidEl = document.createElement("div");
      uuidEl.innerHTML = `ResultID: <strong>${item.uuid}</strong>`;

      const statusEl = document.createElement("div");
      statusEl.style.fontSize = "14px";
      statusEl.textContent = item.deleted
        ? "Статус: 🔴 Unavailable"
        : "Статус: 🟢 Active";

      const copyBtn = document.createElement("button");
      copyBtn.textContent = "Скопіювати ResultID";
      copyBtn.style.marginTop = "5px";
      copyBtn.onclick = () => {
        navigator.clipboard.writeText(item.uuid)
          .then(() => {
            copyBtn.textContent = "✅ Скопійовано!";
            setTimeout(() => {
              copyBtn.textContent = "Скопіювати ResultID";
            }, 2000);
          })
          .catch(err => {
            copyBtn.textContent = "❌ Помилка";
            console.error(err);
          });
      };

      container.appendChild(uuidEl);
      container.appendChild(statusEl);
      container.appendChild(copyBtn);
      resultDiv.appendChild(container);
    });
  } else {
    resultDiv.textContent = "Співпадінь не знайдено.";
  }
});

loadData();