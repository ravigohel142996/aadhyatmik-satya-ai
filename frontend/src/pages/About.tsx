export default function About() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-12 leading-7 text-[#3f342c]">
      <p className="kicker">About</p>
      <h1 className="mt-2 font-dev text-4xl text-maroon">एक ग्रंथ-आधारित मार्गदर्शक</h1>
      <p className="mt-4">
        Aadhyatmik Satya AI is a digital guide for seekers who want to ask a question and see what the indexed granth
        actually contains. It is not a living guru, and it does not claim divine authority.
      </p>
      <h2 className="mt-8 font-dev text-2xl">The book, from its own front matter</h2>
      <p className="mt-2">
        The indexed opening pages describe आध्यात्मिक सत्य as messages given by Param Pujya Shree Shivkrupanand Swamiji
        for sadhaks during the 45-day Gahan Dhyan Anushthan from 20 February 2007 to 5 April 2007. The role page in the
        corpus is signed Baba Swami, 15 April 2007. A request page is signed Guruma. Those attributions are kept distinct.
      </p>
      <h2 className="mt-8 font-dev text-2xl">Organizations, from their own sites</h2>
      <p className="mt-2">
        Guru Tattva describes itself as an initiative by Shree Shivkrupanand Swami Foundation, a platform led by
        H. H. Shree Shivkrupanand Swamiji. Its parichay page says Samarpan Dhyanyog was introduced in 1994 and has
        evolved into Guru Tattva. Tattvatrends lists the book as “Adhyatmik Satya With Velvet Cover” and is the product
        reference used here.
      </p>
      <p className="mt-3">
        <a className="text-maroon underline" href="https://gurutattva.org/" target="_blank" rel="noreferrer">gurutattva.org</a>
        {" · "}
        <a className="text-maroon underline" href="https://www.tattvatrends.com/" target="_blank" rel="noreferrer">tattvatrends.com</a>
        {" · "}
        <a className="text-maroon underline" href="https://www.tattvatrends.com/product-page/calendar-2025" target="_blank" rel="noreferrer">book reference</a>
      </p>
      <p className="mt-6 text-sm text-[#6d5e52]">
        Website descriptions are not treated as quotations from the granth unless the same words are retrieved from an indexed page.
      </p>
    </div>
  );
}
