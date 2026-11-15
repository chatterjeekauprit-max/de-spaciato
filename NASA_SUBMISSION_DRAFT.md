# NASA Space Apps 2026 submission draft

This is a factual draft based on the current repository and the official project submission guide. Replace the bracketed fields and complete the NASA data requirement before submission.

## Required team details

- Registered team name: Mavrix
- Local Event: Kolkata (confirm the event's submission time zone with the Local Lead)
- Selected 2026 challenge: Interplanetary Survival Guide: Martian Map
- Confirmed team members at the same Local Event: [NEEDED]

**Challenge mismatch to resolve:** NISAR-PULSE is an Earth SAR concept, while the registered team currently has the Mars map challenge selected. The supplied submission copy names “Dancing with the SARs,” which is a different challenge. Do not submit until the team confirms the intended challenge and the official team selection matches it.

**NASA submission status:** The signed-in profile dashboard showed 0 projects submitted. The Project tab has an editable saved draft, but that does not prove it was submitted for judging.

## Project name

NISAR-PULSE: A Plain-Language SAR Change Explorer

## High-level project summary

NISAR-PULSE is an interactive prototype that helps non-specialists explore how synthetic radar-style changes can be explained through a before/after map and a 3D scene. People can adjust an epoch comparison, inspect plain-language annotations, and optionally load a local real-valued two-dimensional NISAR HDF5 raster for a normalized visual preview. The included scenarios and metrics are synthetic demonstrations; they are not NISAR observations, measurements, hazard warnings, or validated scientific analysis.

## Project demo

- Required format: a video of 30 seconds or less, or a slide deck of no more than seven slides, in English.
- Public demo link: [NEEDED; link must work without sign-in]
- Include the team name, all team members, selected challenge, prototype, NASA data/resource used, and a concise user walkthrough.
- Do not include images, audio, or likenesses of people under 18.
- The supplied 10-second WhatsApp clip meets the duration limit, but it shows unsupported claims and UI from an older concept (including “rejection proof,” high-risk detection, and a 60-FPS guarantee). Do not use it as the submission demo until those visuals and claims are replaced with an accurate capture of the current prototype.

## Final project link

- Public final-project link: [NEEDED; local 127.0.0.1 links do not work for judges]
- Confirm it opens in a private browser without a login: [NEEDED]

## Detailed project description

The prototype provides four views: raw-style terrain, an explained change surface, a top-down plain-language map view, and a simulated phase view. Users may change a synthetic scenario and compare two epochs with a wipe control. The HDF5 reader can list and preview real-valued 2D arrays from a user-selected local file. Files stay in the browser. The reader does not calibrate, geolocate, reproject, unwrap phase, or validate a scientific result. Current bundled fixture files and default AOI values are synthetic. The Python scalar engine is separate from the static browser demo.

The intended benefit is to make SAR change-analysis concepts easier to understand and to provide a starting point for testing a user-provided raster workflow. The current version is an educational prototype, not an operational disaster-monitoring service.

Tools include JavaScript, Three.js, h5wasm, esbuild, HTML/CSS, and a Python standard-library demo engine. The local and static build paths are documented in README.md.

## NASA data and resources (required for Global Award eligibility)

**Not yet satisfied by the current repository.** No actual NASA/ISRO mission dataset is bundled or used in the default scenarios. The HDF5 parser fixtures are synthetic, and the app only supports a user to load a local file. Before submission, add and document the exact NASA dataset or NASA resource actually used, including its product name, acquisition date/area if applicable, source URL, and what the project does with it. Do not claim the synthetic fixtures or merely optional file support as NASA data use.

The existing NASA Project tab draft claims live NISAR and Sentinel-1 processing, phase unwrapping, 60-FPS guarantees, offline device-to-device sync, and other features that the current app does not implement. Its NASA-data statements are not supported by the files reviewed so far. Replace those claims with an accurate description before submission.

## Space Agency Partner data and other references

- NASA NISAR data user guide and product specifications: [add exact resources actually consulted/used]
- Three.js: https://threejs.org/
- h5wasm: https://github.com/usnistgov/h5wasm
- Other code, text, images, or datasets: [list every item actually used and its license/source]

## Use of Super Intelligence (SI)

AI-assisted tools were used to help author and refine code and documentation. No trained machine-learning model is included, and the default scenario metrics are generated by deterministic synthetic logic and a heuristic score. No model accuracy or scientific performance is claimed. Identify any AI-generated image, video, audio, code, or data used in the final materials and add the required visible image/video watermark or descriptive metadata where applicable. Confirm the final media contains no NASA branding generated or modified by SI tools.

## Final pre-submit checklist

- [ ] Fill in the registered team name, members, event/time zone, and exact selected challenge.
- [ ] Use at least one actual NASA data/resource and document it accurately.
- [ ] Create and publicly host the 30-second-or-less video or seven-slides-or-less deck.
- [ ] Publish the final project and test both links without authentication.
- [ ] Complete every required form field in English.
- [ ] Confirm all team members meet the same-Local-Event eligibility requirement.
- [ ] Agree to the terms and confirm original work only after the team verifies those statements.
- [ ] Select “Submit for Judging” before 11:59 p.m. in the Local Event time zone (Universal Event uses the Team Owner's local time).
- [ ] Verify the site's submission confirmation banner.
