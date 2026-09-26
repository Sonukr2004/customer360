import { Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";

import Dashboard from "./pages/Dashboard";
import Customers from "./pages/Customers";
import Customer360 from "./pages/Customer360";
import Ingestion from "./pages/Ingestion";
import Quality from "./pages/Quality";


function App() {
  return (
    <div className="app">
      <Sidebar />

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/customers/:id" element={<Customer360 />} />
          <Route path="/ingestion" element={<Ingestion />} />
          <Route path="/quality" element={<Quality />} />
          
        </Routes>
      </main>
    </div>
  );
}

export default App;