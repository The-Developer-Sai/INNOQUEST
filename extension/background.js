let stream;

chrome.action.onClicked.addListener(() => {
  chrome.tabCapture.capture({ audio: true, video: false }, (capturedStream) => {
    if (chrome.runtime.lastError) {
      console.error(chrome.runtime.lastError.message);
      return;
    }
    stream = capturedStream;
    console.log("Audio stream captured!");
    sendAudioToBackend(stream);
  });
});

function sendAudioToBackend(audioStream) {
  const audioContext = new AudioContext();
  const source = audioContext.createMediaStreamSource(audioStream);
  const processor = audioContext.createScriptProcessor(4096, 1, 1);

  processor.onaudioprocess = (event) => {
    const audioData = event.inputBuffer.getChannelData(0);
    const int16Array = new Int16Array(audioData.map((x) => x * 32767)); // Convert float to 16-bit PCM
    fetch("http://localhost:5000/transcribe", {
      method: "POST",
      body: JSON.stringify({ audio: Array.from(int16Array) })
    }).then(response => response.json()).then(data => console.log(data));
  };

  source.connect(processor);
  processor.connect(audioContext.destination);
}
