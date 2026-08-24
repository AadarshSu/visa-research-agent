const form = document.querySelector("#plan-form");
const destinationSelect = document.querySelector("#destination");
const nationalitySelect = document.querySelector("#nationality");
const residenceSelect = document.querySelector("#residence");
const purposeSelect = document.querySelector("#purpose");
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
  const freshness = source.is_stale ? "could not be re-checked since" : "retrieved";
  return `${source.authority} · ${freshness} ${retrieved}`;
}

// One card component for every outgoing link. Role is either the single action
// the traveller must take ("action") or supporting provenance ("evidence").
function linkCard(role, title, url, subtext, isStale = false) {
  const card = externalLink("", url, `link-card link-card--${role}${isStale ? " link-card--stale" : ""}`);
  const body = element("div", "link-card-body");
  const roleRow = element("span", "link-card-role-row");
  roleRow.append(element("span", "link-card-role", role === "action" ? "Go here" : "Evidence"));
  if (isStale) roleRow.append(element("span", "stale-badge", "Not re-checked"));
  body.append(roleRow, element("span", "link-card-title", title));
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
    group.append(
      linkCard("evidence", source.title, source.url, sourceSubtext(source), source.is_stale),
    );
  });
  return group;
}

function appendIfFilled(container, group) {
  if (group.childElementCount) container.append(group);
}

function hasIncompleteEvidence(plan) {
  return (
    plan.status !== "verified"
    || plan.sources.some((source) => source.is_stale)
    || (plan.unavailable_sources || []).length > 0
  );
}

// A partial plan is still useful, but it must never look as complete as a verified one.
function renderEvidenceBanner(plan) {
  const staleSources = plan.sources.filter((source) => source.is_stale);
  const missing = plan.unavailable_sources || [];
  if (!hasIncompleteEvidence(plan)) return null;

  const banner = element("div", "evidence-banner");
  banner.append(element("p", "evidence-banner-title", "Evidence is incomplete"));

  const list = element("ul");
  missing.forEach((failure) => {
    // An authority refusing this program is the one gap a traveller can close themselves, so it
    // gets the sentence that says so and a link they can open. Everything else stays a statement.
    if (failure.outcome === "blocked" && failure.attempted_url) {
      const item = element(
        "li",
        "",
        `${failure.authority} does not permit automated retrieval, so its guidance could not be `
          + "verified here. It is published at ",
      );
      item.append(externalLink(failure.attempted_url, failure.attempted_url));
      item.append(document.createTextNode(" — open it yourself to check."));
      list.append(item);
      return;
    }
    list.append(
      element("li", "", `${failure.title} (${failure.authority}) — ${failure.detail}`),
    );
  });
  staleSources.forEach((source) => {
    const checked = new Date(source.retrieved_at).toLocaleDateString();
    list.append(
      element(
        "li",
        "",
        `${source.title} could not be re-checked; showing the copy retrieved ${checked}.`,
      ),
    );
  });
  banner.append(list);
  banner.append(
    element(
      "p",
      "evidence-banner-note",
      "Everything in this plan is still drawn only from official sources, but confirm these points "
        + "directly with the responsible authority before you rely on them.",
    ),
  );
  return banner;
}

// A question an authority answers only through its own questionnaire is guidance it has published,
// not a gap: the traveller can get the real answer in a few clicks, which is more than a page we
// could not find gives them. So a tool is offered beside the question it settles rather than filed
// under caveats — and never as evidence, because nobody has answered it.
const TOOL_TOPICS = {
  visa_decision: ["decides whether you need a visa", "the decision for your own passport and trip"],
  document_checklist: ["lists the documents through a questionnaire", "the document list for your own application"],
  application_route: ["sets out where to apply through a questionnaire", "where and how you apply"],
  fees: ["works out the fee through a questionnaire", "the fee for your own application"],
  processing_times: ["works out the processing time through a questionnaire", "how long your own application should take"],
  general_entry: ["sets out entry requirements through a questionnaire", "the entry requirements for your own trip"],
};

function toolsFor(plan, topic) {
  return (plan.official_tools || []).filter((tool) => tool.topic === topic);
}

function toolCallout(tool) {
  const [what, gives] = TOOL_TOPICS[tool.topic] || ["answers this through a questionnaire", "the answer for your own trip"];
  const callout = element("div", "decision-tool");
  callout.append(element("p", "decision-tool-title", `${tool.authority} ${what}`));
  const body = element("p", "", `This is the official tool, and answering its questions gives you ${gives}. It asks things we cannot answer on your behalf. Open it at `);
  body.append(externalLink(tool.url, tool.url));
  body.append(document.createTextNode("."));
  callout.append(body);
  return callout;
}

function appendTools(container, plan, topic) {
  toolsFor(plan, topic).forEach((tool) => container.append(toolCallout(tool)));
}

function renderDecision(plan, ctx) {
  const { container, header } = panel(plan.destination, "Visa decision");
  const decision = plan.visa_required === null ? "Uncertain" : plan.visa_required ? "Visa required" : "No visa required";
  const chips = element("div", "chip-group");
  chips.append(
    element("span", "decision-chip", decision),
    element("span", `status-chip status-chip--${plan.status}`, plan.status === "verified" ? "Evidence verified" : "Evidence partial"),
  );
  header.append(chips);
  // A partial plan must not look complete, so it says so above the guidance — but briefly. The
  // reasons and links are long enough to bury the answer, so they sit with the other caveats at the
  // end instead.
  if (hasIncompleteEvidence(plan)) {
    container.append(
      element(
        "p",
        "evidence-pointer",
        "Some evidence is incomplete — see Evidence and caveats below before relying on this.",
      ),
    );
  }
  container.append(element("p", "lead", `${plan.visa_type || "Visa type unresolved"}. ${plan.explanation}`));
  appendTools(container, plan, "visa_decision");
  appendIfFilled(container, renderEvidence(plan.decision_source_ids, ctx, "decision"));
  return container;
}

