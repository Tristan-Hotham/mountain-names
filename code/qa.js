// QA: open index.html at desktop and phone widths, log console errors, exercise the map, take screenshots to qa/.
// Run from the study root with a static server (PORT, default 8803). MapLibre from a local npm copy (MAPLIBRE_DIST).
const { chromium } = require("playwright");
const ML = process.env.MAPLIBRE_DIST || "/tmp/ml/node_modules/maplibre-gl/dist";
(async () => {
  const b = await chromium.launch({ args: ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"] });
  const errs = [], checks = [];
  const ok = (c, m) => checks.push((c ? "ok   " : "FAIL ") + m);
  for (const [nm, vw, vh] of [["desktop", 1280, 900], ["phone", 390, 844]]) {
    const p = await b.newPage({ viewport: { width: vw, height: vh }, deviceScaleFactor: nm === "phone" ? 2 : 1 });
    await p.route(/googleapis|gstatic|site-nav/, r => r.abort());
    await p.route(/maplibre-gl\.js$/, r => r.fulfill({ path: ML + "/maplibre-gl.js" }));
    await p.route(/maplibre-gl\.css$/, r => r.fulfill({ path: ML + "/maplibre-gl.css" }));
    p.on("console", m => { if (m.type() === "error" && !/ERR_FAILED|net::|Failed to load resource|AJAXError|tiles?|terrarium/i.test(m.text())) errs.push(nm + ": " + m.text()); });
    p.on("pageerror", e => errs.push(nm + " pageerror: " + e.message));
    await p.goto("http://localhost:" + (process.env.PORT || 8803) + "/index.html", { waitUntil: "load" });
    await p.waitForTimeout(10000);
    await p.screenshot({ path: `qa/${nm}_top.png` });
    const shot = async (sel, f) => { await p.locator(sel).scrollIntoViewIfNeeded(); await p.waitForTimeout(700); await p.locator(sel).screenshot({ path: `qa/${nm}_${f}.png` }); };
    ok(await p.evaluate(() => eReady), `${nm}: map ready`);
    await shot("#atlas", "atlas");
    await p.evaluate(() => { const k = K.find(k => k.name === "Aoraki / Mount Cook"); pickPeak(k.i, true); }); await p.waitForTimeout(2500);
    ok(await p.locator("#emap .maplibregl-popup").count() === 1, `${nm}: peak popup`);
    ok(await p.evaluate(() => emap.getSource("lsel")._data.features.length > 0), `${nm}: line drawn`);
    await shot("#atlas", "pick_cook");
    await p.click('#contRow [data-c="5"]'); await p.waitForTimeout(1500);
    ok(await p.evaluate(() => S.cont === 5 && emap.getSource("ln")._data.features.length > 100), `${nm}: Oceania filter draws lines`);
    await shot("#atlas", "oceania");
    await p.click('#contRow .btn:not([data-c])'); await p.click('#occRow [data-o="0"]'); await p.waitForTimeout(1200);
    await shot("#atlas", "royals");
    await p.click('#occRow .btn:not([data-o])'); await p.waitForTimeout(500);
    const key = await p.evaluate(() => Object.keys(PLACES).find(k => PLACES[k].n >= 5)); await p.evaluate(k => pickPlace(k), key); await p.waitForTimeout(800);
    ok(await p.locator("#emap .maplibregl-popup .go").count() >= 1, `${nm}: birthplace popup lists mountains`);
    await p.fill("#q", "everest"); await p.waitForTimeout(400);
    ok(await p.locator("#sug li").count() > 0, `${nm}: search suggestions`);
    await p.keyboard.press("Enter"); await p.waitForTimeout(2500);
    ok(await p.evaluate(() => S.sel != null && K[S.sel].name === "Mount Everest"), `${nm}: search picks Everest`);
    await shot("#atlas", "everest");
    await p.locator("#emap .lyrBtn").click(); await p.waitForTimeout(300);
    await p.locator('#emap .lyrPanel [data-k="lines"]').uncheck(); await p.waitForTimeout(300);
    ok(await p.evaluate(() => emap.getLayoutProperty("ln", "visibility") === "none"), `${nm}: lines toggle`);
    await p.locator('#emap .lyrPanel [data-k="lines"]').check(); await p.locator("#emap .lyrBtn").click();
    for (const c of ["colChart", "occChart", "tallTable", "renTable"]) await shot("#" + c, c);
    ok(await p.locator(".mfs-btn").count() === 1, `${nm}: full-screen button`);
    await p.locator("#atlas").scrollIntoViewIfNeeded();
    await p.locator("#emap .mfs-btn").click(); await p.waitForTimeout(1200);
    ok(await p.evaluate(() => !!document.fullscreenElement || document.getElementById("emap").classList.contains("mfs-fake")), `${nm}: full screen on`);
    await p.screenshot({ path: `qa/${nm}_fullscreen.png` });
    await p.locator("#emap .mfs-btn").click(); await p.waitForTimeout(500);
    if (nm === "phone") { await p.click("#theme"); await p.waitForTimeout(600); await shot("#colChart", "dark_col"); }
    const ov = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    ok(ov <= 0, `${nm}: horizontal overflow ${ov}px`);
    await p.close();
  }
  console.log(checks.join("\n")); console.log("errors:", errs.length ? errs : "none");
  await b.close();
})();
