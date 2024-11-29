document.getElementById("start").addEventListener("click", () => {
  const language = document.getElementById("language").value;
  chrome.runtime.sendMessage({ action: "startTranscription", language });
});
