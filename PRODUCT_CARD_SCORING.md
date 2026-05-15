# Product Card Scoring

Before publication, every product card must receive a score from 1 to 10.

## Criteria

1. Text sounds like Nouvel Amour Flowers: 0 to 2 points.
2. Emotion and use scenario are present: 0 to 2 points.
3. No template phrases: 0 to 2 points.
4. SEO fields are present: 0 to 1 point.
5. Substitution note is present: 0 to 1 point.
6. Flower composition is not invented: 0 to 1 point.
7. Text is ready to publish: 0 to 1 point.

## Publication Rules

If score is below 8, do not publish and rewrite automatically.

If banned phrases are present, do not publish.

If Aroma is mentioned, do not publish.

If substitution note is missing for a bouquet or floral composition, do not publish.

If a long dash is present, rewrite.

## Quality Status

Use:

- `approved` when score is at least 8 and no blocking issue is present.
- `rewrite_required` when score is below 8 or any blocking issue is present.
