import { useState } from "react";
import { Link } from "react-router-dom";
import { customers } from "../data/mockCustomers";

function Customers() {
  const [search, setSearch] = useState("");

  const filteredCustomers = customers.filter((customer) => {
    const query = search.toLowerCase();

    return (
      customer.name.toLowerCase().includes(query) ||
      customer.email.toLowerCase().includes(query) ||
      customer.phone.includes(query)
    );
  });

  return (
    <>
      <h1>Customers</h1>

      <p className="page-description">
        Search and manage unified customer records.
      </p>

      <input
        className="search-input"
        type="text"
        placeholder="Search by name, email or phone..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      <div className="customer-table">
        <div className="customer-table-header">
          <span>Customer</span>
          <span>Email</span>
          <span>Phone</span>
          <span>Products</span>
          <span></span>
        </div>

        {filteredCustomers.map((customer) => (
          <div className="customer-table-row" key={customer.id}>
            <div>
              <strong>{customer.name}</strong>
              <small>{customer.id}</small>
            </div>

            <span>{customer.email}</span>

            <span>{customer.phone}</span>

            <span>{customer.products.length}</span>

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
            No customers found.
          </div>
        )}
      </div>
    </>
  );
}

export default Customers;