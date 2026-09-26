import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getCustomers } from "../api/customers";


function Dashboard() {
  const [searchQuery, setSearchQuery] = useState("");
  const [regionQuery, setRegionQuery] = useState("");

  const [customers, setCustomers] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  /*
   * Load customers from backend.
   *
   * The backend performs the actual
   * name/email/phone search.
   */
  useEffect(() => {
    let cancelled = false;

    async function loadCustomers() {
      try {
        setLoading(true);
        setError("");

        const data = await getCustomers(searchQuery);

        if (!cancelled) {
          setCustomers(data.customers || []);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Failed to load customers.");
          setCustomers([]);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    const timer = setTimeout(loadCustomers, 300);

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [searchQuery]);


  /*
   * Region/address filtering happens on the data
   * already returned by the backend.
   */
  const filteredCustomers = customers.filter((customer) => {
    const region = regionQuery.trim().toLowerCase();

    if (!region) {
      return true;
    }

    return (
      customer.address?.toLowerCase().includes(region)
    );
  });


  function clearFilters() {
    setSearchQuery("");
    setRegionQuery("");
  }


  return (
    <div className="page">

      {/* Header */}

      <div className="page-header">
        <h1>Dashboard</h1>

        <p>
          Unified Customer 360 & Golden Record Engine
        </p>
      </div>


      {/* Stats */}

      <div className="stats-grid">

        <div className="stat-card">
          <span>Total Customers</span>

          <strong>
            {loading ? "..." : customers.length}
          </strong>
        </div>


        <div className="stat-card">
          <span>High Quality</span>

          <strong>
            {loading
              ? "..."
              : customers.filter(
                  (customer) =>
                    Number(customer.quality_score || 0) >= 80
                ).length}
          </strong>
        </div>


        <div className="stat-card">
          <span>Needs Review</span>

          <strong>
            {loading
              ? "..."
              : customers.filter(
                  (customer) =>
                    Number(customer.quality_score || 0) < 80
                ).length}
          </strong>
        </div>


        <div className="stat-card">
          <span>Data Source</span>

          <strong>Live</strong>
        </div>

      </div>


      {/* Search */}

      <div className="customer-search">

        <input
          type="text"
          placeholder="Search by name, email or phone..."
          value={searchQuery}
          onChange={(event) =>
            setSearchQuery(event.target.value)
          }
        />

      </div>


      {/* Filters */}

      <div className="customer-filters">

        <div className="filter-group">

          <label>ADDRESS / REGION</label>

          <input
            type="text"
            placeholder="Search address or region..."
            value={regionQuery}
            onChange={(event) =>
              setRegionQuery(event.target.value)
            }
          />

        </div>


        <button
          className="clear-filters"
          onClick={clearFilters}
        >
          Clear Filters
        </button>

      </div>


      {/* Error */}

      {error && (
        <div className="empty-state">
          <strong>Unable to load customers</strong>
          <p>{error}</p>
        </div>
      )}


      {/* Customer Table */}

      <section className="section-card dashboard-customers">

        <div className="section-header">

          <div>

            <h2>Customer Overview</h2>

            <p>
              {loading
                ? "Loading customers..."
                : `${filteredCustomers.length} customer${
                    filteredCustomers.length !== 1
                      ? "s"
                      : ""
                  }`}
            </p>

          </div>

        </div>


        <div className="customer-table">

          <div className="customer-table-header">

            <span>CUSTOMER</span>

            <span>EMAIL</span>

            <span>PHONE</span>

            <span>PROFILE COMPLETION</span>

            <span></span>

          </div>


          {loading && (
            <div className="empty-state">
              Loading customers...
            </div>
          )}


          {!loading &&
            !error &&
            filteredCustomers.map((customer) => (

              <div
                className="customer-table-row"
                key={customer.master_customer_id}
              >

                <div>

                  <strong>
                    {customer.name || "Unnamed Customer"}
                  </strong>

                  <small>
                    {customer.master_customer_id}
                  </small>

                </div>


                <span>
                  {customer.email || "—"}
                </span>


                <span>
                  {customer.phone || "—"}
                </span>


                <strong className="quality-score">
                  {customer.quality_score ?? 0}%
                </strong>


                <Link
                  to={`/customers/${customer.master_customer_id}`}
                  className="view-link"
                >
                  View →
                </Link>

              </div>

            ))}


          {!loading &&
            !error &&
            filteredCustomers.length === 0 && (

              <div className="empty-state">
                No customers found.
              </div>

            )}

        </div>

      </section>

    </div>
  );
}


export default Dashboard;