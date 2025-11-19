const { RTCPeerConnection } = require('wrtc');

// When you receive an offer from a client:
async function handleOffer(clientId, message, ws) {
  const pc = new RTCPeerConnection();

  // Optionally, add media tracks here (e.g., from a file or camera)
  // pc.addTrack(...);

  await pc.setRemoteDescription(message);

  const answer = await pc.createAnswer();
  await pc.setLocalDescription(answer);

  // Send answer back to client
  ws.send(JSON.stringify({ type: 'answer', sdp: pc.localDescription.sdp }));

  // Handle ICE candidates
  pc.onicecandidate = ({ candidate }) => {
    if (candidate) {
      ws.send(JSON.stringify({ type: 'ice-candidate', candidate }));
    }
  };

  // Handle incoming media streams
  pc.ontrack = (event) => {
    // Process incoming media here
  };
}