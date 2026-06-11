# LangGraph-FoundryIQ UI

Ionic + Angular (standalone) responsive front-end for the LangGraph + Foundry IQ POC.

## Layouts per device

| Device  | Width            | Layout                                          |
|---------|------------------|-------------------------------------------------|
| Mobile  | `< 768px`        | Single column. Prompts + profile in slide-out menu (hamburger). |
| iPad    | `768px–1199px`   | 2-column. Left rail holds profile + about; 4 prompts inline in empty state. |
| Desktop | `≥ 1200px`       | 3-column. Profile rail (L) · Chat (center) · Prompts rail (R). |

Breakpoints live in [src/global.scss](src/global.scss) and
[chat.page.scss](src/app/pages/chat/chat.page.scss). The active device class is
computed reactively in [device.service.ts](src/app/services/device.service.ts)
using Ionic `Platform.resize`.

## Run locally

```powershell
cd ui
npm install
npm start
# UI on http://localhost:8100, talks to API at http://localhost:8000
```

## Build

```powershell
npm run build
# emits ./www — ready to ship to AKS / Static Web Apps / App Service
```

## Where things live

```
src/
  app/
    app.component.ts         # standalone bootstrap + icon registration
    app.routes.ts            # lazy-loads the chat page
    components/
      profile-card/          # Michael Yaacoub + GH + LinkedIn
      prompt-grid/           # 10 sample prompts, responsive grid
      chat-message/          # bubble + citations renderer
    pages/
      chat/                  # main page (responsive 1/2/3-col)
    services/
      chat.service.ts        # HTTP to /api/v1/prompts and /api/v1/chat
      device.service.ts      # mobile | tablet | desktop signal
    models/
      chat.models.ts         # TypeScript DTOs mirroring the FastAPI schemas
  environments/              # apiBaseUrl per build target
  theme/variables.scss       # brand colors + radii + shadows
  global.scss                # responsive grid breakpoints
```
