# Rich API Endpoints Usage Guide

This guide shows you how to use the new rich API endpoints that return nested data in the format you requested, with filtering capabilities.

## Available Endpoints

### 1. Rich BA Data Endpoint
**URL:** `/api/rich/ba/{ba_id}/`
**Method:** GET

Returns BA data with nested projects, forms, and fields in the exact format you showed.

#### Example Request:
```
GET /api/rich/ba/2/
```

#### Example Response:
```json
{
    "response": "success",
    "name": "John Doe",
    "ba_id": "2",
    "company": "SKOPE AND KRAFT",
    "projects": [
        {
            "project_title": "KONYAGI-2",
            "code_name": "KONYAGI-2",
            "project_id": "12",
            "start_date": "2025-06-11",
            "end_date": "2025-06-11",
            "forms": [
                {
                    "0": "MAISHA NDIO HAYA - REPORTING TEMPLATE",
                    "form_title": "MAISHA NDIO HAYA - REPORTING TEMPLATE",
                    "1": "64",
                    "form_id": "64",
                    "2": "1",
                    "form_rank": "1",
                    "3": "off",
                    "location_status": "off",
                    "4": "NO",
                    "image_required": "NO",
                    "form_fields": [
                        {
                            "input_title": "ACTIVATION OUTLET DETAILS",
                            "field_id": "label",
                            "input_rank": "1",
                            "field_type": "input",
                            "multiple_choice": "false",
                            "options_available": "0",
                            "field_input_options": []
                        }
                        // ... more fields
                    ]
                }
            ]
        }
    ]
}
```

#### Query Parameters for Filtering:
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)
- `project_id`: Filter by specific project
- `form_id`: Filter by specific form
- `company`: Filter by company name

#### Example with Filters:
```
GET /api/rich/ba/2/?start_date=2025-01-01&end_date=2025-12-31&project_id=12
```

### 2. All BAs Rich Data Endpoint
**URL:** `/api/rich/ba/`
**Method:** GET

Returns data for all BAs with the same nested structure.

#### Example Request:
```
GET /api/rich/ba/?company=SKOPE
```

#### Example Response:
```json
{
    "response": "success",
    "count": 5,
    "data": [
        {
            "response": "success",
            "name": "John Doe",
            "ba_id": "2",
            "company": "SKOPE AND KRAFT",
            "projects": [...]
        }
        // ... more BAs
    ]
}
```

### 3. BA Data with Records Endpoint
**URL:** `/api/rich/ba/{ba_id}/with-data/`
**Method:** GET

Returns BA data with actual data records from wide tables.

#### Query Parameters:
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)
- `project_id`: Filter by specific project
- `include_data`: Include actual data records (true/false)

#### Example Request:
```
GET /api/rich/ba/2/with-data/?include_data=true&start_date=2025-01-01
```

### 4. Wide Data Filter Endpoint
**URL:** `/api/data/filter/`
**Method:** GET

Filter data directly from wide tables (airtel_combined, coke_combined, etc.).

#### Query Parameters:
- `table`: The wide table name (airtel_combined, coke_combined, etc.)
- `ba_id`: Filter by BA ID
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)
- `project_id`: Filter by project ID
- `fields`: Comma-separated list of fields to include
- `limit`: Number of records to return (default: 100)

#### Example Request:
```
GET /api/data/filter/?table=airtel_combined&ba_id=2&start_date=2025-01-01&fields=id,project,sub_1_1,sub_1_2,t_date&limit=50
```

#### Example Response:
```json
{
    "response": "success",
    "table": "airtel_combined",
    "count": 25,
    "data": [
        {
            "id": 1,
            "project": 12,
            "sub_1_1": "Sample data",
            "sub_1_2": "More data",
            "t_date": "2025-01-15"
        }
        // ... more records
    ]
}
```

### 5. Project Data Endpoint
**URL:** `/api/data/project/{project_id}/`
**Method:** GET

Get project data with forms, fields, and optionally actual data records.

#### Query Parameters:
- `ba_id`: Filter by BA ID
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)
- `include_data`: Include actual data records (true/false)
- `data_table`: Specify which data table to use

#### Example Request:
```
GET /api/data/project/12/?include_data=true&data_table=airtel_combined&ba_id=2
```

## Filtering Examples

### Filter by Date Range:
```
GET /api/rich/ba/2/?start_date=2025-01-01&end_date=2025-01-31
```

### Filter by Project:
```
GET /api/rich/ba/2/?project_id=12
```

### Filter by Company:
```
GET /api/rich/ba/?company=SKOPE
```

### Filter Wide Table Data:
```
GET /api/data/filter/?table=coke_combined&start_date=2025-01-01&end_date=2025-01-31&ba_id=2&project_id=12
```

