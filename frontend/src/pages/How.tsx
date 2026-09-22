export default function How() {
  const steps = [
    ["Question", "Hindi, Gujarati, English, Hinglish, or roman script. Recent questions stay in the conversation."],
    ["Hybrid retrieval", "Keyword BM25 and a local multilingual hash embedding are fused, then reranked. Page numbers stay attached."],
    ["Evidence check", "If the granth does not support the question, the guide says so. It does not fill the gap."],
    ["Three voices", "Indexed granth text, a faithful explanation, and a labeled Pure Soul Suggestion."],
    ["Source page", "Open the scan when a Drive file link is indexed, or the text plate of that page."],
  ];
  return (
    <div className="mx-auto max-w-3xl px-5 py-12">
      <p className="kicker">How it works</p>
      <h1 className="mt-2 font-dev text-4xl text-maroon">स्रोत पहले, व्याख्या बाद में</h1>
      <ol className="mt-8 space-y-6">
        {steps.map(([t, d], i) => (
          <li key={t} className="grid grid-cols-[auto_1fr] gap-4">
            <span className="font-display text-3xl text-gold">{String(i + 1).padStart(2, "0")}</span>
            <div>
              <h2 className="font-display text-2xl">{t}</h2>
              <p className="mt-1 text-[#4d4036]">{d}</p>
            </div>
          </li>
        ))}
      </ol>
      <div className="paper-card mt-10 p-5 text-sm leading-6 text-[#4d4036]">
        <p>
          The local index was built from the extracted corpus already in this repository, aligned to scan page numbers.
          Google Drive was listed and file links were stored where the public folder view exposed them. The Colab notebook
          required a Google sign-in and was not readable. OCR was not re-run on the scans in this environment, so quotations
          carry a verification note.
        </p>
        <p className="mt-3">
          An LLM key is optional. Without it, the explanation stays extractive: the granth’s own sentences, not a new doctrine.
          With a key, the model may phrase the explanation, but invented quotations are not accepted as citations.
        </p>
      </div>
    </div>
  );
}
