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

function renderKv(data) {
  return `<dl class="kv">${Object.entries(data)
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
    <thead><tr><th>Stance</th><th>Claim</th><th>Strength</th><th>Source</th><th>Detail</th></tr></thead>
    <tbody>${items
      .map(
        (item) => `<tr>
          <td><span class="tag ${escapeHtml(item.stance)}">${escapeHtml(item.stance)}</span></td>
          <td>${escapeHtml(item.claim)}</td>
          <td>${escapeHtml(item.strength)}</td>
          <td>${escapeHtml(item.source)}</td>
          <td>${escapeHtml(item.detail)}</td>
        </tr>`
      )
      .join("")}</tbody>
  </table>`;
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
  $("explanation").innerHTML = renderExplanation(run.explanation);
}

async function runResearch() {
  const button = $("runResearch");
  button.disabled = true;
  button.textContent = "Running";
  try {
    const run = await postJson("/api/research", { query: $("query").value });
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
$("query").addEventListener("keydown", (event) => {
  if (event.key === "Enter") runResearch();
});
$("scenario").addEventListener("keydown", (event) => {
  if (event.key === "Enter") runScenario();
});

runResearch();
