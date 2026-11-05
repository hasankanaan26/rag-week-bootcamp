// ============================================================
// RAG Workbench — vanilla JS, one small function per job
// ============================================================
// Every tab follows the same pattern:
//   1. read the form
//   2. call the endpoint with api()
//   3. turn the JSON into HTML with a render function
// Checkpoint 5: every retrieval call also sends who() — the user
// picked in "Ask as" and the "As of" date — and every source shows
// its title, version, status and effective date.
// ============================================================

// Confidence thresholds, loaded from /health so distance bars
// use the same cut-offs as the server.
let thresholds = { high: 0.8, low: 1.4, no_result: 1.6 };

// Purpose: the "Ask as" user and the "As of" date from the top bar.
function who() {
    return { user: value("askAs"), as_of: value("asOf") };
}

// Purpose: "Expense Policy (2026 edition) · v1 · current · from 2026-11-01 · Team Events"
function provenance(src) {
    if (!src.title) return src.source;
    return src.title + " · v" + src.version + " · " + src.status + " · from " + src.effective_from +
        (src.section ? " · " + src.section : "");
}


// ---------- Helpers ----------

// Purpose: call an endpoint and return JSON, or throw a readable error.
async function api(path, options = {}) {
    const response = await fetch(path, options);
    if (!response.ok) {
        const body = await response.text();
        let detail = body;
        try { detail = JSON.parse(body).detail || body; } catch (e) { /* plain text */ }
        if (typeof detail !== "string") detail = JSON.stringify(detail);
        throw new Error(response.status + ": " + detail);
    }
    return response.json();
}

function postJson(path, payload) {
    return api(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
}

// Purpose: build a query string, skipping empty values.
function withParams(path, params) {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
        if (value !== "" && value !== null && value !== undefined) query.set(key, value);
    }
    const text = query.toString();
    return text ? path + "?" + text : path;
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text == null ? "" : String(text);
    return div.innerHTML;
}

function value(id) {
    return document.getElementById(id).value.trim();
}

function setOutput(id, html) {
    document.getElementById(id).innerHTML = html;
}

function errorBanner(err) {
    return '<div class="banner banner-error">' + escapeHtml(err.message) +
        "<br><small>If the index is empty, open the Sync tab (or run <code>python sync.py --apply</code>).</small></div>";
}

// Purpose: disable a form's button while a request runs, then restore it.
async function runWithBusy(form, outputId, busyText, task) {
    const button = form.querySelector("button");
    const label = button.textContent;
    button.disabled = true;
    button.textContent = busyText;
    setOutput(outputId, '<p class="loading">' + busyText + "</p>");
    try {
        await task();
    } catch (err) {
        setOutput(outputId, errorBanner(err));
    } finally {
        button.disabled = false;
        button.textContent = label;
    }
}


// ---------- Distance display ----------

// Purpose: map a distance to the same level names the server uses.
function distanceLevel(distance) {
    if (distance <= thresholds.high) return "high";
    if (distance <= thresholds.low) return "medium";
    if (distance <= thresholds.no_result) return "low";
    return "none";
}

// Purpose: a short bar means a close match.
function distanceBar(distance, max, level) {
    const width = Math.max(4, Math.min(100, (distance / max) * 100));
    return '<span class="bar"><i class="' + level + '" style="width:' + width + '%"></i></span>';
}

function badge(confidence) {
    return '<span class="badge badge-' + escapeHtml(confidence) + '">' + escapeHtml(confidence) + " confidence</span>";
}

// Purpose: one collapsible row showing a chunk's source, distance and text.
function chunkRow(title, text, distance, extraHtml = "") {
    let distanceHtml = "";
    if (distance !== undefined && distance !== null) {
        const level = distanceLevel(distance);
        distanceHtml = distanceBar(distance, thresholds.no_result * 1.25, level) +
            '<span class="dist">' + distance.toFixed(3) + "</span>";
    }
    return '<details class="chunk"><summary><span class="name">' + escapeHtml(title) + "</span>" +
        distanceHtml + "</summary><pre>" + escapeHtml(text) + "</pre>" + extraHtml + "</details>";
}

function sourcesList(sources) {
    return sources.map((src, i) =>
        chunkRow("#" + (i + 1) + "  " + provenance(src), src.text, src.distance)
    ).join("");
}


