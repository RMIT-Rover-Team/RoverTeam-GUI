import Head from "next/head";
import { useState, useRef, useEffect, createRef } from "react";

export default function Home() {
  // Adjust this to your rover's IP where the Python WebRTC server is running
  const ROVER_HOST = "192.168.50.1";

  const [activeTab, setActiveTab] = useState("Extraction");
  const [toast, setToast] = useState<string | null>(null);
  const [availableCameras, setAvailableCameras] = useState<
    { id: number; label: string }[]
  >([]);
  const [connectedCameras, setConnectedCameras] = useState<boolean[]>([]);
  const peerConnections = useRef<(RTCPeerConnection | null)[]>([]);
  const [videoRefs, setVideoRefs] = useState<React.RefObject<HTMLVideoElement>[]>([]);

  useEffect(() => {
    fetch(`http://${ROVER_HOST}:3001/cameras`)
      .then((res) => res.json())
      .then((data) => {
        if (data.cameras) {
          setAvailableCameras(data.cameras);
          setConnectedCameras(new Array(data.cameras.length).fill(false));
          setVideoRefs(data.cameras.map(() => createRef<HTMLVideoElement>()));
          peerConnections.current = new Array(data.cameras.length).fill(null);
        }
      })
      .catch(() => {
        setAvailableCameras([]);
        setConnectedCameras([]);
        setVideoRefs([]);
        peerConnections.current = [];
      });
  }, []);

  async function connectToRover(idx: number) {
    const cameraId = availableCameras[idx]?.id;
    if (cameraId === undefined) return;
    setToast(`Connecting to rover USB camera ${cameraId}...`);

    if (peerConnections.current[idx]) {
      setToast(`Camera ${cameraId} already connected`);
      setTimeout(() => setToast(null), 2000);
      return;
    }

    const pc = new window.RTCPeerConnection();
    pc.addTransceiver("video", { direction: "recvonly" });

    let connected = false;
    pc.ontrack = (event) => {
      const videoRef = videoRefs[idx];
      if (videoRef && videoRef.current) {
        // Attach the incoming MediaStream and start playback. Some browsers
        // require an explicit .play() call after setting srcObject.
        videoRef.current.srcObject = event.streams[0];
        // play() returns a promise; ignore or catch to avoid unhandled rejections
        const playPromise = videoRef.current.play();
        if (playPromise && typeof playPromise.then === "function") {
          playPromise.catch(() => {
            /* autoplay might be blocked; user interaction may be required */
          });
        }
        if (!connected) {
          setToast(`Connected to USB Camera ${cameraId} via WebRTC`);
          connected = true;
          setConnectedCameras((prev) => {
            const updated = [...prev];
            updated[idx] = true;
            return updated;
          });
          setTimeout(() => setToast(null), 3000);
        }
      }
    };

    try {
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      const response = await fetch(`http://${ROVER_HOST}:3001/offer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sdp: offer.sdp,
          type: offer.type,
          camera_id: cameraId,
        }),
      });
      const answer = await response.json();
      await pc.setRemoteDescription(new window.RTCSessionDescription(answer));
      peerConnections.current[idx] = pc;
    } catch (err) {
      setToast(`Connection to USB Camera ${cameraId} failed`);
      setTimeout(() => setToast(null), 3000);
    }
  }

  return (
    <>
      <Head>
        <title>Rover GUI</title>
      </Head>
      <div className="rover-bg">
        {toast && (
          <div
            style={{
              position: "fixed",
              top: 24,
              left: "50%",
              transform: "translateX(-50%)",
              background: "#222",
              color: "#fff",
              padding: "12px 32px",
              borderRadius: 8,
              boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
              zIndex: 9999,
              fontSize: 18,
            }}
          >
            {toast}
          </div>
        )}
        <div className="rover-layout">
          {/* ...sidebar, navbar etc... */}
          <div className="rover-main">
            <div style={{ display: activeTab === "Extraction" ? "block" : "none" }}>
              <div className="rover-cameras-label">USB Cameras</div>
              {/* Suppressed the 'No USB cameras detected' message per user request */}
              <div className="rover-cameras-grid">
                {availableCameras.map((cam, i) => (
                  <div key={cam.id} className="rover-camera" style={{ position: "relative" }}>
                    <button
                      onClick={() => connectToRover(i)}
                      style={{ position: "absolute", top: 8, right: 8, zIndex: 2 }}
                      disabled={connectedCameras[i]}
                    >
                      {connectedCameras[i] ? "Connected" : "Connect"}
                    </button>
                    <video
                      ref={videoRefs[i]}
                      autoPlay
                      playsInline
                      style={{ width: "100%", height: "100%", background: "#000" }}
                    />
                    <div
                      style={{
                        position: "absolute",
                        top: 8,
                        left: 8,
                        color: "#fff",
                        fontWeight: "bold",
                      }}
                    >
                      {cam.label}
                    </div>
                    <div style={{ position: "absolute", bottom: 8, left: 8, color: "#fff", fontSize: 12 }}>
                      Index: {cam.id}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          {/* right sidebar... */}
        </div>
      </div>
    </>
  );
}
