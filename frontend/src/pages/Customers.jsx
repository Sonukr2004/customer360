import { useState } from "react";
import { Link } from "react-router-dom";
import { customers } from "../data/mockCustomers";

function Customers() {
  const [search, setSearch] = useState("");
  const [productFilter, setProductFilter] = useState("All");
  const [regionFilter, setRegionFilter] = useState("");

  const filteredCustomers = customers.filter((customer) => {
    const query = search.toLowerCase();
    const regionQuery = regionFilter.toLowerCase();

    // Search
    const matchesSearch =
      customer.name.toLowerCase().includes(query) ||
      customer.email.toLowerCase().includes(query) ||
      customer.phone.includes(query);

    // Product Type Filter
    const matchesProduct =
      productFilter === "All" ||
      customer.products.some((product) => {
        const productType = product.type.toLowerCase();

        if (productFilter === "Savings") {
          return productType.includes("savings");
        }

        if (productFilter === "Credit Card") {
          return productType.includes("credit card");
        }

        if (productFilter === "Loan") {
          return productType.includes("loan");
        }

        if (productFilter === "Current Account") {
          return productType.includes("current");
        }

        return false;
      });

    // Address / Region Filter
    const matchesRegion =
      regionQuery === "" ||
      customer.address.toLowerCase().includes(regionQuery);

    return matchesSearch && matchesProduct && matchesRegion;
  });

  return (
    <>
      <h1>Customers</h1>

      <p className="page-description">
        Search and manage unified customer records.
      </p>

      {/* Search */}
      <input
        className="search-input"
        type="text"
        placeholder="Search by name, email or phone..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {/* Filters */}
      <div className="customer-filters">
        <div className="filter-group">
          <label htmlFor="product-filter">
            Product Type
          </label>

          <select
            id="product-filter"
            value={productFilter}
            onChange={(e) => setProductFilter(e.target.value)}
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
          <label htmlFor="region-filter">
            Address / Region
          </label>

          <input
            id="region-filter"
            type="text"
            placeholder="Search address or region..."
            value={regionFilter}
            onChange={(e) => setRegionFilter(e.target.value)}
          />
        </div>

        <button
          className="clear-filter-button"
          onClick={() => {
            setProductFilter("All");
            setRegionFilter("");
          }}
        >
          Clear Filters
        </button>
      </div>

      {/* Customer Table */}
      <div className="customer-table">
        <div className="customer-table-header">
          <span>Customer</span>
          <span>Email</span>
          <span>Phone</span>
          <span>Products</span>
          <span>Profile Completion</span>
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

            <span>{customer.products.length}</span>

            <span className="quality-score">
              {customer.qualityScore}%
            </span>

            <Link
              to={`/customers/${customer.id}`}
              className="view-button"
            >
              View →
            </Link>
          </div>
        ))}

        {filteredCustomers.length === 0 && (
          <div className="empty-state">
            No customers found matching the selected filters.
          </div>
        )}
      </div>
    </>
  );
}

export default Customers;