// ---------- Status bar ----------

// Purpose: show provider, model, vector store and chunk count in the header.
async function loadStatus() {
    const status = document.getElementById("status");
    try {
        const health = await api("/health");
        thresholds = health.thresholds || thresholds;
        const store = await api("/store/inspect?limit=500").catch(() => null);
        const count = store ? store.total_stored : "?";

        status.replaceChildren(
            chip("Checkpoint ", String(health.checkpoint), "", "ok"),
            chip("LLM ", health.llm_provider, " · " + health.model),
            chip("Embeddings ", health.embedding_model),
            chip("", String(count), " chunks live", count === 0 || count === "?" ? "bad" : "")
        );

        if (store) fillSourceFilter(store.sources);
        if (health.doc_types) fillDocFilter(health.doc_types);
    } catch (err) {
        status.replaceChildren(chip("Server not reachable", "", "", "bad"));
    }
}

// Purpose: one status chip, built with textContent (no HTML strings).
function chip(before, bold, after = "", extraClass = "") {
    const span = document.createElement("span");
    span.className = "chip" + (extraClass ? " " + extraClass : "");
    const b = document.createElement("b");
    b.textContent = bold;
    span.append(document.createTextNode(before), b, document.createTextNode(after));
    return span;
}

// Purpose: add one "force" option per doc type so the fallback is easy to test.
function fillDocFilter(docTypes) {
    const select = document.getElementById("queryDocFilter");
    const current = select.value;
    select.innerHTML =
        '<option value="auto">auto: LLM picks the doc type</option>' +
        '<option value="off">off: search all documents</option>' +
        docTypes.map(t => '<option value="' + escapeHtml(t) + '">force: ' + escapeHtml(t) + "</option>").join("");
    select.value = current;
}

function fillSourceFilter(sources) {
    const select = document.getElementById("storeSource");
    const current = select.value;
    select.innerHTML = '<option value="">All files</option>' +
        sources.map(s => "<option>" + escapeHtml(s) + "</option>").join("");
    select.value = current;
}


// ---------- Ask (RAG): POST /query ----------

async function submitQuery(event) {
    event.preventDefault();
    const url = withParams("/query", {
        ...who(),
        top_k: value("queryTopK"),
        prompt_style: value("queryPromptStyle"),
        high_threshold: value("queryHigh"),
        low_threshold: value("queryLow"),
        no_result_threshold: value("queryNoResult"),
        doc_filter: value("queryDocFilter"),
    });
    await runWithBusy(event.target, "queryOutput", "Classifying, retrieving and generating…", async () => {
        const data = await postJson(url, { question: value("queryQuestion") });
        setOutput("queryOutput", classificationCard(data.doc_filter) + renderRagAnswer(data, true));
    });
}

const FILTER_MODE_LABELS = {
    auto: "auto: LLM classifies the question",
    off: "off: no classification, search all documents",
};

// Purpose: show how the question was classified and how that narrowed retrieval.
function classificationCard(filter) {
    if (!filter) return "";

    const label = filter.doc_type || (filter.mode === "off" ? "filter off" : "unclassified");
    const labelClass = filter.doc_type ? "badge-doctype" : "badge-none";
    const rows = [["Filter mode", escapeHtml(FILTER_MODE_LABELS[filter.mode] || "forced: " + filter.mode)]];

    if (filter.picked_by === "llm") {
        let reply = "<code>" + escapeHtml(filter.classifier_reply || "(empty)") + "</code>";
        if (!filter.doc_type) reply += ' <span class="muted">not one of the known doc types, so no filter</span>';
        rows.push(["LLM reply", reply]);
    }

    if (filter.doc_type) {
        const best = filter.filtered_best_distance;
        rows.push(["Best match in " + escapeHtml(filter.doc_type),
            best != null ? best.toFixed(3) + " (no-result cut-off " + thresholds.no_result + ")" : "no chunks with this doc type"]);
    }

    let outcome;
    if (!filter.doc_type) {
        outcome = '<span class="badge badge-none">unfiltered</span> searched all documents';
    } else if (filter.fallback_used) {
        outcome = '<span class="badge badge-medium">fallback</span> nothing in ' + escapeHtml(filter.doc_type) +
            " was close enough, so all documents were searched";
    } else {
        outcome = '<span class="badge badge-high">filtered</span> searched only ' + escapeHtml(filter.doc_type) + " chunks";
    }
    rows.push(["Retrieval", outcome]);

    return '<div class="card"><h3>Query classification <span class="badge ' + labelClass + '">' + escapeHtml(label) + "</span></h3>" +
        '<table class="kv">' + rows.map(([k, v]) => "<tr><th>" + k + "</th><td>" + v + "</td></tr>").join("") + "</table></div>";
}

