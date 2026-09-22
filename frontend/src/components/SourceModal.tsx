import { useEffect, useState } from "react";
import { getSource, type SourcePage } from "../api";

export default function SourceModal({
  page,
  highlight,
  onClose,
}: {
  page: number;
  highlight?: string;
  onClose: () => void;
}) {
  const [data, setData] = useState<SourcePage | null>(null);
  const [scanFailed, setScanFailed] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    setScanFailed(false);
    getSource(page).then(setData).catch(() => setErr("This page could not be opened."));
  }, [page]);

  const text = data?.text || "";
  const needle = (highlight || "").slice(0, 48);
  const parts = needle && text.includes(needle) ? text.split(needle) : null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-[#1a1422]/70 p-3 sm:items-center" onClick={onClose}>
      <div
        className="paper-card max-h-[92vh] w-full max-w-3xl overflow-auto rounded-sm"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4 border-b border-black/5 px-5 py-4">
          <div>
            <p className="kicker">View Source</p>
            <h3 className="font-dev text-2xl">स्रोत पृष्ठ {page}</h3>
            {data?.chapter && <p className="text-sm text-[#6d5e52]">{data.chapter}</p>}
          </div>
          <button className="text-sm text-maroon" onClick={onClose}>
            Close
          </button>
        </div>
        <div className="grid gap-4 p-5 md:grid-cols-[1.1fr_0.9fr]">
          <div>
            {err && <p>{err}</p>}
            {data?.image.scan_url && !scanFailed ? (
              <img
                src={data.image.scan_url}
                alt={`Scan of page ${page}`}
                className="w-full border border-black/10"
                onError={() => setScanFailed(true)}
              />
            ) : (
              <img src={data?.image.plate_url || `/api/source/${page}/plate`} alt="Indexed text plate" className="w-full border border-black/10" />
            )}
            <p className="mt-2 text-xs leading-5 text-[#6d5e52]">
              {scanFailed || !data?.image.scan_url
                ? "Text plate of the indexed page. This is not a photograph of the printed page."
                : "Scan linked from the source folder. If it fails to load, the text plate remains for verification."}
            </p>
            {data?.image.view_url && (
              <a className="mt-2 inline-block text-sm text-maroon underline" href={data.image.view_url} target="_blank" rel="noreferrer">
                Open scan file
              </a>
            )}
          </div>
          <div>
            <p className="kicker">Indexed text</p>
            <p className="mt-1 text-xs text-[#8a7564]">{data?.verification}</p>
            <div className="mt-3 max-h-[52vh] overflow-auto font-dev text-lg leading-8 text-ink">
              {parts ? (
                parts.map((part, i) => (
                  <span key={i}>
                    {part}
                    {i < parts.length - 1 && <mark className="hit">{needle}</mark>}
                  </span>
                ))
              ) : (
                text
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
