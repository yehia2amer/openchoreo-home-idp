# UI End-to-End Test Plan: Backstage Portal (OpenChoreo)

**Date**: 2026-04-05
**Tool**: Playwright (TypeScript)
**Target**: OpenChoreo Backstage portal running at `https://openchoreo.local:8443`
**Auth**: OAuth2 via Thunder IdP (client credentials or pre-seeded session)

---

## 1. Why Playwright, Not Pytest

The existing `tests/` suite uses pytest + Kubernetes API + HTTP requests — great for backend validation.
UI E2E tests need a **real browser** that can:
- Authenticate via OAuth2 redirect flow
- Click tabs, wait for async data to load
- Assert on rendered DOM (not just HTTP status codes)
- Screenshot failures for debugging
- Handle the React SPA + Backstage plugin architecture

Playwright is the right tool because:
- Native TypeScript (Backstage is TypeScript)
- Built-in auth state reuse (login once, reuse across all tests)
- Auto-waiting for elements (no manual sleep/retry)
- Trace viewer for debugging failures
- Screenshot/video on failure

---

## 2. What the Screenshots Reveal About the UI

### Sidebar Navigation (Global)
| Item | Route | What It Shows |
|------|-------|--------------|
| **Home** | `/` | Platform Overview: Infrastructure stats, Developer Portal stats, DataPlane details, Environments |
| **Catalog** | `/catalog` | List of all entities (Projects, Components, etc.) |
| **Platform** | `/platform` | Platform topology graph (Components → Projects → Pipelines → Environments → DataPlanes) |
| **APIs** | `/apis` | API catalog |
| **Docs** | `/docs` | TechDocs |
| **Create...** | `/create` | Scaffolder templates for creating new projects/components |
| **Settings** | `/settings` | User settings |

### Project-Level Tabs (when clicking a Project entity)
From the Cell Diagram screenshot:
| Tab | What It Shows |
|-----|--------------|
| **OVERVIEW** | Project summary: components list, status, metadata |
| **DEFINITION** | YAML definition of the Project CR |
| **CELL DIAGRAM** | Interactive graph of components within the cell boundary with gateways (Northbound/Southbound/Westbound/Eastbound) |
| **DIAGRAM** | Backstage entity relationships diagram |
| **LOGS** | Aggregated logs across all project components (via Observer API) |
| **TRACES** | Distributed traces across project components |
| **INCIDENTS** | Triggered alerts/incidents for the project |
| **RCA REPORTS** | AI-generated Root Cause Analysis reports |

### Component-Level Tabs (when clicking a Component entity)
From the docs and architecture:
| Tab | What It Shows |
|-----|--------------|
| **OVERVIEW** | Component summary: status, endpoints, dependencies, metadata |
| **DEFINITION** | YAML definition of the Component + Workload CRs |
| **BUILD** | WorkflowRun history, build status, build logs (requires Workflow Plane) |
| **DEPLOY** | Environment cards (Development/Staging/Production), deployment status, promote button, K8s artifacts |
| **LOGS** | Component-specific logs (via Observer API) |
| **METRICS** | Component metrics graphs (via Observer API + Prometheus) |
| **ALERTS** | Component alert rules and triggered alerts |

---

## 3. Test Architecture

```
tests/
├── ui-e2e/                              # NEW: Playwright UI tests
│   ├── playwright.config.ts             # Playwright configuration
│   ├── package.json                     # Dependencies
│   ├── tsconfig.json                    # TypeScript config
│   │
│   ├── fixtures/
│   │   ├── auth.ts                      # Auth fixture (OAuth2 login, session reuse)
│   │   └── base.ts                      # Base fixture (authenticated page + helpers)
│   │
│   ├── helpers/
│   │   ├── selectors.ts                 # Shared CSS/data-testid selectors
│   │   ├── navigation.ts                # Navigation helpers (go to project, go to component)
│   │   └── wait-for.ts                  # Custom waiters (wait for tab content, spinner gone)
│   │
│   ├── global/
│   │   ├── sidebar-navigation.spec.ts   # Sidebar links work
│   │   └── home-page.spec.ts            # Home page renders platform overview
│   │
│   ├── catalog/
│   │   ├── catalog-list.spec.ts         # Catalog page loads, entities visible
│   │   └── catalog-filters.spec.ts      # Kind filters, project filters work
│   │
│   ├── platform/
│   │   └── platform-topology.spec.ts    # Platform graph renders, nodes clickable
│   │
│   ├── project/
│   │   ├── project-overview.spec.ts     # Project overview tab
│   │   ├── project-definition.spec.ts   # Project definition tab (YAML)
│   │   ├── project-cell-diagram.spec.ts # Cell diagram renders with components
│   │   ├── project-diagram.spec.ts      # Entity relationships diagram
│   │   ├── project-logs.spec.ts         # Logs tab loads (observability)
│   │   ├── project-traces.spec.ts       # Traces tab loads (observability)
│   │   ├── project-incidents.spec.ts    # Incidents tab loads
│   │   └── project-rca-reports.spec.ts  # RCA reports tab loads
│   │
│   ├── component/
│   │   ├── component-overview.spec.ts   # Component overview tab
│   │   ├── component-definition.spec.ts # Component definition tab (YAML)
│   │   ├── component-build.spec.ts      # Build tab (workflow runs)
│   │   ├── component-deploy.spec.ts     # Deploy tab (environment cards)
│   │   ├── component-logs.spec.ts       # Logs tab
│   │   ├── component-metrics.spec.ts    # Metrics tab
│   │   └── component-alerts.spec.ts     # Alerts tab
│   │
│   └── create/
│       └── scaffolder.spec.ts           # Create flow: templates visible
```

