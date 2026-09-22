export type Citation = {
  page: number;
  book: string;
  chapter?: string | null;
  chunk_id?: string;
  drive_file_id?: string | null;
};

export type Passage = {
  page: number;
  chapter?: string | null;
  excerpt: string;
  label: string;
  verification: string;
  drive_file_id?: string | null;
};

export type Answer = {
  answer_id: string;
  conversation_id: string;
  language: string;
  status: string;
  labels: {
    quote: string;
    explanation: string;
    suggestion: string;
    reference: string;
  };
  source_quote?: string | null;
  source_passages?: Passage[];
  quote_verification?: string;
  explanation?: string;
  follow_up_hint?: string;
  pure_soul_suggestion?: string | null;
  citations: Citation[];
  confidence?: {
    score: number;
    method: string;
    level: string;
    coverage?: number;
  } | null;
  llm_used?: boolean;
};

export type BookInfo = {
  title: string;
  title_hi: string;
  author: string;
  author_hi: string;
  source_note: string;
  pages_indexed: number;
  page_min: number;
  page_max: number;
  missing_pages: number[];
  chunks_indexed: number;
  product_url: string;
  cover: { image_url: string; fallback: string; note: string };
  chapters: { chapter: string; start_page: number; end_page: number; pages: number }[];
  links: Record<string, string>;
};

export type SourcePage = {
  page: number;
  book: string;
  chapter?: string | null;
  text: string;
  ocr_confidence: number | null;
  ocr_note?: string;
  verification: string;
  image: {
    kind: string;
    scan_url?: string | null;
    view_url?: string | null;
    plate_url: string;
    folder_url: string;
    filename: string;
  };
};

const convKey = "asai-conversation";

export function getConversationId() {
  return localStorage.getItem(convKey) || undefined;
}

export function setConversationId(id: string) {
  localStorage.setItem(convKey, id);
}

export async function ask(question: string): Promise<Answer> {
  const res = await fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, conversation_id: getConversationId() }),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || "The guide could not answer just now.");
  }
  const data = (await res.json()) as Answer;
  setConversationId(data.conversation_id);
  return data;
}

export async function getBook(): Promise<BookInfo> {
  const res = await fetch("/api/book");
  if (!res.ok) throw new Error("Book metadata unavailable");
  return res.json();
}

export async function getSource(page: number): Promise<SourcePage> {
  const res = await fetch(`/api/source/${page}`);
  if (!res.ok) throw new Error("Source page unavailable");
  return res.json();
}

export async function getHealth() {
  const res = await fetch("/api/health");
  if (!res.ok) throw new Error("offline");
  return res.json();
}
