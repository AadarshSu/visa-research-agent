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

function sourceSubtext(source) {
  const retrieved = new Date(source.retrieved_at).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
  return `${source.authority} · retrieved ${retrieved}`;
}

// One card component for every outgoing link. Role is either the single action
// the traveller must take ("action") or supporting provenance ("evidence").
function linkCard(role, title, url, subtext) {
  const card = externalLink("", url, `link-card link-card--${role}`);
  const body = element("div", "link-card-body");
  body.append(
    element("span", "link-card-role", role === "action" ? "Go here" : "Evidence"),
    element("span", "link-card-title", title),
  );
  if (subtext) body.append(element("span", "link-card-sub", subtext));
  card.append(body, element("span", "link-card-arrow", "↗"));
  return card;
}

// Give every source a single home section so no link is repeated across the page.
// Priority runs most-specific first; the first section to claim a source keeps it.
function assignSourceHomes(plan) {
  const home = new Map();
  const claim = (ids, section) =>
    (ids || []).forEach((id) => {
      if (!home.has(id)) home.set(id, section);
    });
  claim(plan.application_document_source_ids, "requirements");
  claim(plan.decision_source_ids, "decision");
  if (plan.where_to_apply) claim(plan.where_to_apply.source_ids, "apply");
  plan.application_steps.forEach((step) => claim(step.source_ids, "timeline"));
  return home;
}

function renderEvidence(sourceIds, ctx, section) {
  const group = element("div", "link-cards");
  [...new Set(sourceIds)].forEach((id) => {
    if (ctx.home.get(id) !== section || ctx.seen.has(id)) return;
    const source = ctx.sourceMap.get(id);
    if (!source || ctx.seenUrls.has(String(source.url))) return;
    ctx.seen.add(id);
    ctx.seenUrls.add(String(source.url));
    group.append(linkCard("evidence", source.title, source.url, sourceSubtext(source)));
  });
  return group;
}

function appendIfFilled(container, group) {
  if (group.childElementCount) container.append(group);
}

function renderDecision(plan, ctx) {
  const { container, header } = panel(plan.destination, "Visa decision");
  const decision = plan.visa_required === null ? "Uncertain" : plan.visa_required ? "Visa required" : "No visa required";
  header.append(element("span", "decision-chip", decision));
  container.append(element("p", "lead", `${plan.visa_type || "Visa type unresolved"}. ${plan.explanation}`));
  appendIfFilled(container, renderEvidence(plan.decision_source_ids, ctx, "decision"));
  return container;
}

function renderApplicationLocation(plan, ctx) {
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
  container.append(grid);

  const actions = element("div", "link-cards");
  ctx.seenUrls.add(String(location.application_url));
  actions.append(
    linkCard("action", "Official application route", location.application_url, location.authority),
  );
  container.append(actions);
  appendIfFilled(container, renderEvidence(location.source_ids, ctx, "apply"));
  return container;
}

function renderRequirements(plan, ctx) {
  const { container } = panel("Visa application documents", "Official checklist");

  container.append(
    element(
      "p",
      "lead",
      "Extracted from the designated official application-document source. Confirm the linked guidance before applying; general entry and travel duties are excluded.",
    ),
  );
  appendIfFilled(container, renderEvidence(plan.application_document_source_ids, ctx, "requirements"));

  const list = element("div", "requirement-list");
  plan.requirements.forEach((requirement) => {
    const card = element("article", "requirement-card");
    card.append(
      element("h3", "", requirement.name),
      element("p", "", requirement.description),
      element("p", "reason", `Source context: ${requirement.reason_it_applies}`),
    );
    list.append(card);
  });
  container.append(list);
  return container;
}

function renderSteps(plan, ctx) {
  const { container } = panel("Application timeline", "Actionable sequence");
  const list = element("ol", "steps");
  plan.application_steps.forEach((step) => {
    const item = element("li");
    const content = element("div", "step-content");
    content.append(
      element("p", "step-timing", `Timing: ${step.timing}`),
      element("h3", "", step.title),
      element("p", "", step.action),
    );
    item.append(content);
    list.append(item);
  });
  container.append(list);

  // Provenance for the steps, grouped once and deduped against the rest of the page,
  // rather than a link repeated inside each step.
  const timelineSources = plan.application_steps.flatMap((step) => step.source_ids);
  const evidence = renderEvidence(timelineSources, ctx, "timeline");
  if (evidence.childElementCount) {
    container.append(element("p", "eyebrow evidence-eyebrow", "Sources for these steps"));
    container.append(evidence);
  }
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
  const ctx = {
    sourceMap: new Map(plan.sources.map((source) => [source.source_id, source])),
    home: assignSourceHomes(plan),
    seen: new Set(),
    seenUrls: new Set(),
  };
  results.replaceChildren(
    renderDecision(plan, ctx),
    renderApplicationLocation(plan, ctx),
    renderRequirements(plan, ctx),
    renderSteps(plan, ctx),
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
