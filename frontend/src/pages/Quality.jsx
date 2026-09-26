const matchRecords = [
  {
    id: 1,
    sourceA: "John Doe",
    sourceB: "Jon Doe",
    matchType: "Phone Match",
    confidence: 98,
    status: "Matched",
  },
  {
    id: 2,
    sourceA: "Priya Shah",
    sourceB: "Priya S.",
    matchType: "Email Match",
    confidence: 96,
    status: "Matched",
  },
  {
    id: 3,
    sourceA: "Rahul Kumar",
    sourceB: "Rahul K.",
    matchType: "Name + Address",
    confidence: 91,
    status: "Fuzzy Match",
  },
  {
    id: 4,
    sourceA: "Ananya Rao",
    sourceB: "Ananya R.",
    matchType: "Name + Address",
    confidence: 87,
    status: "Fuzzy Match",
  },
];

function Quality() {
  const matched = matchRecords.filter(
    (record) => record.status === "Matched"
  ).length;

  const fuzzy = matchRecords.filter(
    (record) => record.status === "Fuzzy Match"
  ).length;

  return (
    <>
      <h1>Data Quality</h1>

      <p className="page-description">
        Review identity matches and data quality.
      </p>

      <div className="quality-summary">
        <div className="quality-stat">
          <span>Matched Records</span>
          <strong>{matched}</strong>
        </div>

        <div className="quality-stat">
          <span>Fuzzy Matches</span>
          <strong>{fuzzy}</strong>
        </div>
      </div>

      <div className="section-card">
        <div className="section-header">
          <div>
            <h2>Match Review</h2>
            <p>Identity matching results</p>
          </div>
        </div>

        <div className="match-table">
          <div className="match-table-header">
            <span>Source Record A</span>
            <span>Source Record B</span>
            <span>Match Method</span>
            <span>Confidence</span>
            <span>Status</span>
          </div>

          {matchRecords.map((record) => (
            <div className="match-table-row" key={record.id}>
              <strong>{record.sourceA}</strong>

              <strong>{record.sourceB}</strong>

              <span>{record.matchType}</span>

              <span className="confidence">
                {record.confidence}%
              </span>

              <span
                className={`match-status ${record.status
                  .toLowerCase()
                  .replace(" ", "-")}`}
              >
                {record.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

export default Quality;