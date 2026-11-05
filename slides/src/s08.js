// s08.js — Session 8: Production Ingestion (rag-week-bootcamp, checkpoint 5)
const path = require("path");
const { Deck } = require("./kit");
const S = require("./sef");
const { C } = S;
const fa = require("react-icons/fa");

const OUT = process.argv[2] || ".";
const CP = "checkpoints/checkpoint-5-production-ingestion";

async function build() {
  const I = {};
  const want = {
    sync: [fa.FaSyncAlt, C.green], plug: [fa.FaPlug, C.green], file: [fa.FaFileAlt, C.green], shield: [fa.FaShieldAlt, C.green],
    chart: [fa.FaChartBar, C.green], laptop: [fa.FaLaptopCode, C.green], coffee: [fa.FaCoffee, C.green], tasks: [fa.FaTasks, C.green],
    load: [fa.FaFolderOpen, C.deep], cut: [fa.FaCut, C.deep], vec: [fa.FaVectorSquare, C.deep], db: [fa.FaDatabase, C.deep],
    search: [fa.FaSearch, C.deep], answer: [fa.FaCommentDots, C.deep], clock: [fa.FaHistory, C.red],
    list: [fa.FaListUl, C.deep], download: [fa.FaDownload, C.deep], tag: [fa.FaTags, C.deep],
    redo: [fa.FaRedo, C.deep], pages: [fa.FaListOl, C.deep], finger: [fa.FaFingerprint, C.deep], trash: [fa.FaTrashAlt, C.deep],
    lockR: [fa.FaLock, C.red], lockG: [fa.FaLock, C.deep], unlock: [fa.FaUnlockAlt, C.red], filter: [fa.FaFilter, C.deep], filterA: [fa.FaFilter, C.amber],
    secret: [fa.FaUserSecret, C.deep], link: [fa.FaLink, C.deep], building: [fa.FaBuilding, C.deep],
    warn: [fa.FaExclamationTriangle, C.amber], check: [fa.FaCheckCircle, C.deep], times: [fa.FaTimesCircle, C.red],
    pdf: [fa.FaFilePdf, C.red], pdfG: [fa.FaFilePdf, C.deep], scan: [fa.FaImage, C.red], code: [fa.FaCode, C.deep],
    cal: [fa.FaCalendarAlt, C.deep], users: [fa.FaUsers, C.deep], book: [fa.FaBookOpen, C.deep], key: [fa.FaKey, C.deep],
    cloud: [fa.FaCloud, C.deep], chat: [fa.FaComments, C.deep], folder: [fa.FaFolder, C.deep], mail: [fa.FaEnvelope, C.deep],
    git: [fa.FaCodeBranch, C.deep], box: [fa.FaBoxOpen, C.deep], idcard: [fa.FaIdBadge, C.deep], robot: [fa.FaRobot, C.deep],
    vote: [fa.FaHandPaper, C.green], flask: [fa.FaFlask, C.deep], layers: [fa.FaLayerGroup, C.green],
  };
  for (const [k, [comp, color]] of Object.entries(want)) I[k] = await S.icon(comp, color);

  const deck = new Deck({ title: "Production Ingestion", author: "SE Factory", company: "SE Factory",
    subject: "Applied AI Engineering Workshop · RAG in production · Production Ingestion" });
  let n = 0;
  const num = (s, dark) => S.slideNumber(s, ++n, dark);

  // ---------------------------------------------------------------- 1 Title
  let s = S.darkSlide(deck, {
    section: "Opening", icon: I.sync,
    kicker: "APPLIED AI ENGINEERING WORKSHOP  ·  RAG IN PRODUCTION",
    title1: "Production", title2: "Ingestion",
    subtitle: "The right documents, at the right version, for the right people",
    footer: "Connect  ·  Parse  ·  Govern  ·  Sync  ·  Measure",
    notes: `About: Last session's pipeline ingested one folder that never changes. Today we point it at a source that changes every day, and make it survive: the right documents, the right version, the right readers. Code: checkpoint 5 in rag-week-bootcamp.
Say: "Last time you built RAG from scratch. Today the question is: what happens on Monday, after real people changed real documents over the weekend?"
Before class: run python ${CP}/warmup.py on the presenting laptop, then sharepoint.py reset, sync.py --wipe, so the demo starts from Friday.`,
  });
  num(s, true);

  // ---------------------------------------------------------------- 2 Recap
  s = S.contentSlide(deck, {
    section: "Opening", title: "Last session, you built this",
    subtitle: "Checkpoints 1 to 4: one folder of documents that never changes.",
    takeaway: "The pipeline works. The folder is what isn't real.",
    notes: `About: Recap of the RAG pipeline from checkpoints 1 to 4, and the one failure mode from last session that today fixes properly.
Say: "Six steps, all yours. And on the last slide of last session we listed questions RAG struggles with. One was temporal: 'what changed in the latest update?' We said chunks don't carry versions. Today they will."
Ask the room: "What else is different about a real company's documents?" Collect 2-3 answers (permissions, formats, deletions) and park them; every one comes back today.`,
  });
  const steps = [["Load", I.load], ["Chunk", I.cut], ["Embed", I.vec], ["Store", I.db], ["Retrieve", I.search], ["Answer", I.answer]];
  steps.forEach(([label, ic], i) => {
    const x = 0.6 + i * 1.5;
    s.rect({ x, y: 1.65, w: 1.25, h: 1.15, fill: C.white, line: C.line, name: `pipe-${i}` });
    s.image(ic, { x: x + 0.43, y: 1.82, w: 0.38, h: 0.38, name: `pipe-icon-${i}` });
    s.text(label, { x, y: 2.3, w: 1.25, h: 0.36, font: "Arial", size: 13, bold: true, color: C.dark, align: "center", name: `pipe-label-${i}` });
    if (i < steps.length - 1) S.arrow(s, x + 1.27, 2.22, x + 1.48, 2.22, C.gray, 1.25);
  });
  s.rect({ x: 0.6, y: 3.15, w: 8.8, h: 1.65, fill: C.white, line: C.red, lineWidth: 1, name: "temporal-box" });
  s.image(I.clock, { x: 0.85, y: 3.35, w: 0.42, h: 0.42, name: "temporal-icon" });
  s.text("LAST SESSION'S FAILURE GALLERY: TEMPORAL", { x: 1.45, y: 3.35, w: 7.6, h: 0.3, size: 11, bold: true, color: C.redText, charSpacing: 1, name: "temporal-kicker" });
  s.text([
    [{ text: "\"What changed in the latest policy update?\"", i: true, color: C.ink, size: 15 }],
    [{ text: "Why it failed: chunks don't carry versions or dates. Today they will, along with who may read them, and what to do when the file changes, moves or disappears.", size: 12.5, color: C.slate }],
  ], { x: 1.45, y: 3.7, w: 7.75, h: 1.0, paraSpace: 6, name: "temporal-text" });
  num(s);

  // ---------------------------------------------------------------- 3 Where time goes
  s = S.contentSlide(deck, {
    section: "Opening", title: "Where production RAG time actually goes",
    subtitle: "A rough split from real projects. Not a survey: an order of magnitude.",
    takeaway: "Retrieval tricks get the blog posts. Ingestion gets the incidents.",
    notes: `About: Sets expectations: most RAG engineering effort is data plumbing, not embeddings or prompts. The numbers are an experienced estimate, say so.
Say: "If you only know how to retrieve and re-rank, you're useful for two weeks. If you can get messy data into a RAG system reliably, and keep it right, you're useful for years."
Don't defend the exact percentages; the order is the point.`,
  });
  // [label, percent, bar fill, label text colour (darker, readable), tag]
  const bars = [["Ingestion & data plumbing", 60, C.deep, C.deep, "today"], ["Retrieval tuning", 20, C.teal, C.tealText, ""],
    ["Evaluation & monitoring", 15, C.amber, C.amberDeep, ""], ["Prompt engineering", 5, C.gray, C.gray, ""]];
  bars.forEach(([label, pct, color, textColor, tag], i) => {
    const y = 1.7 + i * 0.8;
    s.text(label, { x: 0.6, y, w: 2.9, h: 0.5, size: 14, bold: i === 0, color: C.dark, valign: "middle", name: `bar-label-${i}` });
    s.rect({ x: 3.6, y: y + 0.08, w: 5.0, h: 0.34, fill: C.line, name: `bar-track-${i}` });
    s.rect({ x: 3.6, y: y + 0.08, w: 5.0 * pct / 100, h: 0.34, fill: color, name: `bar-${i}` });
    s.text(`${pct}%`, { x: 8.7, y, w: 0.8, h: 0.5, font: "Arial", size: 18, bold: true, color: textColor, valign: "middle", name: `bar-pct-${i}` });
    if (tag) S.chip(s, { x: 3.6 + 5.0 * pct / 100 + 0.1, y: y + 0.11, w: 0.85, h: 0.28, text: "TODAY", fill: C.green, color: C.dark, name: "bar-today" });
  });
  num(s);

  // ---------------------------------------------------------------- 4 Acme SharePoint
  s = S.contentSlide(deck, {
    section: "Opening", title: "Meet Acme's SharePoint",
    subtitle: "data/enterprise: Friday's snapshot. 20 files, 7 sites, 7 formats, one register, five users.",
    takeaway: "sharepoint.py plays SharePoint: reset to Friday, then replay the weekend's changes.",
    notes: `About: The scenario for the whole session (and next). Same company as last session (Acme Corp), now organised the way a company stores documents: sites, owners, permissions, versions.
Say: "Same Acme, same leave and expense policies you know. But now there are seven sites, seven formats, and a register: the list SharePoint keeps about each file. Five people will ask questions: an intern, an engineering manager, an HR partner, a finance lead and a sales rep."
Show: ${CP}/../../data/enterprise in the explorer, then register.json for one entry.`,
  });
  const sites = [["hr", "5 files", "md"], ["finance", "3 files", "md, xlsx"], ["engineering", "7 files", "md, pdf, docx, html, eml"],
    ["it", "2 files", "eml, csv"], ["company", "1 file", "md"], ["people", "1 file", "csv"], ["leadership", "1 file", "md"]];
  sites.forEach(([name, count, fmts], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.6 + col * 2.55, y = 1.6 + row * 0.82;
    s.rect({ x, y, w: 2.4, h: 0.68, fill: C.white, line: C.line, name: `site-${name}` });
    s.image(I.folder, { x: x + 0.14, y: y + 0.16, w: 0.36, h: 0.36, name: `site-icon-${name}` });
    s.text([[{ text: name, b: true, color: C.dark, size: 13, font: "Arial" }, { text: "   " + count, color: C.gray, size: 11 }], [{ text: fmts, color: C.deep, size: 10.5 }]],
      { x: x + 0.6, y: y + 0.08, w: 1.75, h: 0.55, valign: "middle", name: `site-text-${name}` });
  });
  S.code(s, { x: 5.85, y: 1.6, w: 3.55, h: 1.75, label: "register.json (one entry)", size: 10.5, lines: [
    '{ "doc_id": "HR-SALARY-BANDS-2026",', '  "path": "hr/salary-bands-2026.md",', '  "owner": "People Operations",',
    '  "allowed_groups": ["employees"],', '  "status": "current",', '  "effective_from": "2026-01-01" }'] });
  s.text("FIVE USERS", { x: 5.85, y: 3.55, w: 3.5, h: 0.25, size: 10, bold: true, color: C.deep, charSpacing: 1, name: "users-kicker" });
  ["intern", "eng-manager", "hr-partner", "finance-lead", "sales-rep"].forEach((u, i) => {
    S.chip(s, { x: 5.85 + (i % 3) * 1.2, y: 3.85 + Math.floor(i / 3) * 0.4, w: 1.12, h: 0.3, text: u, size: 10, name: `user-${u}` });
  });
  num(s);

  // ---------------------------------------------------------------- 5 Checkpoint 4's ingest on Friday
  s = S.contentSlide(deck, {
    section: "Opening", title: "Checkpoint 4's /ingest, run on Friday",
    subtitle: "Checkpoint 4's code, unchanged, pointed at this SharePoint: python sync.py --naive",
    takeaway: "No error. No warning. It looked like it worked.",
    notes: `About: Run checkpoint 4's ingest logic (kept verbatim in app/ingest/naive.py) against the enterprise folder. It "succeeds".
Demo: python ${CP}/sharepoint.py reset  then  python ${CP}/sync.py --naive
Expected: 50 chunks upserted; silently skipped: onboarding-guide.docx, release-4.2.eml, wiki-vector-database.html, q3-metrics.xlsx, phishing-notice-2026-10.eml; embedded EMPTY text from incident-report-scanned.pdf.
Say: "Five files never made it in, and nobody was told. A scanned PDF went in as an empty string, which has a vector like any other text. And everyone can read everything."`,
  });
  const fri = [["50", "chunks stored", C.deep, "Everything it could read, upserted with ids like leave-policy.md_2"],
    ["5 of 20", "files silently skipped", C.redText, ".docx, .xlsx, .html and two emails: formats it never learned"],
    ["1", "scan embedded as empty text", C.redText, "pypdf found no text layer; the empty string got a vector anyway"],
    ["0", "permissions, versions, owners", C.redText, "The salary bands and the leadership notes are one search away for everyone"]];
  fri.forEach(([v, l, color, body], i) => {
    const x = 0.6 + i * 2.23;
    s.rect({ x, y: 1.65, w: 2.08, h: 2.6, fill: C.white, line: C.line, name: `fri-card-${i}` });
    S.stat(s, { x: x + 0.18, y: 1.75, w: 1.8, value: v, label: l, color, size: 34, labelSize: 12.5, labelColor: C.dark, name: `fri-${i}` });
    s.text(body, { x: x + 0.18, y: 3.2, w: 1.75, h: 0.95, size: 11.5, color: C.slate, name: `fri-body-${i}` });
  });
  s.text([[{ text: "POST /ingest  →  ", font: "Consolas", color: C.slate }, { text: "200 OK", font: "Consolas", b: true, color: C.deep }]],
    { x: 0.6, y: 4.45, w: 8.8, h: 0.4, size: 14, align: "center", valign: "middle", name: "fri-ok" });
  num(s);

  // ---------------------------------------------------------------- 6 The weekend
  s = S.contentSlide(deck, {
    section: "Opening", title: "Then the weekend happens",
    subtitle: "Five ordinary changes. python sharepoint.py apply all replays them.",
    takeaway: "Nothing exotic. This is a normal Monday in any company.",
    notes: `About: The five events in data/enterprise/events/events.json. Each one breaks a different assumption of checkpoint 4.
Demo: python ${CP}/sharepoint.py events   then   python ${CP}/sharepoint.py apply all
Say each in one line. Point out event 4: "not one word of the file changes, only who may read it." And event 5: "a footer, the article is identical."`,
  });
  const ev = [["Finance publishes the 2026 Expense Policy", "The 2023 policy and its 2024 update become superseded"],
    ["HR edits the Leave Policy", "Carry-over 5 → 10 days; two sections move out; the file gets shorter"],
    ["Legal withdraws the Q3 planning notes", "The file is deleted from SharePoint"],
    ["HR fixes who can read the salary bands", "Shared with every employee by mistake; now HR and managers only"],
    ["Someone edits the wiki page footer", "The copyright year changes; the article does not"]];
  // what each event does to checkpoint 4's /ingest
  const breaks = ["serves the old rules", "keeps orphan chunks", "never deletes it", "has no permissions", "re-embeds everything"];
  s.line({ x: 0.82, y: 1.87, w: 0, h: 2.64, color: C.line, width: 2, name: "timeline" });
  s.text("CHECKPOINT 4'S /INGEST", { x: 6.95, y: 1.3, w: 2.45, h: 0.25, size: 9.5, bold: true, color: C.redText, charSpacing: 1, align: "center", name: "breaks-kicker" });
  ev.forEach(([t, d], i) => {
    const y = 1.6 + i * 0.66;
    s.ellipse({ x: 0.6, y: y + 0.05, w: 0.44, h: 0.44, fill: C.deep, name: `ev-dot-${i}` });
    s.text(String(i + 1), { x: 0.6, y: y + 0.05, w: 0.44, h: 0.44, font: "Arial", size: 14, bold: true, color: C.white, align: "center", valign: "middle", name: `ev-num-${i}` });
    s.text([[{ text: t, b: true, color: C.dark, size: 14, font: "Arial" }], [{ text: d, color: C.slate, size: 12 }]],
      { x: 1.25, y, w: 5.55, h: 0.58, valign: "middle", name: `ev-text-${i}` });
    S.chip(s, { x: 6.95, y: y + 0.12, w: 2.45, h: 0.32, text: breaks[i], fill: C.redSoft, color: C.redText, size: 10.5, name: `ev-break-${i}` });
  });
  num(s);

  // ---------------------------------------------------------------- 7 Predict
  s = S.contentSlide(deck, {
    section: "Opening", title: "Predict: checkpoint 4's index on Monday",
    subtitle: "You know its code: ids are file_n, it upserts, never deletes, and has no register. Re-run it after the weekend.",
    takeaway: "Vote first. Then we measure.",
    notes: `About: A prediction with enough groundwork: they wrote checkpoint 4's ingest, and they just saw the five events.
Ask: "Which of these happens?" Hands up for A, B, C, D.
Answer: D, all three. A: the 2023 chunk ('up to $50 per person') still ranks first for team dinners. B: the deleted notes' chunks were never deleted (upsert never removes). C: there is no permission filter at all, so the intern gets the salary bands.
Demo before revealing: python ${CP}/sync.py --naive (re-run after the events), then evaluate on the next slide.`,
  });
  const opts = [["A", "Asked about team dinners, it quotes the 2023 limit", I.clock],
    ["B", "The withdrawn planning notes are still searchable", I.trash],
    ["C", "The intern can read the salary bands", I.unlock],
    ["D", "All three", I.vote]];
  opts.forEach(([letter, text, ic], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.6 + col * 4.45, y = 1.7 + row * 1.55;
    s.rect({ x, y, w: 4.3, h: 1.4, fill: C.white, line: C.line, name: `opt-${letter}` });
    s.ellipse({ x: x + 0.25, y: y + 0.42, w: 0.56, h: 0.56, fill: letter === "D" ? C.green : C.dark, name: `opt-dot-${letter}` });
    s.text(letter, { x: x + 0.25, y: y + 0.42, w: 0.56, h: 0.56, font: "Arial", size: 18, bold: true, color: letter === "D" ? C.dark : C.white, align: "center", valign: "middle", name: `opt-letter-${letter}` });
    s.text(text, { x: x + 1.0, y: y + 0.2, w: 2.75, h: 1.0, size: 15, color: C.dark, valign: "middle", name: `opt-text-${letter}` });
    s.image(ic, { x: x + 3.78, y: y + 0.52, w: 0.36, h: 0.36, name: `opt-icon-${letter}` });
  });
  num(s);

  // ---------------------------------------------------------------- 8 Monday measured (naive)
  s = S.contentSlide(deck, {
    section: "Opening", title: "Monday, measured: checkpoint 4's index",
    subtitle: "31 hand-written questions, top 5 chunks each, judged against the register and the files.",
    takeaway: "Hit@5 is 0.81, so a quality dashboard looks fine. The safety numbers are what hurt.",
    notes: `About: The result of evaluate.py --only naive on Monday's state. Every number on this slide is reproducible on a student laptop (local embeddings).
Demo: python ${CP}/evaluate.py --only naive --details
Say: "Seven questions put a chunk in front of the model that the person asking may not read. Fourteen put an old version or a draft in front of it. Eleven put a chunk of a deleted document, or of text that's no longer in the file. And the top answer for team dinners is the 2023 rule."
Then: "Everything for the rest of the session is about getting these four numbers to zero."`,
  });
  const naive = [["7 of 31", "questions show the model a chunk the user may NOT read", C.redText],
    ["14 of 31", "show a superseded document or a draft", C.redText],
    ["11 of 31", "show a deleted document, or text no longer in the file", C.redText],
    ["4 of 31", "show personal phone numbers or emails", C.amberDeep]];
  naive.forEach(([v, l, color], i) => {
    const y = 1.6 + i * 0.83;
    s.text(v, { x: 0.6, y, w: 1.75, h: 0.7, font: "Arial", size: 30, bold: true, color, valign: "middle", name: `naive-v-${i}` });
    s.text(l, { x: 2.4, y, w: 3.0, h: 0.7, size: 13, color: C.dark, valign: "middle", name: `naive-l-${i}` });
  });
  s.rect({ x: 5.75, y: 1.65, w: 3.65, h: 3.25, fill: C.white, line: C.red, name: "dinner-box" });
  s.text("Q18 · asked by the intern", { x: 5.95, y: 1.78, w: 3.3, h: 0.28, size: 10.5, bold: true, color: C.redText, charSpacing: 0.5, name: "dinner-kicker" });
  s.text("\"How much can I spend per person on a team dinner?\"", { x: 5.95, y: 2.1, w: 3.3, h: 0.62, size: 13.5, italic: true, color: C.ink, name: "dinner-q" });
  s.text("#1 of 5: expense-policy.md", { x: 5.95, y: 2.85, w: 3.3, h: 0.28, size: 11, bold: true, color: C.dark, name: "dinner-rank" });
  s.text(["\"Team meals and events:", " up to $50 per person.\""], { x: 5.95, y: 3.15, w: 3.3, h: 0.5, font: "Consolas", size: 10.5, color: C.slate, name: "dinner-chunk" });
  s.text([[{ text: "The 2023 rule. ", b: true, color: C.redText }, { text: "Since 1 November it is $90.", color: C.dark }]], { x: 5.95, y: 3.78, w: 3.3, h: 0.32, size: 12.5, name: "dinner-verdict" });
  s.text("The current policy came back too, at #2. Nothing told the model which one is in force.", { x: 5.95, y: 4.15, w: 3.3, h: 0.62, size: 11, italic: true, color: C.slate, name: "dinner-note" });
  num(s);

  // ================================================================ PART 1 CONNECT
  s = S.darkSlide(deck, { section: "Connect", icon: I.plug, kicker: "PART 1 OF 5", title1: "Connect",
    subtitle: "Pull documents from where they live, and notice when they change", footer: "list  ·  fetch  ·  describe",
    notes: `About: Connectors. Short part: the pattern matters more than any one API.` });
  num(s, true);

  // ---------------------------------------------------------------- 10 three questions
  s = S.contentSlide(deck, {
    section: "Connect", title: "A connector answers three questions",
    subtitle: "SharePoint, Confluence, Drive, Slack, S3: different APIs, the same three questions.",
    takeaway: "Swap this class for a Microsoft Graph client and nothing else in the pipeline changes.",
    notes: `About: app/ingest/connector.py. LocalFolderConnector stands in for a SharePoint document library.
Say: "Every source answers three questions. What exists right now, with a cheap change signal (the eTag). Give me the bytes. What do you know about it: owner, permissions, status. That third one is the one tutorials skip."
Real thing: Graph's delta query returns changed AND deleted items since your last token, so you never re-list 50,000 files.
Open the file and show list_items(): it computes an eTag as a SHA-256 of the bytes; a real source hands you one.`,
  });
  const qs3 = [["What exists right now?", "list_items()  →  path, size, modified, eTag", "Graph: GET /drives/{id}/root/delta", I.list],
    ["Give me the bytes", "fetch(path)  →  bytes", "Graph: GET /items/{id}/content", I.download],
    ["What do you know about it?", "fetch_register()  →  owner, groups, status, dates", "Graph: /items/{id}/permissions + the register", I.tag]];
  qs3.forEach(([q, ours, graph, ic], i) => {
    const y = 1.6 + i * 1.12;
    s.rect({ x: 0.6, y, w: 5.0, h: 1.0, fill: C.white, line: C.line, name: `q3-box-${i}` });
    s.ellipse({ x: 0.78, y: y + 0.28, w: 0.44, h: 0.44, fill: C.deep, name: `q3-dot-${i}` });
    s.text(String(i + 1), { x: 0.78, y: y + 0.28, w: 0.44, h: 0.44, font: "Arial", size: 14, bold: true, color: C.white, align: "center", valign: "middle", name: `q3-num-${i}` });
    s.text([[{ text: q, b: true, size: 14, color: C.dark, font: "Arial" }], [{ text: ours, font: "Consolas", size: 10.5, color: C.deep }], [{ text: graph, size: 10.5, color: C.gray }]],
      { x: 1.4, y: y + 0.08, w: 4.1, h: 0.86, valign: "middle", name: `q3-text-${i}` });
  });
  S.code(s, { x: 5.85, y: 1.6, w: 3.55, h: 3.25, label: "app/ingest/connector.py", size: 11, lines: [
    "class LocalFolderConnector:", '    """Stands in for SharePoint."""', "",
    "    def list_items(self):", "        # path, size, modified,", "        # eTag = sha256(bytes)[:16]", "",
    "    def fetch(self, path):", "        return bytes", "",
    "    def fetch_register(self):", "        return _register.json"] });
  num(s);

  // ---------------------------------------------------------------- 11 connectors & auth
  s = S.contentSlide(deck, {
    section: "Connect", title: "Connectors and auth",
    subtitle: "Most projects connect to 3 to 7 sources. The loader is the easy part; auth is where integrations fail.",
    takeaway: "A scheduled sync runs as a service principal, never as a person.",
    notes: `About: The landscape (left) and the four auth patterns you'll meet (right).
Say: "LangChain and LlamaIndex have a loader for nearly all of these. They hand you documents. They don't hand you auth that survives someone leaving the company, or rate limits, or deletions."
The trap: a personal access token works in the prototype; the day its owner leaves, the sync silently stops and the index slowly goes stale.`,
  });
  const srcs = [["SharePoint", "service principal", I.folder], ["Confluence", "API token / OAuth", I.book], ["Google Drive", "service account", I.cloud], ["Slack", "bot token + scopes", I.chat],
    ["Notion", "integration token", I.box], ["GitHub", "GitHub App", I.git], ["S3 / Blob", "managed identity", I.db], ["Email", "OAuth (M365)", I.mail]];
  srcs.forEach(([name, auth, ic], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.6 + col * 2.1, y = 1.6 + row * 0.82;
    s.rect({ x, y, w: 1.98, h: 0.7, fill: C.white, line: C.line, name: `src-${i}` });
    s.image(ic, { x: x + 0.12, y: y + 0.17, w: 0.34, h: 0.34, name: `src-icon-${i}` });
    s.text([[{ text: name, b: true, size: 12, color: C.dark, font: "Arial" }], [{ text: auth, size: 10, color: C.gray }]], { x: x + 0.55, y: y + 0.06, w: 1.4, h: 0.58, valign: "middle", name: `src-text-${i}` });
  });
  S.table(s, { x: 4.95, y: 1.6, cols: [1.45, 1.5, 1.5], rowH: 0.705, headH: 0.34, size: 10,
    header: ["Pattern", "Use when", "Watch out"],
    rows: [[{ text: "API token / PAT", b: true, color: C.dark }, "Prototypes, one-off scripts", "Dies when its owner leaves"],
      [{ text: "OAuth 2.0", b: true, color: C.dark }, "Users grant their own access", "Refresh, revoke, scope drift"],
      [{ text: "Service principal", b: true, color: C.dark }, "Scheduled jobs, server to server", "Easy to over-grant"],
      [{ text: "Managed identity", b: true, color: C.dark }, "Same-cloud sources", "Tied to one cloud"]] });
  num(s);

  // ---------------------------------------------------------------- 12 operational realities
  s = S.contentSlide(deck, {
    section: "Connect", title: "Four things a loader won't do for you",
    subtitle: "A loader is a function. A sync is a job that runs every night for years.",
    takeaway: "Every one of these fails silently. None of them throws.",
    notes: `About: The operational gotchas from real connectors, each mapped to where checkpoint 5 handles it.
Say: rate limits → with_retries in app/rag/embedder.py (1s, 2s, 4s, 8s plus jitter, then give up loudly). Pagination → check counts; exactly 100 results smells like a cap. Change detection → eTag first so unchanged files aren't even downloaded, then the content hash so unchanged text isn't re-embedded. Deletions → the sync compares the index with the source and removes what's gone.
Ask: "Which of these did checkpoint 4 handle?" Answer: none, and it didn't need to, because the folder never changed.`,
  });
  const ops = [["Rate limits", "429 Too Many Requests, halfway through 50,000 chunks.", "with_retries(): 1s, 2s, 4s, 8s + jitter, then fail loudly", I.redo],
    ["Pagination", "Results come in pages. Some loaders quietly stop after one.", "Got exactly 100 items? Suspect a cap, and count.", I.pages],
    ["Change detection", "Re-embedding 50,000 unchanged documents every night.", "eTag first: skip the download. Hash next: skip the embedding.", I.finger],
    ["Deletions", "Deleted in SharePoint, still answering questions in RAG.", "Compare index and source every run; remove what's gone", I.trash]];
  ops.forEach(([t, prob, fix, ic], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.6 + col * 4.45, y = 1.6 + row * 1.68;
    s.rect({ x, y, w: 4.3, h: 1.52, fill: C.white, line: C.line, name: `ops-${i}` });
    s.image(ic, { x: x + 0.2, y: y + 0.18, w: 0.38, h: 0.38, name: `ops-icon-${i}` });
    s.text(t, { x: x + 0.72, y: y + 0.16, w: 3.4, h: 0.42, font: "Arial", size: 14, bold: true, color: C.dark, valign: "middle", name: `ops-title-${i}` });
    s.text(prob, { x: x + 0.2, y: y + 0.62, w: 3.95, h: 0.3, size: 11.5, color: C.slate, name: `ops-prob-${i}` });
    s.text("IN SYNC.PY", { x: x + 0.2, y: y + 0.98, w: 3.95, h: 0.2, size: 9, bold: true, color: C.deep, charSpacing: 0.5, name: `ops-fix-label-${i}` });
    s.text(fix, { x: x + 0.2, y: y + 1.17, w: 3.95, h: 0.28, size: 11, color: C.dark, name: `ops-fix-${i}` });
  });
  num(s);

  // ================================================================ PART 2 PARSE
  s = S.darkSlide(deck, { section: "Parse", icon: I.file, kicker: "PART 2 OF 5", title1: "Parse",
    subtitle: "Every format fights back differently", footer: "sections  ·  headers  ·  quarantine",
    notes: `About: Parsing. The goal is not just text: it's text with its structure, and knowing when you got no text at all.` });
  num(s, true);

  // ---------------------------------------------------------------- 14 format zoo
  s = S.contentSlide(deck, {
    section: "Parse", title: "The format zoo",
    subtitle: "Seven formats in Acme's SharePoint. Checkpoint 4 read four of them.",
    takeaway: "parsers.py uses the standard library and pypdf only. A .docx is a zip file full of XML.",
    notes: `About: app/ingest/parsers.py: one function per format, each returns sections (heading + text).
Say: "Notice the last column: checkpoint 4 wasn't wrong for its folder. It just never met these formats, and it never told anyone it skipped them."
Show parse_docx: open the .docx with zipfile, read word/document.xml, keep paragraphs under their Heading style. Same trick for .xlsx (sheets, shared strings).
Production alternatives: Unstructured, LlamaParse, Docling, Azure Document Intelligence. Same contract: give me sections, tell me when you failed.`,
  });
  S.table(s, { x: 0.6, y: 1.55, cols: [1.6, 1.05, 4.15, 2.0], rowH: 0.37, headH: 0.34, size: 10.5,
    header: ["Format", "Difficulty", "What checkpoint 5 does", "Checkpoint 4"],
    rows: [
      [{ text: "Markdown", b: true, color: C.dark }, { text: "easy", color: C.deep, b: true }, "One section per ## heading; heading kept", "read, flattened"],
      [{ text: "CSV", b: true, color: C.dark }, { text: "easy", color: C.deep, b: true }, "One section per row, labelled with column names", "read as one blob"],
      [{ text: "PDF (digital)", b: true, color: C.dark }, { text: "medium", color: C.amberDeep, b: true }, "Text layer, one section per page", "read"],
      [{ text: "PDF (scanned)", b: true, color: C.dark }, { text: "hard", color: C.redText, b: true }, "Detected and quarantined: reported, not indexed", { text: "embedded \"\"", color: C.redText, b: true }],
      [{ text: "Word .docx", b: true, color: C.dark }, { text: "medium", color: C.amberDeep, b: true }, "Zip of XML; paragraphs under their headings", { text: "skipped", color: C.redText, b: true }],
      [{ text: "Excel .xlsx", b: true, color: C.dark }, { text: "hard", color: C.redText, b: true }, "One section per sheet, rows labelled by the header", { text: "skipped", color: C.redText, b: true }],
      [{ text: "HTML", b: true, color: C.dark }, { text: "medium", color: C.amberDeep, b: true }, "The article only: nav, cookie banner, footer dropped", { text: "skipped", color: C.redText, b: true }],
      [{ text: "Email .eml", b: true, color: C.dark }, { text: "medium", color: C.amberDeep, b: true }, "Subject as heading, sender and date, plain body", { text: "skipped", color: C.redText, b: true }],
    ] });
  num(s);

  // ---------------------------------------------------------------- 15 PDF
  s = S.contentSlide(deck, {
    section: "Parse", title: "PDF: a text layer, or a picture of text?",
    subtitle: "pypdf on a scan returns an empty string. Checkpoint 4 embedded it.",
    takeaway: "First step on any PDF corpus: parse ten files and count the empty ones.",
    notes: `About: The first ingestion bug everyone hits. engineering/incident-report-scanned.pdf is one page of pixels.
Say: "A PDF is a presentation format. Sometimes there's text inside, sometimes only an image of text. You have to detect which one you got, not trust the extension."
Our rule (parse_pdf): fewer than 50 characters across all pages → needs_ocr. The sync reports it as quarantine every run until someone OCRs it.
OCR is a cost/quality choice: Tesseract (free, weak on tables), Azure Document Intelligence / AWS Textract (managed, strong on forms), a vision LLM (flexible, slower, pricier).`,
  });
  S.card(s, { x: 0.6, y: 1.6, w: 4.3, h: 2.05, icon: I.pdfG, iconInline: true, title: "Digital PDF", edge: C.deep,
    body: [{ runs: "The text is in there. Ask nicely." }, { runs: "pypdf, pdfplumber: fast, free, fine for plain text", bullet: true }, { runs: "Watch for columns, tables, headers leaking into the body", bullet: true }], bodySize: 12 });
  S.card(s, { x: 5.1, y: 1.6, w: 4.3, h: 2.05, icon: I.scan, iconInline: true, title: "Scanned PDF", edge: C.red,
    body: [{ runs: "No text: pixels in a PDF wrapper. You need OCR." }, { runs: "Tesseract: free, weak on tables and handwriting", bullet: true }, { runs: "Azure Document Intelligence, Textract, or a vision model", bullet: true }], bodySize: 12 });
  S.code(s, { x: 0.6, y: 3.85, w: 8.8, h: 1.1, label: "python sync.py   (one line of the plan)", size: 10.5, lines: [
    { text: " ! quarantine ENG-INCIDENT-REPORT   1 page(s), 0 characters of text: a scan.", color: C.amber },
    { text: "                                    Queued for OCR, not indexed.", color: C.amber }] });
  num(s);

  // ---------------------------------------------------------------- 16 structure is signal
  s = S.contentSlide(deck, {
    section: "Parse", title: "Structure is signal",
    subtitle: "Keep the headings. Put the document's name on every chunk.",
    takeaway: "The header costs a few tokens and tells the retriever and the LLM what they are reading.",
    notes: `About: chunk_sections() in app/rag/chunker.py: one chunk per section (split on line breaks if over 900 characters), each starting with "<title> > <heading>".
Say: "Left is what checkpoint 4 stored: a 500-character window that starts mid-word and doesn't say which policy or which year. Right is one section with its document's title on top."
Numbers: for the query "team dinner limit per person", the windowed chunk sits at distance 1.11, the section with a header at 0.86 (lower is closer). Same embedding model, same text, plus structure.
HTML: the parser drops nav, header, footer, aside, scripts and anything whose class mentions cookie or banner: none of that boilerplate reaches the index.`,
  });
  S.code(s, { x: 0.6, y: 1.6, w: 4.3, h: 1.7, label: "CHECKPOINT 4: A 500-CHARACTER WINDOW", size: 10, lines: [
    { text: "…mployees.      (the window starts mid-word)", color: "F2A19C" }, "", "## Team Events", "", "- Team meals and events: up to $50", "  per person.", "- Offsites and team-building ..."] });
  S.code(s, { x: 5.1, y: 1.6, w: 4.3, h: 1.7, label: "CHECKPOINT 5: ONE SECTION, WITH A HEADER", size: 10, lines: [
    { text: "Expense Policy (2026 edition)", color: C.green, b: true }, { text: "  > Team Events", color: C.green, b: true },
    "- Team meals and events: up to $90", "  per person.", "- Offsites and team-building ..."] });
  S.stat(s, { x: 0.6, y: 3.45, w: 2.0, value: "1.11", label: "distance, window", color: C.redText, size: 30, name: "dist-old" });
  S.stat(s, { x: 2.7, y: 3.45, w: 2.0, value: "0.86", label: "distance, section + header", color: C.deep, size: 30, name: "dist-new" });
  s.text("Query: \"team dinner limit per person\". Lower is closer.", { x: 0.6, y: 4.65, w: 4.2, h: 0.3, size: 10.5, italic: true, color: C.gray, name: "dist-note" });
  S.card(s, { x: 5.1, y: 3.5, w: 4.3, h: 1.45, title: "HTML: the article, not the page", titleSize: 13,
    body: "The wiki page's cookie banner, navigation, sidebar, footer and scripts never reach the index. Only headings and body text do.", bodySize: 11.5 });
  num(s);

  // ---------------------------------------------------------------- 17 break
  s = S.darkSlide(deck, { section: "Parse", icon: I.coffee, kicker: "BREAK", title1: "10 minutes", subtitle: "Next: who may read what, and which version is true", logo: true,
    notes: `About: Break. Before resuming, make sure the weekend has been applied (sharepoint.py status shows 5 events) for the Govern demos.` });
  num(s, true);

  // ================================================================ PART 3 GOVERN
  s = S.darkSlide(deck, { section: "Govern", icon: I.shield, kicker: "PART 3 OF 5", title1: "Govern",
    subtitle: "Who may read it, and is it still true?", footer: "register  ·  permissions  ·  versions  ·  PII",
    notes: `About: The heart of the session: metadata that the text can't carry, and filters that use it.` });
  num(s, true);

  // ---------------------------------------------------------------- 19 register
  s = S.contentSlide(deck, {
    section: "Govern", title: "The register: what the text can't tell you",
    subtitle: "Owner, permissions, status and dates live in the source system, next to the file. They travel with every chunk.",
    takeaway: "A filter can only use what was stored at ingest time. There is no second chance.",
    notes: `About: data/enterprise/register.json, loaded by app/ingest/register.py. SharePoint keeps permissions and metadata columns; policy teams keep a register. We copy both onto every chunk.
Say: "Read the salary bands file: nothing in it says who may read it. That's SharePoint's job. If we don't copy it onto the chunk at ingest time, no query can filter on it later."
Two rules: fail closed (a file with no register entry is skipped: no entry means no permissions, which means nobody), and drafts or withdrawn documents never enter the index.
Show: the draft parental leave policy (24 weeks!) is skipped every sync; checkpoint 4 indexed it.`,
  });
  S.code(s, { x: 0.6, y: 1.65, w: 3.7, h: 2.6, label: "ONE REGISTER ENTRY", size: 10, lines: [
    "{", '  "doc_id": "FIN-EXP-2024-UPDATE",', '  "title": "Expense Policy Update (2024)",', '  "owner": "Finance",',
    '  "allowed_groups": ["employees"],', '  "status": "current",', '  "version": 1,', '  "effective_from": "2024-01-01",', '  "amends": "FIN-EXP-2023"', "}"] });
  S.table(s, { x: 4.5, y: 1.65, cols: [2.2, 2.7], rowH: 0.38, size: 10.5, headH: 0.32,
    header: ["Field", "Answers"],
    rows: [[{ text: "allowed_groups", font: "Consolas", color: C.deep }, "Who may read it"],
      [{ text: "status", font: "Consolas", color: C.deep }, "current, superseded, draft, withdrawn"],
      [{ text: "effective_from, _to", font: "Consolas", color: C.deep }, "When it is in force"],
      [{ text: "superseded_by, amends", font: "Consolas", color: C.deep }, "What replaced it, what it changes"],
      [{ text: "depends_on", font: "Consolas", color: C.deep }, "Which documents it quotes"],
      [{ text: "owner", font: "Consolas", color: C.deep }, "Who to ask when it is wrong"]] });
  S.chip(s, { x: 0.6, y: 4.45, w: 3.7, h: 0.4, text: "Fail closed: no register entry, not indexed", fill: C.redSoft, color: C.redText, size: 11 });
  S.chip(s, { x: 4.5, y: 4.45, w: 4.9, h: 0.4, text: "Drafts and withdrawn documents never enter the index", fill: C.redSoft, color: C.redText, size: 11 });
  num(s);

  // ---------------------------------------------------------------- 20 permissions
  s = S.contentSlide(deck, {
    section: "Govern", title: "Permissions: filter inside the search",
    subtitle: "The intern asks: \"What is the salary range for a Senior Developer?\"",
    takeaway: "Groups come from the login token, never from a field the caller can type.",
    notes: `About: Three ways to "do permissions" in RAG, only one of which works.
Say: "No filter: the intern reads the salary bands. Filter after the search: the top 5 is full of salary chunks, you throw them away and hand the intern three irrelevant chunks, or none, and the forbidden text already left the database. Filter inside the search: forbidden chunks never compete for the top 5."
And: "Telling the model 'don't reveal salaries' is not access control. The text is in its context window."
Chroma detail: metadata values are scalars, so allowed_groups becomes one boolean per group (acl_hr, acl_managers...). In pgvector it's a WHERE clause; in Elasticsearch a filter clause. Same idea.`,
  });
  // [title, sub, body, border, icon, verdict, verdict fill, verdict text]
  const perm = [["No filter", "Checkpoint 4", "Every chunk is a candidate. The salary bands rank first.", C.red, I.unlock, "LEAK", C.redText, C.white],
    ["Filter after the search", "Top 5, then drop", "Forbidden chunks take the top-5 slots; the intern gets leftovers. The text already left the database.", C.amber, I.filterA, "LEAKS AND STARVES", C.amber, C.dark],
    ["Filter inside the search", "Checkpoint 5", "Search only what the user's groups may read, and only what is current. Forbidden chunks never compete.", C.deep, I.lockG, "CORRECT", C.deep, C.white]];
  perm.forEach(([t, sub, body, color, ic, verdict, vFill, vText], i) => {
    const x = 0.6 + i * 2.97;
    s.rect({ x, y: 1.6, w: 2.82, h: 2.45, fill: C.white, line: color, lineWidth: 1.25, name: `perm-${i}` });
    s.image(ic, { x: x + 0.2, y: 1.78, w: 0.38, h: 0.38, name: `perm-icon-${i}` });
    S.chip(s, { x: x + 1.05, y: 1.82, w: 1.6, h: 0.3, text: verdict, fill: vFill, color: vText, size: 9.5, name: `perm-verdict-${i}` });
    s.text([[{ text: t, b: true, size: 14, color: C.dark, font: "Arial" }], [{ text: sub, size: 10.5, color: C.gray }]], { x: x + 0.2, y: 2.3, w: 2.45, h: 0.62, name: `perm-title-${i}` });
    s.text(body, { x: x + 0.2, y: 2.95, w: 2.45, h: 1.0, size: 11.5, color: C.slate, name: `perm-body-${i}` });
  });
  S.code(s, { x: 0.6, y: 4.2, w: 8.8, h: 0.78, size: 10, lines: [
    { text: 'where = {"$and": [{"$or": [{"acl_employees": True}, {"acl_engineering": True}]},', color: C.codeText },
    { text: '                  {"status": "current"}]}            # app/rag/retriever.py: access_filter()', color: C.codeText }] });
  num(s);

  // ---------------------------------------------------------------- 21 LIVE access_filter
  s = S.liveSlide(deck, { section: "Govern", icon: I.laptop, kicker: "LIVE CODING",
    title1: "Let's write", title2: "access_filter()",
    steps: ["Who: one acl_<group> flag per group the user is in, joined with $or",
      "When: status = current, or effective_from ≤ as_of < effective_to",
      "Run search.py as the intern, then as the HR partner (from the checkpoint 5 folder)"],
    command: `python search.py "salary range for a senior developer" --user intern`,
    notes: `About: Write access_filter() live in app/rag/retriever.py (delete the body first; the solution is the file in the repo). 10 lines.
Code:
  who = [{f"acl_{g}": True} for g in groups]
  clauses = [who[0] if len(who) == 1 else {"$or": who}]
  if as_of: clauses += [{"effective_from": {"$lte": day}}, {"effective_to": {"$gt": day}}]
  else: clauses.append({"status": "current"})
  return {"$and": clauses}
Then run:
  search.py "salary range for a senior developer" --user intern      → coding standards, expense policy (best distance ~1.60: nothing relevant)
  search.py "salary range for a senior developer" --user hr-partner  → Engineering Salary Bands (2026), distance ~0.57
Point out: the intern's results are irrelevant AND harmless. Confidence scoring from checkpoint 4 would say "no result".`,
  });
  num(s, true);

  // ---------------------------------------------------------------- 22 versions
  s = S.contentSlide(deck, {
    section: "Govern", title: "Versions: edits replace, publications supersede",
    subtitle: "\"What's the domestic meal per diem?\" asked on three different dates.",
    takeaway: "HR edited the leave policy in place, so its old version is gone. If you need the past, publish versions.",
    notes: `About: How the register models time. effective_from / effective_to become integers (20261101) so the vector store can filter dates.
Say: "By default the filter says status = current: superseded documents stay in the index but out of answers. Ask with as_of and the filter becomes 'in force on that day' instead."
Demo: search.py "meal per diem" ; --as-of 2024-03-15 ; --as-of 2023-06-01 → $85 (2026), $75 (2024 update), $60 (2023).
The hard case: an amendment (the 2024 update) changes only some sections, so the base policy and the update were both current. The prompt (app/prompts/rag_answer.py) now says: blocks are labelled with version and effective date; if they disagree, use the later one and name it. The 2026 consolidated edition ends the ambiguity: that's why policy owners should publish consolidated versions.
Rule of thumb: edits replace (old text gone), publications supersede (old text kept, filtered).`,
  });
  const tl = [["2023-01-01", "Expense Policy (2023)", "$60", "superseded"], ["2024-01-01", "Update (2024) amends it", "$75", "superseded"], ["2026-11-01", "Expense Policy (2026)", "$85", "current"]];
  s.line({ x: 0.9, y: 2.05, w: 8.2, h: 0, color: C.line, width: 3, name: "tl-line" });
  tl.forEach(([d, t, v, st], i) => {
    const x = 0.6 + i * 3.0;
    s.ellipse({ x: x + 0.15, y: 1.9, w: 0.3, h: 0.3, fill: st === "current" ? C.green : C.gray, name: `tl-dot-${i}` });
    s.text([[{ text: d, b: true, color: C.dark, size: 12 }], [{ text: t, color: C.slate, size: 11 }]], { x: x + 0.55, y: 1.62, w: 2.35, h: 0.9, name: `tl-text-${i}` });
  });
  const asks = [["as_of 2023-06-01", "$60", "Expense Policy (2023 edition) · superseded", C.gray],
    ["as_of 2024-03-15", "$75", "Expense Policy Update (2024) · superseded", C.gray],
    ["today (no as_of)", "$85", "Expense Policy (2026 edition) · current", C.deep]];
  asks.forEach(([q, v, src, color], i) => {
    const y = 2.75 + i * 0.5;
    s.text(q, { x: 0.6, y, w: 1.9, h: 0.42, font: "Consolas", size: 11, color: C.deep, valign: "middle", name: `ask-q-${i}` });
    s.text(v, { x: 2.5, y, w: 0.8, h: 0.42, font: "Arial", size: 18, bold: true, color, valign: "middle", name: `ask-v-${i}` });
    s.text(src, { x: 3.3, y, w: 3.3, h: 0.42, size: 11.5, color: C.slate, valign: "middle", name: `ask-src-${i}` });
  });
  S.card(s, { x: 6.75, y: 2.7, w: 2.65, h: 1.85, title: "Amendments", titleSize: 13, edge: C.amber,
    body: "The 2024 update changed some sections, so base and update were both current. The prompt now says: if blocks disagree, the later effective date wins, and name it.", bodySize: 11 });
  num(s);

  // ---------------------------------------------------------------- 23 PII, provenance, tenancy
  s = S.contentSlide(deck, {
    section: "Govern", title: "PII, provenance, tenancy",
    subtitle: "Three things tutorials skip and production audits ask about first.",
    takeaway: "Embeddings are not one-way. Data you embed is data you store, and back up.",
    notes: `About: app/ingest/pii.py and the provenance fields on every chunk.
Say: "The phishing notice quotes a customer's personal email and phone. The helpdesk export has employees' home contacts. The sync redacted 7 values (3 emails, 4 phones) before embedding. Business addresses like security@acmecorp.com stay: same pattern, opposite decision. That's policy, not regex."
Provenance: every chunk carries doc_id, version, effective date, section and a source_url, so citations come from metadata, not from the model's memory.
Tenancy (not built here): one index, many customers → tenant id on every chunk, enforced in the same filter as permissions. Test cross-tenant retrieval on purpose.
Production detectors: Microsoft Presidio, AWS Comprehend, Google DLP.`,
  });
  S.card(s, { x: 0.6, y: 1.6, w: 2.85, h: 2.75, icon: I.secret, iconInline: true, title: "PII: redact first", titleSize: 13.5,
    body: [{ runs: [{ text: "jane.doe1984@gmail.com", font: "Consolas", size: 10 }], spaceAfter: 0 },
      { runs: [{ text: "→ [EMAIL REDACTED]", size: 10.5, b: true }] },
      { runs: [{ text: "+1 415 555 0134", font: "Consolas", size: 10 }], spaceAfter: 0 },
      { runs: [{ text: "→ [PHONE REDACTED]", size: 10.5, b: true }] },
      { runs: [{ text: "security@acmecorp.com", font: "Consolas", size: 10 }], spaceAfter: 0 },
      { runs: [{ text: "stays: a business contact", size: 10.5 }] },
      { runs: "7 values redacted in 2 documents, before a single vector was computed.", spaceBefore: 2 }], bodySize: 11, paraSpace: 5 });
  S.card(s, { x: 3.58, y: 1.6, w: 2.85, h: 2.75, icon: I.link, iconInline: true, title: "Provenance", titleSize: 13.5,
    body: [{ runs: "Every chunk knows its doc_id, version, effective date, section and link." },
      { runs: "Citations come from this metadata, not from the LLM." },
      { runs: "When a document is wrong, one query finds every chunk of it." }], bodySize: 11.5, paraSpace: 6 });
  S.card(s, { x: 6.56, y: 1.6, w: 2.85, h: 2.75, icon: I.building, iconInline: true, title: "Tenancy", titleSize: 13.5,
    body: [{ runs: "One index, many customers? A tenant id on every chunk, enforced in the same filter as permissions." },
      { runs: "Or one index per tenant for the most sensitive ones." },
      { runs: "Test cross-tenant retrieval on purpose." }], bodySize: 11.5, paraSpace: 6 });
  num(s);

  // ================================================================ PART 4 SYNC
  s = S.darkSlide(deck, { section: "Sync", icon: I.sync, kicker: "PART 4 OF 5", title1: "Sync",
    subtitle: "Ingesting once is a demo. Syncing forever is a system.", footer: "plan  ·  price  ·  apply  ·  rebuild",
    notes: `About: The job that replaces POST /ingest.` });
  num(s, true);

  // ---------------------------------------------------------------- 25 one action per document
  s = S.contentSlide(deck, {
    section: "Sync", title: "One action per document",
    subtitle: "sync.py compares the source with the index and decides. Cheapest check first.",
    takeaway: "The content hash includes the parser and pipeline versions: change the chunker and everything re-embeds.",
    notes: `About: build_plan() in app/ingest/sync.py. Reads only; never writes.
Say: "For each document in the register: is it indexable at all? Is the file there? Same eTag as last time? Then don't even download it. Different bytes? Parse, redact, chunk, hash. Same hash but different labels: relabel, no embedding. Same hash, same labels: touch, the footer case. Different hash: change. Then anything in the index the source no longer knows: remove."
Why the content hash is computed AFTER parsing: the wiki footer changed the bytes (new eTag) but not the text, so nothing re-embeds.`,
  });
  const ladder = [["Not indexable (draft, withdrawn, no entry)?", "skip"], ["Same eTag as the index?", "unchanged (no download)"],
    ["No text (a scan)?", "quarantine"], ["Not in the index yet?", "add"], ["Content hash differs?", "change"], ["Labels differ?", "relabel"],
    ["Only the bytes differ?", "touch"], ["In the index, gone from the source?", "remove"]];
  ladder.forEach(([q, a], i) => {
    const y = 1.55 + i * 0.425;
    s.rect({ x: 0.6, y, w: 5.2, h: 0.36, fill: i % 2 ? C.white : C.soft, name: `lad-${i}` });
    s.text(q, { x: 0.72, y, w: 2.95, h: 0.36, size: 11.5, color: C.dark, valign: "middle", name: `lad-q-${i}` });
    s.text(a, { x: 3.62, y, w: 2.15, h: 0.36, size: 10.5, bold: true, color: C.deep, valign: "middle", font: "Consolas", name: `lad-a-${i}` });
  });
  const acts = [["+ add", "parse, embed, insert", C.deep], ["~ change", "embed, delete old, insert new", C.deep], ["* relabel", "metadata only, no embedding", C.amberDeep],
    ["= touch", "new eTag, same text", C.amberDeep], ["- remove", "delete every chunk", C.redText], ["! quarantine", "report, don't index", C.redText]];
  acts.forEach(([a, d, color], i) => {
    const y = 1.55 + i * 0.57;
    s.rect({ x: 6.05, y, w: 3.35, h: 0.48, fill: C.white, line: C.line, name: `act-${i}` });
    s.text(a, { x: 6.15, y, w: 1.25, h: 0.48, font: "Consolas", size: 12, bold: true, color, valign: "middle", name: `act-a-${i}` });
    s.text(d, { x: 7.4, y, w: 1.95, h: 0.48, size: 11, color: C.slate, valign: "middle", name: `act-d-${i}` });
  });
  num(s);

  // ---------------------------------------------------------------- 26 Monday's plan
  s = S.contentSlide(deck, {
    section: "Sync", title: "Monday's plan",
    subtitle: "python sync.py: a dry run. Nothing is written until --apply.",
    takeaway: "The report goes to a human. Some fixes belong to a document's owner, not to the index.",
    notes: `About: The real dry-run output after sharepoint.py apply all.
Demo: python ${CP}/sync.py   (then)   python ${CP}/sync.py --apply
Say: "Eleven chunks to embed, out of 89. Twelve documents not even downloaded. And two lines for a human: the FAQ quotes the expense policy and the leave policy, both changed this weekend. The index can't fix the FAQ; People Operations can."
Find the stale numbers in the FAQ (exercise 3): 'Software under $75/month' (now $100) and '5 days carry over' (now 10).`,
  });
  S.code(s, { x: 0.6, y: 1.55, w: 6.15, h: 3.42, size: 10, lines: [
    { text: " ! quarantine ENG-INCIDENT-REPORT     a scan. Queued for OCR", color: C.amber },
    { text: " = touch      ENG-WIKI-VECTOR-DB      bytes changed, text identical", color: C.codeText },
    { text: " * relabel    FIN-EXP-2023            status: current -> superseded", color: C.codeText },
    { text: " * relabel    FIN-EXP-2024-UPDATE     status: current -> superseded", color: C.codeText },
    { text: " + add        FIN-EXP-2026            new: 7 chunk(s), markdown", color: C.green },
    { text: " ~ change     HR-LEAVE                6 old chunk(s) out, 4 new in", color: C.green },
    { text: " . skip       HR-PARENTAL-2027-DRAFT  status is draft", color: C.mintText },
    { text: " * relabel    HR-SALARY-BANDS-2026    employees -> hr,managers", color: C.codeText },
    { text: " - remove     LEAD-Q3-NOTES           deleted at the source", color: "F2A19C" },
    { text: "   unchanged  12 document(s), not even downloaded", color: C.mintText },
    { text: "", color: C.codeText },
    { text: "For a human to look at:", color: C.amber },
    { text: " - COMPANY-FAQ quotes FIN-EXP-2026 and HR-LEAVE,", color: C.amber },
    { text: "   which changed. Ask People Operations to review it.", color: C.amber }] });
  S.stat(s, { x: 7.0, y: 1.5, w: 2.4, value: "11 / 89", label: "chunks to embed", size: 30, name: "plan-embed" });
  S.stat(s, { x: 7.0, y: 2.65, w: 2.4, value: "12", label: "documents not even downloaded", size: 30, name: "plan-skip" });
  S.stat(s, { x: 7.0, y: 3.8, w: 2.4, value: "$0.0001", label: "at Gemini prices (local: $0)", size: 26, name: "plan-cost" });
  num(s);

  // ---------------------------------------------------------------- 27 embed first
  s = S.contentSlide(deck, {
    section: "Sync", title: "Embed first, then delete",
    subtitle: "What happens when the embedding API goes down halfway through?",
    takeaway: "Batches stay under API limits. Retries survive a 429. The order makes a failure harmless.",
    notes: `About: apply_plan() embeds every new chunk BEFORE touching the index. Batches of 64 (EMBED_BATCH_SIZE) with retries (with_retries).
Say: "Checkpoint 4's fresh=true deleted the collection first, then embedded. If embedding failed, users got an empty index: 'I don't know' to every question until someone noticed."
Proof: tests/test_sync.py::test_a_failed_embedding_leaves_the_index_untouched simulates an outage mid-sync; the old leave policy is still served.
Also: one batch call per 64 chunks, not one giant call (Gemini caps a request at 100 texts, Azure at 2,048).`,
  });
  const before = ["?fresh=true: delete the collection", "Embed everything again", "Embedding fails halfway", "Index is empty: every answer is \"I don't know\""];
  const after = ["Embed new chunks: batches of 64, retried", "Embedding fails? Stop. Nothing was deleted", "Then delete the old chunks of that document", "Then insert the new ones"];
  [[before, "CHECKPOINT 4", C.red, 0.6], [after, "CHECKPOINT 5", C.deep, 5.1]].forEach(([list, label, color, x]) => {
    s.text(label, { x, y: 1.55, w: 4.3, h: 0.3, size: 11, bold: true, color, charSpacing: 1, name: `order-label-${label}` });
    list.forEach((t, i) => {
      const y = 1.95 + i * 0.75;
      s.rect({ x, y, w: 4.3, h: 0.58, fill: C.white, line: i === (color === C.red ? 3 : 1) ? color : C.line, lineWidth: i === (color === C.red ? 3 : 1) ? 1.5 : 1, name: `order-${label}-${i}` });
      s.ellipse({ x: x + 0.15, y: y + 0.12, w: 0.34, h: 0.34, fill: color, name: `order-dot-${label}-${i}` });
      s.text(String(i + 1), { x: x + 0.15, y: y + 0.12, w: 0.34, h: 0.34, font: "Arial", size: 11, bold: true, color: C.white, align: "center", valign: "middle", name: `order-num-${label}-${i}` });
      s.text(t, { x: x + 0.62, y, w: 3.6, h: 0.58, size: 12, color: C.dark, valign: "middle", name: `order-text-${label}-${i}` });
    });
  });
  num(s);

  // ---------------------------------------------------------------- 28 blue/green
  s = S.contentSlide(deck, {
    section: "Sync", title: "Changing the model? Build next to it",
    subtitle: "Vectors from two models cannot share an index. The sync refuses, and tells you what to do.",
    takeaway: "A rebuild is a deploy: build, check, switch, keep the old one for rollback.",
    notes: `About: app/rag/catalog.py keeps a pointer to the live collection. sync.py --rebuild builds a new collection next to it, runs a smoke check, and only then flips the pointer. sync.py --rollback flips it back.
Demo (optional): set EMBEDDING_PROVIDER=gemini in .env and run sync.py: it stops with the message on the slide. Then sync.py --rebuild --apply (costs about a tenth of a cent).
Say: "Vector databases call the pointer an alias. Same idea as blue/green deploys: users never see a half-built index."`,
  });
  s.rect({ x: 0.6, y: 1.7, w: 1.5, h: 0.7, fill: C.dark, name: "bg-queries" });
  s.text("Queries", { x: 0.6, y: 1.7, w: 1.5, h: 0.7, font: "Arial", size: 13, bold: true, color: C.white, align: "center", valign: "middle", name: "bg-queries-t" });
  S.arrow(s, 2.15, 2.05, 2.75, 2.05, C.gray);
  s.rect({ x: 2.8, y: 1.6, w: 1.75, h: 0.9, fill: C.white, line: C.deep, lineWidth: 1.5, name: "bg-pointer" });
  s.text([[{ text: "catalog.json", font: "Consolas", size: 11, b: true, color: C.deep }], [{ text: "active →", size: 11, color: C.slate }]], { x: 2.8, y: 1.6, w: 1.75, h: 0.9, align: "center", valign: "middle", name: "bg-pointer-t" });
  S.arrow(s, 4.6, 2.05, 5.2, 2.05, C.deep, 2);
  s.rect({ x: 5.25, y: 1.6, w: 1.9, h: 0.9, fill: C.greenSoft, line: C.deep, name: "bg-live" });
  s.text([[{ text: "cp5_kb_A", font: "Consolas", size: 11, b: true, color: C.deep }], [{ text: "LIVE", size: 10, b: true, color: C.deep }]], { x: 5.25, y: 1.6, w: 1.9, h: 0.9, align: "center", valign: "middle", name: "bg-live-t" });
  s.rect({ x: 7.5, y: 1.6, w: 1.9, h: 0.9, fill: C.white, line: C.line, name: "bg-new" });
  s.text([[{ text: "cp5_kb_B", font: "Consolas", size: 11, b: true, color: C.slate }], [{ text: "building", size: 10, color: C.gray }]], { x: 7.5, y: 1.6, w: 1.9, h: 0.9, align: "center", valign: "middle", name: "bg-new-t" });
  const bsteps = ["Build B next to A", "Smoke check B", "Switch the pointer", "Keep A for rollback"];
  const stepX = [0.6, 2.8, 5.25, 7.5];  // under the boxes above
  bsteps.forEach((t, i) => {
    const x = stepX[i];
    s.ellipse({ x, y: 2.85, w: 0.36, h: 0.36, fill: C.deep, name: `bg-step-dot-${i}` });
    s.text(String(i + 1), { x, y: 2.85, w: 0.36, h: 0.36, font: "Arial", size: 11, bold: true, color: C.white, align: "center", valign: "middle", name: `bg-step-n-${i}` });
    s.text(t, { x: x + 0.45, y: 2.82, w: 1.7, h: 0.42, size: 12, bold: true, color: C.dark, valign: "middle", name: `bg-step-t-${i}` });
  });
  S.code(s, { x: 0.6, y: 3.5, w: 8.8, h: 1.45, label: "python sync.py   (after changing EMBEDDING_PROVIDER)", size: 10, lines: [
    { text: "STOP: The live index was built with local:all-MiniLM-L6-v2, but the embedder is", color: C.amber },
    { text: "now gemini:gemini-embedding-001. Vectors from two models cannot share an index.", color: C.amber },
    { text: "Run: python sync.py --rebuild", color: C.green }] });
  num(s);

  // ================================================================ PART 5 MEASURE
  s = S.darkSlide(deck, { section: "Measure", icon: I.chart, kicker: "PART 5 OF 5", title1: "Measure",
    subtitle: "Prove the index is right, on every change", footer: "golden set  ·  quality  ·  safety",
    notes: `About: How we got the numbers on slide 8, and the same numbers for today's index.` });
  num(s, true);

  // ---------------------------------------------------------------- 30 golden set
  s = S.contentSlide(deck, {
    section: "Measure", title: "A golden set, and two kinds of numbers",
    subtitle: "31 questions in employees' own words. Each says who asks and which documents may answer.",
    takeaway: "No LLM in this evaluation: it runs in seconds, on every change, for free.",
    notes: `About: app/evals/golden.json and app/evals/judge.py.
Say: "Quality asks: did the right document come back, and how high? Hit@5 and MRR. Safety asks: did anything come back that must not? Five flags, counted per question."
The rules of a golden set: hand-write about 30 to start (not 10, which is noise; not 1,000, which nobody reads). Write questions from the user's mouth, not by reading the docs. Include questions that should return NOTHING (expect: []): the permission traps. Never edit a question because the system got it wrong.
MRR: rank 1 → 1.0, rank 2 → 0.5, rank 5 → 0.2, missing → 0, averaged.`,
  });
  S.code(s, { x: 0.6, y: 1.6, w: 4.4, h: 1.95, label: "app/evals/golden.json (two of 31)", size: 9, lines: [
    '{"id": "Q18", "user": "intern",', ' "question": "How much can I spend per', '   person on a team dinner?",', ' "expect": ["FIN-EXP-2026"]},',
    '{"id": "Q24", "user": "intern",', ' "question": "What is the salary range', '   for a Senior Developer?",', ' "expect": []}            # nothing!'] });
  s.text("RULES OF A GOLDEN SET", { x: 0.6, y: 3.7, w: 4.4, h: 0.28, size: 10, bold: true, color: C.deep, charSpacing: 1, name: "rules-kicker" });
  s.text([{ runs: "Hand-write about 30. Read every result.", bullet: true }, { runs: "From the user's mouth, not from the docs.", bullet: true },
    { runs: "Include questions that must return nothing.", bullet: true }, { runs: "Never edit one because the system missed it.", bullet: true }],
    { x: 0.6, y: 4.0, w: 4.4, h: 1.0, size: 11.5, color: C.slate, paraSpace: 2, name: "rules" });
  S.card(s, { x: 5.25, y: 1.6, w: 4.15, h: 1.55, title: "Quality", titleSize: 14, edge: C.deep,
    body: [{ runs: [{ text: "Hit@5  ", b: true, color: C.dark }, { text: "right document in the top 5?" }] }, { runs: [{ text: "MRR  ", b: true, color: C.dark }, { text: "1 / rank of the first right one" }] }], bodySize: 12, paraSpace: 4 });
  S.card(s, { x: 5.25, y: 3.3, w: 4.15, h: 1.7, title: "Safety (per question)", titleSize: 14, edge: C.red,
    body: [{ runs: [{ text: "leak ", b: true, color: C.dark }, { text: "a chunk this user may not read" }] }, { runs: [{ text: "stale ", b: true, color: C.dark }, { text: "superseded or draft" }] },
      { runs: [{ text: "ghost ", b: true, color: C.dark }, { text: "deleted, or text no longer in the file" }] }, { runs: [{ text: "pii, empty ", b: true, color: C.dark }, { text: "personal data, empty text" }] }], bodySize: 11.5, paraSpace: 2 });
  num(s);

  // ---------------------------------------------------------------- 31 Monday measured
  s = S.contentSlide(deck, {
    section: "Measure", title: "Monday, measured",
    subtitle: "python evaluate.py: the same 31 questions against both indexes.",
    takeaway: "Ingestion took the safety numbers to zero. Quality has one honest miss left.",
    notes: `About: The full comparison. Run it live: python ${CP}/evaluate.py (about 10 seconds, no LLM).
Say: "Same embedding model on both sides. Every difference comes from ingestion: what got in, in what shape, with which labels, and what got deleted."
The one miss (Q08): "How many reviewers does a change to the billing code need?" The answer is mid-paragraph in a PDF page ("A change that touches billing or authentication needs two reviewers"); the coding standards rank higher. That is a retrieval problem, not an ingestion problem: next session's starting point (hybrid search and re-ranking). Say that in words, it is not on the slide.`,
  });
  S.table(s, { x: 0.6, y: 1.55, cols: [3.3, 1.55, 1.55], rowH: 0.39, headH: 0.36, size: 11.5, align: "center",
    header: ["Monday · 31 questions · top 5", { text: "Checkpoint 4's /ingest", align: "center" }, { text: "Today's sync", align: "center" }],
    rows: [
      ["Hit@5 (27 answerable)", { text: "0.81", b: true }, { text: "0.96", b: true, color: C.deep }],
      ["MRR", { text: "0.63", b: true }, { text: "0.90", b: true, color: C.deep }],
      ["Questions with a chunk the user may not read", { text: "7", b: true, color: C.redText, fill: C.redSoft }, { text: "0", b: true, color: C.deep, fill: C.greenSoft }],
      ["... a superseded or draft chunk", { text: "14", b: true, color: C.redText, fill: C.redSoft }, { text: "0", b: true, color: C.deep, fill: C.greenSoft }],
      ["... a deleted or outdated chunk", { text: "11", b: true, color: C.redText, fill: C.redSoft }, { text: "0", b: true, color: C.deep, fill: C.greenSoft }],
      ["... personal data", { text: "4", b: true, color: C.redText, fill: C.redSoft }, { text: "0", b: true, color: C.deep, fill: C.greenSoft }],
      ["Clean questions (none of the above)", { text: "11", b: true }, { text: "31", b: true, color: C.deep }],
    ] });
  S.card(s, { x: 7.2, y: 1.55, w: 2.2, h: 3.09, title: "Today's 1 miss", titleSize: 13, edge: C.amber,
    body: [{ runs: "Q08: \"How many reviewers does a change to the billing code need?\"" },
      { runs: "The rule is in the middle of a paragraph in a PDF page. The coding standards rank higher." }], bodySize: 11, paraSpace: 6 });
  num(s);

  // ---------------------------------------------------------------- 32 stack recap
  s = S.contentSlide(deck, {
    section: "Measure", title: "The ingestion stack, in six files",
    subtitle: "Six layers. Each is where a real system spends real engineering time.",
    takeaway: "Diff it: git diff --no-index checkpoints/checkpoint-4-analysis checkpoints/checkpoint-5-production-ingestion",
    notes: `About: Recap mapping each production layer to checkpoint 5's code. Good slide to leave up while students start the exercises.`,
  });
  const stack = [["Connect & authenticate", "connector.py", "Service principal; list, fetch, register"], ["Detect change", "sync.py", "eTag first, content hash next, labels last"],
    ["Parse format-aware", "parsers.py", "Sections with headings; scans quarantined"], ["Normalize, redact, enrich", "pii.py, chunker.py", "PII out; \"title > heading\" in"],
    ["Embed in batches", "embedder.py", "Batches of 64, retries with backoff"], ["Store, filter, switch", "store_chroma.py, retriever.py, catalog.py", "ACL + version filter; blue/green"]];
  stack.forEach(([layer, file, what], i) => {
    const y = 1.55 + i * 0.57;
    s.rect({ x: 0.6, y, w: 8.8, h: 0.5, fill: C.white, line: C.line, name: `stack-${i}` });
    s.ellipse({ x: 0.72, y: y + 0.08, w: 0.34, h: 0.34, fill: C.deep, name: `stack-dot-${i}` });
    s.text(String(i + 1), { x: 0.72, y: y + 0.08, w: 0.34, h: 0.34, font: "Arial", size: 11, bold: true, color: C.white, align: "center", valign: "middle", name: `stack-n-${i}` });
    s.text(layer, { x: 1.2, y, w: 2.55, h: 0.5, size: 12.5, bold: true, color: C.dark, valign: "middle", name: `stack-layer-${i}` });
    s.text(file, { x: 3.8, y, w: 2.75, h: 0.5, font: "Consolas", size: 10, color: C.deep, valign: "middle", name: `stack-file-${i}` });
    s.text(what, { x: 6.6, y, w: 2.75, h: 0.5, size: 11, color: C.slate, valign: "middle", name: `stack-what-${i}` });
  });
  num(s);

  // ---------------------------------------------------------------- 33 After class divider
  s = S.darkSlide(deck, { section: "After class", icon: I.tasks, kicker: "AFTER CLASS", title1: "Your turn",
    subtitle: "Four exercises on checkpoint 5, then the reference slides", footer: "exercises  ·  commands  ·  checklist",
    notes: `About: Everything after this slide is for students to read at home.` });
  num(s, true);

  // ---------------------------------------------------------------- 34 Exercises
  s = S.contentSlide(deck, {
    section: "After class", title: "Tonight",
    subtitle: "Each exercise changes the register or the source, then you prove the change with evaluate.py.",
    takeaway: "Run the tests after each change: pytest checkpoints/checkpoint-5-production-ingestion/tests -q",
    notes: `About: Homework. Solutions are not in the repo on purpose; discuss at the start of next session.`,
  });
  const ex = [["Withdraw the 2024 update", "Add a sixth event: Finance withdraws the 2024 update outright. What should the sync do? Which golden questions change?"],
    ["Keep the leave policy's past", "HR edited it in place, so \"how many days could I carry over in 2025?\" has no answer. Change the register so both versions survive."],
    ["Fix the FAQ", "The sync says the FAQ quotes two documents that changed. Find the two stale numbers in it."],
    ["Add a fence", "Add a document only sales can read, and one golden question for each side of the fence."]];
  ex.forEach(([t, d], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    S.card(s, { x: 0.6 + col * 4.45, y: 1.55 + row * 1.72, w: 4.3, h: 1.58, num: i + 1, title: t, titleSize: 13.5, body: d, bodySize: 11.5, name: `ex-${i}` });
  });
  num(s);

  // ---------------------------------------------------------------- R1 commands
  s = S.contentSlide(deck, {
    section: "Reference", title: "Reference: the demo, command by command",
    subtitle: "Run from the checkpoint folder (every script also works from any other folder).",
    notes: `About: The exact sequence used in class, for students to replay.`,
  });
  S.code(s, { x: 0.6, y: 1.55, w: 4.3, h: 3.45, size: 10, lines: [
    `cd ${CP}`, "",
    "# once, at home (~80 MB model)",
    "python warmup.py", "",
    "# Friday",
    "python sharepoint.py reset",
    "python sync.py          # dry run",
    "python sync.py --apply",
    "python sync.py --naive  # checkpoint 4's"] });
  S.code(s, { x: 5.1, y: 1.55, w: 4.3, h: 3.45, size: 10, lines: [
    "# the weekend, then Monday",
    "python sharepoint.py apply all",
    "python sync.py          # the plan",
    "python sync.py --apply",
    "python sync.py --naive", "",
    "# measure, then ask",
    "python evaluate.py --details",
    'python search.py "team dinner limit"',
    "    --as-of 2023-06-01"] });
  num(s);

  // ---------------------------------------------------------------- R2 format rules of thumb
  s = S.contentSlide(deck, {
    section: "Reference", title: "Reference: format rules of thumb",
    subtitle: "What to keep, what to drop, and what to watch for, per format.",
    notes: `About: Condensed from the format deep dive. Not presented in class.`,
  });
  S.table(s, { x: 0.6, y: 1.55, cols: [1.35, 3.6, 3.85], rowH: 0.48, headH: 0.34, size: 10.5,
    header: ["Format", "Keep", "Watch out"],
    rows: [[{ text: "DOCX", b: true, color: C.dark }, "H1/H2 as chunk anchors; tables as their own chunks", "Tracked changes and comments leaking into the text"],
      [{ text: "PPTX", b: true, color: C.dark }, "One chunk per slide, speaker notes included", "The real content is often in the notes"],
      [{ text: "XLSX", b: true, color: C.dark }, "Each sheet is its own document; label rows with the header", "Numbers you need to aggregate: use SQL, not RAG"],
      [{ text: "HTML", b: true, color: C.dark }, "The article: trafilatura, readability, or a tag allow-list", "Single-page apps render with JS: static parsing gets an empty div"],
      [{ text: "Email", b: true, color: C.dark }, "The thread is the unit; subject, sender, date", "Signatures, quoted replies, disclaimers, attachments"],
      [{ text: "Code", b: true, color: C.dark }, "Split on functions and classes, keep the imports", "A function without its class is often meaningless"]] });
  num(s);

  // ---------------------------------------------------------------- R3 checklist
  s = S.contentSlide(deck, {
    section: "Reference", title: "Reference: a production ingestion checklist",
    subtitle: "Before you call an ingestion pipeline production-ready.",
    notes: `About: The checklist to take into the capstone design doc.`,
  });
  const cl = [["Source", ["Runs as a service principal, not a person", "Uses the source's change feed (delta, eTags)", "Notices deletions, not only additions"]],
    ["Content", ["Every format parsed or reported, never skipped silently", "Scans detected and queued for OCR", "PII redacted before embedding"]],
    ["Metadata", ["Permissions copied onto every chunk; fail closed", "Status and effective dates; drafts never indexed", "Provenance: doc_id, version, link"]],
    ["Operations", ["Dry run with a cost estimate", "Batches, retries, embed before delete", "Blue/green rebuilds; a golden set run on every change"]]];
  cl.forEach(([t, items], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    S.card(s, { x: 0.6 + col * 4.45, y: 1.55 + row * 1.72, w: 4.3, h: 1.58, title: t, titleSize: 13.5, icon: I.check, iconInline: true,
      body: items.map(x => ({ runs: x, bullet: true })), bodySize: 11.5, name: `cl-${i}` });
  });
  num(s);

  return deck;
}

module.exports = { build };

if (require.main === module) {
  (async () => {
    const deck = await build();
    const out = process.argv[2] || ".";
    deck.saveHtml(path.join(out, "s08-preview.html"));
    await deck.savePptx(path.join(out, "s08.pptx"), S.THEME);
    console.log(`slides: ${deck.slides.length}`);
  })().catch(e => { console.error(e); process.exit(1); });
}
