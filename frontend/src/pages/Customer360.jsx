import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getCustomerById } from "../data/mockCustomers";

function Customer360() {
  const { id } = useParams();
  const customer = getCustomerById(id);

  const [isEditing, setIsEditing] = useState(false);

  if (!customer) {
    return (
      <>
        <h1>Customer Not Found</h1>

        <Link to="/customers">
          ← Back to Customers
        </Link>
      </>
    );
  }

  const productSummary = getProductSummary(customer.products);

  return (
    <>
      {/* Header */}
      <div className="customer-header">
        <div>
          <Link to="/customers" className="back-link">
            ← Back to Customers
          </Link>

          <h1>{customer.name}</h1>

          <p className="page-description">
            Master Customer ID: {customer.id}
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => setIsEditing(true)}
        >
          Edit Customer
        </button>
      </div>

      {/* Golden Record */}
      <section className="section-card">
        <div className="section-header">
          <div>
            <h2>Golden Record</h2>
            <p>Unified customer information</p>
          </div>
        </div>

        <div className="field-grid">
          <Field
            label="Full Name"
            value={customer.name}
            source={customer.lineage.name}
          />

          <Field
            label="Email"
            value={customer.email}
            source={customer.lineage.email}
          />

          <Field
            label="Phone"
            value={customer.phone}
            source={customer.lineage.phone}
          />

          <Field
            label="Date of Birth"
            value={customer.dob}
            source={customer.lineage.dob}
          />

          <Field
            label="Address"
            value={customer.address}
            source={customer.lineage.address}
          />
        </div>
      </section>

      {/* Product Portfolio */}
      <section className="section-card">
        <div className="section-header">
          <div>
            <h2>Product Portfolio</h2>
            <p>
              {customer.products.length} products linked to this customer
            </p>
          </div>
        </div>

        <div className="portfolio-grid">
          {productSummary.map((product) => (
            <div
              className="portfolio-card"
              key={product.category}
            >
              <span className="portfolio-title">
                {product.category}
              </span>

              <strong className="portfolio-count">
                {product.count}
              </strong>

              <span className="portfolio-label">
                {product.label}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* Transaction History */}
      <section className="section-card">
        <div className="section-header">
          <div>
            <h2>Transaction History</h2>
            <p>Recent customer transactions</p>
          </div>
        </div>

        <div className="transaction-timeline">
          {customer.transactions.map((transaction) => (
            <div
              className="transaction-item"
              key={transaction.id}
            >
              <div className="transaction-date">
                {formatDate(transaction.date)}
              </div>

              <div className="transaction-details">
                <div>
                  <strong className="transaction-amount">
                    {transaction.amount}
                  </strong>

                  <span
                    className={`transaction-type ${
                      transaction.type.toLowerCase()
                    }`}
                  >
                    {transaction.type}
                  </span>
                </div>

                <span className="transaction-account">
                  {transaction.account ||
                    transaction.accountType ||
                    "Account"}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Audit History */}
      <section className="section-card">
        <div className="section-header">
          <div>
            <h2>Audit History</h2>
            <p>Changes made to this customer record</p>
          </div>
        </div>

        <div className="transaction-list">
          <div className="transaction-row">
            <div>
              <strong>Customer record created</strong>
              <small>System · Initial Golden Record</small>
            </div>

            <span>Today</span>
          </div>

          <div className="transaction-row">
            <div>
              <strong>Customer data processed</strong>
              <small>MDM Pipeline · Data Processing</small>
            </div>

            <span>Today</span>
          </div>

          <div className="transaction-row">
            <div>
              <strong>Golden Record generated</strong>
              <small>MDM Pipeline · Survivorship</small>
            </div>

            <span>Today</span>
          </div>
        </div>
      </section>

      {/* Edit Customer Modal */}
      {isEditing && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Edit Customer</h2>

              <button
                className="close-button"
                onClick={() => setIsEditing(false)}
              >
                ×
              </button>
            </div>

            <label>
              Name
              <input
                type="text"
                defaultValue={customer.name}
              />
            </label>

            <label>
              Email
              <input
                type="email"
                defaultValue={customer.email}
              />
            </label>

            <label>
              Phone
              <input
                type="text"
                defaultValue={customer.phone}
              />
            </label>

            <label>
              Address
              <input
                type="text"
                defaultValue={customer.address}
              />
            </label>

            <div className="modal-actions">
              <button
                className="secondary-button"
                onClick={() => setIsEditing(false)}
              >
                Cancel
              </button>

              <button
                className="primary-button"
                onClick={() => setIsEditing(false)}
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}


/* =========================
   PRODUCT SUMMARY
========================= */

function getProductSummary(products) {
  const categories = [
    {
      category: "Savings Accounts",
      keywords: ["savings"],
      label: "Accounts",
    },
    {
      category: "Current Accounts",
      keywords: ["current"],
      label: "Accounts",
    },
    {
      category: "Credit Card",
      keywords: ["credit card"],
      label: "Cards",
    },
    {
      category: "Loans",
      keywords: ["loan"],
      label: "Active",
    },
  ];

  return categories
    .map((category) => {
      const matchingProducts = products.filter((product) => {
        const type = product.type.toLowerCase();

        return category.keywords.some((keyword) =>
          type.includes(keyword)
        );
      });

      return {
        category: category.category,
        count: matchingProducts.length,
        label: category.label,
      };
    })
    .filter((category) => category.count > 0);
}


/* =========================
   DATE FORMATTER
========================= */

function formatDate(date) {
  const parsedDate = new Date(date);

  if (Number.isNaN(parsedDate.getTime())) {
    return date;
  }

  return parsedDate.toLocaleDateString("en-IN", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}


/* =========================
   GOLDEN RECORD FIELD
========================= */

function Field({ label, value, source }) {
  return (
    <div className="field">
      <label>{label}</label>

      <strong>{value}</strong>

      <span className="source-badge">
        ● {source}
      </span>
    </div>
  );
}

export default Customer360;