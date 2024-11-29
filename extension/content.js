function displayTranscription({ text }) {
  let transcriptionBox = document.getElementById("transcription-box");
  if (!transcriptionBox) {
    transcriptionBox = document.createElement("div");
    transcriptionBox.id = "transcription-box";
    transcriptionBox.style.position = "absolute";
    transcriptionBox.style.bottom = "10px";
    transcriptionBox.style.left = "10px";
    transcriptionBox.style.backgroundColor = "rgba(0,0,0,0.7)";
    transcriptionBox.style.color = "white";
    transcriptionBox.style.padding = "10px";
    transcriptionBox.style.borderRadius = "5px";
    document.body.appendChild(transcriptionBox);
  }
  transcriptionBox.innerHTML = `<p>${text}</p>`;
}