### Get Specific Fields from Wide Table:
```
GET /api/data/filter/?table=airtel_combined&fields=id,project,sub_1_1,sub_1_2,sub_1_3,t_date,ba_id&ba_id=2
```

## Error Responses

All endpoints return consistent error responses:

```json
{
    "response": "error",
    "message": "Error description"
}
```

## Common HTTP Status Codes

- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Notes

1. **Date Format**: All dates should be in YYYY-MM-DD format
2. **Field Names**: When filtering wide tables, use the actual column names from your database
3. **Limits**: The wide data filter has a default limit of 100 records, which can be adjusted
4. **Nested Data**: The rich endpoints automatically build the nested structure based on your database relationships

## Testing the Endpoints

You can test these endpoints using:
- Your browser (for GET requests)
- Postman or similar API testing tools
- curl commands
- Any HTTP client library in your preferred programming language

Example curl command:
```bash
curl "http://your-domain.com/api/rich/ba/2/?start_date=2025-01-01&end_date=2025-01-31"
```

# BAIMS API Usage Examples

## Brand Ambassador (BA) Endpoints

The BA endpoints provide full CRUD operations for managing Brand Ambassador records. All endpoints require authentication and include proper permission checks based on user roles.

### Base URL
```
/api/data/ba/
```

### Authentication
All BA endpoints require authentication using one of these token types:
- **User Token**: For regular users
- **Admin Token**: For UAdmin users  
- **BA Token**: For Brand Ambassador users

Include the token in the Authorization header:
```
Authorization: Token <your_token_here>
```

---

## 1. List All BAs (GET)

**Endpoint:** `GET /api/data/ba/`

**Description:** Retrieve all BAs that the authenticated user has permission to view.

**Permissions:**
- **UAdmin**: Can see BAs from all their associated agencies
- **BA**: Can only see their own profile
- **User**: Can see BAs from their agency

**Response:**
```json
{
  "success": true,
  "message": "Successfully retrieved 5 BAs",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "John Doe",
        "phone": "+254712345678",
        "company": 1,
        "pass_code": "hashed_password"
      }
    ],
    "count": 5
  }
}
```

---

## 2. Get Specific BA (GET)

**Endpoint:** `GET /api/data/ba/{id}/`

**Description:** Retrieve a specific BA by ID.

**Permissions:** Same as list endpoint

**Response:**
```json
{
  "success": true,
  "message": "Item retrieved successfully",
  "data": {
    "item": {
      "id": 1,
      "name": "John Doe",
      "phone": "+254712345678",
      "company": 1,
      "pass_code": "hashed_password"
    }
  }
}
```

---

## 3. Create New BA (POST)

**Endpoint:** `POST /api/data/ba/`

**Description:** Create a new Brand Ambassador.

**Permissions:**
- **UAdmin**: Can create BAs in their agencies
- **BA**: Cannot create other BAs
- **User**: Can create BAs in their agency

**Request Body:**
```json
{
  "name": "Jane Smith",
  "phone": "+254798765432",
  "pass_code": "secure_password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "BA created and assigned to 3 projects.",
  "data": {
    "id": 2,
    "name": "Jane Smith",
    "phone": "+254798765432",
    "company": 1,
    "pass_code": "hashed_password"
  }
}
```

**Notes:**
- The `company` field is automatically set based on the authenticated user's agency
- The BA is automatically assigned to all projects in their company
- Start and end dates for project assignments can be specified in the request

---

## 4. Update BA (PUT - Full Update)

**Endpoint:** `PUT /api/data/ba/{id}/`

**Description:** Update a BA record with full replacement of all fields.

**Permissions:**
- **UAdmin**: Can update BAs in their agencies
- **BA**: Can only update their own profile
- **User**: Can update BAs in their agency

**Request Body:**
```json
{
  "name": "Jane Smith Updated",
  "phone": "+254798765432",
  "pass_code": "new_secure_password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "BA updated successfully",
  "data": {
    "item": {
      "id": 2,
      "name": "Jane Smith Updated",
      "phone": "+254798765432",
      "company": 1,
      "pass_code": "hashed_new_password"
    }
  }
}
```

**Validation:**
- Phone number must be unique across all BAs
- All required fields must be provided (PUT requires complete data)

---

## 5. Partial Update BA (PATCH)

**Endpoint:** `PATCH /api/data/ba/{id}/`

**Description:** Update specific fields of a BA record.

**Permissions:** Same as PUT endpoint

**Request Body:**
```json
{
  "name": "Jane Smith Updated"
}
```

**Response:**
```json
{
  "success": true,
  "message": "BA updated successfully",
  "data": {
    "item": {
      "id": 2,
      "name": "Jane Smith Updated",
      "phone": "+254798765432",
      "company": 1,
      "pass_code": "hashed_password"
    }
  }
}
```

