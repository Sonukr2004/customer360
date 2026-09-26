import { useMemo, useState } from "react";
import { customers } from "../data/mockCustomers";

function Customers() {
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

      return matchesSearch && matchesProduct && matchesRegion;
    });
  }, [searchQuery, productFilter, regionQuery]);

  function clearFilters() {
    setProductFilter("All");
    setRegionQuery("");
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Customers</h1>
        <p>Search and manage unified customer records.</p>
      </div>

      <div className="customer-search">
        <input
          type="text"
          placeholder="Search by name, email or phone..."
          value={searchQuery}
          onChange={(event) => setSearchQuery(event.target.value)}
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

      <div className="section-card">
        <h2>Customer Search</h2>
        <p>
          {filteredCustomers.length} customer
          {filteredCustomers.length !== 1 ? "s" : ""} found.
        </p>
      </div>
    </div>
  );
}

export default Customers;