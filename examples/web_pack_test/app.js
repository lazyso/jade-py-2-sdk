const logEl = document.querySelector("#log");
const assetInfoEl = document.querySelector("#asset-info");

function writeLog(type, msg) {
  const t = new Date().toLocaleTimeString("zh-CN", { hour12: false });
  const span = document.createElement("span");
  span.innerHTML = `<span style="color:#6c7086">[${t}]</span> <span style="color:${type === 'error' ? '#f38ba8' : type === 'event' ? '#89b4fa' : '#a6e3a1'}">${msg}</span>\n`;
  logEl.appendChild(span);
  logEl.scrollTop = logEl.scrollHeight;
}

function formatResult(value) {
  if (value == null) return String(value);
  if (typeof value === "string") {
    try { return JSON.stringify(JSON.parse(value), null, 2); } catch { return value; }
  }
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

async function loadAssetInfo() {
  const resp = await fetch("./assets/info.json");
  const data = await resp.json();
  assetInfoEl.textContent = JSON.stringify(data, null, 2);
}

async function invoke(channel, payload) {
  if (!window.jade?.invoke) {
    throw new Error("当前页面没有检测到 jade.invoke，通常表示没有通过 JadeView 载入。");
  }
  return window.jade.invoke(channel, payload);
}

document.querySelector("#ping-btn").addEventListener("click", async () => {
  try {
    const result = await invoke("pack:ping", JSON.stringify({ source: "web_pack_test" }));
    writeLog("data", `IPC 成功: ${formatResult(result)}`);
  } catch (error) {
    writeLog("error", `IPC 失败: ${error.message}`);
  }
});

document.querySelector("#info-btn").addEventListener("click", async () => {
  try {
    const result = await invoke("pack:info", "");
    assetInfoEl.textContent = formatResult(result);
    writeLog("data", `资源信息已更新`);
  } catch (error) {
    writeLog("error", `读取失败: ${error.message}`);
  }
});

document.querySelector("#choose-btn").addEventListener("click", async () => {
  try {
    const result = await invoke("pack:choose-japk", "");
    assetInfoEl.textContent = formatResult(result);
    writeLog("event", `已切换 JAPK: ${formatResult(result)}`);
  } catch (error) {
    writeLog("error", `选择失败: ${error.message}`);
  }
});

document.querySelector("#reset-btn").addEventListener("click", async () => {
  try {
    const result = await invoke("pack:reset-source", "");
    assetInfoEl.textContent = formatResult(result);
    writeLog("event", `已切回目录模式`);
  } catch (error) {
    writeLog("error", `切回失败: ${error.message}`);
  }
});

loadAssetInfo()
  .then(() => writeLog("data", "页面资源加载完成，可以开始测试"))
  .catch((error) => {
    assetInfoEl.textContent = error.message;
    writeLog("error", `资源加载失败: ${error.message}`);
  });
