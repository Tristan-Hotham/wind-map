/* ===== charts (inline SVG) ===== */
const goMap = (lat, lon, name) => { choose({ lat, lon, name }); };

/* wind belts: ocean mean west-east wind and speed by latitude */
(() => {
  const box = document.getElementById("zonalChart"); if (!box) return;
  const rows = PD.zonal;
  resp(box, (w, small) => {
    const rh = small ? 7 : 8, H = rows.length * rh + 46, L = 40, s = el("svg", { viewBox: `0 0 ${w} ${H}` }, box);
    const mid = L + (w - L - 20) * .42, ux = v => mid + v * (w - L - 20) * .042, sx = v => L + v / 14 * (w - L - 20);
    [-8, -4, 0, 4, 8].forEach(v => { el("line", { x1: ux(v), x2: ux(v), y1: 14, y2: H - 26, stroke: css("--rule") }, s); lbl(s, ux(v), H - 10, (v > 0 ? "+" : "") + v, "lab s m", "middle"); });
    lbl(s, ux(-1), 10, small ? "← easterly" : "← from the east", "lab s m", "end"); lbl(s, ux(1), 10, small ? "westerly →" : "from the west →", "lab s m");
    const pts = [];
    rows.forEach((r, i) => { const y = 18 + i * rh, u = r[1];
      const b = el("rect", { x: Math.min(ux(0), ux(u)), y, width: Math.abs(ux(u) - ux(0)), height: rh - 1.5, fill: u < 0 ? css("--gold") : css("--teal"), opacity: .85 }, s);
      hover(b, `<b>${Math.abs(r[0])}° ${r[0] >= 0 ? "N" : "S"}</b><br>Mean west to east wind ${r[1] > 0 ? "+" : ""}${f1(r[1])} m/s<br>Mean speed ${f1(r[2])} m/s<br>January ${f1(r[3])}, July ${f1(r[4])} m/s (west to east)`);
      pts.push([sx(r[2]), y + rh / 2]);
      if (r[0] % 15 === 0) lbl(s, L - 6, y + rh - 1, `${Math.abs(r[0])}°${r[0] > 0 ? "N" : r[0] < 0 ? "S" : ""}`, "lab s m", "end");
    });
    el("polyline", { points: pts.map(p => p.join(",")).join(" "), fill: "none", stroke: css("--deep"), "stroke-width": 2 }, s);
    const lab = (lat, t, col) => { const i = rows.findIndex(r => r[0] === lat); if (i < 0) return; const y = 18 + i * rh + rh; (lat < -30 ? lbl(s, L + 4, y, t, "lab s b") : lbl(s, w - 4, y, t, "lab s b", "end")).setAttribute("fill", col); };
    lab(15, "north-east trades", css("--gold")); lab(-15, "south-east trades", css("--gold")); lab(47.5, "westerlies", css("--teal")); lab(-40, "Roaring Forties", css("--teal")); lab(-55, "Furious Fifties", css("--teal"));
    const i0 = rows.findIndex(r => r[0] === 5); lbl(s, sx(rows[i0][2]) + 6, 18 + i0 * rh + rh, "speed (line)", "lab s b").setAttribute("fill", css("--deep"));
  });
})();

