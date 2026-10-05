# Artwork, alignment and reversible expression patches

The PNG artwork, native avatar project and silent preview are [CC BY 4.0](../LICENSE-ARTWORK.md). The Python tools are separately [MIT-licensed](../LICENSE-CODE); the spoken voice examples are excluded from both grants.

`assets/maple-original-unchanged.png` is the unmodified original, SHA-256:

`bc25435e54e6202f7aadf2a8b00dcfe165070b55fbf3d0f910b03b51ebd6b789`

The four frames are 640 × 640 RGBA images. Their entire alpha channels equal the original's. Compared with the original:

- Idle: 0 changed pixels
- Speaking: 713 changed pixels
- Blink: 2,918 changed pixels
- Speaking + blink: 3,631 changed pixels

Every changed pixel is inside the corresponding explicit mouth/eye masks. The mouth and eye masks do not overlap. The combined state is the exact composition of those independent patches. Body, clothes, hair, pose and registration remain unchanged. Original partially transparent edge pixels are preserved.

`assets/references/` contains two AI-generated expression references used only as local sources inside the face masks. They are not production frames and should not be used as full-frame alternates: their wider artwork differs from the original.

`tools/create_expression_patches.py` resizes those references for sampling, compensates a small skin-color offset and feathers RGB edits inward within the masks. It always starts from the immutable original and retains its alpha. Rerun it to reproduce the four frames; use the original as the reversible neutral baseline. Generated review images and pixel reports go to `build/qa/`.
