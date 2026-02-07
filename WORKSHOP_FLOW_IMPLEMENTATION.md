# TerraRisk Workshop Flow - Frontend Implementation

## Overview

Complete implementation of a 4-phase workshop flow for the TerraRisk platform. Participants rank 10 municipalities, explore data, revise their ranking with new information, and compare their decisions with data-driven analysis.

## Implementation Date
February 5, 2026

## Files Created

### 1. Workshop Components (`src/components/workshop/`)

#### `WorkshopStepper.tsx`
Horizontal stepper showing the 4 phases:
- Phase 1: Initial Prioritization (ranking)
- Phase 2: Data Exploration (explore)
- Phase 3: Revise & Select Actions (revised)
- Phase 4: Results (results)

Features:
- Visual indicators: completed (green checkmark), active (purple), upcoming (gray)
- Click to navigate to completed phases
- Responsive layout with connecting lines
- i18n support for all text

#### `MunicipalityRanking.tsx`
Dual-mode ranking component for Phase 1 and Phase 3:
- Left side: Grid of 10 municipality cards with quadrant badges
- Right side: Priority list (1-10) with reorder controls
- Click-to-rank interface (simple, no drag-and-drop)
- Up/down arrows to reorder, X to remove
- Phase 'revised' shows additional data from purchased layers
- "Keep Initial Ranking" button in revised mode
- Submit button enabled when all 10 are ranked

Municipality cards show:
- Name and quadrant badge (Q1/Q2/Q3/Q4 with colors)
- Description
- Risk summary by category (in revised mode if layers purchased)
- Position number overlay when ranked

#### `ActionsSelector.tsx`
PEARC priority actions selection for Phase 3:
- Grid of action cards with checkboxes
- Each action shows:
  - Name (i18n translated)
  - Category badge (governance/biodiversity/climate/health/social)
  - Number of links to risk dimensions
  - Evidence strength (3-dot indicator)
  - Linked dimensions as small badges
- Bottom summary: "X actions selected"
- Submit button

#### `RankingComparison.tsx`
Results visualization for Phase 4:
- Top section: Correlation statistics
  - Spearman correlation (percentage with color coding)
  - Kendall tau
  - Agreement level (High/Moderate/Low)
- Middle section: Side-by-side rankings
  - User ranking vs Platform ranking
  - Position differences with color-coded arrows
- Bottom section: Actions comparison
  - User actions vs Recommended actions
  - Overlap percentage
  - Highlighted matches
- "Back to Exploration" button

### 2. Updated Files

#### `src/lib/types.ts`
Added workshop flow types:
- `WorkshopPhase`: 'ranking' | 'explore' | 'revised' | 'results'
- `WorkshopMunicipality`: Extended municipality with risk summary
- `RankingEntry`: { code, position }
- `PEARCAction`: Action definition with links and evidence
- `RankingComparison`: Complete comparison results
- `QUADRANT_CONFIG`: Q1/Q2/Q3/Q4 configuration
- `PHASE_CONFIG`: Phase metadata

#### `src/lib/store.ts`
Added workshop state management:
- `workshopPhase`: Current phase
- `workshopMunicipalities`: The 10 municipalities for ranking
- `initialRanking`: Phase 1 ranking
- `revisedRanking`: Phase 3 ranking
- `pearcActions`: Available PEARC actions
- `selectedActions`: User-selected actions
- `comparison`: Results comparison data
- Setters and toggles for all state
- Persistence for: workshopPhase, initialRanking, revisedRanking, selectedActions

#### `src/app/workshop/page.tsx`
Complete rewrite with phase-based routing:
- Phase 1: `<MunicipalityRanking phase="initial" />`
- Phase 2: Existing map + sidebar (no changes)
- Phase 3: Split view - MunicipalityRanking (left) + ActionsSelector (right)
- Phase 4: `<RankingComparison />`
- Transition screen after Phase 1 completion
- API handlers for saving rankings and submitting workshop
- Footer with "Continue to..." buttons between phases

