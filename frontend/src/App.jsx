import { Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";

import Dashboard from "./pages/Dashboard";
import Customer360 from "./pages/Customer360";
import Quality from "./pages/Quality";

function App() {
  return (
    <div className="app">
      <Sidebar />

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/customers/:id" element={<Customer360 />} />
          <Route path="/quality" element={<Quality />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;