// Configuration
const SERVER_ADDRESS = "http://10.0.0.23:8080"; // Change this to your server's address

// Auto-start WebRTC connection when page loads
let pc = null;

// Connect to the webcam stream
async function connect() {
  const videoElement = document.getElementById('video');
  const spinner = document.getElementById('spinner');
  if (!videoElement) return;
  try {
    if (spinner) spinner.style.display = "flex";
      // Create peer connection
      // const config = {
      //     iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
      // };
      // pc = new RTCPeerConnection(config);
      pc = new RTCPeerConnection();
      
      // Handle incoming video stream
      pc.addEventListener('track', (event) => {
          if (event.track.kind === 'video') {
              videoElement.srcObject = event.streams[0];
          // Hide spinner when the first frame is received
                videoElement.onloadedmetadata = () => {
              if (spinner) spinner.style.display = "none";
        };
          }
      });
      
      // Create offer with video only
      const offer = await pc.createOffer({
          offerToReceiveVideo: true,
          offerToReceiveAudio: false
      });
      await pc.setLocalDescription(offer);
      
      // Send offer to server using the configured address
      const response = await fetch(`${SERVER_ADDRESS}/offer`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
              sdp: pc.localDescription.sdp,
              type: pc.localDescription.type
          })
      });
      
      // Apply server's answer
      const answer = await response.json();
      await pc.setRemoteDescription(answer);
  } catch (e) {
      console.error("Connection failed:", e);
      if (spinner) spinner.style.display = "none";
  }
}

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (pc) {
        pc.close();
        pc = null;
    }
});

// Start connection when page loads
let observer;
function monitorVideoElement() {
    const targetNode = document.body;
    const config = { childList: true, subtree: true };

    observer = new MutationObserver(() => {
        if (!document.getElementById("video") && pc) {
            console.log("Video element removed, closing WebRTC connection...");
            pc.close();
            pc = null;
            observer.disconnect();
        }
    });

    observer.observe(targetNode, config);
}

document.body.addEventListener('htmx:afterSwap', function () {
    if (document.getElementById("video")) {
        connect();
        monitorVideoElement();
    }
});