// Purpose: answer card + sources, shared by /query and /compare.
function renderRagAnswer(data, showMeta) {
    if (data.no_result) {
        return '<div class="banner banner-none"><b>No relevant documents found.</b> ' + escapeHtml(data.answer) + "</div>" +
            (data.sources && data.sources.length
                ? '<div class="card"><h3>Closest chunks (all beyond the no-result threshold)</h3>' + sourcesList(data.sources) + "</div>"
                : "");
    }

    let html = "";
    if (data.confidence === "low") {
        html += '<div class="banner banner-low">Weak evidence: the retrieved chunks may not answer this. Try rephrasing.</div>';
    }
    html += '<div class="card"><h3>Answer ' + badge(data.confidence) + '</h3><p class="answer">' + escapeHtml(data.answer) + "</p>";
    if (showMeta) {
        html += '<p class="meta">Model ' + escapeHtml(data.model) + (data.request_id ? " · request " + escapeHtml(data.request_id) : "") + "</p>";
    }
    html += "</div>";

    if (data.sources && data.sources.length) {
        html += '<div class="card"><h3>Sources · ' + data.chunks_used + " chunks retrieved</h3>" + sourcesList(data.sources) + "</div>";
    }
    return html;
}


// ---------- RAG vs plain: POST /compare ----------

async function submitCompare(event) {
    event.preventDefault();
    const url = withParams("/compare", { top_k: value("compareTopK"), user: who().user });
    await runWithBusy(event.target, "compareOutput", "Asking both ways…", async () => {
        const data = await postJson(url, { question: value("compareQuestion") });
        setOutput("compareOutput",
            '<div class="columns">' +
                '<div class="card"><h3>With RAG ' + badge(data.rag.confidence) + "</h3>" +
                    '<p class="answer">' + escapeHtml(data.rag.answer) + "</p>" +
                    (data.rag.sources.length ? sourcesList(data.rag.sources) : "") + "</div>" +
                '<div class="card"><h3>Plain LLM</h3><p class="answer">' + escapeHtml(data.plain.answer) + "</p></div>" +
            "</div>" +
            '<p class="meta">' + escapeHtml(data.note) + "</p>");
    });
}


// ---------- LLM only: POST /ask and /ask/grounded ----------

async function submitLlm(event) {
    event.preventDefault();
    const payload = { question: value("llmQuestion") };
    await runWithBusy(event.target, "llmOutput", "Asking the model…", async () => {
        const [plain, grounded] = await Promise.allSettled([
            postJson("/ask", payload),
            postJson("/ask/grounded", payload),
        ]);
        setOutput("llmOutput",
            '<div class="columns">' +
                llmCard("Plain", "/ask", plain) +
                llmCard("Grounded (fixed leave-policy context)", "/ask/grounded", grounded) +
            "</div>");
    });
}

function llmCard(title, path, result) {
    const body = result.status === "fulfilled"
        ? '<p class="answer">' + escapeHtml(result.value.answer) + '</p><p class="meta">Model ' + escapeHtml(result.value.model) + "</p>"
        : errorBanner(result.reason);
    return '<div class="card"><h3>' + escapeHtml(title) + " <code>" + path + "</code></h3>" + body + "</div>";
}


// ---------- Search: GET /search ----------

