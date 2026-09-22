import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Cover from "../components/Cover";
import { getBook, type BookInfo } from "../api";

export default function Granth() {
  const [book, setBook] = useState<BookInfo | null>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    getBook().then(setBook).catch(() => setErr("The index is not ready yet."));
  }, []);

  return (
    <div className="mx-auto max-w-5xl px-5 py-12">
      <p className="kicker">The Granth</p>
      <h1 className="mt-2 font-dev text-4xl text-maroon">आध्यात्मिक सत्य</h1>
      <p className="mt-2 font-display text-2xl italic">Param Pujya Shree Shivkrupanand Swamiji</p>
      {err && <p className="mt-4 text-maroon">{err}</p>}
      {book && (
        <>
          <div className="mt-8 grid gap-8 md:grid-cols-[240px_1fr]">
            <Cover />
            <div className="space-y-3 leading-7 text-[#3f342c]">
              <p>{book.source_note}</p>
              <p>
                Indexed source pages: {book.pages_indexed} (page {book.page_min}–{book.page_max}). Chunks: {book.chunks_indexed}.
                Missing text pages inside that range: {book.missing_pages.join(", ") || "none"}.
              </p>
              <p>
                The accessible Drive folder was inspected. It contains scans through Page 256, not a verified set of 270 pages.
                This guide does not claim that all 270 pages were processed.
              </p>
              <a className="inline-block border border-maroon px-4 py-2 text-maroon" href={book.product_url} target="_blank" rel="noreferrer">
                Read / Buy the Book
              </a>
            </div>
          </div>
          <h2 className="mt-12 font-dev text-3xl">Detected sections</h2>
          <ul className="mt-4 divide-y divide-black/5 border-y border-black/5">
            {book.chapters.map((c) => (
              <li key={c.chapter + c.start_page} className="flex items-center justify-between gap-4 py-3">
                <span className="font-dev text-xl">{c.chapter}</span>
                <span className="text-sm text-[#6d5e52]">
                  pages {c.start_page}–{c.end_page}
                </span>
              </li>
            ))}
          </ul>
          <p className="mt-6 text-sm text-[#6d5e52]">
            Section names are detected from headings in the indexed text. They are not a substitute for the printed table of contents.
            <Link className="ml-2 text-maroon underline" to="/ask">
              Ask a question
            </Link>
          </p>
        </>
      )}
    </div>
  );
}
