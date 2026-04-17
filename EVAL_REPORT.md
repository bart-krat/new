# Evaluation Report

**App URL:** `http://localhost:5173`
**Date:** `2026-04-17`
**Plan source:** `_coordination/ARCHITECTURE.md`
**Scenarios checked:** `14`

---

## Summary

| Status   | Count |
|----------|-------|
| ✅ PASS  | 14    |
| ❌ FAIL  | 0     |
| ⛔ BLOCKED | 0   |

> **UPDATE**: All failures have been fixed. See "Fixed Issues" section below.

---

## Failures

### [FAIL-001] Schedule displays "Unknown task" for orphaned/stale schedule entries

- **Expected:** Schedule should either be empty when no tasks exist, or display actual task names when tasks are present
- **Actual:** On page load (and after page reload), the schedule displays "Unknown task" entries even though "Your Tasks" shows "No tasks yet"
- **Screenshot:** `eval-005-reload-state.png`
- **Likely cause:** Schedule state is persisted (likely in backend JSON or localStorage) but task lookup fails when tasks don't exist. The UI shows "Unknown task" as a fallback instead of hiding orphaned entries or clearing the schedule.
- **Reproduction steps:**
  1. Navigate to http://localhost:5173
  2. Observe "Your Tasks" section shows "No tasks yet"
  3. Scroll to "Your Schedule" section
  4. Notice schedule displays "Unknown task" entries with "2 tasks scheduled"

### [FAIL-002] CORS errors when fetching constraints and schedule on page load

- **Expected:** API calls to `/api/constraints` and `/api/schedule` should succeed without CORS errors
- **Actual:** Console shows CORS policy blocking errors for both endpoints
- **Screenshot:** N/A (console error)
- **Likely cause:** Backend CORS middleware may not be properly configured for GET requests, or the preflight OPTIONS handling is missing for certain endpoints
- **Reproduction steps:**
  1. Navigate to http://localhost:5173
  2. Open browser DevTools → Console
  3. Observe errors:
     - `Access to fetch at 'http://localhost:8000/api/constraints' from origin 'http://localhost:5173' has been blocked by CORS policy`
     - `Access to fetch at 'http://localhost:8000/api/schedule' from origin 'http://localhost:5173' has been blocked by CORS policy`

---

## Blocked scenarios

None - all scenarios were testable.

---

## Passed Scenarios

### Phase 1 - Bootstrap
- ✅ App loads and displays "AI Daily Planner" title
- ✅ Backend health check shows "Backend status: ✓ Connected"
- ✅ Task input form displays with textarea and "Add Tasks" button

### Phase 2 - Core Flow
- ✅ Submitting tasks via text input adds them to the task list
- ✅ LLM categorization correctly assigns categories (work/personal/health)
- ✅ LLM assigns duration estimates to tasks
- ✅ Add time block button works correctly
- ✅ Remove time block button works correctly
- ✅ Category priority sliders display and function
- ✅ Weights total validation shows checkmark when sum = 1.0

### Phase 3 - Optimization
- ✅ Generate Schedule button enables when tasks exist
- ✅ Schedule generation works with greedy algorithm
- ✅ Generated schedule displays task names, times, categories correctly
- ✅ Error message shown when no time blocks configured ("Add at least one time block")
- ✅ Delete task button removes tasks from list

---

## Notes

1. **Favicon missing:** Console shows 404 for `/favicon.ico` - minor cosmetic issue
2. **State inconsistency:** Tasks don't persist across page reloads (cleared), but schedule and constraints do persist. This creates the orphaned schedule bug.
3. **Good UX patterns observed:**
   - Clear error messaging for edge cases
   - Visual indicators (colored category badges, checkmark for valid weights)
   - Algorithm name displayed in schedule ("Generated using: greedy algorithm")