**Validation:**
- Phone number must be unique if being updated
- Only provided fields are updated

---

## 6. Delete BA (DELETE)

**Endpoint:** `DELETE /api/data/ba/{id}/`

**Description:** Delete a BA record and all associated data.

**Permissions:**
- **UAdmin**: Can delete BAs in their agencies
- **BA**: Can only delete their own profile
- **User**: Can delete BAs in their agency

**Response:**
```json
{
  "success": true,
  "message": "BA deleted successfully",
  "data": {
    "deleted_ba": {
      "id": 2,
      "name": "Jane Smith Updated",
      "phone": "+254798765432",
      "company": 1
    },
    "note": "All associated project assignments and data records have been removed"
  }
}
```

**Cleanup Operations:**
When a BA is deleted, the following related data is also removed:
- BA project associations (`BaProject` records)
- BA authentication tokens (`BaAuthToken` records)
- BA data records from all data collection tables:
  - AirtelCombined
  - CokeCombined
  - BaimsCombined
  - KspcaCombined
  - SaffCombined

---

## Error Responses

### 404 Not Found
```json
{
  "success": false,
  "message": "BA with ID '999' does not exist.",
  "data": {
    "errors": "Item not found"
  }
}
```

### 403 Forbidden (Permission Denied)
```json
{
  "success": false,
  "message": "You can only update your own profile",
  "data": {
    "errors": "Permission denied"
  }
}
```

### 400 Bad Request (Validation Error)
```json
{
  "success": false,
  "message": "Phone number already exists",
  "data": {
    "errors": {
      "phone": "This phone number is already registered"
    }
  }
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "An error occurred while updating the BA",
  "data": {
    "errors": "Database connection error"
  }
}
```

---

## Usage Examples

### cURL Examples

**List all BAs:**
```bash
curl -X GET "http://localhost:8000/api/data/ba/" \
  -H "Authorization: Token your_token_here"
```

**Get specific BA:**
```bash
curl -X GET "http://localhost:8000/api/data/ba/1/" \
  -H "Authorization: Token your_token_here"
```

**Create new BA:**
```bash
curl -X POST "http://localhost:8000/api/data/ba/" \
  -H "Authorization: Token your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New BA",
    "phone": "+254712345679",
    "pass_code": "password123"
  }'
```

**Update BA (PUT):**
```bash
curl -X PUT "http://localhost:8000/api/data/ba/1/" \
  -H "Authorization: Token your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated BA Name",
    "phone": "+254712345679",
    "pass_code": "new_password123"
  }'
```

**Partial update BA (PATCH):**
```bash
curl -X PATCH "http://localhost:8000/api/data/ba/1/" \
  -H "Authorization: Token your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated BA Name"
  }'
```

**Delete BA:**
```bash
curl -X DELETE "http://localhost:8000/api/data/ba/1/" \
  -H "Authorization: Token your_token_here"
```

### JavaScript/Fetch Examples

**List all BAs:**
```javascript
fetch('/api/data/ba/', {
  method: 'GET',
  headers: {
    'Authorization': 'Token your_token_here'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

**Create new BA:**
```javascript
fetch('/api/data/ba/', {
  method: 'POST',
  headers: {
    'Authorization': 'Token your_token_here',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'New BA',
    phone: '+254712345679',
    pass_code: 'password123'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Update BA:**
```javascript
fetch('/api/data/ba/1/', {
  method: 'PUT',
  headers: {
    'Authorization': 'Token your_token_here',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Updated BA Name',
    phone: '+254712345679',
    pass_code: 'new_password123'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Delete BA:**
```javascript
fetch('/api/data/ba/1/', {
  method: 'DELETE',
  headers: {
    'Authorization': 'Token your_token_here'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | Integer | Auto | Unique identifier |
| `name` | String (128 chars) | Yes | Full name of the BA |
| `phone` | String (64 chars) | Yes | Phone number (must be unique) |
| `company` | Integer | Auto | Agency/company ID (set automatically) |
| `pass_code` | String (1000 chars) | Yes | Password/passcode for authentication |

---

## Security Considerations

1. **Authentication Required**: All endpoints require valid authentication tokens
2. **Permission-Based Access**: Users can only access/modify BAs within their scope
3. **Phone Number Uniqueness**: Phone numbers must be unique across all BAs
4. **Data Cleanup**: Deleting a BA removes all associated data to prevent orphaned records
5. **Input Validation**: All input data is validated before processing

---

## Rate Limiting

The API includes rate limiting to prevent abuse. Contact the system administrator for specific limits.

---

## Support

For technical support or questions about the BA endpoints, please contact the development team or refer to the system documentation. 