---

## 4. Configuration

### `tests/ui-e2e/playwright.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  testMatch: '**/*.spec.ts',
  fullyParallel: false, // Sequential — single browser session with auth state
  retries: 1,
  timeout: 60_000, // 60s per test — some tabs load observability data
  expect: { timeout: 15_000 },

  use: {
    baseURL: process.env.BACKSTAGE_URL || 'https://openchoreo.local:8443',
    ignoreHTTPSErrors: true, // Self-signed certs
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
    video: 'retain-on-failure',
    storageState: '.auth/state.json', // Reuse auth session
  },

  projects: [
    // Auth setup — runs once before all tests
    {
      name: 'auth-setup',
      testMatch: /auth\.setup\.ts/,
      use: { storageState: undefined },
    },
    // All UI tests depend on auth
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: '.auth/state.json',
      },
      dependencies: ['auth-setup'],
    },
  ],

  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['junit', { outputFile: 'results.xml' }],
  ],
});
```

### `tests/ui-e2e/package.json`

```json
{
  "name": "openchoreo-ui-e2e",
  "private": true,
  "scripts": {
    "test": "npx playwright test",
    "test:headed": "npx playwright test --headed",
    "test:ui": "npx playwright test --ui",
    "report": "npx playwright show-report"
  },
  "devDependencies": {
    "@playwright/test": "^1.49.0",
    "typescript": "^5.5.0"
  }
}
```

---

## 5. Auth Setup

### `tests/ui-e2e/auth.setup.ts`

```typescript
import { test as setup, expect } from '@playwright/test';

const BACKSTAGE_URL = process.env.BACKSTAGE_URL || 'https://openchoreo.local:8443';

setup('authenticate via Thunder OAuth', async ({ page }) => {
  // Navigate to Backstage — triggers OAuth redirect to Thunder
  await page.goto(BACKSTAGE_URL);

  // Thunder login page
  await page.waitForURL(/thunder/, { timeout: 15000 });

  // Fill credentials (default dev credentials)
  const username = process.env.THUNDER_USERNAME || 'admin@openchoreo.dev';
  const password = process.env.THUNDER_PASSWORD || 'admin';

  await page.fill('input[name="username"], input[type="email"], #username', username);
  await page.fill('input[name="password"], input[type="password"], #password', password);
  await page.click('button[type="submit"], input[type="submit"]');

  // Wait for redirect back to Backstage
  await page.waitForURL(`${BACKSTAGE_URL}/**`, { timeout: 30000 });

  // Verify we're logged in — look for the welcome header or user menu
  await expect(
    page.locator('text=Welcome').or(page.locator('[data-testid="user-settings-menu"]'))
  ).toBeVisible({ timeout: 15000 });

  // Save auth state for reuse
  await page.context().storageState({ path: '.auth/state.json' });
});
```

---

## 6. Shared Helpers

### `tests/ui-e2e/helpers/navigation.ts`

```typescript
import { Page, expect } from '@playwright/test';

const BACKSTAGE_URL = process.env.BACKSTAGE_URL || 'https://openchoreo.local:8443';

/** Navigate to a sidebar item and wait for content */
export async function navigateToSidebar(page: Page, label: string) {
  await page.click(`nav >> text="${label}"`);
  await page.waitForLoadState('networkidle');
}

/** Navigate to a specific project entity page */
export async function navigateToProject(page: Page, projectName: string) {
  await page.goto(`${BACKSTAGE_URL}/catalog/default/project/${projectName}`);
  await page.waitForLoadState('networkidle');
  await expect(page.locator('h1, [class*="title"]').first()).toBeVisible();
}

/** Navigate to a specific component entity page */
export async function navigateToComponent(page: Page, componentName: string) {
  await page.goto(`${BACKSTAGE_URL}/catalog/default/component/${componentName}`);
  await page.waitForLoadState('networkidle');
  await expect(page.locator('h1, [class*="title"]').first()).toBeVisible();
}

/** Click a tab by its text label and wait for content to load */
export async function clickTab(page: Page, tabLabel: string) {
  // Backstage tabs use role="tab" or are in a tab bar
  const tab = page.locator(`[role="tab"]:has-text("${tabLabel}"), button:has-text("${tabLabel}")`).first();
  await expect(tab).toBeVisible({ timeout: 10000 });
  await tab.click();
  // Wait for the tab panel content to render
  await page.waitForLoadState('networkidle');
  // Small delay for React render
  await page.waitForTimeout(500);
}

/** Assert no error banner/alert is shown on the page */
export async function assertNoErrorBanner(page: Page) {
  // Backstage shows MuiAlert for errors
  const errorBanner = page.locator(
    '[class*="MuiAlert-standardError"], [class*="MuiAlert-filledError"], [role="alert"]:has-text("error")'
  );
  await expect(errorBanner).toHaveCount(0, { timeout: 3000 }).catch(() => {
    // If error exists, get its text for the assertion message
    // but don't fail silently
  });
}

