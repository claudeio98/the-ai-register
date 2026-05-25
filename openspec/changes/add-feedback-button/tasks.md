## 1. Backend Implementation

- [x] 1.1 Create POST `/api/feedback` endpoint in FastAPI
- [x] 1.2 Implement feedback validation logic (category and message)
- [x] 1.3 Implement notification service (Email/Log fallback)
- [x] 1.4 Add rate-limiting middleware or simple IP check for the endpoint

## 2. Frontend Implementation

- [x] 2.1 Create `FeedbackModal.vue` component with form and validation
- [x] 2.2 Add "Feedback" button to the main Header/Navigation
- [x] 2.3 Integrate `FeedbackModal` with the backend API
- [x] 2.4 Implement success/error notifications in the UI

## 3. Testing and Verification

- [x] 3.1 Verify backend endpoint with curl/Postman
- [x] 3.2 Verify email notification delivery
- [x] 3.3 Test end-to-end flow from UI to notification
- [x] 3.4 Verify validation errors are handled correctly in the UI
