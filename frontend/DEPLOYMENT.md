# Frontend Deployment Instructions

This guide provides steps for packaging and running the Next.js frontend inside a production-ready Docker container.

## 1. Prerequisites
- Docker installed on your host system.
- Backend API running and accessible at a public or internal network URL.

## 2. Docker Container Operations

### Build the Image
From the `frontend/` directory, execute:
```bash
docker build -t geo-frontend .
```

### Run the Container
Launch the container by specifying the backend URL using `NEXT_PUBLIC_API_URL`:
```bash
docker run -d \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 \
  --name geo-frontend-container \
  geo-frontend
```

## 3. Verification Checklist

1. **Static compilation**: Check the Docker build logs to verify all routes under `src/app` compile successfully during the `npm run build` stage.
2. **Exposed Port**: Verify that port `3000` is exposed and accessible by navigating to `http://localhost:3000`.
3. **API Integration**: Check browser console logs when accessing the login page to ensure requests are routed to the target backend URL.