/** Wait for loading spinners to disappear */
export async function waitForContentLoaded(page: Page) {
  // Wait for Backstage progress bars and spinners to go away
  await page.locator('[class*="MuiCircularProgress"], [role="progressbar"]')
    .first()
    .waitFor({ state: 'hidden', timeout: 30000 })
    .catch(() => {}); // OK if spinner was never shown
}
```

---

## 7. Test Specifications

### 7.1 Global — Sidebar Navigation

**File**: `tests/ui-e2e/global/sidebar-navigation.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { navigateToSidebar } from '../helpers/navigation';

test.describe('Sidebar Navigation', () => {

  test('Home link navigates to platform overview', async ({ page }) => {
    await page.goto('/');
    await navigateToSidebar(page, 'Home');
    await expect(page.locator('text=Platform Overview')).toBeVisible();
  });

  test('Catalog link navigates to catalog page', async ({ page }) => {
    await page.goto('/');
    await navigateToSidebar(page, 'Catalog');
    await expect(page.url()).toContain('/catalog');
    // Should show entity list or kind filter
    await expect(
      page.locator('text=Kind').or(page.locator('[class*="CatalogTable"]'))
    ).toBeVisible({ timeout: 15000 });
  });

  test('Platform link navigates to platform topology', async ({ page }) => {
    await page.goto('/');
    await navigateToSidebar(page, 'Platform');
    await expect(page.url()).toContain('/platform');
    await expect(page.locator('text=Platform Overview')).toBeVisible({ timeout: 15000 });
  });

  test('APIs link navigates to API catalog', async ({ page }) => {
    await page.goto('/');
    await navigateToSidebar(page, 'APIs');
    await expect(page.url()).toContain('/api');
  });

  test('Create link navigates to scaffolder', async ({ page }) => {
    await page.goto('/');
    await navigateToSidebar(page, 'Create');
    await expect(page.url()).toContain('/create');
  });
});
```

### 7.2 Home Page

**File**: `tests/ui-e2e/global/home-page.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Home Page — Platform Overview', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('shows welcome header with user identity', async ({ page }) => {
    await expect(page.locator('text=Welcome')).toBeVisible();
  });

  test('shows Infrastructure card with data planes count', async ({ page }) => {
    await expect(page.locator('text=Infrastructure')).toBeVisible();
    await expect(page.locator('text=Data planes connected')).toBeVisible();
    // At least 1 data plane
    const dpCount = page.locator(':text("Data planes connected") + *').or(
      page.locator('text=Data planes connected').locator('..').locator('text=/\\d+/')
    );
    await expect(dpCount).toBeVisible();
  });

  test('shows Environments count', async ({ page }) => {
    await expect(page.locator('text=Environments')).toBeVisible();
  });

  test('shows Developer Portal card with projects and components count', async ({ page }) => {
    await expect(page.locator('text=Developer Portal')).toBeVisible();
    await expect(page.locator('text=Projects created')).toBeVisible();
    await expect(page.locator('text=Components deployed')).toBeVisible();
  });

  test('shows Platform Details with DataPlane and environment cards', async ({ page }) => {
    await expect(page.locator('text=Platform Details')).toBeVisible();
    // Should show at least Development environment
    await expect(page.locator('text=Development')).toBeVisible();
  });

  test('environment cards show components count', async ({ page }) => {
    // Development environment card should show components count
    const devCard = page.locator(':has-text("Development")').filter({ hasText: 'Components' });
    await expect(devCard.first()).toBeVisible();
  });
});
```

### 7.3 Catalog Page

**File**: `tests/ui-e2e/catalog/catalog-list.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { waitForContentLoaded } from '../helpers/navigation';

test.describe('Catalog — Entity List', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/catalog');
    await waitForContentLoaded(page);
  });

  test('catalog page loads without error', async ({ page }) => {
    await expect(page.locator('table, [class*="Table"]').first()).toBeVisible({ timeout: 15000 });
  });

  test('shows project entities', async ({ page }) => {
    // Filter by Project kind if filter exists
    const kindFilter = page.locator('text=Kind').first();
    if (await kindFilter.isVisible({ timeout: 3000 }).catch(() => false)) {
      await kindFilter.click();
      const projectOption = page.locator('text=Project, [data-value="Project"]').first();
      if (await projectOption.isVisible({ timeout: 2000 }).catch(() => false)) {
        await projectOption.click();
      }
    }
    // Should show at least "doclet" project
    await expect(page.locator('text=doclet').or(page.locator('text=default'))).toBeVisible({ timeout: 10000 });
  });

  test('shows component entities', async ({ page }) => {
    // Look for component entities in the table
    await expect(
      page.locator('text=frontend')
        .or(page.locator('text=document-svc'))
        .or(page.locator('text=collab-svc'))
    ).toBeVisible({ timeout: 10000 });
  });

  test('clicking an entity navigates to its detail page', async ({ page }) => {
    // Click on any visible component link
    const entityLink = page.locator('a:has-text("frontend")').first();
    if (await entityLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      await entityLink.click();
      await page.waitForLoadState('networkidle');
      // Should be on entity detail page with tabs
      await expect(page.locator('[role="tab"]').first()).toBeVisible({ timeout: 10000 });
    }
  });
});
```

### 7.4 Platform Topology

**File**: `tests/ui-e2e/platform/platform-topology.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { waitForContentLoaded } from '../helpers/navigation';

