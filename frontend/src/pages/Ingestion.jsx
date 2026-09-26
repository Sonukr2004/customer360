import { useState } from "react";

const initialFiles = [
  {
    name: "core_banking.csv",
    type: "CSV",
    status: "Valid",
  },
  {
    name: "credit_card.csv",
    type: "CSV",
    status: "Valid",
  },
  {
    name: "loan_system.csv",
    type: "CSV",
    status: "Valid",
  },
  {
    name: "transaction_data.csv",
    type: "CSV",
    status: "Valid",
  },
];

const pipelineSteps = [
  "Validation",
  "Standardization",
  "Matching",
  "Survivorship",
  "Golden Records",
];

function Ingestion() {
  const [files, setFiles] = useState(initialFiles);
  const [running, setRunning] = useState(false);
  const [completed, setCompleted] = useState([]);

  const handleUpload = (event) => {
    const uploadedFiles = Array.from(event.target.files);

    const newFiles = uploadedFiles.map((file) => ({
      name: file.name,
      type: file.name.endsWith(".json") ? "JSON" : "CSV",
      status: "Valid",
    }));

    setFiles((prev) => [...prev, ...newFiles]);
  };

  const runPipeline = () => {
    setRunning(true);
    setCompleted([]);

    pipelineSteps.forEach((step, index) => {
      setTimeout(() => {
        setCompleted((prev) => [...prev, step]);

        if (index === pipelineSteps.length - 1) {
          setRunning(false);
        }
      }, (index + 1) * 700);
    });
  };

  return (
    <>
      <h1>Data Ingestion</h1>

      <p className="page-description">
        Upload source data and run the MDM processing pipeline.
      </p>

      <div className="section-card ingestion-card">
        <div className="section-header">
          <div>
            <h2>Upload Files</h2>
            <p>CSV source files and configuration data</p>
          </div>

          <label className="upload-button">
            + Upload Files
            <input
              type="file"
              multiple
              accept=".csv,.json,.jsonl"
              onChange={handleUpload}
            />
          </label>
        </div>

        <div className="file-list">
          {files.map((file, index) => (
            <div className="file-row" key={`${file.name}-${index}`}>
              <div>
                <strong>{file.name}</strong>
                <small>{file.type}</small>
              </div>

              <span className="valid-status">
                ✓ {file.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="section-card pipeline-card">
        <div className="section-header">
          <div>
            <h2>MDM Pipeline</h2>
            <p>Simulated processing workflow</p>
          </div>

          <button
            className="primary-button"
            onClick={runPipeline}
            disabled={running}
          >
            {running ? "Processing..." : "Run Pipeline"}
          </button>
        </div>

        <div className="pipeline">
          {pipelineSteps.map((step) => {
            const isComplete = completed.includes(step);

            return (
              <div
                className={`pipeline-step ${
                  isComplete ? "pipeline-complete" : ""
                }`}
                key={step}
              >
                <span className="pipeline-icon">
                  {isComplete ? "✓" : "○"}
                </span>

                <span>{step}</span>
              </div>
            );
          })}
        </div>

        {completed.length === pipelineSteps.length && (
          <div className="pipeline-success">
            ✓ Pipeline completed successfully. Golden Records generated.
          </div>
        )}
      </div>
    </>
  );
}

export default Ingestion;