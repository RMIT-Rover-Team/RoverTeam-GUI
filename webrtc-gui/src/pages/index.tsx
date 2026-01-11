import Cameras from "@/components/cameras";
import Detection from "@/components/detection";
import Extraction from "@/components/extraction";
import Navbar from "@/components/navbar";
import Head from "next/head";
import { useState, useRef, useEffect, createRef } from "react";

export default function Home() {
  // COMMENTED OUT WHILE WORKING ON UI

  // const [roverUrl, setRoverUrl] = useState("");
  // const [availableCameras, setAvailableCameras] = useState([]);
  // const [connectedCameras, setConnectedCameras] = useState([]);
  // const [toast, setToast] = useState(null);

  // const videoRefs = useRef([]);
  // const peerConnections = useRef([]);

  // useEffect(() => {
  //   // AUTOMATIC LAN DETECTION
  //   // If you visit http://192.168.1.50:3000, this sets the API to http://192.168.1.50:3001
  //   const hostname = typeof window !== "undefined" ? window.location.hostname : "localhost";
  //   const url = `http://${hostname}:3001`;
  //   setRoverUrl(url);

  //   // Fetch cameras from that dynamically detected URL
  //   fetch(`${url}/cameras`)
  //     .then((res) => res.json())
  //     .then((data) => {
  //       if (data.cameras) {
  //         setAvailableCameras(data.cameras);
  //         setConnectedCameras(new Array(data.cameras.length).fill(false));

  //         videoRefs.current = data.cameras.map(() => createRef());
  //         peerConnections.current = new Array(data.cameras.length).fill(null);

  //         // Auto-connect
  //         data.cameras.forEach((_, idx) => connectToCamera(idx, data.cameras[idx].id, url));
  //       }
  //     })
  //     .catch((err) => showToast(`Error connecting to rover at ${url}: ${err.message}`));

  //   return () => {
  //     peerConnections.current.forEach(pc => pc && pc.close());
  //   };
  // }, []);

  // const showToast = (msg) => {
  //   setToast(msg);
  //   setTimeout(() => setToast(null), 3000);
  // };

  // const connectToCamera = async (idx, cameraId, baseUrl) => {
  //   if (peerConnections.current[idx]) return;

  //   showToast(`Connecting Camera ${cameraId}...`);

  //   // LAN CONFIG: No ICE servers needed.
  //   // This defaults to Host Candidates (Local IP), which is perfect for LAN.
  //   const pc = new RTCPeerConnection({
  //       iceServers: []
  //   });

  //   pc.addTransceiver("video", { direction: "recvonly" });

  //   pc.ontrack = (event) => {
  //     const vid = videoRefs.current[idx]?.current;
  //     if (vid) {
  //       vid.srcObject = event.streams[0];
  //       vid.play().catch(e => console.warn("Autoplay blocked:", e));

  //       setConnectedCameras(prev => {
  //          const next = [...prev];
  //          next[idx] = true;
  //          return next;
  //       });
  //     }
  //   };

  //   peerConnections.current[idx] = pc;

  //   try {
  //     const offer = await pc.createOffer();
  //     await pc.setLocalDescription(offer);

  //     // Use the baseUrl passed in (ensures we don't rely on stale state)
  //     const res = await fetch(`${baseUrl}/offer`, {
  //       method: "POST",
  //       headers: { "Content-Type": "application/json" },
  //       body: JSON.stringify({
  //         sdp: offer.sdp,
  //         type: offer.type,
  //         camera_id: cameraId,
  //       }),
  //     });

  //     if (!res.ok) throw new Error(await res.text());

  //     const answer = await res.json();
  //     await pc.setRemoteDescription(answer);

  //     showToast(`Camera ${cameraId} Live`);

  //   } catch (err) {
  //     console.error(err);
  //     showToast(`Failed: ${err.message}`);
  //     // Clean up failed connection
  //     pc.close();
  //     peerConnections.current[idx] = null;
  //   }
  // };

  // return (
  //   <div style={{ background: "#111", minHeight: "100vh", color: "#fff", fontFamily: "sans-serif", padding: 20 }}>
  //     <Head>
  //       <title>Rover Feed</title>
  //     </Head>

  //     {toast && (
  //       <div style={{
  //         position: "fixed", top: 20, left: "50%", transform: "translate(-50%)",
  //         background: "#333", padding: "10px 20px", borderRadius: 8, zIndex: 100, boxShadow: "0 2px 10px rgba(0,0,0,0.5)"
  //       }}>
  //         {toast}
  //       </div>
  //     )}

  //     <h1>Rover Camera Feed</h1>
  //     <p style={{color: "#888", fontSize: "0.9rem"}}>Connected to Rover at: {roverUrl}</p>

  //     <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))", gap: 20 }}>
  //       {availableCameras.map((cam, i) => (
  //         <div key={cam.id} style={{ background: "#222", padding: 10, borderRadius: 8 }}>
  //           <div style={{ marginBottom: 5, fontWeight: "bold", display:"flex", justifyContent:"space-between" }}>
  //             <span>{cam.label}</span>
  //             <span style={{color: connectedCameras[i] ? "#4f4" : "#f44"}}>
  //               ● {connectedCameras[i] ? "LIVE" : "OFFLINE"}
  //             </span>
  //           </div>
  //           <div style={{ position: "relative", paddingTop: "75%", background: "#000" }}>
  //             <video
  //               ref={videoRefs.current[i]}
  //               autoPlay
  //               playsInline
  //               muted // Muted often helps autoplay work reliably
  //               style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", objectFit: "cover" }}
  //             />
  //           </div>
  //         </div>
  //       ))}
  //     </div>
  //   </div>
  // );

  const [currPage, setCurrPage] = useState("home"); //the current page navbar has showing, default home
  return (
    <div className="ml-28">
      <Navbar currPage={currPage} setCurrPage={setCurrPage} />

      <div className={currPage !== "home" ? "hidden" : "flex"}>
        <Cameras />
      </div>
      <div className={currPage !== "extraction" ? "hidden" : "flex"}>
        <Extraction />
      </div>
      <div className={currPage !== "detection" ? "hidden" : "flex"}>
        <Detection />
      </div>
    </div>
  );
}
