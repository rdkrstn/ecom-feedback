interface BandSetupPanelProps {
  kickoffMessage: string;
  reviewId?: string;
}

const agents = [
  "Intake Review",
  "Customer Feedback Review",
  "UGC Review",
  "Support Review",
  "Product Page Review",
  "Action Review"
];

const yamlExample = `intake_review:
  agent_id: "<band-agent-uuid>"
  api_key: "<band-agent-api-key>"
customer_feedback_review:
  agent_id: "<band-agent-uuid>"
  api_key: "<band-agent-api-key>"
ugc_review:
  agent_id: "<band-agent-uuid>"
  api_key: "<band-agent-api-key>"
support_review:
  agent_id: "<band-agent-uuid>"
  api_key: "<band-agent-api-key>"
product_page_review:
  agent_id: "<band-agent-uuid>"
  api_key: "<band-agent-api-key>"
action_review:
  agent_id: "<band-agent-uuid>"
  api_key: "<band-agent-api-key>"`;

export function BandSetupPanel({ kickoffMessage, reviewId }: BandSetupPanelProps) {
  return (
    <section className="panel band-panel">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">BAND SETUP</p>
          <h2>REAL BAND MODE CHECKLIST</h2>
        </div>
        {reviewId ? <span className="review-id">review_id={reviewId}</span> : null}
      </div>
      <div className="band-grid">
        <div>
          <h3>REMOTE AGENTS</h3>
          <ul className="plain-list">
            {agents.map((agent) => (
              <li key={agent}>{agent}</li>
            ))}
          </ul>
        </div>
        <div>
          <h3>AGENT CONFIG KEYS</h3>
          <pre className="json-block">{yamlExample}</pre>
        </div>
        <div>
          <h3>RUN COMMANDS</h3>
          <pre className="json-block">{`cd agents
uv sync
uv run python -m sagad_feedback.band_agent --all`}</pre>
          <p>
            Local mock mode works without Band keys. Real mode uses Band rooms for agent coordination and mirrors each
            event into this FastAPI-backed UI.
          </p>
        </div>
        <div>
          <h3>KICKOFF MESSAGE</h3>
          <pre className="json-block">{kickoffMessage || "Create a review to generate the kickoff message."}</pre>
        </div>
      </div>
    </section>
  );
}
