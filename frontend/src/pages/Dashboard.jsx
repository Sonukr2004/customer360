import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { customers } from "../data/mockCustomers";

function Dashboard() {
  const [searchQuery, setSearchQuery] = useState("");
  const [productFilter, setProductFilter] = useState("All");
  const [regionQuery, setRegionQuery] = useState("");

  const filteredCustomers = useMemo(() => {
    const search = searchQuery.trim().toLowerCase();
    const region = regionQuery.trim().toLowerCase();

    return customers.filter((customer) => {
      const matchesSearch =
        !search ||
        customer.name.toLowerCase().includes(search) ||
        customer.email.toLowerCase().includes(search) ||
        customer.phone.toLowerCase().includes(search);

      const matchesProduct =
        productFilter === "All" ||
        customer.products.some((product) =>
          product.type
            .toLowerCase()
            .includes(productFilter.toLowerCase())
        );

      const matchesRegion =
        !region ||
        customer.address.toLowerCase().includes(region);

      return (
        matchesSearch &&
        matchesProduct &&
        matchesRegion
      );
    });
  }, [searchQuery, productFilter, regionQuery]);

  function clearFilters() {
    setProductFilter("All");
    setRegionQuery("");
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Unified Customer 360 & Golden Record Engine</p>
      </div>

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

      <div className="customer-filters">
        <div className="filter-group">
          <label>PRODUCT TYPE</label>

          <select
            value={productFilter}
            onChange={(event) =>
              setProductFilter(event.target.value)
            }
          >
            <option value="All">All Products</option>
            <option value="Savings">Savings</option>
            <option value="Credit Card">Credit Card</option>
            <option value="Loan">Loan</option>
            <option value="Current Account">
              Current Account
            </option>
          </select>
        </div>

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

      <section className="section-card dashboard-customers">
        <div className="section-header">
          <div>
            <h2>Customer Overview</h2>
            <p>
              {filteredCustomers.length} customer
              {filteredCustomers.length !== 1 ? "s" : ""}
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

          {filteredCustomers.map((customer) => (
            <div
              className="customer-table-row"
              key={customer.id}
            >
              <div>
                <strong>{customer.name}</strong>
                <small>{customer.id}</small>
              </div>

              <span>{customer.email}</span>

              <span>{customer.phone}</span>

              <strong className="quality-score">
                {customer.qualityScore}%
              </strong>

              <Link
                to={`/customers/${customer.id}`}
                className="view-link"
              >
                View →
              </Link>
            </div>
          ))}

          {filteredCustomers.length === 0 && (
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