#### i18n Messages (`messages/en.json`, `messages/es.json`, `messages/pt.json`)
Added `workshopFlow` section with:
- Phase titles and descriptions
- UI labels (ranked, yourPriorityList, submitRanking, etc.)
- Action comparison labels
- Button labels

Added `actionNames` section with 15 PEARC actions:
- reforestation
- urban_drainage
- vector_surveillance
- water_management
- protected_areas
- climate_agriculture
- community_health
- green_infrastructure
- environmental_monitoring
- land_use_zoning
- social_protection
- emergency_response
- biodiversity_corridors
- pollution_control
- climate_education

Added `actionDescriptions` with detailed descriptions for each action.

## API Endpoints Required (Backend Implementation Pending)

### GET `/api/workshop/municipalities`
Returns 10 municipalities for ranking with basic info:
```typescript
{
  code: string;
  name: string;
  quadrant: string; // Q1/Q2/Q3/Q4
  description: string;
  riskSummary: {
    governance: number;
    biodiversity: number;
    climate: number;
    health: number;
    social: number;
  };
}[]
```

### GET `/api/workshop/actions`
Returns PEARC priority actions:
```typescript
{
  id: string;
  category: string; // governance/biodiversity/climate/health/social
  links: Record<string, number>; // dimension -> strength
  totalLinks: number;
  avgEvidence: number; // 0-1
}[]
```

### POST `/api/groups/:id/initial-ranking`
Save initial ranking (Phase 1):
```typescript
{
  ranking: RankingEntry[]; // { code, position }[]
}
```

### POST `/api/groups/:id/revised-ranking`
Save revised ranking (Phase 3):
```typescript
{
  ranking: RankingEntry[];
}
```

### POST `/api/groups/:id/submit-workshop`
Submit final actions and get comparison:
```typescript
Request: { actions: string[] }
Response: RankingComparison
```

## Design System

