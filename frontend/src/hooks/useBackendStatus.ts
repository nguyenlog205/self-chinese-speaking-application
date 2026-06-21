import { useState, useEffect } from "react";

export const useBackendStatus = () => {
  const [status, setStatus] = useState<"online" | "offline" | "checking">("checking");
  const [ping, setPing] = useState<number | null>(null);

  const checkStatus = async () => {
    const start = Date.now();
    try {
      const res = await fetch("http://localhost:8000/tts/speakers/", {
        method: "GET",
        signal: AbortSignal.timeout(3000),
      });
      if (res.ok) {
        setStatus("online");
        setPing(Date.now() - start);
      } else {
        setStatus("offline");
        setPing(null);
      }
    } catch {
      setStatus("offline");
      setPing(null);
    }
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return { status, ping, checkStatus };
};