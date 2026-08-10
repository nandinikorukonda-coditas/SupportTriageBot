Frontend plan (Angular)

This repository contains a placeholder for the Angular frontend. To scaffold the Angular app run:

```bash
cd frontend
npx @angular/cli new support-frontend --defaults
cd support-frontend
npm install
```

Integrate the frontend with the backend by calling the API endpoints:
- `GET /tickets` — list historical tickets
- `POST /submit` — submit ticket text (form-encoded)
- `POST /submit-voice` — upload voice file (if STT implemented)
- `POST /mcp/file` — confirm filing of ticket (send `confirm=true`)

UI components to implement:
- Dashboard (ticket list)
- New Ticket (text & voice)
- Ticket Details (show RAG references and agent trace)
- Corpus Viewer (list of historical tickets)

The Angular app is intentionally left as scaffold steps so you can customize UI quickly.
