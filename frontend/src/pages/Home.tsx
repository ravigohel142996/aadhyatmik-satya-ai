import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import Cover from "../components/Cover";

const suggestions = [
  "समर्पण क्या है?",
  "गुरु तत्त्व क्या है?",
  "ध्यान का महत्व क्या है?",
  "साधक किसे कहते हैं?",
];

export default function Home() {
  const [q, setQ] = useState("");
  const nav = useNavigate();

  function go(question: string) {
    const query = question.trim();
    if (!query) return;
    nav(`/ask?q=${encodeURIComponent(query)}`);
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    go(q);
  }

  return (
    <div>
      <section className="relative min-h-[78vh] overflow-hidden text-[#f6f0e6]">
        <img src="/art/hero-himalaya.jpg" alt="" className="absolute inset-0 h-full w-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-[#1a1422] via-[#1a1422]/75 to-[#1a1422]/25" />
        <div className="relative mx-auto flex min-h-[78vh] max-w-4xl flex-col justify-end px-5 pb-14 pt-20">
          <p className="kicker text-[#e4d3ae]">Param Pujya Shree Shivkrupanand Swamiji</p>
          <h1 className="mt-3 font-dev text-5xl leading-tight sm:text-7xl">आध्यात्मिक सत्य</h1>
          <p className="mt-3 max-w-xl font-display text-2xl italic text-[#f0e2c8] sm:text-3xl">
            आध्यात्मिक सत्य के संदर्भ में अपने प्रश्नों की खोज करें।
          </p>
          <p className="mt-2 font-display text-xl text-[#e4d3ae]">प्रश्न आपका — संदर्भ ग्रंथ का।</p>
          <form onSubmit={onSubmit} className="mt-8 flex max-w-2xl flex-col gap-3 sm:flex-row">
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Ask your question…"
              className="w-full border border-white/20 bg-white/10 px-4 py-3 text-[#f6f0e6] placeholder:text-white/50 outline-none"
            />
            <button className="bg-[#c4622d] px-6 py-3 text-white" type="submit">
              खोजें
            </button>
          </form>
          <div className="mt-5 flex flex-wrap gap-2">
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => go(s)}
                className="border border-white/25 px-3 py-1.5 text-sm text-[#f6f0e6] hover:bg-white/10"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-6xl gap-8 px-5 py-16 md:grid-cols-[0.9fr_1.1fr] md:items-center">
        <Cover className="mx-auto w-full max-w-sm shadow-2xl" />
        <div>
          <p className="kicker">The Granth</p>
          <h2 className="mt-2 font-dev text-4xl text-maroon">Aadhyatmik Satya</h2>
          <p className="mt-1 font-display text-2xl italic">By Param Pujya Shree Shivkrupanand Swamiji</p>
          <p className="mt-4 max-w-xl leading-7 text-[#4d4036]">
            Explore the teachings through a source-grounded digital guide. Answers begin with the indexed granth,
            then a faithful explanation, then a clearly labeled Pure Soul Suggestion that is not a quotation.
          </p>
          <a
            href="https://www.tattvatrends.com/product-page/calendar-2025"
            className="mt-6 inline-block border border-maroon px-5 py-2 text-maroon"
            target="_blank"
            rel="noreferrer"
          >
            Read / Buy the Book
          </a>
          <p className="mt-2 text-xs text-[#8a7564]">Official product reference on Tattvatrends. Availability is shown on that page.</p>
        </div>
      </section>

      <section className="border-y border-black/5 bg-[#fbf7f1]">
        <div className="mx-auto grid max-w-6xl gap-8 px-5 py-12 md:grid-cols-3">
          {[
            ["01", "ग्रंथ पहले", "Every substantive answer searches the indexed pages before any explanation is written."],
            ["02", "उद्धरण अलग", "Swamiji’s indexed words, the explanation, and the AI suggestion are never mixed."],
            ["03", "पृष्ठ खोलें", "A citation is a page you can open. If the scan cannot load, the indexed text plate remains."],
          ].map(([n, t, d]) => (
            <div key={n}>
              <p className="font-display text-3xl text-gold">{n}</p>
              <h3 className="mt-2 font-dev text-2xl">{t}</h3>
              <p className="mt-2 text-sm leading-6 text-[#5c4e43]">{d}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