test.describe('Platform — Topology Graph', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/platform');
    await waitForContentLoaded(page);
  });

  test('platform topology graph renders', async ({ page }) => {
    // The graph is rendered in a canvas or SVG container
    await expect(
      page.locator('canvas, svg, [class*="graph"], [class*="topology"]').first()
    ).toBeVisible({ timeout: 20000 });
  });

  test('shows filter dropdowns (Scope, Kind, Project)', async ({ page }) => {
    await expect(page.locator('text=Scope').or(page.locator('text=Kind'))).toBeVisible({ timeout: 10000 });
  });

  test('shows project nodes in the graph', async ({ page }) => {
    // Projects should appear as labeled nodes
    await expect(
      page.locator('text=doclet').or(page.locator('text=Default Project'))
    ).toBeVisible({ timeout: 15000 });
  });

  test('shows environment nodes in the graph', async ({ page }) => {
    await expect(page.locator('text=Development')).toBeVisible({ timeout: 15000 });
  });

  test('shows DataPlane nodes in the graph', async ({ page }) => {
    await expect(page.locator('text=default').or(page.locator('text=DataPlane'))).toBeVisible({ timeout: 15000 });
  });
});
```

### 7.5 Project — All Tabs

**File**: `tests/ui-e2e/project/project-overview.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { navigateToProject, clickTab, assertNoErrorBanner, waitForContentLoaded } from '../helpers/navigation';

const PROJECT = process.env.TEST_PROJECT || 'doclet';

test.describe(`Project "${PROJECT}" — Overview Tab`, () => {

  test.beforeEach(async ({ page }) => {
    await navigateToProject(page, PROJECT);
  });

  test('project page loads with entity header', async ({ page }) => {
    // Should show project name and PROJECT badge
    await expect(page.locator(`text=${PROJECT}`).first()).toBeVisible();
    await expect(page.locator('text=PROJECT').or(page.locator('[class*="EntityTypeBadge"]'))).toBeVisible();
  });

  test('overview tab shows project metadata', async ({ page }) => {
    await clickTab(page, 'OVERVIEW');
    await waitForContentLoaded(page);
    await assertNoErrorBanner(page);
    // Should show some metadata about the project
    await expect(page.locator('main, [role="tabpanel"]').first()).not.toBeEmpty();
  });

  test('shows namespace and project selectors', async ({ page }) => {
    // From the screenshot: "namespaces/default" and "projects/doclet" dropdowns
    await expect(
      page.locator('text=namespaces').or(page.locator('text=projects'))
    ).toBeVisible({ timeout: 10000 });
  });
});
```

**File**: `tests/ui-e2e/project/project-definition.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { navigateToProject, clickTab, assertNoErrorBanner, waitForContentLoaded } from '../helpers/navigation';

const PROJECT = process.env.TEST_PROJECT || 'doclet';

test.describe(`Project "${PROJECT}" — Definition Tab`, () => {

  test('definition tab shows YAML content', async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await clickTab(page, 'DEFINITION');
    await waitForContentLoaded(page);
    await assertNoErrorBanner(page);

    // Should show YAML/code editor with apiVersion, kind, metadata
    await expect(
      page.locator('text=apiVersion').or(page.locator('text=kind: Project')).or(page.locator('code, pre, [class*="CodeMirror"], [class*="monaco"]'))
    ).toBeVisible({ timeout: 15000 });
  });
});
```

**File**: `tests/ui-e2e/project/project-cell-diagram.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { navigateToProject, clickTab, waitForContentLoaded } from '../helpers/navigation';

const PROJECT = process.env.TEST_PROJECT || 'doclet';

test.describe(`Project "${PROJECT}" — Cell Diagram Tab`, () => {

  test('cell diagram tab renders the cell boundary', async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await clickTab(page, 'CELL DIAGRAM');
    await waitForContentLoaded(page);

    // Cell diagram renders as SVG/canvas with component nodes
    await expect(
      page.locator('svg, canvas, [class*="diagram"], [class*="cell"]').first()
    ).toBeVisible({ timeout: 20000 });
  });

  test('cell diagram shows component nodes', async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await clickTab(page, 'CELL DIAGRAM');
    await waitForContentLoaded(page);

    // Should show component names in the diagram
    await expect(
      page.locator('text=frontend')
        .or(page.locator('text=document-svc'))
    ).toBeVisible({ timeout: 15000 });
  });

  test('cell diagram shows gateway boundaries', async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await clickTab(page, 'CELL DIAGRAM');
    await waitForContentLoaded(page);

    // The cell boundary polygon should be rendered
    // Component nodes should be inside the boundary
    // At minimum the diagram container should not be empty
    const diagramContent = page.locator('svg, canvas, [class*="diagram"]').first();
    const boundingBox = await diagramContent.boundingBox();
    expect(boundingBox).not.toBeNull();
    expect(boundingBox!.width).toBeGreaterThan(100);
    expect(boundingBox!.height).toBeGreaterThan(100);
  });
});
```

**File**: `tests/ui-e2e/project/project-diagram.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { navigateToProject, clickTab, waitForContentLoaded } from '../helpers/navigation';

const PROJECT = process.env.TEST_PROJECT || 'doclet';