/* monsoon clock */
(() => {
  const box = document.getElementById("monsoonChart"); if (!box) return;
  resp(box, (w, small) => {
    const cols = small ? 6 : 12, L0 = small ? 0 : 110, cw = (w - L0) / cols, rowH = small ? 64 : 70, H = (small ? 4 : 2) * rowH + (small ? 60 : 34), s = el("svg", { viewBox: `0 0 ${w} ${H}` }, box);
    [["Arabian Sea", PD.arabian], ["Bay of Bengal", PD.bengal]].forEach(([nm, arr], r) => {
      const yb = small ? 26 + r * (2 * rowH + 30) : 40 + r * 70; if (small) lbl(s, 0, yb - 8, nm, "lab b"); else lbl(s, 0, yb + 4, nm, "lab b");
      arr.forEach((a, k) => { const y = small ? yb + 34 + Math.floor(k / 6) * rowH : yb, x = L0 + (k % cols) * cw + cw / 2, sc = Math.min(cw, 60) / 2 / 12, len = Math.hypot(a[0], a[1]) * sc, dx = a[0] / Math.hypot(a[0], a[1]), dy = -a[1] / Math.hypot(a[0], a[1]);
        const col = a[0] > 0 ? css("--teal") : css("--gold"), x0 = x - dx * len, y0 = y - dy * len, x1 = x + dx * len, y1 = y + dy * len;
        const g = el("g", {}, s); el("circle", { cx: x, cy: y, r: Math.min(cw, 60) / 2 - 2, fill: "none", stroke: css("--rule") }, g);
        el("line", { x1: x0, y1: y0, x2: x1, y2: y1, stroke: col, "stroke-width": 3, "stroke-linecap": "round" }, g);
        el("path", { d: `M${x1},${y1} L${x1 - dx * 7 - dy * 4},${y1 - dy * 7 + dx * 4} L${x1 - dx * 7 + dy * 4},${y1 - dy * 7 - dx * 4} Z`, fill: col }, g);
        const frm = (Math.atan2(-a[0], -a[1]) * 180 / Math.PI + 360) % 360;
        hover(g, `<b>${nm}, ${MON[k]}</b><br>From the ${PTS[Math.round(frm / 22.5) % 16]}<br>${f1(Math.hypot(a[0], a[1]))} m/s as an average arrow; mean speed ${f1(a[2])} m/s`);
        if (small) lbl(s, x, y + Math.min(cw, 60) / 2 + 12, MON[k].slice(0, 3), "lab s m", "middle"); else if (r === 0) lbl(s, x, 14, MON[k][0], "lab s m", "middle");
      });
    });
  });
})();

/* sortable tables */
function table(id, cols, rows, sk0, onRow) {
  const t = document.getElementById(id); if (!t) return; let sk = sk0, dir = -1;
  const draw = () => {
    const rs = rows.slice().sort((a, b) => (typeof a[sk] === "string" ? a[sk].localeCompare(b[sk]) : (a[sk] ?? -1) - (b[sk] ?? -1)) * dir);
    t.innerHTML = `<thead><tr>${cols.map(c => `<th class="${c.num ? "num " : ""}${c.wide ? "wide" : ""}" data-k="${c.k}">${c.h}${c.k === sk ? (dir > 0 ? " ↑" : " ↓") : ""}</th>`).join("")}</tr></thead><tbody>${rs.map((r, i) => `<tr class="go" data-i="${rows.indexOf(r)}">${cols.map(c => `<td class="${c.num ? "num " : ""}${c.wide ? "wide" : ""}">${c.f ? c.f(r[c.k], r) : esc(r[c.k])}</td>`).join("")}</tr>`).join("")}</tbody>`;
    t.querySelectorAll("th").forEach(th => th.onclick = () => { const k = +th.dataset.k; if (k === sk) dir = -dir; else { sk = k; dir = typeof rows[0][k] === "string" ? 1 : -1; } draw(); });
    t.querySelectorAll("tr.go").forEach(tr => tr.onclick = () => onRow && onRow(rows[+tr.dataset.i]));
  };
  draw();
}
const swW = v => `<span class="sw" style="background:${rgb(windRGB(v))}"></span>`;
table("placeTable", [{ h: "Place", k: 0, f: (v, r) => `${esc(v)}<small>${esc(r[1])}</small>` }, { h: "m/s", k: 4, num: 1, f: v => swW(v) + f1(v) }, { h: "Windiest", k: 5, wide: 1 }, { h: "Calmest", k: 6, wide: 1 }], PD.places, 4, r => goMap(r[2], r[3], r[0]));
table("seasTable", [{ h: "Place", k: 0, f: (v, r) => `${esc(v)}<small>${esc(r[1])}</small>` }, { h: "Ratio", k: 4, num: 1, f: v => `<span class="sw" style="background:${rgb(seasRGB(v))}"></span>${v.toFixed(1)}×` }, { h: "Mean m/s", k: 5, num: 1, f: f1, wide: 1 }, { h: "Windiest", k: 6 }, { h: "Calmest", k: 7, wide: 1 }], PD.seasonal, 4, r => goMap(r[2], r[3], r[0]));
table("farmTable", [{ h: "Country", k: 0 }, { h: "Land", k: 2, num: 1, f: f1 }, { h: "Farms", k: 3, num: 1, f: f1 }, { h: "Less windy", k: 4, num: 1, f: v => v + "%" }, { h: "MW land", k: 5, num: 1, f: fmt, wide: 1 }, { h: "MW sea", k: 7, num: 1, f: fmt, wide: 1 }], PD.farmc, 5, null);

