import { useEffect, useState } from "react";

import { getQualityData } from "../api/quality";


function Quality() {
  const [qualityData, setQualityData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  /*
   * ============================================================
   * SOURCE SYSTEM DISPLAY NAMES
   * ============================================================
   */

  const sourceSystemNames = {
    SourceA: "Core Banking",
    SourceB: "Credit Card",
    SourceC: "Loan",
  };


  /*
   * ============================================================
   * LOAD DATA QUALITY
   * ============================================================
   */

  useEffect(() => {
    let cancelled = false;


    async function loadQualityData() {
      try {
        setLoading(true);
        setError("");


        const data = await getQualityData();


        if (cancelled) {
          return;
        }


        setQualityData(data);

      } catch (err) {
        if (!cancelled) {
          setError(
            err.message ||
              "Failed to load data quality."
          );
        }

      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }


    loadQualityData();


    return () => {
      cancelled = true;
    };

  }, []);


  /*
   * ============================================================
   * LOADING STATE
   * ============================================================
   */

  if (loading) {
    return (
      <div className="page">

        <div className="page-header">

          <h1>
            Data Quality
          </h1>

          <p>
            Review identity matches and data quality.
          </p>

        </div>


        <section className="section-card">

          <div className="empty-state">
            Loading data quality...
          </div>

        </section>

      </div>
    );
  }


  /*
   * ============================================================
   * ERROR STATE
   * ============================================================
   */

  if (error) {
    return (
      <div className="page">

        <div className="page-header">

          <h1>
            Data Quality
          </h1>

          <p>
            Review identity matches and data quality.
          </p>

        </div>


        <section className="section-card">

          <div className="empty-state">

            <strong>
              Unable to load data quality
            </strong>

            <p>
              {error}
            </p>

          </div>

        </section>

      </div>
    );
  }


  /*
   * ============================================================
   * DATA
   * ============================================================
   */

  const matches = qualityData?.matches || [];


  /*
   * ============================================================
   * SORT MATCHES
   *
   * Records with a match score come first.
   * Records with NULL match_score come afterward.
   *
   * We do NOT change the actual values.
   * ============================================================
   */

  const sortedMatches = [...matches].sort((a, b) => {

    const aHasScore =
      a.match_score !== null &&
      a.match_score !== undefined;

    const bHasScore =
      b.match_score !== null &&
      b.match_score !== undefined;


    if (aHasScore && !bHasScore) {
      return -1;
    }


    if (!aHasScore && bHasScore) {
      return 1;
    }


    return 0;
  });


  const totalMatches =
    qualityData?.total_matches ||
    matches.length;


  /*
   * ============================================================
   * UI
   * ============================================================
   */

  return (
    <div className="page">


      {/* ======================================================
          PAGE HEADER
      ====================================================== */}

      <div className="page-header">

        <h1>
          Data Quality
        </h1>

        <p>
          Review identity matches and data quality.
        </p>

      </div>


      {/* ======================================================
          SUMMARY CARDS
      ====================================================== */}

      <div className="stats-grid">

        <div className="stat-card">

          <span>
            Identity Matches
          </span>

          <strong>
            {totalMatches}
          </strong>

        </div>


        <div className="stat-card">

          <span>
            Records
          </span>

          <strong>
            {matches.length}
          </strong>

        </div>

      </div>


      {/* ======================================================
          MATCH REVIEW
      ====================================================== */}

      <section className="section-card">


        <div className="section-header">

          <div>

            <h2>
              Match Review
            </h2>

            <p>
              Identity matching results from identity_map
            </p>

          </div>

        </div>


        {sortedMatches.length === 0 ? (

          <div className="empty-state">
            No identity matches found.
          </div>

        ) : (

          <div className="customer-table">


            {/* ==================================================
                TABLE HEADER
            ================================================== */}

            <div className="customer-table-header">

              <span>
                SOURCE SYSTEM
              </span>

              <span>
                SOURCE CUSTOMER ID
              </span>

              <span>
                MASTER CUSTOMER ID
              </span>

              <span>
                MATCH TYPE
              </span>

              <span>
                MATCH SCORE
              </span>

            </div>


            {/* ==================================================
                TABLE ROWS
            ================================================== */}

            {sortedMatches.map((match) => (

              <div
                className="customer-table-row"
                key={match.identity_map_id}
              >


                {/* SOURCE SYSTEM */}

                <div>

                  <strong>
                    {
                      sourceSystemNames[
                        match.source_system
                      ] || match.source_system || "—"
                    }
                  </strong>

                </div>


                {/* SOURCE CUSTOMER ID */}

                <div>

                  <strong>
                    {match.source_customer_id || "—"}
                  </strong>

                </div>


                {/* MASTER CUSTOMER ID */}

                <div>

                  <small>
                    {match.master_customer_id || "—"}
                  </small>

                </div>


                {/* MATCH TYPE */}

                <div>

                  <span>
                    {match.match_type || "—"}
                  </span>

                </div>


                {/* MATCH SCORE */}

                <div>

                  <strong className="quality-score">

                    {match.match_score !== null &&
                    match.match_score !== undefined
                      ? `${(
                          Number(match.match_score) * 100
                        ).toFixed(2)}%`
                      : "—"}

                  </strong>

                </div>


              </div>

            ))}

          </div>

        )}

      </section>

    </div>
  );
}


export default Quality;