async function submitSearch(event) {
    event.preventDefault();
    const url = withParams("/search", { q: value("searchQuery"), top_k: value("searchTopK"), ...who() });
    await runWithBusy(event.target, "searchOutput", "Searching…", async () => {
        const data = await api(url);
        if (!data.results.length) {
            setOutput("searchOutput", '<div class="banner banner-none">Nothing this user may read matches ' +
                "(or the index is empty: open the Sync tab).</div>");
            return;
        }
        const rows = data.results.map((r, i) =>
            chunkRow("#" + (i + 1) + "  " + provenance(r), r.text, r.distance)
        ).join("");
        const asked = "as " + escapeHtml(data.user) + " (" + escapeHtml(data.groups.join(", ")) + ")" +
            (data.as_of ? ", as of " + escapeHtml(data.as_of) : ", today");
        setOutput("searchOutput",
            '<div class="card"><h3>' + data.total_results + " closest chunks " + asked + "</h3>" + rows +
            '<p class="meta">Bar colours use the server thresholds: green ≤ ' + thresholds.high +
            ", amber ≤ " + thresholds.low + ", red ≤ " + thresholds.no_result + ", grey = no result.</p></div>");
    });
}


// ---------- Embeddings: POST /embed ----------

async function submitEmbed(event) {
    event.preventDefault();
    const texts = value("embedTexts").split("\n").map(t => t.trim()).filter(Boolean);
    if (texts.length < 2) {
        setOutput("embedOutput", '<div class="banner banner-error">Enter at least two lines of text.</div>');
        return;
    }
    await runWithBusy(event.target, "embedOutput", "Embedding…", async () => {
        const data = await postJson("/embed", { texts: texts });
        const pairs = Object.entries(data.distances).sort((a, b) => a[1] - b[1]);
        const max = Math.max(...pairs.map(p => p[1]), 0.01);
        const rows = pairs.map(([label, dist]) =>
            "<tr><td>" + escapeHtml(label) + '</td><td class="num">' + dist.toFixed(4) +
            "</td><td>" + distanceBar(dist, max, "medium") + "</td></tr>"
        ).join("");
        setOutput("embedOutput",
            '<div class="card"><h3>Pairwise distances · ' + data.dimensions + "-dimension vectors</h3>" +
            "<table><tr><th>Pair (closest first)</th><th>L2 distance</th><th></th></tr>" + rows + "</table>" +
            '<p class="meta">Plain Euclidean distance. The store’s search distances are this number squared.</p></div>');
    });
}


// ---------- Sync: POST /sync (Checkpoint 4's Ingest tab) ----------

async function submitSync(event) {
    event.preventDefault();
    const apply = document.getElementById("syncApply").checked;
    const url = withParams("/sync", { apply: apply });
    await runWithBusy(event.target, "syncOutput", apply ? "Syncing…" : "Planning…", async () => {
        const data = await api(url, { method: "POST" });
        setOutput("syncOutput", renderSync(data));
        loadStatus();
    });
}

// One badge colour per action: green = adds content, amber = metadata only, red = removes.
const ACTION_LEVEL = { add: "high", change: "high", relabel: "medium", touch: "medium",
    remove: "low", quarantine: "low", skip: "none", unchanged: "none" };

function renderSync(data) {
    const counts = Object.entries(data.counts).map(([action, n]) => stat(n, action)).join("");
    const rows = data.documents.filter(d => d.action !== "unchanged").map(d =>
        '<tr><td><span class="badge badge-' + ACTION_LEVEL[d.action] + '">' + escapeHtml(d.action) + "</span></td>" +
        "<td>" + escapeHtml(d.doc_id) + "</td><td>" + escapeHtml(d.reason) + "</td></tr>"
    ).join("");
    const warnings = data.warnings.length
        ? '<div class="card"><h3>For a human to look at</h3><ul>' +
          data.warnings.map(w => "<li>" + escapeHtml(w) + "</li>").join("") + "</ul></div>"
        : "";
    const banner = data.applied
        ? '<div class="banner banner-high">Applied to ' + escapeHtml(data.collection) + ". Report: " + escapeHtml(data.report_file || "") + "</div>"
        : '<div class="banner banner-none">Dry run: nothing was written. Tick “Apply” to run it.</div>';
    return banner +
        '<div class="card"><div class="stats">' + counts +
        stat(data.chunks_to_embed, "chunks to embed") +
        stat("$" + data.estimated_cost_usd.toFixed(4), "estimated cost") +
        "</div></div>" +
        '<div class="card"><h3>Plan · ' + escapeHtml(data.embedding_model) + "</h3>" +
        "<table><tr><th>Action</th><th>Document</th><th>Why</th></tr>" + rows + "</table></div>" + warnings;
}

