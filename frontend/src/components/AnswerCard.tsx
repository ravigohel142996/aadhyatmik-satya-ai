import { useState } from "react";
import type { Answer } from "../api";
import SourceModal from "./SourceModal";

export default function AnswerCard({ answer }: { answer: Answer }) {
  const [page, setPage] = useState<number | null>(null);
  const labels = answer.labels;
  const passages = answer.source_passages || [];

  return (
    <article className="paper-card rounded-sm px-5 py-6 sm:px-8">
      {answer.status === "insufficient" || answer.status.startsWith("refused") ? (
        <div>
          <p className="kicker">Granth</p>
          <p className="mt-3 font-dev text-2xl leading-9">{answer.explanation}</p>
          {answer.follow_up_hint && <p className="mt-3 text-[#5c4e43]">{answer.follow_up_hint}</p>}
        </div>
      ) : (
        <div className="space-y-7">
          <section>
            <p className="kicker">{labels.quote}</p>
            <p className="mt-1 text-xs text-[#8a7564]">{answer.quote_verification}</p>
            {passages.map((p) => (
              <blockquote key={p.page} className="mt-4 whitespace-pre-wrap border-l-2 border-[#c6a15b] pl-4 font-dev text-xl leading-9">
                {p.excerpt}
                <footer className="mt-2 font-ui text-sm text-[#6d5e52]">
                  {p.label !== labels.quote ? p.label + " · " : ""}
                  Aadhyatmik Satya · पृष्ठ {p.page}
                  {p.chapter ? ` · ${p.chapter}` : ""}
                </footer>
              </blockquote>
            ))}
          </section>
          <div className="gold-rule" />
          <section>
            <p className="kicker">{labels.explanation}</p>
            <p className="mt-3 whitespace-pre-wrap font-dev text-xl leading-9">{answer.explanation}</p>
          </section>
          {answer.pure_soul_suggestion && (
            <>
              <div className="gold-rule" />
              <section className="bg-[#f3eadc] px-4 py-4">
                <p className="kicker">{labels.suggestion}</p>
                <p className="mt-1 text-xs uppercase tracking-wider text-[#8a7564]">AI-generated · not a quotation</p>
                <p className="mt-3 whitespace-pre-wrap leading-7 text-[#3a2c24]">{answer.pure_soul_suggestion}</p>
              </section>
            </>
          )}
          <div className="gold-rule" />
          <section>
            <p className="kicker">{labels.reference}</p>
            <ul className="mt-3 space-y-2 text-sm">
              {answer.citations.map((c) => (
                <li key={c.page} className="flex flex-wrap items-center justify-between gap-2">
                  <span>
                    Aadhyatmik Satya · Page {c.page}
                    {c.chapter ? ` · ${c.chapter}` : ""}
                  </span>
                  <button className="border border-maroon px-3 py-1 text-maroon" onClick={() => setPage(c.page)}>
                    View Source Page
                  </button>
                </li>
              ))}
            </ul>
            {answer.confidence && (
              <p className="mt-3 text-xs text-[#8a7564]">
                Retrieval confidence {answer.confidence.score} · {answer.confidence.level} · {answer.confidence.method}
              </p>
            )}
          </section>
        </div>
      )}
      {page && (
        <SourceModal
          page={page}
          highlight={answer.source_quote || undefined}
          onClose={() => setPage(null)}
        />
      )}
    </article>
  );
}
