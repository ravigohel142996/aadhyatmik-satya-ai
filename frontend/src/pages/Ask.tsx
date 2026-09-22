import { FormEvent, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { ask, type Answer } from "../api";
import AnswerCard from "../components/AnswerCard";

const STAGES = [
  "Searching Aadhyatmik Satya…",
  "Finding relevant pages…",
  "Analyzing source…",
  "Preparing grounded response…",
];

type Turn = { question: string; answer?: Answer; error?: string };

export default function Ask() {
  const [params] = useSearchParams();
  const [q, setQ] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [busy, setBusy] = useState(false);
  const [stage, setStage] = useState(0);

  useEffect(() => {
    const initial = params.get("q");
    if (initial) {
      setQ(initial);
      void submit(initial);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params]);

  useEffect(() => {
    if (!busy) return;
    setStage(0);
    const id = window.setInterval(() => setStage((s) => Math.min(s + 1, STAGES.length - 1)), 700);
    return () => window.clearInterval(id);
  }, [busy]);

  async function submit(question: string) {
    const text = question.trim();
    if (!text || busy) return;
    setBusy(true);
    setTurns((t) => [...t, { question: text }]);
    try {
      const answer = await ask(text);
      setTurns((t) => t.map((turn, i) => (i === t.length - 1 ? { ...turn, answer } : turn)));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Request failed";
      setTurns((t) => t.map((turn, i) => (i === t.length - 1 ? { ...turn, error: message } : turn)));
    } finally {
      setBusy(false);
      setQ("");
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    void submit(q);
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <p className="kicker">Ask</p>
      <h1 className="mt-2 font-dev text-4xl text-maroon">अपना प्रश्न ग्रंथ के पास लाएँ</h1>
      <p className="mt-2 text-[#5c4e43]">Hindi, English, Gujarati, Hinglish — the quotation stays in the granth’s language.</p>
      <form onSubmit={onSubmit} className="mt-6 flex flex-col gap-3 sm:flex-row">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="समर्पण क्या है?"
          className="w-full border border-black/10 bg-white px-4 py-3 outline-none"
        />
        <button disabled={busy} className="bg-maroon px-6 py-3 text-white disabled:opacity-60">
          पूछें
        </button>
      </form>

      <div className="mt-8 space-y-8">
        {turns.map((turn, i) => (
          <section key={i}>
            <p className="text-sm text-[#8a7564]">प्रश्न</p>
            <h2 className="font-dev text-2xl">{turn.question}</h2>
            {busy && i === turns.length - 1 && !turn.answer && !turn.error && (
              <ol className="mt-4 space-y-1 text-sm text-[#5c4e43]">
                {STAGES.map((s, idx) => (
                  <li key={s} className={idx <= stage ? "text-maroon" : "opacity-40"}>
                    {idx < stage ? "✓ " : idx === stage ? "· " : ""}
                    {s}
                  </li>
                ))}
              </ol>
            )}
            {turn.error && <p className="mt-4 text-maroon">{turn.error}</p>}
            {turn.answer && (
              <div className="mt-4">
                <AnswerCard answer={turn.answer} />
              </div>
            )}
          </section>
        ))}
        {turns.length === 0 && (
          <p className="text-[#6d5e52]">A seeker may begin with a definition, a life situation, or a request for the granth’s own wording.</p>
        )}
      </div>
    </div>
  );
}