/* cities */
(() => {
  const box = document.getElementById("cityChart"); if (!box) return;
  const top = PD.cities.slice(0, 10), bot = PD.cities.slice(10, 20);
  resp(box, (w, small) => {
    const half = small ? w : (w - 24) / 2, rh = 21, H = small ? 2 * (10 * rh + 30) : 10 * rh + 34, s = el("svg", { viewBox: `0 0 ${w} ${H}` }, box);
    [[top, "Windiest", 0, 0], [bot, "Calmest", small ? 0 : half + 24, small ? 10 * rh + 30 : 0]].forEach(([arr, t, x0, y0]) => {
      const Lw = small ? 108 : 112, x = v => x0 + Lw + v / 6.5 * (half - Lw - 34);
      lbl(s, x0, y0 + 12, t, "lab b");
      arr.forEach((c, i) => { const y = y0 + 22 + i * rh; lbl(s, x0 + Lw - 6, y + 12, c[0].length > 14 ? c[0].slice(0, 13) + "." : c[0], "lab", "end");
        const r = el("rect", { x: x(0), y: y + 2, width: x(c[4]) - x(0), height: rh - 7, fill: rgb(windRGB(c[4])), stroke: css("--border") }, s);
        lbl(s, x(c[4]) + 4, y + 13, f1(c[4]), "lab s"); r.onclick = () => goMap(c[2], c[3], c[0]); hover(r, `<b>${esc(c[0])}</b>, ${esc(c[1])}<br>${f1(c[4])} m/s annual mean at 10 m`); });
    });
  });
})();

/* hemispheres and UK by month */
(() => {
  const box = document.getElementById("hemiChart"); if (!box) return;
  const ser = [["Northern hemisphere land", PD.nh, css("--teal")], ["Southern hemisphere land", PD.sh, css("--gold")], ["United Kingdom", PD.uk, css("--deep")]];
  resp(box, (w, small) => {
    const H = 250, L = 34, T = 34, B = 30, s = el("svg", { viewBox: `0 0 ${w} ${H}` }, box), x = k => L + k / 11 * (w - L - 16), y = v => T + (1 - (v - 2) / 4.2) * (H - T - B);
    [2, 3, 4, 5, 6].forEach(v => { el("line", { x1: L, x2: w - 16, y1: y(v), y2: y(v), stroke: css("--rule") }, s); lbl(s, L - 6, y(v) + 4, v, "lab s m", "end"); });
    MON.forEach((m, k) => lbl(s, x(k), H - 10, small ? m[0] : m.slice(0, 3), "lab s m", "middle"));
    ser.forEach(([n, arr, col], j) => { el("polyline", { points: arr.map((v, k) => `${x(k)},${y(v)}`).join(" "), fill: "none", stroke: col, "stroke-width": 2.5 }, s);
      arr.forEach((v, k) => hover(el("circle", { cx: x(k), cy: y(v), r: 4, fill: col }, s), `<b>${n}</b><br>${MON[k]}: ${v.toFixed(2)} m/s`));
      el("rect", { x: L + j * (small ? 0 : 200), y: small ? 4 + j * 0 : 6, width: 0, height: 0 }, s); });
    ser.forEach(([n, , col], j) => { const lx = small ? L + (j % 2) * 150 : L + j * 210, ly = small ? 6 + Math.floor(j / 2) * 14 : 12; el("rect", { x: lx, y: ly, width: 12, height: 4, fill: col }, s); lbl(s, lx + 16, ly + 6, n.replace(" hemisphere", "").replace("United Kingdom", "UK"), "lab s"); });
    lbl(s, w - 16, T - 4, "m/s at 10 m", "lab s m", "end");
  });
})();

