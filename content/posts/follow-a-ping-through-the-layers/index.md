---
title: "Follow a ping through the layers"
description: "One ping, box by box, first inside one operator and then across two. In each box the packet climbs only as far as the first envelope that isn't addressed to it, and that's the one layer the box relays in."
date: 2026-10-09T21:00:00+02:00
wide: true
showTableOfContents: false
categories:
    - "Article"
tags:
    - "6G-RUPA"
    - "RINA"
    - "IPC model"
    - "Roaming"
---

The [previous article](/posts/5g-already-has-layers/) ended on stacking another layer on top of the operator's own for mobility and roaming between operators, and then left it there. Here I'll call them by what they cover: the operator's layer (the N Layer last time) and an internetwork layer shared by operators (the N+1). Before drawing what the internetwork layer does, I wanted to be sure what a single box does with a packet, because that's exactly where our own figures went wrong.

So here's one `ping 8.8.8.8`, followed box by box. Every layer puts its own envelope around the packet and writes its own destination on it, and a box opens envelopes from the outside in until it finds one addressed to someone else. That layer forwards the packet, and it's the only layer in that box that ever does. Press **Next box** or click any box in the figure.

## One operator

The ping passes through four of the operator's boxes before it leaves for 8.8.8.8: the phone itself, its base station (gNB), an intermediate GUPF, and the GUPF where the operator hands traffic to the internet. Below the IP that applications see sits the Operator A layer, the one that replaces GTP-U in 6G-RUPA, and below that the radio and core links.

{{< packet-walk src="one-operator.json" caption="One operator. The addresses are made up but shaped like real ones: 1.1.21 is host 21 under the gNB's region 1.1 of the Operator A layer." >}}

The gNB and the I-GUPF never read 8.8.8.8. They open the operator layer's envelope, see 1.0.1 and send the packet towards it, while the IP packet inside rides along shut. Only at the GUPF, where the operator layer's flow ends, does the packet climb up to IP. RINA's Reference Model states this as a rule, "if an IPCP in an (N)-DIF contains a Relaying Task, there will be no RTs in IPCPs of lower rank in the same processing system and no RTs in IPCPs in the same processing system of higher rank", and the walkthrough shows why it holds: the layers below the relay end in that box, and the layers above it never get opened there.

## Two operators

Now the session leaves for the internet from a second operator, B, while the phone stays a member of the Operator A layer. On top of the two operator layers there's an internetwork layer they share, with members only at the hosts and at the two border GUPFs where the operators meet.

{{< packet-walk src="two-operators.json" caption="Two operators. A.1.21 is the phone's address in the internetwork layer, under border GUPF A (A.1); B.1 is border GUPF B." >}}

Inside operator A nothing changed: the gNB and the I-GUPF still stop at the Operator A layer and never see the internetwork envelope. The internetwork layer only does work in border GUPF A, which relays it across to B, and it ends in border GUPF B, which hands the IP packet to the internet just like the GUPF did with one operator.

That split is what keeps moving cheap. A phone that moves between base stations of operator A changes its address in the Operator A layer (1.1.21 becomes something under another region), and the internetwork layer never hears about it. Only when it crosses to operator B does it join the Operator B layer and change its internetwork address, from A.1.21 to something under B.1. Each kind of move stays in the smallest layer that can see it.
