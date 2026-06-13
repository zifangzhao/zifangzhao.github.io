# Xiaohongshu Science Communication Kits

This folder is a first-pass production workspace for short, accessible posts about Zifang Zhao's neural-interface and bioelectronics papers.

Each paper has its own folder with:

- a 4-5 page Xiaohongshu carousel plan,
- a 60-90 second dubbed video script,
- a figure-story map for selecting the main figures,
- a short caption and hashtag set,
- an asset checklist for figure exports, annotations, and voiceover.
- `PUBLISH.md` with the final post title, caption, hashtags, upload order, and pre-flight checks,
- `extracted_figures/` with parsed figure candidates from the source PDF,
- `jpg/` with Chinese 1080 x 1440 upload-ready carousel images,
- `video/short_video.mp4` with a local 30-60 second still-image preview video,
- `ai_video/README.md` with Seedance/GPT-style story-video prompts and shot lists.

Recommended workflow:

1. Open each paper folder's `PUBLISH.md`.
2. Use `jpg/01.jpg` to `jpg/05.jpg` as the publication-ready Xiaohongshu carousel draft.
3. Review `extracted_figures/contact_sheet.jpg` only if a page needs a better figure choice.
4. For AI-generated storytelling video, upload the selected figure panels plus the prompt in `ai_video/README.md` to Seedance / GPT video / Sora-like tools.
5. Record the video voiceover from the draft script, then revise for your own speaking style.
6. Avoid claiming clinical readiness unless the paper directly demonstrates it.

## Regeneration Scripts

Run from the repository root:

```powershell
& 'C:\Users\aeria\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' Content\Xiaohongshu\tools\extract_pdf_figures.py
& 'C:\Users\aeria\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' Content\Xiaohongshu\tools\generate_media.py
& 'C:\Users\aeria\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' Content\Xiaohongshu\tools\generate_ai_video_briefs.py
```

## Paper Folders

| Folder | Source paper |
| --- | --- |
| `2021-pnas-responsive-neuroelectronics` | Responsive manipulation of neural circuit pathology by fully implantable, front-end multiplexed embedded neuroelectronics |
| `2022-sciadv-ionic-communication` | Ionic communication for implantable bioelectronics |
| `2022-advanced-science-single-neuron-interface` | Translational organic neural interface devices at single neuron resolution |
| `2023-nature-materials-vigt-bioelectronics` | Integrated internal ion-gated organic electrochemical transistors for stand-alone conformable bioelectronics |
| `2024-advanced-science-aci-epidermal-emg` | Formation of anisotropic conducting interlayer for high-resolution epidermal electromyography |
| `2026-nature-sensors-event-based-neurostimulation` | High-frequency, low-energy organic event-based sensors for closed-loop neurostimulation |
| `2026-wild-datalogger-manuscript` | A wireless modular platform for neuro-behavioral recording and closed-loop manipulation in small animals |

## Common Post Positioning

The recurring message across these posts should be:

> Neural interfaces are not only "recording tools"; they are becoming soft, low-power, closed-loop systems that can sense, compute, communicate, and intervene inside real biological environments.

Use the Chinese phrase "神经接口" consistently, and explain it as "把电子系统和神经活动连接起来的工具" for general audiences.
