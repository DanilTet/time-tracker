function getDomain(url) {
  if (!url || !url.startsWith("http")) {
    return null; // chrome://, новая вкладка, настройки и т.д.
  }
  try {
    return new URL(url).hostname;
  } catch (e) {
    return null;
  }
}

function sendTabStatus(tab) {
  if (!tab) return;

  const payload = {
    domain: getDomain(tab.url),
    audible: !!tab.audible
  };

  fetch("http://localhost:5500/update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }).catch(() => {
    // сервер на компе ещё не запущен то игнорируем
  });
}

chrome.tabs.onActivated.addListener((activeInfo) => {
  chrome.tabs.get(activeInfo.tabId, (tab) => {
    sendTabStatus(tab);
  });
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (tab.active && ("url" in changeInfo || "audible" in changeInfo)) {
    sendTabStatus(tab);
  }
});