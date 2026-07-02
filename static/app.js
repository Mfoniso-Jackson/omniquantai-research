const state = {
  runId: null,
};

const $ = (id) => document.getElementById(id);

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function postJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "Request failed");
  return payload;
}

function renderBids(bids) {
  return `<table class="evidence-table">
    <thead><tr><th>Seller</th><th>Price</th><th>Speed</th><th>Confidence</th><th>Value</th><th>Reasoning</th></tr></thead>
    <tbody>${bids
      .map(
        (bid) => `<tr>
          <td>${escapeHtml(bid.name)}<div class="muted">${escapeHtml(bid.domain)}</div></td>
          <td>${escapeHtml(bid.price_sol)} SOL</td>
          <td>${escapeHtml(bid.speed_seconds)}s</td>
          <td>${escapeHtml(bid.confidence)}/100</td>
          <td><strong>${escapeHtml(bid.value_score)}</strong></td>
          <td>${escapeHtml(bid.bid_reasoning)}<div class="muted">${escapeHtml(bid.reason)}</div></td>
        </tr>`
      )
      .join("")}</tbody>
  </table>`;
}

function renderMarketplace(flow) {
  $("marketStatus").textContent = "Auction complete";
  $("winnerName").textContent = flow.selection.selected_winner.name;
  $("escrowStatus").textContent = flow.escrow.status;
  $("marketRecommendation").textContent = flow.final_report.recommendation;

  $("agentBids").classList.remove("muted");
  $("winnerReasoning").classList.remove("muted");
  $("escrowPanel").classList.remove("muted");
  $("deliveryPanel").classList.remove("muted");
  $("finalThesis").classList.remove("muted");

  $("agentBids").innerHTML = renderBids(flow.bids);
  $("winnerReasoning").innerHTML = `
    <p><strong>${escapeHtml(flow.selection.selected_winner.name)}</strong></p>
    <p>${escapeHtml(flow.selection.final_reasoning)}</p>
    <p class="muted">CoralOS pattern: ${escapeHtml(flow.coralos.coordination_pattern)}</p>
    <p class="muted">Session: ${escapeHtml(flow.coralos.session_id)}</p>
  `;
  $("escrowPanel").innerHTML = `
    <dl class="kv">
      <dt>Network</dt><dd>${escapeHtml(flow.escrow.network)}</dd>
      <dt>Status</dt><dd>${escapeHtml(flow.escrow.status)}</dd>
      <dt>Amount</dt><dd>${escapeHtml(flow.escrow.amount_sol)} SOL</dd>
      <dt>Reference</dt><dd>${escapeHtml(flow.escrow.reference)}</dd>
      <dt>Link</dt><dd><a href="${escapeHtml(flow.escrow.settlement_link)}" target="_blank" rel="noreferrer">Devnet reference</a></dd>
    </dl>
    <p class="muted">${escapeHtml(flow.escrow.note)}</p>
  `;
  $("deliveryPanel").innerHTML = `
    <p><strong>${escapeHtml(flow.delivery.agent_name)}</strong></p>
    <p>${escapeHtml(flow.delivery.recommendation_contribution)}</p>
    <h2>Key Evidence</h2>${renderList(flow.delivery.key_evidence)}
    <h2>Risks</h2>${renderList(flow.delivery.risks)}
    <p class="muted">${escapeHtml(flow.delivery.disclaimer)}</p>
  `;
  $("finalThesis").innerHTML = `
    <p>${escapeHtml(flow.final_report.executive_summary)}</p>
    <dl class="kv">
      <dt>Recommendation</dt><dd>${escapeHtml(flow.final_report.recommendation)}</dd>
      <dt>Confidence</dt><dd>${escapeHtml(flow.final_report.confidence_score)}/100</dd>
    </dl>
    <h2>Hypotheses</h2>
    ${renderList(flow.final_report.hypotheses.map((item) => `${item.case}: ${item.probability}% - ${item.thesis}`))}
    <p class="muted">${escapeHtml(flow.final_report.human_approval_reminder)}</p>
  `;
}

async function runMarketplace() {
  const button = $("runMarketplace");
  button.disabled = true;
  button.textContent = "Running";
  try {
    const flow = await postJson("/api/marketplace", { request: $("marketRequest").value });
    renderMarketplace(flow);
  } catch (error) {
    alert(error.message);
  } finally {
    button.disabled = false;
    button.textContent = "Run Agent Market";
  }
}

