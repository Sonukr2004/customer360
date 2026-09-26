function Dashboard() {
  return (
    <>
      <h1>Dashboard</h1>
      <p className="page-description">
        Unified Customer 360 & Golden Record Engine
      </p>

      <div className="stats-grid">
        <div className="stat-card">
          <span>Total Customers</span>
          <strong>12,482</strong>
        </div>

        <div className="stat-card">
          <span>High Quality</span>
          <strong>10,941</strong>
        </div>

        <div className="stat-card">
          <span>Needs Review</span>
          <strong>327</strong>
        </div>

        <div className="stat-card">
          <span>Last Ingestion</span>
          <strong>2 min ago</strong>
        </div>
      </div>

      <div className="placeholder-card">
        <h2>Customer Overview</h2>
        <p>Customer records will appear here.</p>
      </div>
    </>
  );
}

export default Dashboard;