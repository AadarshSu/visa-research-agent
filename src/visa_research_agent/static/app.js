const form = document.querySelector("#plan-form");
const destinationSelect = document.querySelector("#destination");
const nationalitySelect = document.querySelector("#nationality");
const residenceSelect = document.querySelector("#residence");
const purposeSelect = document.querySelector("#purpose");
const generateButton = document.querySelector("#generate-button");
const progress = document.querySelector("#progress");
const errorMessage = document.querySelector("#error-message");
const results = document.querySelector("#results");
const passportNote = document.querySelector("#passport-note");
const passportChoices = document.querySelector("#passport-choices");

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

// A passage copied from the page, shown only because the application found it in the text it
// retrieved (TODO item 21). It answers "which sentence", where the link card answers "which page".
function appendQuotes(container, quotes, ctx) {
  (quotes || []).forEach((quote) => {
    const source = ctx.sourceMap.get(quote.source_id);
    const figure = element("figure", "source-quote");
    figure.append(element("blockquote", "", `“${quote.text}”`));
    if (source) figure.append(element("figcaption", "", `— ${source.title}`));
    container.append(figure);
  });
}

function appendLinks(item, failures) {
  failures.forEach((failure, index) => {
    if (index) item.append(document.createTextNode(", "));
    item.append(externalLink(failure.attempted_url, failure.attempted_url));
  });
}

// One authority's refusals as one sentence. The pages judged able to hold the visa decision lead,
// said as "may" because nobody read them; the rest follow, linked, never dropped (entry 32 bounds
// what may resolve a corridor, never what is reported).
function refusalItem(authority, failures) {
  const decision = failures.filter((failure) => failure.may_hold_decision);
  const others = failures.filter((failure) => !failure.may_hold_decision);
  const item = element(
    "li",
    "",
    `${authority} does not permit automated retrieval, so its guidance could not be verified here.`,
  );
  if (decision.length) {
    item.append(document.createTextNode(
      decision.length === 1
        ? " Start with the page that may say whether you need a visa: "
        : " Start with the pages that may say whether you need a visa: ",
    ));
    appendLinks(item, decision);
    item.append(document.createTextNode(decision.length === 1 ? " — open it yourself to check." : " — open them yourself to check."));
    if (others.length) {
      item.append(document.createTextNode(others.length === 1 ? " It also refused " : " Other pages it refused: "));
      appendLinks(item, others);
      item.append(document.createTextNode("."));
    }
    return item;
  }
  item.append(document.createTextNode(others.length === 1 ? " It is published at " : " The refused pages are at "));
  appendLinks(item, others);
  item.append(document.createTextNode(others.length === 1 ? " — open it yourself to check." : " — open them yourself to check."));
  return item;
}

