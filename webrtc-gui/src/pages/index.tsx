
import Head from "next/head";
import { useState, useRef, useEffect } from "react";

export default function Home() {
  const [activeTab, setActiveTab] = useState("Extraction");
  const [toast, setToast] = useState<string | null>(null);
  // USB camera refs (support up to 2)
  const videoRef0 = useRef<HTMLVideoElement>(null);
  const videoRef1 = useRef<HTMLVideoElement>(null);
  const videoRefs = [videoRef0, videoRef1];
  const [availableCameras, setAvailableCameras] = useState<{id: number, label: string}[]>([]);
  const peerConnections = useRef<(RTCPeerConnection | null)[]>([null, null]);
  const [connectedCameras, setConnectedCameras] = useState<boolean[]>([false, false]);

  useEffect(() => {
    fetch("http://192.168.50.1:3001/cameras")
      .then(res => res.json())
      .then(data => {
        if (data.cameras) setAvailableCameras(data.cameras);
      })
      .catch(() => setAvailableCameras([]));
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
      if (videoRefs[idx].current) {
        videoRefs[idx].current.srcObject = event.streams[0];
        if (!connected) {
          setToast(`Connected to USB Camera ${cameraId} via WebRTC`);
          connected = true;
          setConnectedCameras(prev => {
            const updated = [...prev];
            updated[idx] = true;
            return updated;
          });
          setTimeout(() => setToast(null), 3000);
        }
      }
    };

    pc.onicecandidate = (event) => {
      // ICE candidate handling (optional for simple setup)
    };

    try {
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      const roverHost = "192.168.50.1";
      const response = await fetch(`http://${roverHost}:3001/offer`, {
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
          <div style={{
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
          }}>
            {toast}
          </div>
        )}
        <div className="rover-layout">
          {/* Sidebar */}
          <div className="rover-sidebar">
            <div className="rover-icon"><span>★</span></div>
            <div className="rover-icon"><span>▲</span></div>
            <div className="rover-icon"><span>●</span></div>
            <div className="rover-icon"><span>■</span></div>
          </div>
          {/* Main Content */}
          <div className="rover-main">
            {/* Navbar with tabs, left-aligned, no title or extra links */}
            <nav className="rover-navbar rover-navbar-left">
              <div className="rover-navbar-links">
                <a href="#" className="rover-navbar-link">Home</a>
                <a
                  href="#"
                  className={`rover-navbar-link rover-tab${activeTab === "Extraction" ? " rover-tab-active" : ""}`}
                  onClick={e => { e.preventDefault(); setActiveTab("Extraction"); }}
                  style={{ cursor: "pointer" }}
                >
                  Extraction
                </a>
                <a
                  href="#"
                  className={`rover-navbar-link rover-tab${activeTab === "Detection" ? " rover-tab-active" : ""}`}
                  onClick={e => { e.preventDefault(); setActiveTab("Detection"); }}
                  style={{ cursor: "pointer" }}
                >
                  Detection
                </a>
              </div>
            </nav>
            {/* Tab content below */}
            {/* Always render camera grid, but hide when not on Extraction tab */}
            <div style={{ display: activeTab === "Extraction" ? "block" : "none" }}>
              <div className="rover-cameras-label">USB Cameras</div>
              {availableCameras.length === 0 ? (
                <div style={{ color: '#fff', background: '#c00', padding: '16px', borderRadius: '8px', textAlign: 'center', margin: '24px 0' }}>
                  No USB cameras detected. Please check your connections and refresh.
                </div>
              ) : (
                <div className="rover-cameras-grid">
                  {availableCameras.map((cam, i) => (
                    <div key={cam.id} className="rover-camera" style={{ position: "relative" }}>
                      <button onClick={() => connectToRover(i)} style={{ position: "absolute", top: 8, right: 8, zIndex: 2 }} disabled={connectedCameras[i]}>
                        {connectedCameras[i] ? "Connected" : "Connect"}
                      </button>
                      <video ref={videoRefs[i]} autoPlay playsInline style={{ width: "100%", height: "100%", background: "#000" }} />
                      <div style={{ position: "absolute", top: 8, left: 8, color: "#fff", fontWeight: "bold" }}>{cam.label}</div>
                      <div style={{ position: "absolute", bottom: 8, left: 8, color: "#fff", fontSize: 12 }}>Index: {cam.id}</div>
                    </div>
                  ))}
                </div>
              )}
              <div className="rover-row">
                <div className="rover-section">
                  <div className="rover-section-title">Auger</div>
                  <div className="rover-control-group">
                    <div>Vertical Stepper</div>
                    <div className="rover-control"></div>
                  </div>
                  <div className="rover-control-group rover-motor-row">
                    <div>Motor Speed</div>
                    <div className="rover-control rover-motor"></div>
                    <div>Direction</div>
                    <div className="rover-control rover-direction"></div>
                  </div>
                </div>
                <div className="rover-section">
                  <div className="rover-section-title">Water Collection</div>
                  <div className="rover-control-group">
                    <div>Heatpad</div>
                    <div className="rover-control"></div>
                  </div>
                  <div className="rover-control-group">
                    <div>Peltier</div>
                    <div className="rover-control"></div>
                  </div>
                </div>
                <div className="rover-visualizer">Visualizer?</div>
              </div>
            </div>
            {/* Detection tab content */}
            {activeTab !== "Extraction" && (
              <>
                <div className="rover-cameras-label">Detection Tab Content</div>
                <div style={{ textAlign: "center", marginTop: 40, fontSize: 20 }}>
                  {/* Placeholder for detection tab UI */}
                  Detection controls and content go here.
                </div>
              </>
            )}
          </div>
          {/* Right Sidebar */}
          <div className="rover-rightbar">
            <div className="rover-clock">Clock</div>
            <div className="rover-temperatures">Temperatures</div>
          </div>
        </div>
      </div>
    </>
  );
}