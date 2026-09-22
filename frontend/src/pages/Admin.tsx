import { FormEvent, useEffect, useState } from "react";

const tokenKey = "asai-admin";

async function api(path: string, token: string, init?: RequestInit) {
  const res = await fetch(path, {
    ...init,
    headers: { ...(init?.headers || {}), "X-Admin-Token": token },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || res.statusText);
  return data;
}

export default function Admin() {
  const [token, setToken] = useState(localStorage.getItem(tokenKey) || "");
  const [tab, setTab] = useState("overview");
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState("");
  const [q, setQ] = useState("समर्पण");

  function save(e: FormEvent) {
    e.preventDefault();
    localStorage.setItem(tokenKey, token);
    setErr("");
    void load("overview");
  }

  async function load(next = tab) {
    setTab(next);
    setErr("");
    try {
      if (next === "overview") setData(await api("/api/admin/overview", token));
      if (next === "pages") setData(await api("/api/admin/pages?limit=40", token));
      if (next === "chunks") setData(await api("/api/admin/chunks?limit=20", token));
      if (next === "failed") setData(await api("/api/admin/failed", token));
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Admin request failed");
    }
  }

  useEffect(() => {
    if (token) void load("overview");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="mx-auto max-w-5xl px-5 py-10">
      <p className="kicker">Admin</p>
      <h1 className="font-dev text-4xl text-maroon">Knowledge desk</h1>
      <form onSubmit={save} className="mt-4 flex gap-2">
        <input
          value={token}
          onChange={(e) => setToken(e.target.value)}
          placeholder="Admin token"
          type="password"
          className="border border-black/10 px-3 py-2"
        />
        <button className="bg-maroon px-4 text-white">Open</button>
      </form>
      {err && <p className="mt-3 text-maroon">{err}</p>}
      <div className="mt-6 flex flex-wrap gap-3 text-sm">
        {["overview", "pages", "chunks", "failed", "ingest"].map((t) => (
          <button key={t} className={tab === t ? "text-maroon" : ""} onClick={() => (t === "ingest" ? setTab(t) : load(t))}>
            {t}
          </button>
        ))}
        <button
          onClick={async () => {
            try {
              setData(await api("/api/admin/reindex", token, { method: "POST" }));
              setTab("overview");
            } catch (e) {
              setErr(e instanceof Error ? e.message : "reindex failed");
            }
          }}
        >
          reindex
        </button>
        <button
          onClick={async () => {
            try {
              setData(await api("/api/admin/evaluation/run", token, { method: "POST" }));
              setTab("eval");
            } catch (e) {
              setErr(e instanceof Error ? e.message : "eval failed");
            }
          }}
        >
          run evaluation
        </button>
      </div>

      {tab === "ingest" && (
        <form
          className="mt-6 space-y-3"
          onSubmit={async (e) => {
            e.preventDefault();
            const form = e.currentTarget;
            const body = new FormData(form);
            try {
              setData(await api("/api/ingest", token, { method: "POST", body }));
            } catch (ex) {
              setErr(ex instanceof Error ? ex.message : "ingest failed");
            }
          }}
        >
          <input name="file" type="file" required />
          <input name="page_number" placeholder="page number if image" className="border px-2 py-1" />
          <button className="block bg-maroon px-4 py-2 text-white">Upload and ingest</button>
        </form>
      )}

      {tab === "chunks" && (
        <form
          className="mt-4 flex gap-2"
          onSubmit={async (e) => {
            e.preventDefault();
            setData(await api(`/api/admin/chunks?q=${encodeURIComponent(q)}`, token));
          }}
        >
          <input value={q} onChange={(e) => setQ(e.target.value)} className="border px-2 py-1" />
          <button>Search chunks</button>
        </form>
      )}

      <pre className="mt-6 overflow-auto bg-[#1a1422] p-4 text-xs text-[#f6f0e6]">
        {data ? JSON.stringify(data, null, 2).slice(0, 8000) : "No data yet."}
      </pre>
    </div>
  );
}