function renderApplicationLocation(plan, ctx) {
  const { container } = panel("Where to apply", "Application route");
  const location = plan.where_to_apply;
  if (!location) {
    container.append(element("p", "lead", "The application location remains unresolved."));
    appendTools(container, plan, "application_route");
    return container;
  }
  appendTools(container, plan, "application_route");

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
  const checklistTools = toolsFor(plan, "document_checklist");
  // No checklist source means no documents may be listed, so the panel would be a heading and a
  // caveat above nothing. The absence is not hidden by dropping it: it is stated under unresolved
  // questions, which the plan is structurally required to carry when there is no checklist source.
  // Unless the authority publishes its list through a questionnaire — then there is somewhere to
  // send the traveller, and that is worth a panel even with nothing to list.
  if (!plan.requirements.length && !checklistTools.length) return null;

  const { container } = panel("Visa application documents", "Official checklist");

  if (!plan.requirements.length) {
    container.append(
      element(
        "p",
        "lead",
        "No official page lists the documents for this application. The authority publishes them through its own questionnaire instead.",
      ),
    );
    appendTools(container, plan, "document_checklist");
    return container;
  }

  container.append(
    element(
      "p",
      "lead",
      "Extracted from the designated official application-document source. Confirm the linked guidance before applying; general entry and travel duties are excluded.",
    ),
  );
  appendTools(container, plan, "document_checklist");
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
  const displayItems = items.length ? items : ["None reported for this run."];
  displayItems.forEach((item) => list.append(element("li", "", item)));
  block.append(list);
  return block;
}

// Name the authorities this plan actually rests on, so the caveat is never wrong for a country.
function authoritiesSentence(plan) {
  const names = [...new Set(plan.sources.map((source) => source.authority))];
  if (!names.length) return "the responsible authority";
  if (names.length === 1) return names[0];
  return `${names.slice(0, -1).join(", ")} and ${names[names.length - 1]}`;
}

function renderReliability(plan) {
  const { container } = panel("Evidence and caveats", "Reliability");
  const banner = renderEvidenceBanner(plan);
  if (banner) container.append(banner);
  container.append(
    element("p", "checked-at", `Evidence last checked ${new Date(plan.last_checked).toLocaleString()}.`),
  );

  // One block now, so no grid: "Source conflicts" was unverified model prose under a heading that
  // made it read as a finding, and nothing checked it — see DECISIONS entry 30. A disagreement
  // between official pages is stated as something unresolved instead, which is what it honestly is.
  // The two-column grid went with it rather than being left to render one block in half the width.
  // Fees, processing times and entry conditions have no panel of their own — they live inside the
  // steps — so a questionnaire holding one is offered here rather than dropped.
  ["fees", "processing_times", "general_entry"].forEach((topic) => appendTools(container, plan, topic));
  container.append(issueBlock("Unresolved questions", plan.unresolved_questions));
  container.append(
    element(
      "p",
      "disclaimer",
      `Requirements can change. Confirm the current rules, fees, documents and appointment instructions with ${authoritiesSentence(plan)} before applying. A visa does not guarantee approval or entry.`,
    ),
  );
  return container;
}

// Refusing is a legitimate outcome for high-stakes guidance, so it gets a real explanation
// rather than a generic failure message.
function renderRefusal(detail) {
  const { container } = panel("No verified plan", "Evidence unavailable");
  container.append(
    element(
      "p",
      "lead",
      detail.message || "A verified plan could not be produced from official sources.",
    ),
  );

  const reasons = detail.reasons || [];
  if (reasons.length) {
    const block = element("div", "reliability-block");
    block.append(element("h3", "", "What could not be verified"));
    const list = element("ul");
    reasons.forEach((reason) => list.append(element("li", "", reason)));
    block.append(list);
    container.append(block);
  }

  container.append(
    element(
      "p",
      "disclaimer",
      "Rather than show guidance that may be wrong or out of date, no plan is produced. "
        + "Try again later, or check the responsible authority directly.",
    ),
  );
  results.replaceChildren(container);
}

function renderPlan(plan) {
  const ctx = {
    sourceMap: new Map(plan.sources.map((source) => [source.source_id, source])),
    home: assignSourceHomes(plan),
    seen: new Set(),
    seenUrls: new Set(),
  };
  results.replaceChildren(
    ...[
      renderDecision(plan, ctx),
      renderApplicationLocation(plan, ctx),
      renderRequirements(plan, ctx),
      renderSteps(plan, ctx),
      renderReliability(plan),
    ].filter(Boolean),
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
      body: JSON.stringify({
        destination: destinationSelect.value,
        traveller: {
          passport_nationality: nationalitySelect.value,
          country_of_residence: residenceSelect.value,
          travel_purpose: purposeSelect.value,
        },
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      // A refusal names the evidence it could not verify, rather than failing opaquely.
      const detail = payload.detail || {};
      renderRefusal(detail);
      results.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
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
