import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  getCustomerById,
  getCustomerAudit,
  updateCustomer,
} from "../api/customers";


function Customer360() {
  const { id } = useParams();

  const [customer360, setCustomer360] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const [editForm, setEditForm] = useState({
    name: "",
    email: "",
    phone: "",
    dob: "",
    address: "",
  });


  /*
   * ============================================================
   * LOAD CUSTOMER 360 + AUDIT HISTORY
   * ============================================================
   */

  useEffect(() => {
    let cancelled = false;

    async function loadCustomer() {
      try {
        setLoading(true);
        setError("");

        const [customerData, auditData] =
          await Promise.all([
            getCustomerById(id),
            getCustomerAudit(id),
          ]);

        if (cancelled) {
          return;
        }

        setCustomer360(customerData);

        setAuditLogs(
          auditData.audit_logs || []
        );

        setEditForm({
          name: customerData.customer?.name || "",
          email: customerData.customer?.email || "",
          phone: customerData.customer?.phone || "",
          dob: customerData.customer?.dob || "",
          address: customerData.customer?.address || "",
        });

      } catch (err) {

        if (!cancelled) {
          setError(
            err.message ||
              "Failed to load customer."
          );
        }

      } finally {

        if (!cancelled) {
          setLoading(false);
        }

      }
    }

    loadCustomer();

    return () => {
      cancelled = true;
    };

  }, [id]);


  /*
   * ============================================================
   * LOADING
   * ============================================================
   */

  if (loading) {
    return (
      <div className="page">

        <Link
          to="/"
          className="back-link"
        >
          ← Back to Customers
        </Link>

        <h1>Loading Customer 360...</h1>

      </div>
    );
  }


  /*
   * ============================================================
   * ERROR
   * ============================================================
   */

  if (error || !customer360) {
    return (
      <div className="page">

        <h1>Customer Not Found</h1>

        <p>
          {error || "Unable to load customer."}
        </p>

        <Link
          to="/"
          className="back-link"
        >
          ← Back to Customers
        </Link>

      </div>
    );
  }


  /*
   * ============================================================
   * DATA
   * ============================================================
   */

  const customer = customer360.customer;

  const lineage = customer360.lineage || [];

  const products = customer360.products || {};

  const transactions =
    customer360.transactions || [];

  const coreProducts =
    products.core || [];

  const creditCards =
    products.credit_cards || [];

  const loans =
    products.loans || [];


  /*
   * ============================================================
   * PRODUCT SUMMARY
   * ============================================================
   */

  const productSummary = [
    {
      category: "Core Banking",
      count: coreProducts.length,
      label: "Accounts",
    },
    {
      category: "Credit Card",
      count: creditCards.length,
      label: "Cards",
    },
    {
      category: "Loan",
      count: loans.length,
      label: "Active",
    },
  ].filter(
    (product) => product.count > 0
  );


  /*
   * ============================================================
   * FIND FIELD LINEAGE
   * ============================================================
   */

  function getLineage(fieldName) {
    const entry = lineage.find(
      (item) =>
        item.field_name?.toLowerCase() ===
        fieldName.toLowerCase()
    );

    if (!entry) {
      return null;
    }

    return entry;
  }


  /*
   * ============================================================
   * EDIT CUSTOMER
   * ============================================================
   */

  function openEditModal() {
    setEditForm({
      name: customer.name || "",
      email: customer.email || "",
      phone: customer.phone || "",
      dob: customer.dob || "",
      address: customer.address || "",
    });

    setIsEditing(true);
  }


  function handleInputChange(event) {
    const { name, value } = event.target;

    setEditForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }


  /*
   * ============================================================
   * SAVE CUSTOMER
   * ============================================================
   */

  async function handleSave() {
    try {
      setIsSaving(true);

      const updatedData =
        await updateCustomer(
          id,
          {
            ...editForm,
            changed_by: "Data Steward",
          }
        );


      /*
       * Update Customer 360 immediately.
       */

      setCustomer360((previous) => ({
        ...previous,
        customer: updatedData.customer,
      }));


      /*
       * Reload audit history.
       */

      const auditData =
        await getCustomerAudit(id);

      setAuditLogs(
        auditData.audit_logs || []
      );


      setIsEditing(false);

    } catch (err) {

      alert(
        err.message ||
          "Failed to update customer."
      );

    } finally {

      setIsSaving(false);

    }
  }


  /*
   * ============================================================
   * UI
   * ============================================================
   */

  return (
    <div className="page">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="customer-header">

        <div>

          <Link
            to="/"
            className="back-link"
          >
            ← Back to Customers
          </Link>

          <h1>
            {customer.name ||
              "Unnamed Customer"}
          </h1>

          <p className="page-description">
            Master Customer ID:{" "}
            {customer.master_customer_id}
          </p>

        </div>


        <button
          className="primary-button"
          onClick={openEditModal}
        >
          Edit Customer
        </button>

      </div>


      {/* ======================================================
          GOLDEN RECORD
      ====================================================== */}

      <section className="section-card">

        <div className="section-header">

          <div>

            <h2>Golden Record</h2>

            <p>
              Unified customer information
            </p>

          </div>

        </div>


        <div className="field-grid">

          <Field
            label="Full Name"
            value={customer.name}
            source={getLineage("name")}
          />


          <Field
            label="Email"
            value={customer.email}
            source={getLineage("email")}
          />


          <Field
            label="Phone"
            value={customer.phone}
            source={getLineage("phone")}
          />


          <Field
            label="Date of Birth"
            value={customer.dob}
            source={getLineage("dob")}
          />


          <Field
            label="Address"
            value={customer.address}
            source={getLineage("address")}
          />

        </div>

      </section>


      {/* ======================================================
          PRODUCT PORTFOLIO
      ====================================================== */}

      <section className="section-card">

        <div className="section-header">

          <div>

            <h2>
              Product Portfolio
            </h2>

            <p>
              {coreProducts.length +
                creditCards.length +
                loans.length}{" "}
              products linked to this customer
            </p>

          </div>

        </div>


        <div className="portfolio-grid">

          {productSummary.length === 0 && (
            <div className="empty-state">
              No products linked to this customer.
            </div>
          )}


          {productSummary.map(
            (product) => (

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

            )
          )}

        </div>


        {/* ====================================================
            CORE BANKING PRODUCTS
        ==================================================== */}

        {coreProducts.length > 0 && (

          <div className="transaction-list">

            {coreProducts.map(
              (product) => (

                <div
                  className="transaction-row"
                  key={product.core_product_id}
                >

                  <div>

                    <strong>
                      {product.account_type ||
                        "Core Banking Account"}
                    </strong>

                    <small>
                      Account:{" "}
                      {product.account_id ||
                        "—"}
                    </small>

                  </div>

                  <span>
                    Core Banking
                  </span>

                </div>

              )
            )}

          </div>

        )}


        {/* ====================================================
            CREDIT CARD PRODUCTS
        ==================================================== */}

        {creditCards.length > 0 && (

          <div className="transaction-list">

            {creditCards.map(
              (product) => (

                <div
                  className="transaction-row"
                  key={
                    product.credit_card_product_id
                  }
                >

                  <div>

                    <strong>
                      Credit Card
                    </strong>

                    <small>
                      Account:{" "}
                      {product.account_id ||
                        "—"}
                    </small>

                  </div>

                  <span>
                    Limit:{" "}
                    {formatCurrency(
                      product.credit_limit
                    )}
                  </span>

                </div>

              )
            )}

          </div>

        )}


        {/* ====================================================
            LOAN PRODUCTS
        ==================================================== */}

        {loans.length > 0 && (

          <div className="transaction-list">

            {loans.map(
              (product) => (

                <div
                  className="transaction-row"
                  key={product.loan_product_id}
                >

                  <div>

                    <strong>
                      Loan
                    </strong>

                    <small>
                      Source: Loan
                    </small>

                  </div>

                  <span>
                    {formatCurrency(
                      product.loan_amount
                    )}
                  </span>

                </div>

              )
            )}

          </div>

        )}

      </section>


      {/* ======================================================
          TRANSACTION HISTORY
      ====================================================== */}

      <section className="section-card">

        <div className="section-header">

          <div>

            <h2>
              Transaction History
            </h2>

            <p>
              Recent customer transactions
            </p>

          </div>

        </div>


        {transactions.length === 0 ? (

          <div className="empty-state">
            No transactions found.
          </div>

        ) : (

          <div className="transaction-timeline">

            {transactions.map(
              (transaction) => (

                <div
                  className="transaction-item"
                  key={
                    transaction.transaction_id
                  }
                >

                  <div className="transaction-date">

                    {formatDate(
                      transaction.transaction_date
                    )}

                  </div>


                  <div className="transaction-details">

                    <div>

                      <strong className="transaction-amount">

                        {formatCurrency(
                          transaction.amount
                        )}

                      </strong>


                      <span
                        className={`transaction-type ${
                          transaction.transaction_type
                            ?.toLowerCase() || ""
                        }`}
                      >

                        {transaction.transaction_type ||
                          "Transaction"}

                      </span>

                    </div>


                    <span className="transaction-account">

                      {transaction.account_id ||
                        transaction.product_type ||
                        "Account"}

                    </span>

                  </div>

                </div>

              )
            )}

          </div>

        )}

      </section>


      {/* ======================================================
          AUDIT HISTORY
      ====================================================== */}

      <section className="section-card">

        <div className="section-header">

          <div>

            <h2>
              Audit History
            </h2>

            <p>
              Changes made to this customer record
            </p>

          </div>

        </div>


        {auditLogs.length === 0 ? (

          <div className="empty-state">
            No audit history found.
          </div>

        ) : (

          <div className="transaction-list">

            {auditLogs.map(
              (audit) => (

                <div
                  className="transaction-row"
                  key={audit.audit_id}
                >

                  <div>

                    <strong>

                      {audit.field_name
                        ? `${capitalize(
                            audit.field_name
                          )} updated`
                        : "Customer record updated"}

                    </strong>


                    <small>

                      {audit.changed_by ||
                        "System"}

                      {" · "}

                      {audit.action ||
                        "UPDATE"}


                      {audit.old_value !== null &&
                        audit.new_value !== null &&
                        ` · ${audit.old_value} → ${audit.new_value}`}

                    </small>

                  </div>


                  <span>

                    {formatDateTime(
                      audit.changed_at
                    )}

                  </span>

                </div>

              )
            )}

          </div>

        )}

      </section>


      {/* ======================================================
          EDIT CUSTOMER MODAL
      ====================================================== */}

      {isEditing && (

        <div className="modal-overlay">

          <div className="modal">

            <div className="modal-header">

              <h2>
                Edit Customer
              </h2>


              <button
                className="close-button"
                onClick={() =>
                  setIsEditing(false)
                }
                disabled={isSaving}
              >
                ×
              </button>

            </div>


            <label>

              Name

              <input
                type="text"
                name="name"
                value={editForm.name}
                onChange={handleInputChange}
              />

            </label>


            <label>

              Email

              <input
                type="email"
                name="email"
                value={editForm.email}
                onChange={handleInputChange}
              />

            </label>


            <label>

              Phone

              <input
                type="text"
                name="phone"
                value={editForm.phone}
                onChange={handleInputChange}
              />

            </label>


            <label>

              Date of Birth

              <input
                type="date"
                name="dob"
                value={editForm.dob || ""}
                onChange={handleInputChange}
              />

            </label>


            <label>

              Address

              <input
                type="text"
                name="address"
                value={editForm.address}
                onChange={handleInputChange}
              />

            </label>


            <div className="modal-actions">

              <button
                className="secondary-button"
                onClick={() =>
                  setIsEditing(false)
                }
                disabled={isSaving}
              >
                Cancel
              </button>


              <button
                className="primary-button"
                onClick={handleSave}
                disabled={isSaving}
              >
                {isSaving
                  ? "Saving..."
                  : "Save Changes"}
              </button>

            </div>

          </div>

        </div>

      )}

    </div>
  );
}


