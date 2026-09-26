const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * Generic API request helper.
 */
async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  let data = null;

  try {
    data = await response.json();
  } catch {
    // Some responses may not contain JSON.
  }

  if (!response.ok) {
    const message =
      data?.detail ||
      `Request failed with status ${response.status}`;

    throw new Error(message);
  }

  return data;
}


/**
 * GET /api/customers
 *
 * Optional search:
 * GET /api/customers?search=john
 */
export async function getCustomers(search = "") {
  const trimmedSearch = search.trim();

  const query = trimmedSearch
    ? `?search=${encodeURIComponent(trimmedSearch)}`
    : "";

  return apiRequest(`/api/customers${query}`);
}


/**
 * GET /api/customers/{customer_id}
 *
 * Returns the complete Customer 360 profile.
 */
export async function getCustomerById(customerId) {
  return apiRequest(`/api/customers/${encodeURIComponent(customerId)}`);
}


/**
 * PATCH /api/customers/{customer_id}
 *
 * Updates Golden Record fields.
 *
 * Example:
 * {
 *   name: "John Doe",
 *   email: "john@example.com",
 *   phone: "9876543210",
 *   address: "Mumbai",
 *   changed_by: "Data Steward"
 * }
 */
export async function updateCustomer(customerId, customerData) {
  return apiRequest(
    `/api/customers/${encodeURIComponent(customerId)}`,
    {
      method: "PATCH",
      body: JSON.stringify(customerData),
    }
  );
}


/**
 * GET /api/customers/{customer_id}/audit
 */
export async function getCustomerAudit(customerId) {
  return apiRequest(
    `/api/customers/${encodeURIComponent(customerId)}/audit`
  );
}