# Tier 3 — Future conversions (needs a backend)

ConvertX currently ships Tier 1 and Tier 2: everything runs
client-side (WASM/JS in the browser), with no server and no uploads.
Tier 3 is the set of conversions that can't realistically be done that
way — each of these needs a real backend, which means giving up the
"100% private, nothing ever leaves your device" pitch for whichever of
these get built.

Not scheduled — revisit if there's actual user demand.

## What's in it

| From | To | Why it needs a server |
|---|---|---|
| Legacy `.doc`, `.xls`, `.ppt` (old binary Office formats) | modern formats (`.docx`, `.xlsx`, `.pptx`) | Needs a LibreOffice/Aspose-style rendering engine — no practical WASM equivalent |
| — | RAR creation, 7Z creation | Licensing + native compression; no good WASM library for creating (not just reading) these |
| RAW camera formats (CR2, NEF, ARW, ...) | JPG | Needs `dcraw`/`libraw` |
| PDF | DOCX (high-fidelity: exact layout, tables, columns preserved) | Current client-side approach is text-only by design; true fidelity needs a real rendering engine like headless LibreOffice |
| Large / long video files | any format | ffmpeg.wasm is single-threaded in a browser tab — fine for short clips, but a real server-side ffmpeg is far faster and more reliable at scale |

## Why each one is actually hard

### Legacy Office binary formats (`.doc`, `.xls`, `.ppt`)

These predate the XML-based Office Open XML formats (`.docx`/`.xlsx`/`.pptx`)
that ConvertX already handles. The old formats use **OLE Compound File
Binary Format** — a proprietary, deeply nested binary container
(basically a mini filesystem-within-a-file) that Microsoft never fully
open-documented until much later, and even then it's notoriously
intricate. There's no lightweight WASM library for this because
there's no *simple* underlying spec to reimplement — it took Microsoft
and the LibreOffice team years of reverse-engineering to get
compatibility right. Apache POI (Java) has partial support (`HSSF` for
`.xls` is decent, `HWPF`/`HSLF` for `.doc`/`.ppt` are shakier). The
practical real-world solution — what services like CloudConvert or
Zamzar actually do — is running **LibreOffice headless**
(`soffice --headless --convert-to docx legacy.doc`) on a server.
That's a ~500MB+ install, not something you ship to a browser tab.

### RAR / 7z creation

This one's not really a technical-difficulty problem, it's a
**licensing** one. You can freely *extract* RAR archives (the format
is documented enough for that), but the RAR *compressor* is proprietary
— owned by RARLAB, the WinRAR people. There is no free/open
implementation of RAR compression, only decompression. To create
`.rar` files you need their actual licensed `rar` binary running
somewhere — which rules out both client-side WASM and most
open-source server tooling.

7z is different: it's fully open (built on the LZMA SDK), so creating
`.7z` files isn't a legal problem — it's just that no one has published
a mature, widely-used WASM encoder for it the way `jszip` exists for
`.zip`. That one's arguably closer to "Tier 2.5" (doable client-side,
just needs someone to have built the WASM port) than a hard
architectural wall like RAR is.

### RAW camera formats (CR2, CR3, NEF, ARW...)

RAW files are near-unprocessed sensor data — each camera manufacturer
has its own format (Canon, Nikon, Sony all differ; Adobe's DNG is the
one open standard). Turning that into a viewable JPG requires
**demosaicing** (reconstructing full RGB per pixel from the sensor's
Bayer color filter pattern), white balance, color science/profiles,
and often lens corrections — a real image-processing pipeline, not a
format conversion. The standard tools are `dcraw` (old but
foundational, open source) and `libraw` (its actively maintained
fork). These are C libraries; people have compiled `dcraw` to WASM as
hobby projects, but RAW files run 20–60+ megapixels and the
demosaicing math is heavy — it'd be slow and memory-hungry in a
browser tab, and you'd inherit `dcraw`'s aging color science instead of
a modern pipeline. Realistically better as a server job with real
CPU/RAM to throw at it.

### High-fidelity PDF ↔ DOCX

This is genuinely one of the hardest problems in document tooling —
even paid commercial SDKs (Aspose, Syncfusion) don't get it perfect.
ConvertX's current approach deliberately simplifies: it extracts text
runs (bold/italic/font size) and reflows them, which is honest and
works well for reading/editing text, but it can't capture:

- Merged table cells and precise column grids
- Exact positioning of floating elements, headers/footers, footnotes
- Embedded fonts and complex vector graphics/shapes
- Form fields, tracked changes, comments

The only way to meaningfully close that gap is a real layout/rendering
engine — again, LibreOffice headless is the realistic open-source
option (its PDF import/export filters aren't perfect either, but
they're far more complete than a from-scratch text-extraction
approach).

### Large-scale video transcoding

This one's about hard resource ceilings rather than missing software.
In the browser, ffmpeg.wasm is:

- **Single-threaded** (the alternative needs COOP/COEP headers, which
  we specifically avoided to protect `@vercel/analytics` and other
  cross-origin scripts)
- **No GPU access** — no NVENC/QuickSync/hardware encoding, everything
  is CPU-bound WASM
- **Memory-constrained** — we already hit a real tab crash from the
  VP9 encoder during testing; a browser tab has maybe a few GB before
  things fall over

For a short clip this is fine (that's what shipped). For a
multi-minute 4K video, client-side WASM encoding could take many
minutes to hours and risk crashing outright, versus a server with real
cores and hardware encoding finishing in seconds. There's no clever
fix here — it's a fundamental ceiling of running a video codec inside
a browser sandbox.

## What building this would actually mean

- Standing up a server or serverless functions (uploads, processing, download)
- Hosting something like LibreOffice headless (or an equivalent engine)
- New security surface: file uploads, storage, cleanup, abuse/rate limiting
- Ongoing hosting cost, unlike the current setup which is just a static
  Next.js app
- Breaking the "no server, no upload" claim for whichever of these ship —
  worth deciding whether that's scoped to *only* these tools (private by
  default, server-processed only when the user picks one of these
  specific conversions) or a broader architecture change

## Recommendation

Hold off unless there's real demand for legacy Office formats or RAW
photos specifically — the current 10 tools (Tier 1 + Tier 2) already
cover the large majority of real-world conversion requests, and this
is a meaningfully bigger commitment than anything shipped so far.
