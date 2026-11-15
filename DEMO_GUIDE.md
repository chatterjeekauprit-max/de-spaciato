# NISAR-PULSE v2.0 Demo Guide

## Start

1. Extract the final ZIP.
2. On Windows, double-click `start_nisar_pulse.bat`.
3. Wait for the browser to open. No internet connection or Node.js install is required at runtime.
4. Click **Reset demo inputs** before presenting.

The console is an offline-capable simulation. It does not claim that its synthetic terrain or metrics are NASA observations.

## Five-Feature Walkthrough

For each feature, present the **input**, perform the **action**, point to the
visible **output**, and capture the listed **evidence** (a screenshot or a
short screen recording). This proves the prototype's local demo path ran; it
does not validate scientific accuracy or real-world NISAR performance.

### 1. Micro-process pipeline

**Input:** Select an AOI. Use the included `tests/fixtures/NISAR_GCOV_demo.h5` as T0 and `tests/fixtures/NISAR_GCOV_demo_T1.h5` as T1; choose a supported 2D real-valued dataset for each.

**Action:** Click **Show T0 base layer** and **Show T1 layer**. Wait for preview progress, then try **MAP / EXPLAIN** for a top-down view with a plain-language key, or use **EXPLAIN 3D** and drag to orbit the scene.

**Output and evidence:** The file status reports the loaded preview, the granule indicator changes, and the 3D view shows the raster layer. Capture those statuses with the scene visible. The FPS readout is measured in the active browser tab.

**Proof limits:** Work is chunked in a background worker; this reduces UI blocking but cannot guarantee zero lag or 60 FPS on every device. The included HDF5 fixtures are not mission data. Complex SLC datasets are not supported.

### 2. A1/B1/C1 packet and offline edge simulation

**Input and action:** Click **Simulate link drop**, then **Build A1 / B1 / C1 packet**.

**Output and evidence:** The link status changes to `LINK DOWN / OFFLINE SIM`, queue count increments, packet size appears, and virtual device rows show `QUEUED` or `SKIP` based on demo capacity. Capture these states, then click **Simulate reconnect** and capture the queue clearing and `RECEIVED ... / SIM` status.

**Proof limits:** A1/B1/C1 values are demo data. Devices are virtual capacity examples; this does not send data to a satellite, another device, or a cloud service.

### 3. Phase / displacement demonstration

**Input and action:** Select an AOI, set **Scenario intensity** to 68%, set **Epoch comparison** to 50%, then click **PHASE / SIM**.

**Output and evidence:** The scene changes to generated phase bands; the output rail displays synthetic phase and LOS displacement, and the wipe visibly changes the T0/T1 comparison. Capture the selected mode, input values, scene and output rail together. The A1 packet also reflects the selected AOI and related demo metrics.

**Default example:** Sundarbans, 50% wipe, 68% intensity gives approximately -4.2 dB backscatter change, -2.1 cm LOS displacement, 0.42 coherence proxy, 42.8 km² illustrative area, and -1.100 rad synthetic phase.

**Proof limits:** No phase unwrapping, atmospheric correction, calibrated displacement retrieval, or cloud/smoke experiment is performed. SAR physics is not a guarantee of immunity from atmospheric phase error.

### 4. Local operation and reconnect simulation

**Input and action:** Load a local HDF5 layer, click **Simulate link drop**, build a packet, and click **Simulate reconnect**.

**Output and evidence:** The local raster remains visible while offline; reconnect clears the queue and updates compatible virtual-device statuses. Capture the offline state and the post-reconnect state. The status explicitly says `CLOUD NOT CONFIGURED`.

**Proof limits:** This demonstrates a local queue state transition only. There is no cloud endpoint, automatic cloud sync, satellite link, or P2P transport in the prototype.

### 5. Stress alert

**Input and action:** Move **Scenario intensity** to 75%, note the banner, then move it to 76%.

**Output and evidence:** At 75%, no high-stress banner appears; at 76%, the dashboard shows `HIGH DEMO STRESS / ≥76% / NOT A GEOPHYSICAL ASSESSMENT`. Capture both values and corresponding banner states. The separate theta heuristic notice is not the stress trigger.

**Proof limits:** The alert threshold is a presentation rule on synthetic intensity, not a validated geophysical hazard decision.

## Export

Click **Export demo JSON**. On localhost, the JSON includes a SHA-256 integrity checksum when Web Crypto is available. The checksum is not a digital signature. The export includes synthetic metrics and states that transport is only simulated.

## Feature / Claim Checklist

- Included: AOI selector, 0-100% wipe, 10-100% intensity, local HDF5 numeric 2D preview, background row sampling, top-down map/explain view, 3D raw-style/explained/phase views, plain-language map legend, A1/B1/C1 demo packet, virtual capacity checks, offline queue simulation, reconnect simulation, 76% stress banner, JSON export.
- Not implemented: complex SLC decoding, georeferencing, SAR calibration, real phase unwrapping, ATMOS-GOD correction, actual satellite or P2P sharing, cloud sync, Markov intent model, validated risk alerts, and universal 60 FPS.