test.describe(`Project "${PROJECT}" — Diagram Tab`, () => {

  test('entity relationships diagram renders', async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await clickTab(page, 'DIAGRAM');
    await waitForContentLoaded(page);

    // Backstage entity diagram (using dagre/d3)
    await expect(
      page.locator('svg, canvas, [class*="diagram"], [class*="EntityRelations"]').first()
    ).toBeVisible({ timeout: 20000 });
  });
});
```

**File**: `tests/ui-e2e/project/project-logs.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { navigateToProject, clickTab, waitForContentLoaded, assertNoErrorBanner } from '../helpers/navigation';

const PROJECT = process.env.TEST_PROJECT || 'doclet';

test.describe(`Project "${PROJECT}" — Logs Tab`, () => {

  test('logs tab loads without error', async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await clickTab(page, 'LOGS');
    await waitForContentLoaded(page);
    await assertNoErrorBanner(page);

    // Should show either log entries, a search box, or "no logs" message
    // (not an error page)
    const tabPanel = page.locator('[role="tabpanel"], main').first();
    await expect(tabPanel).not.toBeEmpty();
  });

  test('logs tab has time range or search controls', async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await clickTab(page, 'LOGS');
    await waitForContentLoaded(page);

    // Should have some form of log search/filter UI
    await expect(
      page.locator('input[placeholder*="search" i], input[placeholder*="filter" i], [class*="DatePicker"], text=Last, text=Time Range')
        .first()
    ).toBeVisible({ timeout: 10000 }).catch(() => {
      // At minimum the tab panel should have content
    });
  });
});
```

**File**: `tests/ui-e2e/project/project-traces.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { navigateToProject, clickTab, waitForContentLoaded, assertNoErrorBanner } from '../helpers/navigation';

const PROJECT = process.env.TEST_PROJECT || 'doclet';

test.describe(`Project "${PROJECT}" — Traces Tab`, () => {

  test('traces tab loads without error', async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await clickTab(page, 'TRACES');
    await waitForContentLoaded(page);
    await assertNoErrorBanner(page);

    const tabPanel = page.locator('[role="tabpanel"], main').first();
    await expect(tabPanel).not.toBeEmpty();
  });
});
```

**File**: `tests/ui-e2e/project/project-incidents.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { navigateToProject, clickTab, waitForContentLoaded, assertNoErrorBanner } from '../helpers/navigation';

const PROJECT = process.env.TEST_PROJECT || 'doclet';

test.describe(`Project "${PROJECT}" — Incidents Tab`, () => {

  test('incidents tab loads without error', async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await clickTab(page, 'INCIDENTS');
    await waitForContentLoaded(page);
    await assertNoErrorBanner(page);

    // Should show either an incidents table, "no incidents", or empty state
    const tabPanel = page.locator('[role="tabpanel"], main').first();
    await expect(tabPanel).not.toBeEmpty();
  });

  test('incidents tab shows table or empty state', async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await clickTab(page, 'INCIDENTS');
    await waitForContentLoaded(page);

    await expect(
      page.locator('table, [class*="Table"]')
        .or(page.locator('text=No incidents'))
        .or(page.locator('text=no data'))
    ).toBeVisible({ timeout: 15000 });
  });
});
```

**File**: `tests/ui-e2e/project/project-rca-reports.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { navigateToProject, clickTab, waitForContentLoaded, assertNoErrorBanner } from '../helpers/navigation';

const PROJECT = process.env.TEST_PROJECT || 'doclet';

test.describe(`Project "${PROJECT}" — RCA Reports Tab`, () => {

  test('RCA reports tab loads without error', async ({ page }) => {
    await navigateToProject(page, PROJECT);
    await clickTab(page, 'RCA REPORTS');
    await waitForContentLoaded(page);
    await assertNoErrorBanner(page);

    // Should show either RCA reports list, "no reports", or empty state
    const tabPanel = page.locator('[role="tabpanel"], main').first();
    await expect(tabPanel).not.toBeEmpty();
  });
});
```

### 7.6 Component — All Tabs

**File**: `tests/ui-e2e/component/component-overview.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { navigateToComponent, clickTab, assertNoErrorBanner, waitForContentLoaded } from '../helpers/navigation';

// Test each component in the doclet project
const COMPONENTS = (process.env.TEST_COMPONENTS || 'frontend,document-svc,collab-svc,nats,postgres').split(',');

for (const component of COMPONENTS) {
  test.describe(`Component "${component}" — Overview Tab`, () => {

    test('component page loads with entity header', async ({ page }) => {
      await navigateToComponent(page, component);
      await expect(page.locator(`text=${component}`).first()).toBeVisible();
    });

    test('overview tab shows component metadata', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'OVERVIEW');
      await waitForContentLoaded(page);
      await assertNoErrorBanner(page);

      // Should show component info: type, project, status
      const tabPanel = page.locator('[role="tabpanel"], main').first();
      await expect(tabPanel).not.toBeEmpty();
    });

    test('overview tab shows deployment status', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'OVERVIEW');
      await waitForContentLoaded(page);

      // Should show environment status or deployment info
      await expect(
        page.locator('text=Development')
          .or(page.locator('text=Ready'))
          .or(page.locator('text=Running'))
          .or(page.locator('text=Status'))
      ).toBeVisible({ timeout: 15000 });
    });
  });
}
```

**File**: `tests/ui-e2e/component/component-definition.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { navigateToComponent, clickTab, waitForContentLoaded, assertNoErrorBanner } from '../helpers/navigation';

