"""Build the two walkthrough configs (one operator, two operators) for the 6grupa.com
packet-walk shortcode: an SVG of the path (cells with ids, wires, the ping's path in
segments) plus the step data the page script renders."""
import html
import json
import sys

E = html.escape
RH, TOP, GAP = 44, 100, 16


class Walk:
    def __init__(self, cols, nrows):
        self.o, self.X = [], cols
        self.R = {r: TOP + (r - 1) * (RH + GAP) for r in range(1, nrows + 1)}
        self.n = nrows
        self.YL = self.R[nrows] + RH + 26

    def half(self, k, s, gap=8):
        a, b = self.X[k]["x"]
        m = (a + b) // 2
        return (a, m - gap // 2) if s == "L" else (m + gap // 2, b) if s == "R" else (a, b)

    def hc(self, k, s="F"):
        a, b = self.half(k, s)
        return (a + b) // 2

    def rc(self, r):
        return self.R[r] + RH // 2

    def text(self, x, y, s, cls, a="middle"):
        self.o.append('<text x="%d" y="%d" text-anchor="%s" class="%s">%s</text>' % (x, y, a, cls, E(s)))

    def band(self, r, x0, x1, k, label, r1=None, pad=18, gutter=True):
        y0 = self.R[r] - 4
        y1 = (self.R[r1] if r1 else self.R[r]) + RH + 4
        if gutter:
            lab = '<text x="8" y="%d" class="pw-bandlab">%s</text>' % ((y0 + y1) // 2 + 4, E(label))
        else:
            lab = '<text x="%d" y="%d" class="pw-bandlab">%s</text>' % (x0 - pad + 4, y0 - 3, E(label))
        self.o.insert(0, '<g class="pw-band pw-b-%s"><rect x="%d" y="%d" width="%d" height="%d" rx="8"/>%s</g>' % (
            k, x0 - pad, y0, x1 - x0 + 2 * pad, y1 - y0, lab))

    def cols(self):
        for i, (k, c) in enumerate(self.X.items()):
            a, b = c["x"]
            self.o.append('<g class="pw-col" data-stop="%d" tabindex="0" role="button" aria-label="Go to %s">' % (i, E(c["name"])))
            self.o.append('<rect x="%d" y="52" width="%d" height="%d" rx="12" class="pw-sys"/>' % (a - 10, b - a + 20, self.R[self.n] + RH + 12 - 52))
            self.text((a + b) // 2, 30, c["name"], "pw-name")
            self.text((a + b) // 2, 45, c["role"], "pw-role")
            self.o.append("</g>")

    def cell(self, cid, k, side, r0, r1, cls, t, sub=None, relay=False):
        x0, x1 = self.half(k, side)
        y0, y1 = self.R[r0], self.R[r1] + RH
        self.o.append('<rect data-cell="%s" x="%d" y="%d" width="%d" height="%d" rx="6" class="pw-k-%s%s"/>' % (
            cid, x0, y0, x1 - x0, y1 - y0, cls, " pw-relay" if relay else ""))
        cy = (y0 + y1) / 2 + (0 if sub else 4)
        self.text((x0 + x1) / 2, cy, t, "pw-lab")
        if sub:
            self.text((x0 + x1) / 2, cy + 14, sub, "pw-sub")

    def line(self, x0, x1, r, k):
        y = self.rc(r)
        self.o.append('<path d="M%d %dH%d" class="pw-l-%s"/>' % (x0, y, x1, k))

    def wire(self, x0, x1, lbl):
        self.o.append('<path d="M%d %dV%dH%dV%d" class="pw-wire"/>' % (x0, self.R[self.n] + RH, self.YL, x1, self.R[self.n] + RH))
        self.text((x0 + x1) // 2, self.YL + 18, lbl, "pw-iface")

    def path(self, segs):
        ends = []
        for k, pts in enumerate(segs):
            d = "M%d %d" % pts[0] + "".join("L%d %d" % p for p in pts[1:])
            self.o.append('<path data-seg="%d" d="%s" class="pw-seg"/>' % (k, d))
            ends.append(pts[-1])
        self.o.append('<circle class="pw-dot" r="7" cx="%d" cy="%d"/>' % segs[0][0])
        return ends

    def svg(self, title):
        W = max(c["x"][1] for c in self.X.values()) + 30
        H = self.YL + 34
        return "\n".join(['<svg viewBox="0 0 %d %d" role="img" class="pw-fig"><title>%s</title>' % (W, H, E(title))] + self.o + ["</svg>"])


def single():
    cols = {"ue": {"name": "UE", "role": "host", "x": (130, 250)}, "gnb": {"name": "gNB", "role": "router", "x": (300, 480)},
            "ig": {"name": "I-GUPF", "role": "router", "x": (530, 690)}, "ga": {"name": "GUPF", "role": "egress", "x": (740, 920)},
            "dn": {"name": "8.8.8.8", "role": "host", "x": (970, 1090)}}
    w = Walk(cols, 4)
    w.cols()
    w.cell("ue-app", "ue", "F", 1, 1, "app", "ping")
    w.cell("ue-pdu", "ue", "F", 2, 2, "pdu", "IP", "10.60.0.2")
    w.cell("ue-n", "ue", "F", 3, 3, "na", "Operator A", "1.1.21")
    w.cell("ue-m", "ue", "F", 4, 4, "m", "radio link")
    w.cell("gnb-n", "gnb", "F", 3, 3, "na", "Operator A relay", "1.1.0", relay=True)
    w.cell("gnb-mL", "gnb", "L", 4, 4, "m", "radio link")
    w.cell("gnb-mR", "gnb", "R", 4, 4, "m", "core link")
    w.cell("ig-n", "ig", "F", 3, 3, "na", "Operator A relay", "1.2.0", relay=True)
    w.cell("ig-mL", "ig", "L", 4, 4, "m", "core link")
    w.cell("ig-mR", "ig", "R", 4, 4, "m", "core link")
    w.cell("ga-pdu", "ga", "F", 2, 2, "pdu", "IP relay", "to the internet", relay=True)
    w.cell("ga-n", "ga", "L", 3, 3, "na", "Operator A", "1.0.1")
    w.cell("ga-mL", "ga", "L", 4, 4, "m", "core link")
    w.cell("ga-mR", "ga", "R", 3, 4, "m", "N6 link")
    w.cell("dn-app", "dn", "F", 1, 1, "app", "ping", "responder")
    w.cell("dn-pdu", "dn", "F", 2, 2, "pdu", "IP", "8.8.8.8")
    w.cell("dn-m", "dn", "F", 3, 4, "m", "link")
    X = lambda k, s="F": w.half(k, s)
    w.line(X("ue")[1], X("dn")[0], 1, "app")
    w.line(X("ue")[1], X("ga")[0], 2, "pdu"); w.line(X("ga")[1], X("dn")[0], 2, "pdu")
    w.line(X("ue")[1], X("gnb")[0], 3, "na"); w.line(X("gnb")[1], X("ig")[0], 3, "na"); w.line(X("ig")[1], X("ga", "L")[0], 3, "na")
    w.wire(w.hc("ue"), w.hc("gnb", "L"), "Uu")
    w.wire(w.hc("gnb", "R"), w.hc("ig", "L"), "N3")
    w.wire(w.hc("ig", "R"), w.hc("ga", "L"), "N9")
    w.wire(w.hc("ga", "R"), w.hc("dn"), "N6")
    for a, b, lbl in [(X("ue"), X("gnb", "L"), "radio link"), (X("gnb", "R"), X("ig", "L"), "core link"),
                      (X("ig", "R"), X("ga", "L"), "core link"), (X("ga", "R"), X("dn"), "N6 link")]:
        w.band(4, a[0], b[1], "m", "", pad=3, gutter=False)
    w.band(3, X("ue")[0], X("ga", "L")[1], "na", "Operator A layer")
    w.band(2, X("ue")[0], X("dn")[1], "pdu", "IP")
    w.band(1, X("ue")[0], X("dn")[1], "app", "application")
    Y = w.YL - 8
    segs = [
        [(w.hc("ue") - 30, w.rc(1)), (w.hc("ue") - 30, Y)],
        [(w.hc("ue") - 30, Y), (w.hc("gnb", "L"), Y), (w.hc("gnb", "L"), w.rc(3))],
        [(w.hc("gnb", "L"), w.rc(3)), (w.hc("gnb", "R"), w.rc(3)), (w.hc("gnb", "R"), Y), (w.hc("ig", "L"), Y), (w.hc("ig", "L"), w.rc(3))],
        [(w.hc("ig", "L"), w.rc(3)), (w.hc("ig", "R"), w.rc(3)), (w.hc("ig", "R"), Y), (w.hc("ga", "L") - 20, Y), (w.hc("ga", "L") - 20, w.rc(2))],
        [(w.hc("ga", "L") - 20, w.rc(2)), (w.hc("ga", "R"), w.rc(2)), (w.hc("ga", "R"), Y), (w.hc("dn") - 30, Y), (w.hc("dn") - 30, w.rc(1))],
    ]
    ends = w.path(segs)
    env = {
        "radio": {"k": "m", "name": "radio frame", "dst": "the gNB's cell"},
        "n3": {"k": "m", "name": "core frame (N3)", "dst": "I-GUPF"},
        "n9": {"k": "m", "name": "core frame (N9)", "dst": "GUPF"},
        "n6": {"k": "m", "name": "link frame (N6)", "dst": "the internet side"},
        "na": {"k": "na", "name": "Operator A layer", "dst": "1.0.1 (GUPF), from 1.1.21"},
        "pdu": {"k": "pdu", "name": "IPv4", "dst": "8.8.8.8, from 10.60.0.2"},
    }
    wires = {"uu": ["radio", "na", "pdu"], "n3": ["n3", "na", "pdu"], "n9": ["n9", "na", "pdu"], "n6": ["n6", "pdu"]}
    hops = {"uu": "Uu", "n3": "N3", "n9": "N9", "n6": "N6"}
    steps = [
        {"name": "UE", "role": "host: sends, relays nothing", "hop": None, "out": "uu", "lit": ["ue-app", "ue-pdu", "ue-n", "ue-m"],
         "stack": [["app", "ping", "wrap", "builds an ICMP Echo Request"], ["pdu", "IP", "wrap", "10.60.0.2 → 8.8.8.8"],
                   ["na", "Operator A layer (1.1.21)", "wrap", "→ 1.0.1, the GUPF that leads to the internet"], ["m", "radio link", "wrap", "frame to the gNB"]],
         "read": [], "words": "<p>The phone builds the packet from the top down. <code>ping</code> makes an Echo Request; IP addresses it from 10.60.0.2 to 8.8.8.8; the operator layer wraps that for the GUPF, 1.0.1, because the GUPF is where the operator hands traffic to the internet. The radio then sends the frame to the gNB.</p><p>The phone relays nothing: it's a host, so every layer in it is an end.</p>"},
        {"name": "gNB", "role": "router in the Operator A layer", "hop": "uu", "out": "n3", "lit": ["gnb-mL", "gnb-n"],
         "stack": [["na", "Operator A layer (1.1.0)", "relay", "reads 1.0.1: not me → next hop I-GUPF (1.2.0)"], ["m", "radio link | core link", "up", "the frame is for me, hand it up"]],
         "read": ["radio", "na"], "words": "<p>The radio frame is for the gNB, so it hands up what's inside. The operator layer envelope says 1.0.1 and the gNB is 1.1.0, so the operator layer relays it: next hop the I-GUPF, out on N3.</p><p>The IP envelope stays shut. A gNB has no business reading 8.8.8.8, and in this drawing it doesn't even have an IP layer for user traffic. <b>Relay here: the Operator A layer.</b></p>"},
        {"name": "I-GUPF", "role": "router in the Operator A layer", "hop": "n3", "out": "n9", "lit": ["ig-mL", "ig-n"],
         "stack": [["na", "Operator A layer (1.2.0)", "relay", "reads 1.0.1: not me → next hop the GUPF"], ["m", "core link | core link", "up", "the frame is for me, hand it up"]],
         "read": ["n3", "na"], "words": "<p>The I-GUPF does what the gNB did: the frame is for it, the operator layer envelope still says 1.0.1, and since that isn't 1.2.0 the packet goes on over N9. <b>Relay here: the Operator A layer.</b></p>"},
        {"name": "GUPF", "role": "egress to the internet", "hop": "n9", "out": "n6", "lit": ["ga-mL", "ga-n", "ga-pdu"],
         "stack": [["pdu", "IP", "relay", "reads 8.8.8.8: not me → out on N6"], ["na", "Operator A layer (1.0.1)", "up", "1.0.1: that's me, open it"], ["m", "core link", "up", "the frame is for me, hand it up"]],
         "read": ["n9", "na", "pdu"], "words": "<p>Here the packet climbs one level higher. The operator layer envelope says 1.0.1, which is this box, so the operator layer's flow ends here and it opens the envelope.</p><p>Inside is the phone's IP packet for 8.8.8.8. That isn't this box either, so IP relays it out on N6. <b>Relay here: IP.</b></p>"},
        {"name": "8.8.8.8", "role": "host: answers, relays nothing", "hop": "n6", "out": None, "lit": ["dn-m", "dn-pdu", "dn-app"],
         "stack": [["app", "ping responder", "up", "Echo Request in, Echo Reply out"], ["pdu", "IP (8.8.8.8)", "up", "that's me, open it"], ["m", "link", "up", "hand it up"]],
         "read": ["n6", "pdu"], "words": "<p>Every envelope is for 8.8.8.8, so each layer opens its own and hands up until ICMP answers. The reply goes back the same way, and on the phone you get <code>64 bytes from 8.8.8.8: icmp_seq=1</code>.</p><p>Look at the line in the figure: the ping went up to the operator layer in the gNB and in the I-GUPF, and up to IP in the GUPF. One layer in each box.</p>"},
    ]
    addr = [["IP", "pdu", ["10.60.0.2", "—", "—", "—", "8.8.8.8"]], ["Operator A layer", "na", ["1.1.21", "1.1.0", "1.2.0", "1.0.1", "—"]]]
    return {"svg": w.svg("One operator: the ping climbs to the operator layer in the gNB and the I-GUPF, and to IP in the GUPF"), "ends": ends,
            "env": env, "wires": wires, "hops": hops, "steps": steps, "addr": addr, "cols": [c["name"] for c in cols.values()],
            "data": "ICMP Echo Request · seq 1"}


def multi():
    cols = {"ue": {"name": "UE", "role": "host", "x": (130, 250)}, "gnb": {"name": "gNB", "role": "router", "x": (300, 480)},
            "ig": {"name": "I-GUPF", "role": "router", "x": (530, 690)}, "ga": {"name": "border GUPF A", "role": "border router", "x": (740, 920)},
            "gb": {"name": "border GUPF B", "role": "egress", "x": (970, 1150)}, "dn": {"name": "8.8.8.8", "role": "host", "x": (1200, 1320)}}
    w = Walk(cols, 5)
    w.cols()
    w.cell("ue-app", "ue", "F", 1, 1, "app", "ping")
    w.cell("ue-pdu", "ue", "F", 2, 2, "pdu", "IP", "10.60.0.2")
    w.cell("ue-f", "ue", "F", 3, 3, "f", "internetwork", "A.1.21")
    w.cell("ue-n", "ue", "F", 4, 4, "na", "Operator A", "1.1.21")
    w.cell("ue-m", "ue", "F", 5, 5, "m", "radio link")
    w.cell("gnb-n", "gnb", "F", 4, 4, "na", "Operator A relay", "1.1.0", relay=True)
    w.cell("gnb-mL", "gnb", "L", 5, 5, "m", "radio link")
    w.cell("gnb-mR", "gnb", "R", 5, 5, "m", "core link")
    w.cell("ig-n", "ig", "F", 4, 4, "na", "Operator A relay", "1.2.0", relay=True)
    w.cell("ig-mL", "ig", "L", 5, 5, "m", "core link")
    w.cell("ig-mR", "ig", "R", 5, 5, "m", "core link")
    w.cell("ga-f", "ga", "F", 3, 3, "f", "internetwork relay", "A.1", relay=True)
    w.cell("ga-n", "ga", "L", 4, 4, "na", "Operator A", "1.0.1")
    w.cell("ga-mL", "ga", "L", 5, 5, "m", "core link")
    w.cell("ga-mR", "ga", "R", 4, 5, "m", "link to B")
    w.cell("gb-pdu", "gb", "F", 2, 2, "pdu", "IP relay", "to the internet", relay=True)
    w.cell("gb-f", "gb", "F", 3, 3, "f", "internetwork", "B.1")
    w.cell("gb-mL", "gb", "L", 4, 5, "m", "link to A")
    w.cell("gb-n", "gb", "R", 4, 4, "nb", "Operator B")
    w.cell("gb-mR", "gb", "R", 5, 5, "m", "core link")
    w.cell("dn-app", "dn", "F", 1, 1, "app", "ping", "responder")
    w.cell("dn-pdu", "dn", "F", 2, 2, "pdu", "IP", "8.8.8.8")
    w.cell("dn-m", "dn", "F", 3, 5, "m", "link")
    X = lambda k, s="F": w.half(k, s)
    w.line(X("ue")[1], X("dn")[0], 1, "app")
    w.line(X("ue")[1], X("gb")[0], 2, "pdu"); w.line(X("gb")[1], X("dn")[0], 2, "pdu")
    w.line(X("ue")[1], X("ga")[0], 3, "f"); w.line(X("ga")[1], X("gb")[0], 3, "f")
    w.line(X("ue")[1], X("gnb")[0], 4, "na"); w.line(X("gnb")[1], X("ig")[0], 4, "na"); w.line(X("ig")[1], X("ga", "L")[0], 4, "na")
    w.wire(w.hc("ue"), w.hc("gnb", "L"), "Uu")
    w.wire(w.hc("gnb", "R"), w.hc("ig", "L"), "N3")
    w.wire(w.hc("ig", "R"), w.hc("ga", "L"), "N9")
    w.wire(w.hc("ga", "R"), w.hc("gb", "L"), "between operators")
    w.wire(w.hc("gb", "R"), w.hc("dn"), "N6")
    for a, b, lbl in [(X("ue"), X("gnb", "L"), "radio link"), (X("gnb", "R"), X("ig", "L"), "core link"),
                      (X("ig", "R"), X("ga", "L"), "core link"), (X("ga", "R"), X("gb", "L"), "link A–B"), (X("gb", "R"), X("dn"), "N6 link")]:
        w.band(5, a[0], b[1], "m", "", pad=3, gutter=False)
    w.band(4, X("gb", "R")[0], X("gb", "R")[1], "nb", "Operator B layer", gutter=False)
    w.band(4, X("ue")[0], X("ga", "L")[1], "na", "Operator A layer")
    w.band(3, X("ue")[0], X("gb")[1], "f", "internetwork layer")
    w.band(2, X("ue")[0], X("dn")[1], "pdu", "IP")
    w.band(1, X("ue")[0], X("dn")[1], "app", "application")
    Y = w.YL - 8
    segs = [
        [(w.hc("ue") - 30, w.rc(1)), (w.hc("ue") - 30, Y)],
        [(w.hc("ue") - 30, Y), (w.hc("gnb", "L"), Y), (w.hc("gnb", "L"), w.rc(4))],
        [(w.hc("gnb", "L"), w.rc(4)), (w.hc("gnb", "R"), w.rc(4)), (w.hc("gnb", "R"), Y), (w.hc("ig", "L"), Y), (w.hc("ig", "L"), w.rc(4))],
        [(w.hc("ig", "L"), w.rc(4)), (w.hc("ig", "R"), w.rc(4)), (w.hc("ig", "R"), Y), (w.hc("ga", "L") - 20, Y), (w.hc("ga", "L") - 20, w.rc(3))],
        [(w.hc("ga", "L") - 20, w.rc(3)), (w.hc("ga", "R"), w.rc(3)), (w.hc("ga", "R"), Y), (w.hc("gb", "L") - 20, Y), (w.hc("gb", "L") - 20, w.rc(2))],
        [(w.hc("gb", "L") - 20, w.rc(2)), (w.hc("gb", "R"), w.rc(2)), (w.hc("gb", "R"), Y), (w.hc("dn") - 30, Y), (w.hc("dn") - 30, w.rc(1))],
    ]
    ends = w.path(segs)
    env = {
        "radio": {"k": "m", "name": "radio frame", "dst": "the gNB's cell"},
        "n3": {"k": "m", "name": "core frame (N3)", "dst": "I-GUPF"},
        "n9": {"k": "m", "name": "core frame (N9)", "dst": "border GUPF A"},
        "ab": {"k": "m", "name": "link frame (A to B)", "dst": "border GUPF B"},
        "n6": {"k": "m", "name": "link frame (N6)", "dst": "the internet side"},
        "na": {"k": "na", "name": "Operator A layer", "dst": "1.0.1 (border GUPF A), from 1.1.21"},
        "f": {"k": "f", "name": "internetwork layer", "dst": "B.1 (border GUPF B), from A.1.21"},
        "pdu": {"k": "pdu", "name": "IPv4", "dst": "8.8.8.8, from 10.60.0.2"},
    }
    wires = {"uu": ["radio", "na", "f", "pdu"], "n3": ["n3", "na", "f", "pdu"], "n9": ["n9", "na", "f", "pdu"],
             "ab": ["ab", "f", "pdu"], "n6": ["n6", "pdu"]}
    hops = {"uu": "Uu", "n3": "N3", "n9": "N9", "ab": "the link between operators", "n6": "N6"}
    steps = [
        {"name": "UE", "role": "host: sends, relays nothing", "hop": None, "out": "uu", "lit": ["ue-app", "ue-pdu", "ue-f", "ue-n", "ue-m"],
         "stack": [["app", "ping", "wrap", "builds an ICMP Echo Request"], ["pdu", "IP", "wrap", "10.60.0.2 → 8.8.8.8"],
                   ["f", "internetwork layer (A.1.21)", "wrap", "→ B.1, where this session meets the internet"],
                   ["na", "Operator A layer (1.1.21)", "wrap", "→ 1.0.1, border GUPF A: the internetwork layer's next hop"], ["m", "radio link", "wrap", "frame to the gNB"]],
         "read": [], "words": "<p>One more envelope this time. The session leaves for the internet from operator B, so the IP packet rides an internetwork flow to B's border GUPF, B.1. To get there the internetwork layer's next hop is A's border GUPF, A.1, across operator A, which is why the operator layer envelope says 1.0.1.</p><p>The phone still relays nothing; it just has one more layer to wrap with.</p>"},
        {"name": "gNB", "role": "router in Operator A layer", "hop": "uu", "out": "n3", "lit": ["gnb-mL", "gnb-n"],
         "stack": [["na", "Operator A layer (1.1.0)", "relay", "reads 1.0.1: not me → next hop I-GUPF"], ["m", "radio link | core link", "up", "the frame is for me, hand it up"]],
         "read": ["radio", "na"], "words": "<p>The gNB does exactly what it did with one operator: it reads 1.0.1, sees that it isn't 1.1.0, and the operator layer sends the packet on to the I-GUPF.</p><p>The internetwork envelope with B.1 on it goes through unread, because the gNB has no internetwork process and doesn't need one. <b>Relay here: Operator A layer.</b></p>"},
        {"name": "I-GUPF", "role": "router in Operator A layer", "hop": "n3", "out": "n9", "lit": ["ig-mL", "ig-n"],
         "stack": [["na", "Operator A layer (1.2.0)", "relay", "reads 1.0.1: not me → next hop border GUPF A"], ["m", "core link | core link", "up", "the frame is for me, hand it up"]],
         "read": ["n3", "na"], "words": "<p>1.0.1 isn't 1.2.0 either, so the packet goes on over N9. Nothing inside operator A has read B.1 or 8.8.8.8 so far. <b>Relay here: Operator A layer.</b></p>"},
        {"name": "border GUPF A", "role": "border router of the internetwork layer", "hop": "n9", "out": "ab", "lit": ["ga-mL", "ga-n", "ga-f"],
         "stack": [["f", "internetwork layer (A.1)", "relay", "reads B.1: not me → next hop B.1, over the link to B"],
                   ["na", "Operator A layer (1.0.1) | link to B", "up", "1.0.1: that's me, open it"], ["m", "core link", "up", "the frame is for me, hand it up"]],
         "read": ["n9", "na", "f"], "words": "<p>This is the box that changed. The operator layer envelope says 1.0.1, which is this box, so operator A's layer ends here and opens. Inside, the internetwork envelope says B.1, and since this box is A.1 the internetwork layer relays it across the link to operator B.</p><p>On the way out there's no Operator A layer envelope any more: 1.1.21 and 1.0.1 only mean something inside operator A. <b>Relay here: the internetwork layer.</b></p>"},
        {"name": "border GUPF B", "role": "egress to the internet", "hop": "ab", "out": "n6", "lit": ["gb-mL", "gb-f", "gb-pdu"],
         "stack": [["pdu", "IP", "relay", "reads 8.8.8.8: not me → out on N6"], ["f", "internetwork layer (B.1)", "up", "B.1: that's me, open it"], ["m", "link to A", "up", "the frame is for me, hand it up"]],
         "read": ["ab", "f", "pdu"], "words": "<p>The internetwork envelope says B.1, which is this box, so the internetwork flow ends and opens. Inside is the phone's IP packet for 8.8.8.8, which IP relays out on N6, the same job the GUPF did with one operator. <b>Relay here: IP.</b></p>"},
        {"name": "8.8.8.8", "role": "host: answers, relays nothing", "hop": "n6", "out": None, "lit": ["dn-m", "dn-pdu", "dn-app"],
         "stack": [["app", "ping responder", "up", "Echo Request in, Echo Reply out"], ["pdu", "IP (8.8.8.8)", "up", "that's me, open it"], ["m", "link", "up", "hand it up"]],
         "read": ["n6", "pdu"], "words": "<p>The server answers and the reply comes back the same way, wrapped for A.1.21 by border GUPF B and for 1.1.21 by border GUPF A.</p><p>Compare the two lines. Inside operator A nothing changed, and the gNB and the I-GUPF still stop at the operator layer; the internetwork layer only shows up in the two boxes where the operators meet.</p>"},
    ]
    addr = [["IP", "pdu", ["10.60.0.2", "—", "—", "—", "—", "8.8.8.8"]], ["internetwork layer", "f", ["A.1.21", "—", "—", "A.1", "B.1", "—"]],
            ["Operator A layer", "na", ["1.1.21", "1.1.0", "1.2.0", "1.0.1", "—", "—"]]]
    return {"svg": w.svg("Two operators: the ping climbs to Operator A layer in the gNB and the I-GUPF, to the internetwork layer in border GUPF A, and to IP in border GUPF B"),
            "ends": ends, "env": env, "wires": wires, "hops": hops, "steps": steps, "addr": addr, "cols": [c["name"] for c in cols.values()],
            "data": "ICMP Echo Request · seq 1"}


if __name__ == "__main__":
    out = sys.argv[1]
    json.dump(single(), open(out + "/one-operator.json", "w"), ensure_ascii=False)
    json.dump(multi(), open(out + "/two-operators.json", "w"), ensure_ascii=False)