function stat(number, label) {
    return '<div class="stat"><b>' + number + "</b><span>" + label + "</span></div>";
}


// ---------- Store: GET /store/inspect ----------

async function submitStore(event) {
    if (event) event.preventDefault();
    const form = document.getElementById("storeForm");
    const url = withParams("/store/inspect", {
        source: value("storeSource"),
        limit: value("storeLimit"),
        show_embeddings: document.getElementById("storeEmbeddings").checked,
    });
    await runWithBusy(form, "storeOutput", "Reading the store…", async () => {
        const data = await api(url);
        // A filtered result only lists one source, so keep the full dropdown
        if (!value("storeSource")) fillSourceFilter(data.sources);
        setOutput("storeOutput", renderStore(data));
    });
}

function renderStore(data) {
    if (data.total_stored === 0) {
        return '<div class="banner banner-none">The index is empty. Open the Sync tab first.</div>';
    }
    const dims = data.chunks.find(c => c.embedding_dimensions);
    const rows = data.chunks.map(c => {
        const vector = c.embedding_preview
            ? '<p class="vector">[' + c.embedding_preview.map(n => n.toFixed(4)).join(", ") +
              ", … ] · " + c.embedding_dimensions + " numbers</p>"
            : "";
        return chunkRow(c.id + " · " + (c.doc_type || "no doc_type, re-ingest"), c.text, null, vector);
    }).join("");

    return '<div class="card"><div class="stats">' +
            stat(data.total_stored, "chunks in store") +
            stat(data.sources.length, "source files") +
            stat(dims ? dims.embedding_dimensions : "–", "vector dimensions") +
            stat(data.chunks.length, "shown below") +
        "</div></div>" +
        '<div class="card"><h3>Chunks</h3>' + rows + "</div>";
}


// ---------- Visualize: GET /visualize ----------

async function submitVisualize(event) {
    if (event) event.preventDefault();
    const form = document.getElementById("visualizeForm");
    const method = value("visualizeMethod");
    await runWithBusy(form, "visualizeOutput", "Drawing " + method.toUpperCase() + " plot…", async () => {
        const response = await fetch("/visualize?method=" + method);
        if (!response.ok) throw new Error(response.status + ": " + (await response.text()));
        const url = URL.createObjectURL(await response.blob());
        setOutput("visualizeOutput",
            '<div class="card"><img class="plot" src="' + url + '" alt="2D map of chunk embeddings coloured by source file"></div>');
    });
}


// ---------- Tabs ----------

// Purpose: show the panel named in the URL hash (e.g. #search).
function showTab() {
    const name = location.hash.slice(1) || "query";
    document.querySelectorAll("section").forEach(s => s.classList.toggle("active", s.dataset.panel === name));
    document.querySelectorAll("#tabs a").forEach(a => a.classList.toggle("active", a.dataset.tab === name));

    // Data tabs load themselves the first time they open
    if (name === "store" && !document.getElementById("storeOutput").innerHTML) submitStore();
    if (name === "visualize" && !document.getElementById("visualizeOutput").innerHTML) submitVisualize();

    const firstInput = document.querySelector("section.active input[type=text]");
    if (firstInput) firstInput.focus();
}

// Purpose: clicking a sample question fills the box and submits it.
function wireSamples() {
    document.querySelectorAll(".samples").forEach(group => {
        group.addEventListener("click", event => {
            if (event.target.tagName !== "SPAN") return;
            const input = document.getElementById(group.dataset.target);
            input.value = event.target.textContent;
            input.form.requestSubmit();
        });
    });
}


// ---------- Start ----------

document.getElementById("queryForm").addEventListener("submit", submitQuery);
document.getElementById("compareForm").addEventListener("submit", submitCompare);
document.getElementById("llmForm").addEventListener("submit", submitLlm);
document.getElementById("searchForm").addEventListener("submit", submitSearch);
document.getElementById("embedForm").addEventListener("submit", submitEmbed);
document.getElementById("syncForm").addEventListener("submit", submitSync);
document.getElementById("storeForm").addEventListener("submit", submitStore);
document.getElementById("visualizeForm").addEventListener("submit", submitVisualize);
window.addEventListener("hashchange", showTab);

wireSamples();
loadStatus();
showTab();
