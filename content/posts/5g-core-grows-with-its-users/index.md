---
title: "Why the 5G core needs more memory for every new user"
description: "A 5G UPF keeps tunnel and forwarding state for every session it serves, so its tables grow with the number of users. 6G-RUPA forwards on addresses that name base stations instead, and the table stops caring how many phones sit behind them."
date: 2026-09-25T10:00:00+02:00
categories:
    - "Article"
tags:
    - "6G-RUPA"
    - "5G"
    - "UPF"
    - "Scalability"
    - "Forwarding state"
---

Every time a phone opens a data session, the User Plane Function (UPF) that anchors it writes a small record into memory. One record costs almost nothing. A national operator has tens of millions of them, though, and the UPF has to find the right one for every packet it forwards.

That record is why the 5G user plane gets more expensive as it grows. It's also what 6G-RUPA gets rid of. Below I open the record up and put numbers on what changes when forwarding runs on addresses instead of tunnels, using figures from our preprint, [Beyond 5G Architectural Constraints](https://hdl.handle.net/2072/489603), and from PLMN-GraphSim, the simulator we built to test the model on real operator topologies.

## What a UPF remembers about your session

In 5G, user traffic travels inside GTP-U tunnels between the base station (gNB) and the UPF. When the Session Management Function (SMF) sets up a PDU session, it programs the UPF with a set of rules defined in 3GPP TS 29.244:

- Packet Detection Rules (PDRs) work out which session a packet belongs to.
- Forwarding Action Rules (FARs) decide what happens next: forward, drop or buffer, plus the GTP-U header to add when the packet heads back towards the gNB.
- QoS Enforcement Rules (QERs) cap bit rates and open or close the gate.
- Usage Reporting Rules (URRs) count bytes and time, mostly so someone can send a bill.

Open-source cores keep all of this in one object per session. In open5gs it's `ogs_pfcp_sess_t`, a struct that holds lists of PDRs, FARs, URRs and QERs, and every PDU session gets its own.

Next to the rules sit the tunnel identifiers. A PDU session has a Tunnel Endpoint Identifier (TEID) in each direction, and uplink packets reach the UPF carrying the TEID it has to look up.

## The part that won't shrink

QoS rules and usage counters aren't what separates 5G from 6G-RUPA. Both architectures need per-user state for billing and QoS enforcement, so the preprint leaves those out of the comparison and counts only the forwarding state.

What's left per session is small, a tunnel entry and a forwarding rule for each direction, but none of it merges. A TEID names one session at one tunnel endpoint, so ten thousand phones behind the same gNB need ten thousand pairs of entries, even though all of their traffic takes the same path. The UPF can't write "everything for gNB A goes this way" because the fields it matches on (the TEID going up, the phone's IP address coming down) identify a session, not a place in the network.

So the memory a UPF needs is roughly the number of sessions multiplied by the cost of two tunnel entries and two forwarding rules. Double the phones and you double the table. And that's with one session per phone; a device that opens a second session for redundancy doubles its own share again.

## What 6G-RUPA does instead

6G-RUPA replaces GTP-U and SDAP/PDCP with a single protocol, the Error and Flow Control Protocol (EFCP), which runs end to end between the phone and the UPF's counterpart, the Generalized UPF (GUPF). Its addresses name points of attachment rather than sessions, and they follow the topology, so every phone attached to gNB A gets an address under gNB A's prefix.

That one property changes the table completely, which is easiest to see with an example: suppose two base stations serve 20,000 phones between them. The 5G UPF needs something like this:

| Matches on | Action |
| --- | --- |
| Uplink TEID of UE 1's session | Remove the GTP-U header, send to the data network |
| IP address of UE 1 | Add a GTP-U header for UE 1's tunnel, send to gNB A |
| Uplink TEID of UE 2's session | Remove the GTP-U header, send to the data network |
| IP address of UE 2 | Add a GTP-U header for UE 2's tunnel, send to gNB A |
| … | 40,000 rows in total, one pair per phone |

The GUPF serving the same phones needs three rows (the addresses are illustrative):

| Matches on | Action |
| --- | --- |
| `1.1.0/24`, everything behind gNB A | Send to gNB A |
| `1.2.0/24`, everything behind gNB B | Send to gNB B |
| The data network gateway | Send it out to the data network |

A new gNB adds a row. Another hundred thousand phones behind gNBs the GUPF already knows add nothing, which is why the preprint describes the GUPF's forwarding state as growing with the topology it serves rather than with its users.

One caveat on scope: all of this is about the core. Base stations keep per-phone radio state in both designs, and the preprint doesn't count it.

## How much memory that is

To see the difference at operator scale, we built [PLMN-GraphSim](https://github.com/Fundacio-i2CAT/PLMN-GraphSim), a discrete-event simulator. It builds a network from real base-station locations in OpenCellID and national population data, attaches users, places UPFs the way an operator might, and adds up the state. We ran it on Movistar's network in Spain and on Verizon's in the USA.

For Movistar, the 5G forwarding state across the core comes to 1,395 MB, while 6G-RUPA needs 0.82 MB for the same topology: roughly 1,700 times less. Verizon's larger network gives 9,435 MB against 2.06 MB, about 4,600 times less.

{{< figure src="images/memory-vs-users-movistar-spain.png" alt="Line chart of forwarding-state memory against active sessions. The 5G line rises steadily to about 460 MB at 40 million sessions; the 6G-RUPA line stays at zero." caption="Forwarding-state memory in a centralized UPF of the simulated Movistar network in Spain, as the number of active sessions grows. From the preprint." >}}

I care more about the shape of that chart than about the exact figures, which depend on how many bytes each entry takes. The 5G line is straight because every session adds the same few entries; the 6G-RUPA line stays flat because it only moves when someone builds a base station.

## Why a few gigabytes are a problem

A server has plenty of RAM, so 9 GB might not sound alarming. Forwarding at line rate is another matter: the hardware that does it keeps its tables in small, fast on-chip memory, and you count that budget in megabytes. A table of a couple of megabytes fits there. One of several gigabytes has to live further away, in slower memory, and every lookup pays for the trip.

I want to be careful with that argument. PLMN-GraphSim counts state; it doesn't forward packets, so what it shows is which tables could fit in fast memory, not a measured speed-up.

There's a second effect that's easier to miss. The QoS and billing rules that stay per-user in both designs compete for the same fast memory, and in 5G they share it with per-session tunnels and forwarding rules. With 6G-RUPA the forwarding part stops growing, which leaves that room for QoS and billing, or lets an operator buy smaller, cheaper hardware.

## What stays the same

The 5G control plane stays: the SMF, the Access and Mobility Management Function (AMF) and the Policy Control Function (PCF) keep their jobs, and the GUPF takes the UPF's place. Radio bearers and QoS flows stay too. How that fits together is the subject of the next article, [5G already has layers. It just can't change their policies](/posts/5g-already-has-layers/).

The [preprint](https://hdl.handle.net/2072/489603) has the full model and the rest of the results. PLMN-GraphSim is [open source](https://github.com/Fundacio-i2CAT/PLMN-GraphSim) and its [input data](https://doi.org/10.34810/data3210) is public, and if you'd rather listen than read, I gave a [27-minute seminar](https://www.youtube.com/watch?v=19YaJ6ufPfw) on this at Boston University last fall.