// A partial plan is still useful, but it must never look as complete as a verified one.
function renderEvidenceBanner(plan) {
  const staleSources = plan.sources.filter((source) => source.is_stale);
  const missing = plan.unavailable_sources || [];
  if (!hasIncompleteEvidence(plan)) return null;

  const banner = element("div", "evidence-banner");
  banner.append(element("p", "evidence-banner-title", "Evidence is incomplete"));

  const list = element("ul");
  // An authority refusing this program is the one gap a traveller can close themselves, so it gets
  // the sentence that says so and links they can open — once per authority. One US plan said it
  // nine times, the fee table beside the visitor-visa page (TODO item 54). Every page keeps its link.
  const refusals = new Map();
  missing.forEach((failure) => {
    if (failure.outcome !== "blocked" || !failure.attempted_url) return;
    if (!refusals.has(failure.authority)) refusals.set(failure.authority, []);
    refusals.get(failure.authority).push(failure);
  });
  refusals.forEach((failures, authority) => list.append(refusalItem(authority, failures)));
  missing.forEach((failure) => {
    if (failure.outcome === "blocked" && failure.attempted_url) return;
    const item = element("li", "", `${failure.title} (${failure.authority}) — ${failure.detail}`);
    // An official page we could not read is still one the traveller can open, so it gets its link.
    if (failure.attempted_url) {
      item.append(document.createTextNode(". It is at "));
      item.append(externalLink(failure.attempted_url, failure.attempted_url));
      item.append(document.createTextNode(" — open it yourself to check."));
    }
    list.append(item);
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

const DELEGATE_TOPICS = {
  visa_decision: "whether you need a visa",
  document_checklist: "the documents you will need",
  application_route: "how and where to apply",
  fees: "what it costs",
  processing_times: "how long it takes",
  general_entry: "the entry requirements for your trip",
};

function delegatesFor(plan, topic) {
  return (plan.delegated_services || []).filter((service) => service.topic === topic);
}

function delegateCallout(service) {
  const gives = DELEGATE_TOPICS[service.topic] || "the answer for your own trip";
  const callout = element("div", "decision-tool decision-tool--delegated");
  callout.append(element("p", "decision-tool-title", `Published by ${service.provider}, a company rather than a government site`));
  // What was seen is a government page linking to the company for this topic. Whether the authority
  // also publishes it somewhere of its own is not something anyone here established (TODO item 9).
  const body = element("p", "", `For ${gives}, the authority's own page at `);
  body.append(externalLink(service.appointed_by, service.appointed_by));
  body.append(document.createTextNode(" sends you to "));
  body.append(externalLink(service.url, service.url));
  // The honest limit, said where the link is rather than in a footnote. This is a commercial site,
  // so nothing in this plan was read from it and nothing here can vouch for what it says.
  body.append(document.createTextNode(", a company it contracts with. We have not read that site and nothing in this plan comes from it \u2014 check it against the government page above."));
  callout.append(body);
  return callout;
}

function appendDelegates(container, plan, topic, seen) {
  delegatesFor(plan, topic).forEach((service) => {
    if (seen) {
      if (seen.has(service.url)) return;
      seen.add(service.url);
    }
    container.append(delegateCallout(service));
  });
}

function appendTools(container, plan, topic, seen) {
  toolsFor(plan, topic).forEach((tool) => {
    // One page can settle several questions, and each is a different answer worth giving — France's
    // mission page covers the decision, the documents and the fee. So a repeated URL is fine across
    // panels, where the panel supplies the question. It is not fine inside the catch-all panel that
    // carries fees, times and entry conditions together, which would just show the same link thrice.
    if (seen) {
      if (seen.has(tool.url)) return;
      seen.add(tool.url);
    }
    container.append(toolCallout(tool));
  });
}

// A plan whose decision is a stated "no" describes an entry, not an application: no route, no
// checklist, and steps that are duties on arrival rather than stages of a submission. Three panels
// below would otherwise describe an application that does not exist — see DECISIONS entry 95.
// Keyed on false rather than "not true" on purpose: an unverified decision is null, and null keeps
// the application shape so the four questions stay visible for the traveller to notice.
function needsNoVisa(plan) {
  return plan.visa_required === false;
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
  // "Visa type unresolved" is a gap where a visa is needed and noise where none is: nothing failed
  // to resolve, there is simply no visa to have a type.
  const lead = needsNoVisa(plan)
    ? plan.explanation
    : `${plan.visa_type || "Visa type unresolved"}. ${plan.explanation}`;
  container.append(element("p", "lead", lead));
  appendQuotes(container, plan.decision_quotes, ctx);
  appendTools(container, plan, "visa_decision");
  appendDelegates(container, plan, "visa_decision");
  appendIfFilled(container, renderEvidence(plan.decision_source_ids, ctx, "decision"));
  return container;
}

function renderApplicationLocation(plan, ctx) {
  const { container } = panel("Where to apply", "Application route");
  const location = plan.where_to_apply;
  if (!location) {
    // "Unresolved" is a claim about a search that failed, and it is false when the traveller needs
    // no visa: there is nowhere to apply because the question does not arise.
    container.append(
      element(
        "p",
        "lead",
        needsNoVisa(plan)
          ? "There is nowhere to apply \u2014 this traveller needs no visa, so there is no application to make."
          : "The application location remains unresolved.",
      ),
    );
    appendTools(container, plan, "application_route");
    appendDelegates(container, plan, "application_route");
    return container;
  }
  appendTools(container, plan, "application_route");
  appendDelegates(container, plan, "application_route");

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
  // A traveller who needs no visa is owed the panel even with nothing in it, because "no documents"
  // is the answer to the question they came with rather than a gap. The other empty case stays
  // dropped: a heading over nothing states an absence the unresolved questions already carry.
  if (!plan.requirements.length && !checklistTools.length && !needsNoVisa(plan)) return null;

  const { container } = panel("Visa application documents", "Official checklist");

  if (!plan.requirements.length) {
    // Four different reasons end up here and the sentence has to be true of the one that applies.
    // Saying "through its own questionnaire" when the authority actually contracted the work out
    // would misdescribe who published the checklist, which is the thing the reader has to judge.
    // The fourth is not a variant of the other three: nobody withheld this list and nobody
    // contracted it out — there is no application, so there is no list to publish.
    if (needsNoVisa(plan)) {
      container.append(
        element(
          "p",
          "lead",
          "There are no application documents to gather \u2014 this traveller needs no visa. What they must carry and do on arrival is under Before you travel below.",
        ),
      );
      appendTools(container, plan, "document_checklist");
      appendDelegates(container, plan, "document_checklist");
      return container;
    }
    const viaTool = toolsFor(plan, "document_checklist").length > 0;
    const viaDelegate = delegatesFor(plan, "document_checklist").length > 0;
    // Said as what we found, never as what the authority publishes: the same empty list arises when a
    // checklist exists and could not be found or read, and nobody can show that one does not exist.
    let why = "We did not find an official page listing the documents for this application among the pages we could read.";
    if (viaTool && viaDelegate) {
      why += " The authority sets them out through its own questionnaire, and sends applicants to a company it contracts with.";
    } else if (viaTool) {
      why += " The authority sets them out through its own questionnaire.";
    } else if (viaDelegate) {
      why += " The authority sends applicants to a company it contracts with for them.";
    }
    container.append(element("p", "lead", why));
    appendTools(container, plan, "document_checklist");
    appendDelegates(container, plan, "document_checklist");
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
  appendDelegates(container, plan, "document_checklist");
  appendIfFilled(container, renderEvidence(plan.application_document_source_ids, ctx, "requirements"));

  const list = element("div", "requirement-list");
  plan.requirements.forEach((requirement) => {
    const card = element("article", "requirement-card");
    card.append(
      element("h3", "", requirement.name),
      element("p", "", requirement.description),
      element("p", "reason", `Source context: ${requirement.reason_it_applies}`),
    );
    appendQuotes(card, requirement.supporting_quotes, ctx);
    list.append(card);
  });
  container.append(list);
  return container;
}

function renderSteps(plan, ctx) {
  // The steps of a visa-free plan are entry duties, not stages of a submission, and calling them a
  // timeline would describe an application the traveller is not making. Nothing about the list
  // changes; the heading is what has to be true. An entry list may also be empty, where the pages
  // stated the decision and no duty beyond it — the panel is dropped rather than filled.
  const entry = needsNoVisa(plan);
  if (entry && !plan.application_steps.length) return null;
  const { container } = entry
    ? panel("Before you travel", "Entry requirements")
    : panel("Application timeline", "Actionable sequence");
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
  const shown = new Set();
  ["fees", "processing_times", "general_entry"].forEach((topic) => {
    appendTools(container, plan, topic, shown);
    appendDelegates(container, plan, topic, shown);
  });
  container.append(issueBlock("Unresolved questions", plan.unresolved_questions));
  // The standing caveat is about an application, and half of it is false where there is none: there
  // is nothing to apply for and no visa to be approved. What still holds is the part that matters
  // most to a visa-free traveller — the rules change, and the border decides.
  container.append(
    element(
      "p",
      "disclaimer",
      needsNoVisa(plan)
        ? `Entry rules can change, including which passports need a visa. Confirm the current rules with ${authoritiesSentence(plan)} before you travel. Meeting them does not guarantee entry, which is decided at the border.`
        : `Requirements can change. Confirm the current rules, fees, documents and appointment instructions with ${authoritiesSentence(plan)} before applying. A visa does not guarantee approval or entry.`,
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

// Signed in with Ofself, the form starts from what the traveller's account holds (TODO item 55,
// DECISIONS entries 180 and 181): their passports, a residence permit, and journeys they are
// considering. Every part is a default they confirm. One is filled in and stays editable; several
// are offered with none chosen, because a dual national's answer depends on which passport the
// trip is on; none leaves the field to them. Nothing here is ever the default traveller.
//
// An empty answer never becomes "you have none": Ofself answers a schema this app was not granted
// exactly as it answers one with nothing recorded.

const destinationNote = document.querySelector("#destination-note");
const destinationChoices = document.querySelector("#destination-choices");
const residenceNote = document.querySelector("#residence-note");
const residenceChoices = document.querySelector("#residence-choices");
const purposeNote = document.querySelector("#purpose-note");
const ofselfNote = document.querySelector("#ofself-note");

function countryName(code) {
  const option = nationalitySelect.querySelector(`option[value="${code}"]`);
  return option ? option.textContent.trim() : code;
}

// A note keeps its own style — a field's note or the form's — and only its tone changes.
function showNote(note, parts, tone = "") {
  const base = note.dataset.base || (note.dataset.base = note.classList[0]);
  note.replaceChildren(...parts);
  note.className = tone ? `${base} ${base}--${tone}` : base;
  note.hidden = parts.length === 0;
}

function formatDate(value) {
  return new Date(`${value}T00:00:00`).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function markChoice(container, key) {
  container.querySelectorAll("button").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.key === key));
  });
}

// Choices are offered with none pressed; picking one fills the field and says what it came with.
function offerChoices(container, choices, onPick) {
  container.replaceChildren(
    ...choices.map((choice) => {
      const button = element("button", "field-choice", choice.label);
      button.type = "button";
      button.dataset.key = choice.key;
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => {
        markChoice(container, choice.key);
        onPick(choice.value);
      });
      return button;
    }),
  );
  container.hidden = choices.length === 0;
}

// A date the person typed in may raise a question and never close one, so the note says which
// kind of date it is, and an expired document is said plainly.
function expirySentence(record, noun) {
  if (!record.expires_at) return { text: "", tone: "" };
  const when = formatDate(record.expires_at);
  if (record.expired) {
    return { text: ` Ofself records that this ${noun} expired on ${when}.`, tone: "warn" };
  }
  if (record.expiry_attested) {
    return { text: ` Expires ${when}, read from the ${noun} itself.`, tone: "" };
  }
  return {
    text: ` Expires ${when}, as entered in Ofself — check it against the ${noun} itself.`,
    tone: "",
  };
}

function passportSentences(payload) {
  const notes = [];
  for (const withheld of payload.withheld_passports || []) {
    const name = withheld.label || (withheld.nationality ? `${countryName(withheld.nationality)} passport` : "A passport");
    notes.push(
      ` ${name} (document code ${withheld.document_code}) is not offered: this app researches ordinary passports only.`,
    );
  }
  if (payload.other_holders) {
    notes.push(
      ` ${payload.other_holders === 1 ? "One travel document belongs" : `${payload.other_holders} travel documents belong`} to someone else on your account and ${payload.other_holders === 1 ? "is" : "are"} not offered.`,
    );
  }
  if ((payload.unrecognised || []).length) {
    notes.push(
      ` It also lists ${payload.unrecognised.map((value) => `“${value}”`).join(", ")}, which this app has no country data for.`,
    );
  }
  if (payload.encrypted_values) {
    notes.push(" Some of it is encrypted, and this app does not read encrypted details.");
  }
  return notes.join("");
}

function describePassport(passport, lead, extra) {
  const expiry = passport.from_document ? expirySentence(passport, "passport") : { text: "", tone: "" };
  showNote(passportNote, [`${lead}${expiry.text}${extra}`], expiry.tone);
}

function prefillPassport(payload) {
  const passports = payload.passports || [];
  const extra = passportSentences(payload);
  const pick = (passport) => {
    nationalitySelect.value = passport.nationality;
    describePassport(passport, "From your Ofself account. Change it if this trip is on another passport.", extra);
  };
  if (passports.length === 1) {
    pick(passports[0]);
  } else if (passports.length > 1) {
    offerChoices(
      passportChoices,
      passports.map((passport) => ({
        key: passport.nationality,
        label: passport.label || countryName(passport.nationality),
        value: passport,
      })),
      pick,
    );
    showNote(passportNote, [
      `Your Ofself account lists ${passports.length} passports or citizenships. Choose the one this trip is on.${extra}`,
    ]);
  } else if (extra) {
    // Nothing to offer; what was withheld or unreadable is still said. That nothing was shared at
    // all is said once, above the form.
    showNote(passportNote, [extra.trim()]);
  }
  nationalitySelect.addEventListener("change", () => {
    markChoice(passportChoices, nationalitySelect.value);
    const chosen = passports.find((passport) => passport.nationality === nationalitySelect.value);
    if (chosen) describePassport(chosen, "From your Ofself account.", extra);
    else showNote(passportNote, []);
  });
}

function prefillResidence(payload) {
  // A permit that has expired is still shown, marked, but a current one is offered first.
  const residences = [...(payload.residences || [])].sort((a, b) => Number(a.expired) - Number(b.expired));
  const describe = (residence) => {
    const kind = residence.permit_class ? `residence permit (${residence.permit_class})` : "residence permit";
    const expiry = expirySentence(residence, "permit");
    showNote(
      residenceNote,
      [`From your ${kind} in Ofself. Change it if you apply from somewhere else.${expiry.text}`],
      expiry.tone,
    );
  };
  const pick = (residence) => {
    residenceSelect.value = residence.country;
    describe(residence);
  };
  if (residences.length === 1) {
    pick(residences[0]);
  } else if (residences.length > 1) {
    offerChoices(
      residenceChoices,
      residences.map((residence, index) => ({
        key: `${residence.country}-${index}`,
        label: residence.label || countryName(residence.country),
        value: residence,
      })),
      pick,
    );
    showNote(residenceNote, ["Your Ofself account lists more than one residence permit. Choose where you apply from."]);
  }
}

function destinationLabel(select, slug) {
  const option = select.querySelector(`option[value="${slug}"]`);
  return option ? option.textContent.trim() : slug;
}

function windowSentence(plan) {
  if (!plan.earliest && !plan.latest) return "";
  if (plan.earliest && plan.latest) return `, ${formatDate(plan.earliest)} to ${formatDate(plan.latest)}`;
  return `, ${formatDate(plan.earliest || plan.latest)}`;
}

function prefillDestination(payload) {
  const choices = [];
  for (const plan of payload.plans || []) {
    for (const candidate of plan.candidates) {
      // A destination this page cannot research is not offered at all.
      const option = destinationSelect.querySelector(`option[value="${candidate.destination_slug}"]`);
      if (!option || option.disabled) continue;
      choices.push({ plan, candidate });
    }
  }
  const unresolved = payload.unresolved_candidates
    ? ` ${payload.unresolved_candidates === 1 ? "One place" : `${payload.unresolved_candidates} places`} in your plans could not be matched to a country.`
    : "";

  const pick = ({ plan, candidate }) => {
    destinationSelect.value = candidate.destination_slug;
    showNote(destinationNote, [`From your Ofself plan “${plan.label}”${windowSentence(plan)}.${unresolved}`]);
    if (candidate.purpose) {
      purposeSelect.value = candidate.purpose;
      showNote(purposeNote, ["From the same plan."]);
    } else if (candidate.recorded_purpose) {
      showNote(
        purposeNote,
        [`Your plan says “${candidate.recorded_purpose}”, which this app does not research. Choose the closest purpose.`],
        "warn",
      );
    } else {
      showNote(purposeNote, []);
    }
  };

  if (choices.length === 1) {
    pick(choices[0]);
  } else if (choices.length > 1) {
    offerChoices(
      destinationChoices,
      choices.map((choice, index) => ({
        key: String(index),
        label: `${destinationLabel(destinationSelect, choice.candidate.destination_slug)} · ${choice.plan.label}`,
        value: choice,
      })),
      pick,
    );
    showNote(destinationNote, [`From your Ofself plans. Choose a destination to research.${unresolved}`]);
  } else if (unresolved) {
    showNote(destinationNote, [unresolved.trim()]);
  }
  destinationSelect.addEventListener("change", () => {
    markChoice(destinationChoices, "");
    showNote(destinationNote, []);
    showNote(purposeNote, []);
  });
}

async function prefillFromOfself() {
  if (document.body.dataset.signedIn !== "true") return;

  let response;
  let payload = {};
  try {
    response = await fetch("/oauth/traveller", { headers: { Accept: "application/json" } });
    payload = await response.json();
  } catch {
    showNote(ofselfNote, ["Your Ofself account could not be reached. Fill the form in yourself."], "warn");
    return;
  }

  if (!response.ok) {
    const detail = payload.detail || {};
    if (detail.reconnect || detail.sign_in) {
      const link = element("a", "", "Reconnect with Ofself");
      link.href = "/oauth/login";
      showNote(
        ofselfNote,
        ["This app no longer has access to your Ofself account. ", link, " or fill the form in yourself."],
        "warn",
      );
      return;
    }
    showNote(
      ofselfNote,
      [`${detail.message || "Your Ofself details could not be read."} Fill the form in yourself.`],
      "warn",
    );
    return;
  }

  prefillDestination(payload);
  prefillPassport(payload);
  prefillResidence(payload);
  showNote(ofselfNote, [formSentence(payload)]);
}

// One statement for the whole form, so an empty field does not each say the same thing. It never
// says the traveller has no documents or plans: Ofself answers a schema this app was not granted
// exactly as it answers one with nothing recorded.
function formSentence(payload) {
  const found =
    (payload.passports || []).length + (payload.residences || []).length + (payload.plans || []).length;
  if (!found) return "Nothing shared from your Ofself account fills this form yet. Fill it in yourself.";
  return "Fields filled from your Ofself account say so. Check them, and fill in the rest.";
}

prefillFromOfself();
