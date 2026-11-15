# NISAR-PULSE Local Scenario Console

This is a click-to-run, offline-capable demonstration of SAR change-analysis
concepts. It contains an interactive Three.js terrain scene, a browser-side
synthetic scenario model, local HDF5 raster previews, a Python scalar calculation
engine, and a local-only HTTP launcher. The bundled scene and HDF5 reader work
without a CDN or network connection.

For a click-by-click presentation with inputs, expected outputs, and proof
limits for each feature, see [DEMO_GUIDE.md](DEMO_GUIDE.md).
For the NASA Space Apps submission fields, requirements, and remaining blockers,
see [NASA_SUBMISSION_DRAFT.md](NASA_SUBMISSION_DRAFT.md).

## Demo Inputs and Outputs

- Choose Sundarbans, Joshimath, Gangotri, or Sierra Nevada from **Area of
  interest**.
- Move **Epoch comparison** from 0% (all baseline) to 100% (all scenario).
- Move **Scenario intensity** from 10% to 100% to scale the synthetic change.
- Optionally load a T0 and/or T1 NISAR HDF5 granule. The local worker lists
  real-valued 2D numeric datasets (for example, GCOV layers) and samples them in
  row chunks into a display preview. Select the dataset, then load it into the
  corresponding map layer. Files stay in the browser and are not uploaded.
- Orbit the terrain with pointer drag and zoom with the wheel. **Raw-style**
  shows a synthetic intensity mesh until a local raster is loaded; click
  **Explain 3D** to show an annotated change view. **Map / explain** switches
  to a top-down synthetic view and explains the baseline, modeled change area,
  event marker, and epoch slider in plain language. **Phase / sim** shows
  generated bands. These views are not georeferenced imagery or a measured
  interferogram.
- Read the derived backscatter change, LOS displacement, coherence proxy, area
  scale, synthetic phase, and heuristic theta score in the output rail.
- Export a JSON demo packet. On localhost, Web Crypto adds a SHA-256 integrity
  checksum over the payload. This checksum is not a digital signature.
- Use **Simulate link drop** to queue A1/B1/C1 packets locally. The virtual field
  tablet, relay, and low-power node accept or skip packets according to their
  displayed byte capacities. **Simulate reconnect** replays the queue to those
  virtual devices; no satellite, P2P, or cloud endpoint is contacted.
- Scenario intensity at or above 76% triggers the high demo-stress banner. This
  is a threshold demonstration, not a geophysical risk assessment.

Default demonstration values are Sundarbans, 50% epoch wipe, and 68% scenario
intensity. They produce approximately -4.2 dB backscatter change, -2.1 cm LOS
displacement, 0.42 coherence proxy, 42.8 km² illustrative area, and a -1.100 rad
synthetic phase input at a 0.240 m wavelength. These are deterministic demo
values, not observations.

## Run

On Windows, double-click `start_nisar_pulse.bat`. It starts the Python standard-
library server on loopback and opens the app. Alternatively run:

```powershell
py -3 start_nisar_pulse.py
```

The Python engine can be run separately with `py -3 nisar_valrix_engine.py`.
The prebuilt Three.js and HDF5 worker assets are included, so Node is not needed
at runtime. The UI controller, 3D renderer, and HDF5 worker live in separate
source modules under `src/`; `npm.cmd run build` regenerates their local bundles
in `assets/` and stages the deployable site in `dist/`.

## Deploy to Vercel

Push the project to GitHub, import that repository into Vercel, and deploy from
the repository root. `vercel.json` selects Vercel's static **Other** framework,
runs `npm ci --include=dev` and `npm run build`, serves the generated `dist/`
directory, and routes `/` to the demo page. No Python runtime or external data
service is required for the hosted UI. The optional `/api/health` and
`/api/analysis` endpoints exist only in the local Python launcher and are not
part of the static Vercel deployment; the browser UI does not call them.

## Checks

```powershell
npm.cmd test
py -3 -m unittest discover -s tests -v
```

## Scope and Limitations

All AOI profiles, terrain, phase inputs, coherence, backscatter changes, areas,
and theta scores are synthetic. The phase value is generated from a scenario
displacement target and then passed through the scalar relation
`d_LOS = wavelength * (delta_phi - phi_iono) / (4*pi)`; no phase is unwrapped
and atmospheric phase is not estimated. The theta value is a heuristic, not a
Markov model. FPS displayed in the console is measured locally and may vary;
there is no 60 FPS guarantee.

HDF5 input supports only real-valued numeric 2D datasets. Complex/compound SLC
datasets are rejected; there is no phase extraction, product calibration,
geolocation, coordinate reprojection, or map-tile basemap. Each loaded raster
gets an independent percentile display stretch, so visual T0/T1 differences
are not calibrated measurements. `tests/fixtures/NISAR_GCOV_demo.h5` and
`tests/fixtures/NISAR_GCOV_demo_T1.h5` are tiny contrasting synthetic parser
fixtures, not NASA/ISRO mission data.

The browser only simulates offline queueing and reconnect behavior; it does not
implement actual P2P sync, cloud reconnection, emergency key exchange,
cryptographic signing, atmospheric correction, calibrated
polarimetric change detection, temporal differencing, validated speckle
filtering, segmentation, ROI scanning, or target tracking. The local API is not
called by the browser UI. No external winning-team code or data was provided
or integrated.
