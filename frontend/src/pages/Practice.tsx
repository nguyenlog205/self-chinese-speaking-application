import { useState, useRef } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import axios from "axios";

export default function Practice() {
  const { t } = useLanguage();
  const [text, setText] = useState("");
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [scoreResult, setScoreResult] = useState<any>(null);
  const [showWERInfo, setShowWERInfo] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const handleSpeak = async () => {
    if (!text.trim()) {
      alert(t("practice.alert.empty_text"));
      return;
    }
    setLoading(true);
    try {
      const res = await axios.get("http://localhost:8000/tts/synthesize/", {
        params: { text, speaker: "Vivian", bitrate: "192k" },
        responseType: "blob",
        timeout: 30000,
      });
      if (res.status === 200) {
        const url = URL.createObjectURL(res.data);
        setAudioUrl(url);
      } else {
        alert(t("practice.alert.server_error") + res.status);
      }
    } catch (err: any) {
      console.error("TTS error:", err);
      if (err.response) {
        const text = await err.response.text();
        alert(t("practice.alert.backend_error") + text);
      } else {
        alert(t("practice.alert.network_error") + err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/wav" });
        handleScore(blob);
        setIsRecording(false);
      };

      mediaRecorder.start();
      setIsRecording(true);

      setTimeout(() => {
        if (mediaRecorder.state === "recording") {
          mediaRecorder.stop();
        }
      }, 6000);
    } catch (err) {
      console.error(err);
      alert(t("practice.alert.mic_error"));
    }
  };

  const handleScore = async (blob: Blob) => {
    if (!text.trim()) {
      alert(t("practice.alert.empty_ref"));
      return;
    }

    try {
      const formData = new FormData();
      formData.append("audio", blob, "recording.wav");

      const res = await axios.post(
        "http://localhost:8000/pronunciation/score/",
        formData,
        {
          params: { reference_text: text },
          headers: { "Content-Type": "multipart/form-data" },
          timeout: 30000,
        }
      );
      setScoreResult(res.data);
    } catch (err) {
      console.error(err);
      alert(t("practice.alert.scoring_error"));
    }
  };

  const toggleWERInfo = () => setShowWERInfo(!showWERInfo);

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-primary mb-4">
        {t("practice.title")}
      </h2>

      <textarea
        className="w-full p-3 border rounded-lg bg-white dark:bg-gray-800 dark:border-gray-600 focus:ring-2 focus:ring-primary focus:outline-none"
        rows={5}
        placeholder={t("practice.text")}
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <div className="flex gap-3 mt-4 flex-wrap">
        <button
          onClick={handleSpeak}
          disabled={loading || !text.trim()}
          className="bg-primary text-white px-6 py-2 rounded-lg hover:bg-primary/90 disabled:opacity-50 transition"
        >
          {loading ? t("practice.generating") : t("practice.speak")}
        </button>

        <button
          onClick={startRecording}
          disabled={isRecording || !text.trim()}
          className={`px-6 py-2 rounded-lg text-white transition ${
            isRecording
              ? "bg-red-500"
              : "bg-blue-600 hover:bg-blue-700"
          } disabled:opacity-50`}
        >
          {isRecording ? t("practice.recording") : t("practice.record")}
        </button>
      </div>

      {audioUrl && (
        <div className="mt-4">
          <audio controls src={audioUrl} className="w-full" />
        </div>
      )}

      {scoreResult && (
        <div className="mt-4 p-4 bg-green-100 dark:bg-green-900/30 rounded-lg">
          <div className="flex justify-between items-center">
            <p className="font-bold">{t("practice.score")}: {scoreResult.score}/100</p>
            <div className="flex items-center gap-2">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                WER: {scoreResult.wer.toFixed(2)}
              </p>
              <button
                onClick={toggleWERInfo}
                className="text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                {showWERInfo ? "▾" : "▸"}
              </button>
            </div>
          </div>

          {showWERInfo && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              {t("practice.wer_explanation")}
            </p>
          )}

          <div className="mt-2 text-sm">
            <p><span className="font-medium">{t("practice.you_said")}:</span> {scoreResult.transcribed}</p>
            <p><span className="font-medium">{t("practice.reference")}:</span> {scoreResult.reference}</p>
            <p className="mt-1 italic">{scoreResult.feedback}</p>
          </div>
        </div>
      )}

      <div className="mt-6 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg text-sm text-gray-600 dark:text-gray-400">
        <p>{t("practice.instructions")}</p>
      </div>
    </div>
  );
}