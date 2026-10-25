# Methodology — Field Note #07

> **Status: AI-only preliminary.** Hand detections come from MediaPipe Hands. Review labels come from an AI visual review (multimodal model), not from people. No human verification has been performed. No number here is a certified hand-visibility rate.

## 1. Recordings
| ID | Device and mount | Image | Task | Frames |
|---|---|---|---|---:|
| stereo_rig_left | Head-mounted stereo + IMU rig, left camera, wide-angle lens | 1600×1200, 30 fps | Bench work (drill, screwdriver, heater) | 3,600 |
| phone_knife_prep | Body-worn Android phone, rear camera | 1920×1080, 30 fps | Peeling and cutting vegetables | 1,979 |
| phone_seasoning | Same phone setup and operator | 1920×1080, 30 fps | Pouring seasonings, stirring | 1,978 |

Device, mounting, task and session differ between the rig and the phone recordings; comparisons are observations, not controlled experiments.

## 2. Definitions (per hand, wearer's anatomical side)
* **F — fully in view:** wrist to fingertips inside the image; holding an object or partial occlusion by an object still counts as F.
* **C — cut by border:** part of the hand outside the image boundary.
* **N — not visible.**
* Both hands visible = neither hand N. Both hands fully in view = both F.
* Detector rates and review rates are always reported separately.

## 3. Detection
* MediaPipe Hands 0.10.14 (legacy solution, bundled models), static-image mode, max 2 hands, min detection confidence 0.5, input resized to 960 px width.
* Three passes per frame: full model; full model on the mirrored frame (coordinates mapped back); lite model.
* MediaPipe handedness assumes a mirrored image, so labels are swapped for egocentric video. When both hands are detected, the wearer-left hand lies left of the wearer-right hand in 99–100% of frames.
* Consensus: hand present if any pass detected it within ±2 frames.

## 4. Independent check (performed)
* 40 frames per recording drawn uniformly at random (NumPy seed 20261025).
* Reviewed by an AI visual review (multimodal model) on downscaled frames, blind to detector output, per hand F / C / N.
* Recall = detected / visible hands; Wilson 95% intervals.
* Only 3 reviewed hands were absent, so false-positive rates are not estimated.
* The ±2-frame window was chosen after inspecting this sample; its recall is optimistic until confirmed on new frames.

## 5. Human verification (designed, not performed)
| Stratum | stereo_rig_left | phone_knife_prep | phone_seasoning |
|---|---:|---:|---:|
| Random frames (seed 7) | 100 | 100 | 100 |
| Consensus reports fewer than two hands | 39 | 37 | 40 |

* 416 frames, shuffled, reviewers blind to stratum and detector output.
* Random stratum: unbiased visibility rate and recall; Wilson half-width about 4–6 points at 90–95% visibility.
* Suspect stratum: separates true out-of-view moments from detector misses; estimates precision of absence calls.
* Recommended: two reviewers on an overlapping subset to report inter-reviewer agreement.

## 6. Links to other notes
* Motion: `blur_px_pred` and `rotation_dps` come from Field Note #06 and are aligned frame by frame.
* Keysteps: phone frames are mapped to the human keystep annotation of Field Note #05 by frame time.

## 7. Limitations
* AI-only; small review sample; window tuned on the review sample; three recordings; occlusion folded into F; landmark accuracy not evaluated.
