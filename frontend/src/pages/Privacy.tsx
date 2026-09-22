export default function Privacy() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-12 leading-7 text-[#3f342c]">
      <p className="kicker">Privacy</p>
      <h1 className="mt-2 font-dev text-4xl text-maroon">What stays on this machine</h1>
      <ul className="mt-6 list-disc space-y-3 pl-5">
        <li>Questions and answers are stored in the local database so a follow-up can keep context, and so an admin can inspect a failed retrieval.</li>
        <li>The browser remembers only a conversation id in local storage.</li>
        <li>No API key is written into the source. If an LLM is configured, the question and the retrieved excerpts are sent to that provider.</li>
        <li>This guide is not medical, psychological, legal, or financial advice. It does not diagnose a condition or promise a result.</li>
        <li>It will not imitate Swamiji or claim a personal message from him.</li>
      </ul>
    </div>
  );
}
