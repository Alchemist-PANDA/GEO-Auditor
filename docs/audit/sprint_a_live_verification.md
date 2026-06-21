# Sprint A Live Verification Report

**Date**: 2026-06-20



### Register User A
* **Request**: `POST /api/v1/workspaces/register`
* **Payload**:
```json
{
  "email": "usera_cce7fb@example.com",
  "password": "password123",
  "full_name": "User A",
  "organization_name": "Org A"
}
```
* **Status Code**: **201**
* **Response**:
```json
{
  "message": "User registered successfully"
}
```


### Register User B
* **Request**: `POST /api/v1/workspaces/register`
* **Payload**:
```json
{
  "email": "userb_a55406@example.com",
  "password": "password123",
  "full_name": "User B",
  "organization_name": "Org B"
}
```
* **Status Code**: **201**
* **Response**:
```json
{
  "message": "User registered successfully"
}
```

## 1. User A accessing User A resources -> 200


### User A Accesses Project A Prompts
* **Request**: `GET /api/v1/prompts?project_id=9d970ea4-2000-43b2-a392-ae03fd23970b`
* **Payload**:
```json
{}
```
* **Status Code**: **200**
* **Response**:
```json
[]
```

## 2. User A accessing User B resources -> 403


### User A Accesses Project B Prompts
* **Request**: `GET /api/v1/prompts?project_id=36d84048-7b79-4f50-9916-8052d3eaa6f0`
* **Payload**:
```json
{}
```
* **Status Code**: **403**
* **Response**:
```json
{
  "detail": "Not authorized to access this project"
}
```

## 3. User B accessing User A resources -> 403


### User B Accesses Project A Prompts
* **Request**: `GET /api/v1/prompts?project_id=9d970ea4-2000-43b2-a392-ae03fd23970b`
* **Payload**:
```json
{}
```
* **Status Code**: **403**
* **Response**:
```json
{
  "detail": "Not authorized to access this project"
}
```

## 4. Invalid workspace -> 404


### Invalid workspace
* **Request**: `POST /api/v1/workspaces/projects`
* **Payload**:
```json
{
  "name": "Orphan Proj",
  "workspace_id": "f0f5aa82-ec0e-45a1-9325-f2e0c0531f0a"
}
```
* **Status Code**: **404**
* **Response**:
```json
{
  "detail": "Workspace not found"
}
```

## 5. Invalid project -> 404/403


### Invalid project
* **Request**: `GET /api/v1/prompts?project_id=ba6d0673-1c19-4896-b51c-323cb4445ec3`
* **Payload**:
```json
{}
```
* **Status Code**: **403**
* **Response**:
```json
{
  "detail": "Not authorized to access this project"
}
```
