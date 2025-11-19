import { useEffect, useState, useRef, createRef } from "react";
import Head from "next/head";

export default function Home() {
  const ROVER_HOST = "192.168.50.1";

  const [cams, setCams] = useState<{ id: number; label: string }[]>([]);
  const [connections, setConnections] = useState<(RTCPeerConnection | null)[]>([]);
  const [videorefs, setVideorefs] = useState<React.RefObject<HTMLVideoElement>[]>([]);

  // ---------------------------------------
  // Load camera list once
  // ---------------------------------------
  useEffect(() => {
    fetch(`http://${ROVER_HOST}:3001/cameras`)
      .then((res) => res.json())
      .then((data) => {
        if (data.cameras) {
          setCams(data.cameras);
          setConnections(new Array(data.cameras.length).fill(null));
          setVideorefs(data.cameras.map(() => createRef<HTMLVideoElement>()));
        }
      });
  }, []);

  // ---------------------------------------
  // Auto-connect once cameras + refs are ready
  // ---------------------------------------
  useEffect(() => {
    if (cams.length === 0 || videorefs.length === 0) return;

    cams.forEach((cam, idx) => {
      connect(idx);
    });
  }, [cams, videorefs]);

  // ---------------------------------------
  // WebRTC connect function
  // ---------------------------------------
  async function connect(idx: number) {
    const cam = cams[idx];
    if (!cam) return;

    const pc = new RTCPeerConnection();
    connections[idx] = pc;

    pc.addTransceiver("video", { direction: "recvonly" });

    pc.ontrack = (ev) => {
      const video = videorefs[idx].current;
      if (!video) return;

      video.srcObject = ev.streams[0];
      video.play().catch(() => {});
    };

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    const ans = await fetch(`http://${ROVER_HOST}:3001/offer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sdp: offer.sdp,
        type: offer.type,
        camera_id: cam.id,
      }),
    });

    const ans_json = await ans.json();
    await pc.setRemoteDescription(ans_json);
  }

  // ---------------------------------------
  // UI
  // ---------------------------------------
  return (
    <>
      <Head><title>USB Cameras</title></Head>
      <h1>USB Cameras</h1>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20 }}>
        {cams.map((cam, i) => (
          <div key={cam.id}
            style={{ width: 320, height: 240, background: "#111", position: "relative" }}
          >
            <video
              ref={videorefs[i]}
              autoPlay
              playsInline
              style={{ width: "100%", height: "100%" }}
            />
            <div style={{
              position: "absolute", top: 8, left: 8,
              color: "#fff", background: "#0008", padding: "4px 6px",
              borderRadius: 4
            }}>
              {cam.label}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