/* farms against land */
(() => {
  const box = document.getElementById("farmChart"); if (!box) return;
  const rows = PD.farmc.slice().sort((a, b) => b[4] - a[4]);
  resp(box, (w, small) => {
    const L = small ? 94 : 130, R0 = 56, rh = 24, H = rows.length * rh + 44, s = el("svg", { viewBox: `0 0 ${w} ${H}` }, box), x = v => L + (v - 1) / 5 * (w - L - R0 - 10);
    [1, 2, 3, 4, 5, 6].forEach(v => { el("line", { x1: x(v), x2: x(v), y1: 18, y2: H - 22, stroke: css("--rule") }, s); lbl(s, x(v), H - 6, v + " m/s", "lab s m", "middle"); });
    lbl(s, w, 12, "less windy", "lab s m", "end");
    rows.forEach((r, i) => { const y = 24 + i * rh + rh / 2;
      lbl(s, L - 8, y + 4, small && r[0].length > 12 ? r[0].slice(0, 11) + "." : r[0], "lab", "end");
      el("line", { x1: x(r[2]), x2: x(r[3]), y1: y, y2: y, stroke: r[3] >= r[2] ? css("--coral") : css("--muted"), "stroke-width": 3 }, s);
      el("circle", { cx: x(r[2]), cy: y, r: 5, fill: css("--muted") }, s);
      const c = el("circle", { cx: x(r[3]), cy: y, r: 6, fill: css("--coral"), stroke: css("--card"), "stroke-width": 1.5 }, s);
      lbl(s, w, y + 4, r[4] + "%", "lab b", "end");
      hover(c, `<b>${esc(r[0])}</b><br>Land mean ${f1(r[2])} m/s; farms ${f1(r[3])} m/s<br>${r[6]} listed farms on land, ${fmt(r[5])} MW${r[7] ? `; ${fmt(r[7])} MW at sea` : ""}<br>The average farm is windier than ${r[4]}% of the country's land`);
    });
  });
})();

/* UK counties */
(() => {
  const box = document.getElementById("ukChart"); if (!box) return;
  const all = PD.ukc, rows = all.slice(0, 10).concat([null]).concat(all.slice(-10));
  resp(box, (w, small) => {
    const L = small ? 132 : 180, rh = 20, H = rows.length * rh + 30, s = el("svg", { viewBox: `0 0 ${w} ${H}` }, box), x = v => L + v / 8 * (w - L - 40);
    [0, 2, 4, 6, 8].forEach(v => { el("line", { x1: x(v), x2: x(v), y1: 6, y2: H - 22, stroke: css("--rule") }, s); lbl(s, x(v), H - 6, v, "lab s m", "middle"); });
    rows.forEach((r, i) => { const y = 8 + i * rh; if (!r) { lbl(s, L - 8, y + 13, "...", "lab m", "end"); return; }
      lbl(s, L - 8, y + 13, small && r[0].length > 18 ? r[0].slice(0, 17) + "." : r[0], "lab", "end");
      const b = el("rect", { x: x(0), y: y + 3, width: x(r[2]) - x(0), height: rh - 6, fill: rgb(windRGB(r[2])), stroke: css("--border") }, s);
      lbl(s, x(r[2]) + 4, y + 13, f1(r[2]), "lab s"); hover(b, `<b>${esc(r[0])}</b>, ${esc(r[1])}<br>${f1(r[2])} m/s mean wind at 10 m`); });
  });
})();
