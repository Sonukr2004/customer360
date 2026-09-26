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

      {/* Transaction History */}
      <section className="section-card">
        <div className="section-header">
          <div>
            <h2>Transaction History</h2>
            <p>Recent customer transactions</p>
          </div>
        </div>

        <div className="transaction-list">
          {customer.transactions.map((transaction) => (
            <div
              className="transaction-row"
              key={transaction.id}
            >
              <div>
                <strong>{transaction.type}</strong>
                <small>{transaction.date}</small>
              </div>

              <strong>{transaction.amount}</strong>
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