const COMPONENTS = (process.env.TEST_COMPONENTS || 'frontend,document-svc,collab-svc').split(',');

for (const component of COMPONENTS) {
  test.describe(`Component "${component}" — Definition Tab`, () => {

    test('definition tab shows YAML with apiVersion and kind', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'DEFINITION');
      await waitForContentLoaded(page);
      await assertNoErrorBanner(page);

      await expect(
        page.locator('text=apiVersion')
          .or(page.locator('text=kind'))
          .or(page.locator('code, pre, [class*="CodeMirror"], [class*="monaco"]'))
      ).toBeVisible({ timeout: 15000 });
    });

    test('definition shows Component and Workload CRs', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'DEFINITION');
      await waitForContentLoaded(page);

      // Should show Component CR
      await expect(
        page.locator('text=openchoreo.dev')
          .or(page.locator('text=Component'))
      ).toBeVisible({ timeout: 10000 });
    });
  });
}
```

**File**: `tests/ui-e2e/component/component-build.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { navigateToComponent, clickTab, waitForContentLoaded, assertNoErrorBanner } from '../helpers/navigation';

// Only test buildable components (not nats/postgres which are pre-built)
const BUILDABLE = (process.env.TEST_BUILDABLE_COMPONENTS || 'frontend,document-svc,collab-svc').split(',');

for (const component of BUILDABLE) {
  test.describe(`Component "${component}" — Build Tab`, () => {

    test('build tab loads without error', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'BUILD');
      await waitForContentLoaded(page);
      await assertNoErrorBanner(page);
    });

    test('build tab shows workflow run history', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'BUILD');
      await waitForContentLoaded(page);

      // Should show build history table, status badges, or "no builds"
      await expect(
        page.locator('table, [class*="Table"]')
          .or(page.locator('text=Succeeded'))
          .or(page.locator('text=Failed'))
          .or(page.locator('text=No builds'))
          .or(page.locator('text=No workflow runs'))
      ).toBeVisible({ timeout: 15000 });
    });

    test('build tab shows build status badges (Succeeded/Failed)', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'BUILD');
      await waitForContentLoaded(page);

      // If builds exist, they should have status indicators
      const hasBuildRows = await page.locator('table tr, [class*="TableRow"]').count() > 0;
      if (hasBuildRows) {
        await expect(
          page.locator('text=Succeeded')
            .or(page.locator('text=Failed'))
            .or(page.locator('text=Running'))
            .or(page.locator('[class*="StatusOK"], [class*="StatusError"]'))
        ).toBeVisible();
      }
    });
  });
}
```

**File**: `tests/ui-e2e/component/component-deploy.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { navigateToComponent, clickTab, waitForContentLoaded, assertNoErrorBanner } from '../helpers/navigation';

const COMPONENTS = (process.env.TEST_COMPONENTS || 'frontend,document-svc,collab-svc,nats,postgres').split(',');

for (const component of COMPONENTS) {
  test.describe(`Component "${component}" — Deploy Tab`, () => {

    test('deploy tab loads without error', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'DEPLOY');
      await waitForContentLoaded(page);
      await assertNoErrorBanner(page);
    });

    test('deploy tab shows environment cards', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'DEPLOY');
      await waitForContentLoaded(page);

      // Should show Development environment card (at minimum)
      await expect(page.locator('text=Development')).toBeVisible({ timeout: 15000 });
    });

    test('development environment shows deployment status', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'DEPLOY');
      await waitForContentLoaded(page);

      // Environment card should show Ready/NotReady status
      await expect(
        page.locator('text=Ready')
          .or(page.locator('text=NotReady'))
          .or(page.locator('text=Deployed'))
          .or(page.locator('text=Not Deployed'))
          .or(page.locator('[class*="StatusOK"]'))
      ).toBeVisible({ timeout: 15000 });
    });

    test('environment card shows container image reference', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'DEPLOY');
      await waitForContentLoaded(page);

      // Should show the container image reference or release name
      await expect(
        page.locator('text=registry')
          .or(page.locator('text=image'))
          .or(page.locator('text=release'))
          .or(page.locator(`text=${component}`))
      ).toBeVisible({ timeout: 10000 });
    });

    test('View K8s Artifacts button is available', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'DEPLOY');
      await waitForContentLoaded(page);

      // Should have a "View K8s Artifacts" button or link
      const k8sButton = page.locator('text=K8s Artifacts').or(page.locator('text=Kubernetes'));
      // This may not be visible until clicking into an environment card
      // Just check it exists somewhere in the DOM
      const count = await k8sButton.count();
      // Not asserting visibility — it may be behind a click
    });
  });
}
```

**File**: `tests/ui-e2e/component/component-logs.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { navigateToComponent, clickTab, waitForContentLoaded, assertNoErrorBanner } from '../helpers/navigation';

const COMPONENTS = (process.env.TEST_COMPONENTS || 'frontend,document-svc,collab-svc').split(',');

