import { useState } from "react";

const SOURCES = [
  "https://lh3.googleusercontent.com/d/1_ngnzVImWtRswOvMivCiBepXWFyAFtG4=w900",
  "https://drive.google.com/thumbnail?id=1_ngnzVImWtRswOvMivCiBepXWFyAFtG4&sz=w900",
  "https://static.wixstatic.com/media/9a33e9_3f2b4ffdb425447fa48a97c7d8d1e346~mv2.jpg",
  "/art/cover-fallback.jpg",
];

export default function Cover({ className = "" }: { className?: string }) {
  const [i, setI] = useState(0);
  const fallback = i === SOURCES.length - 1;
  return (
    <figure className={className}>
      <img
        src={SOURCES[i]}
        alt="Aadhyatmik Satya"
        className="h-full w-full object-cover"
        onError={() => setI((n) => Math.min(n + 1, SOURCES.length - 1))}
      />
      {fallback && (
        <figcaption className="mt-2 text-xs text-[#6d5e52]">
          App artwork shown because the source cover could not be loaded in this browser.
        </figcaption>
      )}
    </figure>
  );
}
