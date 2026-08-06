const form = document.querySelector("#plan-form");
const destinationSelect = document.querySelector("#destination");
const generateButton = document.querySelector("#generate-button");
const progress = document.querySelector("#progress");
const errorMessage = document.querySelector("#error-message");
const results = document.querySelector("#results");

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function externalLink(label, url, className = "") {
  const link = element("a", className, label);
  link.href = url;
  link.target = "_blank";
  link.rel = "noreferrer noopener";
  return link;
}

function panel(title, eyebrow) {
  const container = element("section", "panel");
  const header = element("div", "panel-header");
  const headingGroup = element("div");
  headingGroup.append(element("p", "eyebrow", eyebrow), element("h2", "", title));
  header.append(headingGroup);
  container.append(header);
  return { container, header };
}

function renderCitations(sourceIds, sourceMap) {
  const citations = element("div", "citations");
  sourceIds.forEach((sourceId) => {
    const source = sourceMap.get(sourceId);
    if (source) citations.append(externalLink(source.title, source.url, "citation"));
  });
  return citations;
}

function renderDecision(plan) {
  const { container, header } = panel(plan.destination, "Visa decision");
  const decision = plan.visa_required === null ? "Uncertain" : plan.visa_required ? "Visa required" : "No visa required";
  header.append(element("span", "decision-chip", decision));
  container.append(
    element("p", "lead", `${plan.visa_type || "Visa type unresolved"}. ${plan.explanation}`),
  );
  return container;
}

function renderApplicationLocation(plan) {
  const { container } = panel("Where to apply", "UK application route");
  const location = plan.where_to_apply;
  if (!location) {
    container.append(element("p", "lead", "The application location remains unresolved."));
    return container;
  }

  const grid = element("div", "detail-grid");
  const details = [
    ["Authority", location.authority],
    ["Method", location.application_method],
    ["Location", location.location || "Online"],
  ];
  details.forEach(([label, value]) => {
    const cell = element("div", "detail-cell");
    cell.append(element("span", "", label), element("p", "", value));
    grid.append(cell);
  });
  container.append(grid, externalLink("Open the official application route ↗", location.application_url));
  return container;
}

function renderRequirements(plan, sourceMap) {
  const { container } = panel("Document checklist", "Requirements");
  const labels = {
    mandatory: "Mandatory",
    conditional: "Conditional",
    recommended: "Recommended",
  };

  Object.entries(labels).forEach(([category, label]) => {
    const requirements = plan.requirements.filter((item) => item.category === category);
    const group = element("div", "requirement-group");
    group.append(element("span", `category-label ${category}`, `${label} · ${requirements.length}`));
    const list = element("div", "requirement-list");
    requirements.forEach((requirement) => {
      const card = element("article", "requirement-card");
      card.append(
        element("h3", "", requirement.name),
        element("p", "", requirement.description),
        element("p", "reason", `Why it applies: ${requirement.reason_it_applies}`),
        renderCitations(requirement.source_ids, sourceMap),
      );
      list.append(card);
    });
    group.append(list);
    container.append(group);
  });
  return container;
}

function renderSteps(plan) {
  const { container } = panel("Application sequence", "Ordered steps");
  const list = element("ol", "steps");
  plan.application_steps.forEach((step) => list.append(element("li", "", step)));
  container.append(list);
  return container;
}

function issueBlock(title, items) {
  const block = element("div", "reliability-block");
  block.append(element("h3", "", title));
  const list = element("ul");
  const displayItems = items.length ? items : ["None reported in this fixture snapshot."];
  displayItems.forEach((item) => list.append(element("li", "", item)));
  block.append(list);
  return block;
}

function renderReliability(plan) {
  const { container } = panel("Evidence and caveats", "Reliability");
  container.append(
    element("p", "checked-at", `Fixture snapshot checked ${new Date(plan.last_checked).toLocaleString()}.`),
  );

  const grid = element("div", "reliability-grid");
  grid.append(
    issueBlock("Unresolved questions", plan.unresolved_questions),
    issueBlock("Source conflicts", plan.conflicts),
  );
  container.append(grid);

  const sourceList = element("div", "source-list");
  plan.sources.forEach((source) => {
    const card = element("article", "source-card");
    card.append(
      externalLink(source.title, source.url),
      element("p", "source-meta", `${source.authority} · retrieved ${new Date(source.retrieved_at).toLocaleString()}`),
    );
    if (source.supporting_excerpt) card.append(element("p", "", source.supporting_excerpt));
    sourceList.append(card);
  });
  container.append(sourceList);
  container.append(
    element(
      "p",
      "disclaimer",
      "Requirements can change. Confirm the current rules, fees, documents and appointment instructions with ICA, the Singapore High Commission and its authorised provider before applying. A visa does not guarantee approval or entry.",
    ),
  );
  return container;
}

function renderPlan(plan) {
  const sourceMap = new Map(plan.sources.map((source) => [source.source_id, source]));
  results.replaceChildren(
    renderDecision(plan),
    renderApplicationLocation(plan),
    renderRequirements(plan, sourceMap),
    renderSteps(plan),
    renderReliability(plan),
  );
}

async function generatePlan(event) {
  event.preventDefault();
  errorMessage.hidden = true;
  progress.hidden = false;
  results.setAttribute("aria-busy", "true");
  generateButton.disabled = true;

  try {
    const response = await fetch("/visa-plans", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ destination: destinationSelect.value }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail?.message || "The plan could not be generated.");
    renderPlan(payload);
    results.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    errorMessage.textContent = error instanceof Error ? error.message : "The plan could not be generated.";
    errorMessage.hidden = false;
  } finally {
    progress.hidden = true;
    results.setAttribute("aria-busy", "false");
    generateButton.disabled = false;
  }
}

form.addEventListener("submit", generatePlan);
