# Design of an Ultra-Low-Power 8-Bit Linear-Feedback Shift Register (LFSR) and BIST Architecture Using True Single-Phase-Clock (TSPC) Flip-Flops in 90nm CMOS

[![Process Node](https://img.shields.io/badge/Process-gpdk090%20(90nm%20CMOS)-blue.svg)](#)
[![EDA Tool](https://img.shields.io/badge/EDA%20Tool-Cadence%20Virtuoso%20IC6.1.5-orange.svg)](#)
[![Simulator](https://img.shields.io/badge/Simulator-Cadence%20Spectre-red.svg)](#)
[![Verification](https://img.shields.io/badge/Physical%20Verification-Assura%20%2F%20Diva%20(DRC%20%26%20LVS)-success.svg)](#)

> **Course Project:** VLSI Integrated Circuit Design  
> **Topic Code:** 3A — Design for Testability (DFT) & High-Speed Sequential Circuits  
> **Reference Textbook:** N. H. E. Weste and D. M. Harris, *CMOS VLSI Design: A Circuits and Systems Perspective*, 4th ed.

---

## Abstract

As modern System-on-Chip (SoC) designs integrate hundreds of millions of transistors on a single silicon die, relying solely on external Automatic Test Equipment (ATE) introduces prohibitive testing costs and I/O bandwidth bottlenecks. **Built-In Self-Test (BIST)** mitigates these challenges by embedding a **Pseudo-Random Pattern Generator (PRPG)**—typically realized via a **Linear-Feedback Shift Register (LFSR)**—and a **Multiple-Input Signature Register (MISR)** directly onto the chip. However, because BIST registers operate continuously at an activity factor of $\alpha_{clk} = 1$ during test mode, conventional LFSR architectures employing Transmission-Gate Master-Slave (TG-MS) D Flip-Flops suffer from excessive dynamic clock power dissipation, large silicon area overhead (20–24 transistors per stage), and high susceptibility to clock skew between dual-phase clocks (`CLK` and `CLKB`). 

This project presents the transistor-level design, physical layout, and PVT verification of an **8-bit TSPC-based LFSR and Built-In Logic Block Observer (BILBO) BIST system** in a **90nm CMOS process (`gpdk090`, $V_{DD} = 1.2\text{ V}$)**. By replacing conventional dual-phase TG-MS flip-flops with **True Single-Phase-Clock (TSPC) dynamic flip-flops** (9–12 transistors per stage) and integrating **Transmission-Gate (TG) XOR** feedback networks, the proposed architecture eliminates the inverted clock distribution network, reduces flip-flop transistor count by **$\ge 45\%$**, lowers dynamic clock power by **35–50%**, and achieves gigahertz-regime maximum operating frequencies ($f_{max} > 1.2\text{ GHz}$).

---

## 1. Introduction & Problem Statement

In contemporary semiconductor manufacturing, Design for Testability (DFT) is mandatory to ensure high fault coverage and manufacturing yield. A standard BIST architecture requires:
1. **Test Pattern Generation:** An $N$-bit maximal-length LFSR generating $2^N - 1$ pseudo-random test vectors to stimulate the **Circuit Under Test (CUT)**.
2. **Response Compaction:** A signature analyzer (MISR) compacting the output responses of the CUT into a deterministic signature compared against a golden reference.

### Limitations of Conventional Architectures
When implemented at the transistor level using static CMOS Master-Slave D Flip-Flops:
* **Dual-Phase Clock Routing & Skew:** Requires both true (`CLK`) and complementary (`CLKB`) clock signals, doubling clock routing tracks and introducing phase-overlap race conditions.
* **Excessive Test Power:** Continuous switching during BIST mode elevates dynamic power ($P_{dynamic} = \alpha C V_{DD}^2 f$) well beyond normal functional operation, risking IR drop and thermal runaway during wafer-level testing.
* **Area Overhead:** A conventional resettable TG-MS DFF requires 22–24 MOSFETs, resulting in significant silicon area penalty when scaled across wide scan chains and BILBO registers.

### Key Contributions of This Work
* **Single-Phase Clocking (TSPC):** Implementation of a seed-initializable TSPC D Flip-Flop utilizing a single non-inverted clock phase (`CLK`), completely eliminating local clock inverters and clock-skew sensitivity.
* **Complete Feedback Shift Register (CFSR) & TG-XOR:** Optimization of the linear feedback path using 6T/8T Transmission-Gate XOR gates alongside all-zero state prevention logic.
* **Multi-Mode 8-Bit BILBO Integration:** Full transistor-level realization of a 4-mode reconfigurable BILBO register validating end-to-end stuck-at fault detection on a 4-bit Ripple Carry Adder (CUT).

---

## 2. System Architecture & Theoretical Foundation

### 2.1. Maximal-Length 8-Bit LFSR Mathematical Model
The 8-bit PRNG is constructed around a primitive characteristic polynomial over Galois Field $GF(2)$ to guarantee a maximal sequence length of $2^8 - 1 = 255$ distinct non-zero pseudo-random states:

$$P(x) = 1 + x^1 + x^6 + x^7 + x^8$$

The linear feedback input $D_0$ is derived from the tapped outputs $Q_0, Q_5, Q_6,$ and $Q_7$:

$$D_0 = Q_0 \oplus Q_5 \oplus Q_6 \oplus Q_7$$

### 2.2. Top-Level BIST / BILBO Block Diagram

```text
                       Control Mode Select: C[1:0]
                                    |
                                    v
+-----------------------------------------------------------------------+
|                8-BIT TSPC-BILBO PRPG (LFSR Mode: C = 01)              |
|  [TSPC FF0] -> [TSPC FF1] -> ... -> [TSPC FF5] -> [TSPC FF6] -> [FF7] |
|      ^                                  |             |           |   |
|      +---------- [TG-XOR Feedback Tree] <-------------+-----------+   |
+-----------------------------------------------------------------------+
                                    |
                     8-Bit Pseudo-Random Test Vectors
                                    |
                                    v
+-----------------------------------------------------------------------+
|                    CIRCUIT UNDER TEST (CUT)                           |
|       4-Bit 28T CMOS Mirror Ripple-Carry Adder (with Fault Switches)  |
|             (Internal Nodes Equipped with SA0 / SA1 Injection)        |
+-----------------------------------------------------------------------+
                                    |
                        5-Bit Output Response Bus
                                    |
                                    v
+-----------------------------------------------------------------------+
|                8-BIT TSPC-BILBO MISR (Signature Compactor)            |
|        Compresses CUT Responses over N Clock Cycles -> Signature      |
+-----------------------------------------------------------------------+
                                    |
                                    v
                     [Golden Signature Comparator] ---> PASS / FAIL