/* ============================================================
   GOLDEN RECORD FIELD
============================================================ */

function Field({
  label,
  value,
  source,
}) {

  /*
   * Map database source identifiers to
   * business-facing names.
   *
   * SourceA → Core Banking
   * SourceB → Credit Card
   * SourceC → Loan
   */

  const sourceLabels = {
    SourceA: "Core Banking",
    SourceB: "Credit Card",
    SourceC: "Loan",
  };


  const sourceName = source
    ? sourceLabels[source.source_system] ||
      source.source_system ||
      "Unknown Source"
    : "Source unavailable";


  return (
    <div className="field">

      <label>
        {label}
      </label>


      <strong>
        {value || "—"}
      </strong>


      <span className="source-badge">
        ● {sourceName}
      </span>

    </div>
  );
}


/* ============================================================
   DATE FORMATTER
============================================================ */

function formatDate(date) {

  if (!date) {
    return "—";
  }


  const parsedDate = new Date(date);


  if (Number.isNaN(parsedDate.getTime())) {
    return date;
  }


  return parsedDate.toLocaleDateString(
    "en-IN",
    {
      month: "short",
      day: "numeric",
      year: "numeric",
    }
  );
}


/* ============================================================
   DATE + TIME FORMATTER
============================================================ */

function formatDateTime(date) {

  if (!date) {
    return "—";
  }


  const parsedDate = new Date(date);


  if (Number.isNaN(parsedDate.getTime())) {
    return date;
  }


  return parsedDate.toLocaleString(
    "en-IN",
    {
      dateStyle: "medium",
      timeStyle: "short",
    }
  );
}


/* ============================================================
   CURRENCY FORMATTER
============================================================ */

function formatCurrency(value) {

  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—";
  }


  const number = Number(value);


  if (Number.isNaN(number)) {
    return value;
  }


  return new Intl.NumberFormat(
    "en-IN",
    {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 2,
    }
  ).format(number);
}


/* ============================================================
   CAPITALIZE
============================================================ */

function capitalize(value) {

  if (!value) {
    return "";
  }


  return (
    value.charAt(0).toUpperCase() +
    value.slice(1)
  );
}


export default Customer360;