function renderKv(data) {
  return `<dl class="kv">${Object.entries(data)
    .filter(([key]) => key !== "source_metadata")
    .map(([key, value]) => {
      const cleanKey = key.replaceAll("_", " ");
      const cleanValue = Array.isArray(value)
        ? `<ul class="list">${value.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
        : escapeHtml(value);
      return `<dt>${escapeHtml(cleanKey)}</dt><dd>${cleanValue}</dd>`;
    })
    .join("")}</dl>`;
}

function renderList(items) {
  return `<ul class="list">${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function renderEvidence(items) {
  return `<table class="evidence-table">
    <thead><tr><th>Stance</th><th>Claim</th><th>Strength</th><th>Source</th><th>Detail</th><th>Timestamp</th></tr></thead>
    <tbody>${items
      .map(
        (item) => {
          const citation = item.source_url
            ? `<div><a href="${escapeHtml(item.source_url)}" target="_blank" rel="noreferrer">Citation</a></div>`
            : "";
          return `<tr>
            <td><span class="tag ${escapeHtml(item.stance)}">${escapeHtml(item.stance)}</span></td>
            <td>${escapeHtml(item.claim)}</td>
            <td>${escapeHtml(item.strength)}</td>
            <td>${escapeHtml(item.source)}${citation}</td>
            <td>${escapeHtml(item.detail)}</td>
            <td>${escapeHtml(item.timestamp || "n/a")}</td>
          </tr>`;
        }
      )
      .join("")}</tbody>
  </table>`;
}

function portfolioContext() {
  return {
    current_weight: $("currentWeight").value.trim(),
    max_weight: $("maxWeight").value.trim(),
    mandate: $("mandate").value.trim(),
  };
}

function renderPortfolioContext(context) {
  const entries = Object.entries(context || {});
  if (!entries.length) return "";
  return `<h2>Portfolio Context</h2><dl class="kv">${entries
    .map(([key, value]) => `<dt>${escapeHtml(key.replaceAll("_", " "))}</dt><dd>${escapeHtml(value)}</dd>`)
    .join("")}</dl>`;
}

function memoUrl() {
  return state.runId ? `/api/memo?run_id=${encodeURIComponent(state.runId)}` : "#";
}

function exportMemo() {
  if (!state.runId) return;
  window.location.href = memoUrl();
}

function renderHypotheses(items) {
  return items
    .map(
      (item) => `<div class="hypothesis-row">
        <strong>${escapeHtml(item.name)}</strong>
        <div>
          <div>${escapeHtml(item.thesis)}</div>
          <small class="muted">Supports: ${escapeHtml(item.supporting_evidence.join("; "))}</small>
        </div>
        <strong>${escapeHtml(item.probability)}%</strong>
      </div>`
    )
    .join("");
}

function renderExplanation(explanation) {
  const note = explanation.scenario_note ? `<p><strong>${escapeHtml(explanation.scenario_note)}</strong></p>` : "";
  return `
    <p>${escapeHtml(explanation.executive_summary)}</p>
    ${note}
    <h2>Counterarguments</h2>
    ${renderList(explanation.counterarguments)}
    <h2>What Would Change The Recommendation</h2>
    ${renderList(explanation.what_would_change_the_recommendation)}
    <p class="muted">${escapeHtml(explanation.disclaimer)}</p>
  `;
}

function renderRun(run) {
  state.runId = run.run_id;
  $("exportMemo").disabled = false;
  $("providerMode").textContent = run.provider_mode || "Mock data";
  $("action").innerHTML = `<span class="tag ${run.recommendation.action.toLowerCase()}">${escapeHtml(run.recommendation.action)}</span>`;
  $("confidence").textContent = `${run.recommendation.confidence_score}/100`;
  $("asset").textContent = `${run.asset.company} (${run.asset.ticker})`;
  $("horizon").textContent = run.recommendation.time_horizon;

  $("market").classList.remove("muted");
  $("news").classList.remove("muted");
  $("macro").classList.remove("muted");
  $("evidence").classList.remove("muted");
  $("hypotheses").classList.remove("muted");
  $("risks").classList.remove("muted");
  $("recommendation").classList.remove("muted");
  $("explanation").classList.remove("muted");

  $("market").innerHTML = renderKv(run.market);
  $("news").innerHTML = renderKv(run.news);
  $("macro").innerHTML = renderKv(run.macro);
  $("evidence").innerHTML = renderEvidence(run.evidence);
  $("hypotheses").innerHTML = renderHypotheses(run.hypotheses);
  $("risks").innerHTML = renderKv(run.risks);
  $("recommendation").innerHTML = renderKv(run.recommendation);
  $("explanation").innerHTML = renderPortfolioContext(run.portfolio_context) + renderExplanation(run.explanation);
}

async function runResearch() {
  const button = $("runResearch");
  button.disabled = true;
  button.textContent = "Running";
  try {
    const run = await postJson("/api/research", {
      query: $("query").value,
      portfolio_context: portfolioContext(),
    });
    renderRun(run);
  } catch (error) {
    alert(error.message);
  } finally {
    button.disabled = false;
    button.textContent = "Run Research";
  }
}

async function runScenario() {
  const button = $("runScenario");
  button.disabled = true;
  button.textContent = "Running";
  try {
    const run = await postJson("/api/scenario", { run_id: state.runId, scenario: $("scenario").value });
    renderRun(run);
  } catch (error) {
    alert(error.message);
  } finally {
    button.disabled = false;
    button.textContent = "Run Scenario";
  }
}

$("runResearch").addEventListener("click", runResearch);
$("runScenario").addEventListener("click", runScenario);
$("exportMemo").addEventListener("click", exportMemo);
$("runMarketplace").addEventListener("click", runMarketplace);
$("marketRequest").addEventListener("keydown", (event) => {
  if (event.key === "Enter") runMarketplace();
});
$("query").addEventListener("keydown", (event) => {
  if (event.key === "Enter") runResearch();
});
$("scenario").addEventListener("keydown", (event) => {
  if (event.key === "Enter") runScenario();
});

runMarketplace();
runResearch();
