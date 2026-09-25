---
title: "5G already has layers. It just can't change their policies"
description: "Read as layers, the 5G user plane already has the shape 6G-RUPA builds on. Two things hold it back: a protocol split at the base station, and data transfer policies fixed by the standards."
date: 2026-09-25T10:30:00+02:00
categories:
    - "Article"
tags:
    - "6G-RUPA"
    - "5G"
    - "IPC model"
    - "User plane"
    - "EFCP"
---

A while ago I wrote about [network slicing from the UPF's point of view](/posts/understanding-network-slicing/) and slipped in a diagram that drew the 5G user plane as a stack of layers. That diagram deserves a post of its own, because once you read 5G that way, 6G-RUPA stops looking like a new architecture. It looks like the same one with two restrictions lifted.

## Reading 5G as layers

The view comes from the interprocess communication (IPC) model that RINA is built on. Networking, in that model, is processes talking to each other, and a layer is a set of processes that move data for whoever sits above them over a given scope. Every layer does the same kind of job; what changes from one to the next is how far it reaches and which policies it runs.

Apply that to the path between a phone and the network it's trying to reach, and 5G turns out to have an N Layer on top of two N−1 Layers:

| Layer | Scope | In 5G | In 6G-RUPA |
| --- | --- | --- | --- |
| N Layer | UE ↔ UPF | SDAP/PDCP + GTP-U | EFCP |
| N−1 Layer (radio) | UE ↔ gNB | Data radio bearers | Data radio bearers |
| N−1 Layer (core) | gNB ↔ UPF | QoS flows | QoS flows |

The N Layer carries the user's traffic end to end. The N−1 Layers carry it hop by hop underneath, over the air between the phone and the base station (gNB), and across the transport network between the gNB and the UPF.

{{< figure src="images/5g-user-plane-layers.png" alt="Diagram of the 5G user plane as layers across the UE, gNB, UPF and a host in the data network. The N Layer spans UE to UPF but contains two protocols, SDAP on the radio side and GTP-U in the core. Below it sit the N−1 Layers for radio and core." caption="The 5G user plane drawn as layers. The N Layer is split between SDAP on the radio side and GTP-U in the core, and the two halves meet at the gNB." >}}

## A translator in the middle

Look closely at that N Layer and it isn't one protocol. On the radio side it's SDAP and PDCP over the data radio bearer; in the core it's GTP-U over UDP and IP. The halves meet at the gNB, which has to lift every packet out of one and put it into the other, stripping the SDAP header and adding a GTP-U one on the way up, and the reverse on the way down.

A router in the middle of a layer should read an address and pick an output. The gNB works as a translator between two protocols instead, and the cost shows up further along the path: since the core half is a tunnel with an identifier per session, the UPF at the far end turns into an anchor that keeps state for every session it serves. That's the growth problem from the [previous article](/posts/5g-core-grows-with-its-users/), and it starts here.

## Policies you can't swap

The second restriction is quieter. Every data transfer protocol makes choices: whether to retransmit what gets lost, whether to deliver in order, how fast to let a sender go, whether to set up something like a virtual circuit at all. In 5G those choices come with the protocols. GTP-U, for example, is always a per-session tunnel, whether the traffic inside needs one or not, and you get the options the specifications expose and nothing else.

6G-RUPA puts error control, flow control and retransmission into one protocol, the Error and Flow Control Protocol (EFCP), and leaves its behaviour to policies you choose per flow. The preprint's example is a good one: a fleet of IoT sensors can run a light best-effort policy, roughly what UDP gives you, while an XR application on the same network asks for strict ordering and retransmission, closer to TCP. The machinery doesn't change between the two; the policy does.

## What 6G-RUPA keeps

6G-RUPA swaps the N Layer's two protocols for EFCP, running from the phone to the Generalized UPF (GUPF). With one protocol end to end, the gNB goes back to being an ordinary router inside that layer, forwarding on addresses instead of rewriting headers.

Below the N Layer, nothing changes. Data radio bearers still carry traffic over the air and QoS flows still carry it through the core; in 6G-RUPA they're simply the N−1 Layers that EFCP runs over. The control plane stays as well: its functions (SMF, AMF and PCF) do the jobs they do today, and operators replace only the user plane.

{{< figure src="images/6g-rupa-user-plane-layers.png" alt="The same layered diagram for 6G-RUPA. The N Layer spans UE to GUPF as a single layer, with the same N−1 Layers for radio and core underneath." caption="The same path with 6G-RUPA. EFCP runs across the whole N Layer and the GUPF takes the UPF's place; the N−1 Layers are the ones 5G already has." >}}

Keeping the radio side is deliberate. It means 6G-RUPA can go into existing 5G networks next to what's there, instead of asking operators to rip anything out first.

## Room for more layers

5G has one N Layer, and that's where it stops. Because every 6G-RUPA layer is built from the same machinery, you can stack more on top when a problem calls for a different scope: an N+1 or an N+2, each with its own addresses and its own policies. The preprint names mobility and roaming between operators as the places where that should pay off and leaves them for later work, which is where this post leaves them too.

When I first drew this out, last October, the conclusion caught me off guard: 6G-RUPA is a generalization of the 5G user plane. It keeps the layers that already work and turns the split N Layer into a single protocol whose policies you get to choose.

The layer mapping and the figures come from our preprint, [Beyond 5G Architectural Constraints](https://hdl.handle.net/2072/489603). The original proposal is in the [6G-RUPA position paper](https://doi.org/10.3390/computers13080186).
