"use client";
import { useEffect, useState } from "react";

export default function Clock() {
  const [now, setNow] = useState(
    new Date().toLocaleTimeString("en-US", { hour12: false })
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setNow(new Date().toLocaleTimeString("en-US", { hour12: false }));
    }, 1000);
  }, []);

  return (
    <>
      <div className="GUI-HFlex p-4 text-center ">
        <text className="GUI-clock">{now}</text>;
      </div>
    </>
  );
}
