---
name: heritage-extraction
description: Prompt architecture for parsing oral transcripts into structured cultural metadata, regional dialect tags, and generational age context.
---

# Heritage Extraction Skill

This skill defines the extraction of cultural anthropologists' metadata from first-person oral stories.

## Extracted Schema & Rules

1. **Title:** Warm, poetic 4-7 word title reflecting emotional essence.
2. **Era & Year:** Decade classification (`1950s`, `1960s`, etc.) or specific year.
3. **Author Age Context:**
   - Input: Elder's current age.
   - Deduction: Calculate birth year (`2026 - Age`).
   - Derive age during memory: `Year - Birth Year`.
   - Format: *"You were 16 when this happened"*.
4. **Sensory Details:**
   - Categorize by `sight`, `smell`, `sound`, `taste`, `touch`.
5. **Cultural Traditions:**
   - Rituals, sacred festivals (Pongal, Diwali, Onam, Bihu), traditional games, songs, and heirloom recipes.
6. **Emotion Vector:**
   - Scores between 0.0 and 1.0 for: `Joy`, `Sadness`, `Nostalgia`, `Wonder`, `Pride`.
7. **Cross-Check Detection:**
   - Detect chronological or geographical collisions with existing family memories.
