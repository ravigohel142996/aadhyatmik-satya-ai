import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import Ask from "./pages/Ask";
import Granth from "./pages/Granth";
import How from "./pages/How";
import About from "./pages/About";
import Privacy from "./pages/Privacy";
import Admin from "./pages/Admin";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/ask" element={<Ask />} />
        <Route path="/granth" element={<Granth />} />
        <Route path="/how" element={<How />} />
        <Route path="/about" element={<About />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/admin/*" element={<Admin />} />
      </Routes>
    </Layout>
  );
}