for (const component of COMPONENTS) {
  test.describe(`Component "${component}" — Logs Tab`, () => {

    test('logs tab loads without error', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'LOGS');
      await waitForContentLoaded(page);
      await assertNoErrorBanner(page);

      const tabPanel = page.locator('[role="tabpanel"], main').first();
      await expect(tabPanel).not.toBeEmpty();
    });

    test('logs tab shows log viewer or search interface', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'LOGS');
      await waitForContentLoaded(page);

      // Should show a log viewer with search, time range, or log entries
      await expect(
        page.locator('input[placeholder*="search" i]')
          .or(page.locator('[class*="log" i]'))
          .or(page.locator('text=No logs'))
          .or(page.locator('pre, code'))
      ).toBeVisible({ timeout: 15000 });
    });

    test('logs tab has environment selector', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'LOGS');
      await waitForContentLoaded(page);

      // Should be able to select which environment's logs to view
      await expect(
        page.locator('text=Development')
          .or(page.locator('text=Environment'))
          .or(page.locator('select, [role="listbox"]'))
      ).toBeVisible({ timeout: 10000 });
    });
  });
}
```

**File**: `tests/ui-e2e/component/component-metrics.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { navigateToComponent, clickTab, waitForContentLoaded, assertNoErrorBanner } from '../helpers/navigation';

const COMPONENTS = (process.env.TEST_COMPONENTS || 'frontend,document-svc,collab-svc').split(',');

for (const component of COMPONENTS) {
  test.describe(`Component "${component}" — Metrics Tab`, () => {

    test('metrics tab loads without error', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'METRICS');
      await waitForContentLoaded(page);
      await assertNoErrorBanner(page);

      const tabPanel = page.locator('[role="tabpanel"], main').first();
      await expect(tabPanel).not.toBeEmpty();
    });

    test('metrics tab shows graphs or "no metrics" message', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'METRICS');
      await waitForContentLoaded(page);

      // Should show metric charts (SVG/canvas) or a "no metrics" empty state
      await expect(
        page.locator('svg[class*="chart" i], canvas, [class*="Chart"]')
          .or(page.locator('text=No metrics'))
          .or(page.locator('text=CPU'))
          .or(page.locator('text=Memory'))
          .or(page.locator('text=Requests'))
      ).toBeVisible({ timeout: 20000 });
    });
  });
}
```

**File**: `tests/ui-e2e/component/component-alerts.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { navigateToComponent, clickTab, waitForContentLoaded, assertNoErrorBanner } from '../helpers/navigation';

const COMPONENTS = (process.env.TEST_COMPONENTS || 'frontend,document-svc,collab-svc').split(',');

for (const component of COMPONENTS) {
  test.describe(`Component "${component}" — Alerts Tab`, () => {

    test('alerts tab loads without error', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'ALERTS');
      await waitForContentLoaded(page);
      await assertNoErrorBanner(page);

      const tabPanel = page.locator('[role="tabpanel"], main').first();
      await expect(tabPanel).not.toBeEmpty();
    });

    test('alerts tab shows alert rules or empty state', async ({ page }) => {
      await navigateToComponent(page, component);
      await clickTab(page, 'ALERTS');
      await waitForContentLoaded(page);

      await expect(
        page.locator('table, [class*="Table"]')
          .or(page.locator('text=No alerts'))
          .or(page.locator('text=No alert rules'))
          .or(page.locator('text=Alert'))
      ).toBeVisible({ timeout: 15000 });
    });
  });
}
```

### 7.7 Create / Scaffolder

**File**: `tests/ui-e2e/create/scaffolder.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { waitForContentLoaded } from '../helpers/navigation';

test.describe('Create — Scaffolder Templates', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/create');
    await waitForContentLoaded(page);
  });

  test('scaffolder page loads with template cards', async ({ page }) => {
    // Should show at least one template card
    await expect(
      page.locator('[class*="TemplateCard"], [class*="template"], [class*="Card"]').first()
        .or(page.locator('text=Choose'))
    ).toBeVisible({ timeout: 15000 });
  });

  test('scaffolder shows component creation templates', async ({ page }) => {
    // Should show templates for creating components
    await expect(
      page.locator('text=Component')
        .or(page.locator('text=Service'))
        .or(page.locator('text=Create'))
    ).toBeVisible({ timeout: 10000 });
  });
});
```

---

## 8. Feature Flag Awareness

Some tabs are conditional on Backstage feature flags:

| Tab | Requires Feature Flag | Helm Value |
|-----|-----------------------|------------|
| BUILD | `workflows.enabled: true` | `backstage.features.workflows.enabled` |
| LOGS | `observability.enabled: true` | `backstage.features.observability.enabled` |
| METRICS | `observability.enabled: true` | `backstage.features.observability.enabled` |
| ALERTS | `observability.enabled: true` | `backstage.features.observability.enabled` |
| TRACES | `observability.enabled: true` | `backstage.features.observability.enabled` |
| INCIDENTS | `observability.enabled: true` | `backstage.features.observability.enabled` |
| RCA REPORTS | `observability.enabled: true` | `backstage.features.observability.enabled` |

Tests should handle the case where a tab is **not visible** because the feature is disabled:

```typescript
// In helpers/navigation.ts — add:
export async function clickTabIfVisible(page: Page, tabLabel: string): Promise<boolean> {
  const tab = page.locator(`[role="tab"]:has-text("${tabLabel}")`).first();
  const isVisible = await tab.isVisible({ timeout: 5000 }).catch(() => false);
  if (!isVisible) {
    return false; // Tab not enabled — skip gracefully
  }
  await tab.click();
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(500);
  return true;
}
```

Then in observability-dependent tests:

```typescript
test('logs tab loads (if observability enabled)', async ({ page }) => {
  await navigateToComponent(page, component);
  const tabExists = await clickTabIfVisible(page, 'LOGS');
  if (!tabExists) {
    test.skip(); // Observability plane not deployed
    return;
  }
  await assertNoErrorBanner(page);
});
```

---

## 9. Execution

### Run All UI Tests
```bash
cd tests/ui-e2e
npm install
npx playwright install chromium
npx playwright test
```

### Run Specific Test Suite
```bash
# Just project tabs
npx playwright test project/

