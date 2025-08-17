

import Head from "next/head";
import { useState, useRef } from "react";

export default function Home() {
  const [activeTab, setActiveTab] = useState("Extraction");
  const [toast, setToast] = useState<string | null>(null);
  const videoRefs = Array.from({ length: 8 }, () => useRef<HTMLVideoElement>(null));
  const peerConnections = useRef<(RTCPeerConnection | null)[]>(Array(8).fill(null));

  async function connectToRover(cameraId: number) {
    setToast(`Connecting to rover camera ${cameraId + 1}...`);
    const pc = new window.RTCPeerConnection();
    pc.addTransceiver("video", { direction: "recvonly" });

    let connected = false;
    pc.ontrack = (event) => {
      if (videoRefs[cameraId].current) {
        videoRefs[cameraId].current.srcObject = event.streams[0];
        if (!connected) {
          setToast(`Connected to Camera ${cameraId + 1} via WebRTC`);
          connected = true;
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
      peerConnections.current[cameraId] = pc;
    } catch (err) {
      setToast(`Connection to Camera ${cameraId + 1} failed`);
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
            {activeTab === "Extraction" ? (
              <>
                <div className="rover-cameras-label">Cameras</div>
                <div className="rover-cameras-grid">
                  {[...Array(8)].map((_, i) => (
                    <div key={i} className="rover-camera" style={{ position: "relative" }}>
                      <button onClick={() => connectToRover(i)} style={{ position: "absolute", top: 8, right: 8, zIndex: 2 }}>
                        Connect
                      </button>
                      <video ref={videoRefs[i]} autoPlay playsInline style={{ width: "100%", height: "100%", background: "#000" }} />
                      <div style={{ position: "absolute", top: 8, left: 8, color: "#fff", fontWeight: "bold" }}>Camera{i+1}</div>
                    </div>
                  ))}
                </div>
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
              </>
            ) : (
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