### Colors
- Purple (#7B1FA2): Active phase, primary actions
- Green (#2E7D32): Completed phases, positive indicators
- Gray: Upcoming phases, neutral
- Red (#C62828): Critical/high risk
- Yellow (#FFC107): Medium risk
- Orange (#E65100): Warning/potential

### Quadrant Colors
- Q1 Model: Green (#2E7D32)
- Q2 Risk: Yellow (#FFC107)
- Q3 Critical: Red (#C62828)
- Q4 Potential: Orange (#E65100)

### Layout
- Header: 56px (h-14)
- Stepper: 64px (h-16)
- Footer: 64px (h-16) with action button
- Content: flex-1 (remaining space)

## User Flow

1. **Phase 1 - Initial Ranking**
   - User sees 10 municipality cards
   - Clicks to add to priority list (1-10)
   - Can reorder with up/down arrows
   - Submits ranking when all 10 are ranked
   - Transition screen appears
   - Click "Continue to Data Exploration"

2. **Phase 2 - Explore**
   - Existing workshop experience (map + sidebar)
   - User buys layers, explores data
   - Click "Continue to Revision" in footer when ready

3. **Phase 3 - Revised Ranking & Actions**
   - Split view: ranking (left) + actions (right)
   - User can revise ranking with new data
   - User selects priority actions (checkboxes)
   - Submit both ranking and actions together

4. **Phase 4 - Results**
   - View correlation statistics
   - Compare rankings side-by-side
   - See position differences
   - Compare actions overlap
   - "Back to Exploration" to continue learning

## Responsive Considerations

- Stepper: Horizontal on desktop, should stack on mobile (future enhancement)
- Phase 3 split: 50/50 on desktop, could use tabs on tablet
- Cards: 2-column grid on desktop, 1-column on mobile
- Priority list: Fixed width sidebar on desktop

## Testing Checklist

### Phase 1
- [ ] Can click municipalities to add to ranking
- [ ] Position numbers update correctly
- [ ] Up/down arrows reorder correctly
- [ ] Remove button works
- [ ] Submit button disabled until 10 ranked
- [ ] Transition screen appears after submit
- [ ] API call saves ranking

### Phase 2
- [ ] Existing map/sidebar works
- [ ] Footer button advances to Phase 3

### Phase 3
- [ ] Can revise ranking with new data
- [ ] Risk summary shows if layers purchased
- [ ] "Keep Initial Ranking" copies Phase 1 ranking
- [ ] Action cards display correctly
- [ ] Can select/deselect actions
- [ ] Submit button enabled when actions selected
- [ ] API call saves revised ranking and actions

### Phase 4
- [ ] Correlation statistics display
- [ ] Rankings compare side-by-side
- [ ] Position differences show with arrows
- [ ] Actions comparison shows overlap
- [ ] "Back to Exploration" button works

## Internationalization

All text is fully translated in 3 languages:
- English (en)
- Spanish (es)
- Portuguese (pt)

Uses Next.js `useTranslations` hook with namespaces:
- `workshopFlow`: Main workshop UI
- `actionNames`: PEARC action names
- `actionDescriptions`: Action descriptions

## Performance Considerations

- State persisted in localStorage (Zustand persist)
- No unnecessary re-renders (component memoization where needed)
- ScrollArea for long lists (virtualization not needed for 10 items)
- API calls only on user actions (submit, phase change)

## Accessibility

- Semantic HTML (button, aside, main, header, footer)
- ARIA labels on interactive elements
- Keyboard navigation support
- Color contrast follows WCAG AA
- Focus indicators on all interactive elements

## Future Enhancements

1. Mobile responsiveness (tabs for Phase 3 split)
2. Drag-and-drop ranking (alternative to click + arrows)
3. Undo/redo functionality
4. Save draft (auto-save every N seconds)
5. Export results to PDF
6. Social sharing of results
7. Group leaderboard (compare with other groups)
8. Animated transitions between phases
9. Tooltips on action links/evidence
10. Real-time collaboration (multiple users in same group)

## Dependencies

All dependencies already in place:
- Next.js 15+ with App Router
- next-intl for i18n
- Zustand for state management
- shadcn/ui components
- Tailwind CSS
- TypeScript

## File Structure

```
terrarisk-workshop/frontend/
├── src/
│   ├── app/
│   │   └── workshop/
│   │       └── page.tsx (UPDATED - main workshop page)
│   ├── components/
│   │   ├── workshop/ (NEW DIRECTORY)
│   │   │   ├── WorkshopStepper.tsx
│   │   │   ├── MunicipalityRanking.tsx
│   │   │   ├── ActionsSelector.tsx
│   │   │   └── RankingComparison.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx (no changes)
│   │   │   └── Sidebar.tsx (no changes)
│   │   ├── map/
│   │   │   └── MapViewer.tsx (no changes)
│   │   └── ui/
│   │       ├── card.tsx (existing)
│   │       ├── badge.tsx (existing)
│   │       ├── button.tsx (existing)
│   │       ├── scroll-area.tsx (existing)
│   │       └── separator.tsx (existing)
│   └── lib/
│       ├── types.ts (UPDATED - added workshop types)
│       └── store.ts (UPDATED - added workshop state)
└── messages/
    ├── en.json (UPDATED - added workshopFlow, actionNames, actionDescriptions)
    ├── es.json (UPDATED - same)
    └── pt.json (UPDATED - same)
```

## Summary

Complete frontend implementation of the TerraRisk Workshop Flow. All 4 components created, types and state management updated, i18n messages added for 3 languages. The workshop page now has a stepper-based flow with clear phase transitions. Backend API endpoints need to be implemented to support the data loading and submission.

**Ready for backend integration and testing.**

---

**Next Steps:**
1. Implement backend API endpoints (Point 11)
2. Test with real data from integrated dataset
3. Deploy to staging environment
4. Conduct user testing with SEMIL-USP workshop participants (Feb 22-26)