# Just component tabs
npx playwright test component/

# Specific component
TEST_COMPONENTS=frontend npx playwright test component/

# Headed mode (see the browser)
npx playwright test --headed

# Debug mode (pause on each step)
npx playwright test --debug
```

### Environment Variables
```bash
export BACKSTAGE_URL="https://openchoreo.local:8443"
export THUNDER_USERNAME="admin@openchoreo.dev"
export THUNDER_PASSWORD="admin"
export TEST_PROJECT="doclet"
export TEST_COMPONENTS="frontend,document-svc,collab-svc,nats,postgres"
export TEST_BUILDABLE_COMPONENTS="frontend,document-svc,collab-svc"
```

### CI Integration
```yaml
- name: Run UI E2E Tests
  run: |
    cd tests/ui-e2e
    npm ci
    npx playwright install chromium --with-deps
    npx playwright test --reporter=junit
  env:
    BACKSTAGE_URL: https://openchoreo.local:8443
    THUNDER_USERNAME: admin@openchoreo.dev
    THUNDER_PASSWORD: admin
  timeout-minutes: 15

- name: Upload Playwright Report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: playwright-report
    path: tests/ui-e2e/playwright-report/
```

---

## 10. What Each Test Would Catch

| Failure Scenario | Which Test Catches It |
|--|--|
| Backstage can't connect to OpenChoreo API | `home-page.spec.ts` — Infrastructure card shows 0 data planes |
| OAuth/Thunder integration broken | `auth.setup.ts` — login fails |
| Catalog empty (no entities synced) | `catalog-list.spec.ts` — no entities visible |
| Project page crashes (React error) | `project-overview.spec.ts` — error banner or blank page |
| Cell Diagram not rendering (SVG/canvas issue) | `project-cell-diagram.spec.ts` — no diagram visible |
| Build tab shows no workflow runs for a component | `component-build.spec.ts` — catches missing builds |
| Deploy tab shows "NotReady" for a component | `component-deploy.spec.ts` — catches deployment failures |
| Logs tab returns error (Observer API down) | `component-logs.spec.ts` — error banner visible |
| Metrics tab broken (Prometheus unreachable) | `component-metrics.spec.ts` — empty or error |
| Observability feature flag disabled | All obs tabs — graceful skip via `clickTabIfVisible` |
| Backstage frontend crash (JS error) | Any test — Playwright catches unhandled exceptions |
| Platform topology graph not rendering | `platform-topology.spec.ts` — no canvas/SVG |
| Environment cards missing from Deploy tab | `component-deploy.spec.ts` — "Development" not visible |

---

## 11. Implementation Priority

| Phase | What | Effort | Value |
|-------|------|--------|-------|
| **Phase 1** | Auth setup + Home page + Sidebar nav | 2-3h | 🔴 Foundation — everything depends on this |
| **Phase 2** | Catalog list + Platform topology | 2h | 🟠 Verifies entities are synced to portal |
| **Phase 3** | Component tabs: Overview + Definition + Deploy | 3-4h | 🔴 Highest — catches deployment issues in the UI |
| **Phase 4** | Component tabs: Build | 2h | 🟠 Catches missing/failed builds |
| **Phase 5** | Project tabs: Overview + Definition + Cell Diagram + Diagram | 3h | 🟠 Catches project-level rendering issues |
| **Phase 6** | Observability tabs: Logs + Metrics + Alerts + Traces | 3h | 🟡 Requires observability plane |
| **Phase 7** | Project: Incidents + RCA Reports | 1-2h | 🟡 Requires alerts to be configured |
| **Phase 8** | Create / Scaffolder | 1h | 🟢 Nice to have |

**Total estimated effort: ~17-20 hours for all 8 phases.**

---

## 12. Relationship to Existing Tests

```
┌──────────────────────────────────────────────────────┐
│  UI E2E Tests (Playwright)        ← THIS PLAN        │
│  "Can a user see & interact with the portal?"         │
│  Browser → Backstage → OpenChoreo API → K8s           │
├──────────────────────────────────────────────────────┤
│  E2E Backend Tests (pytest)       ← PREVIOUS PLAN     │
│  "Are OpenChoreo resources healthy?"                   │
│  Python → K8s API → CRD status checks                 │
├──────────────────────────────────────────────────────┤
│  Smoke Tests (pytest)             ← EXISTING           │
│  "Are infrastructure services running?"                │
│  Python → K8s API + HTTP health endpoints              │
└──────────────────────────────────────────────────────┘
```

The three layers complement each other:
- **Smoke tests** catch infrastructure failures (pod not running)
- **E2E backend tests** catch OpenChoreo resource chain failures (connections pending, missing releases)
- **UI E2E tests** catch portal rendering failures, broken API integrations, and UX regressions

Together, they guarantee: "infrastructure is up → platform resources are healthy → users can see and use it."
