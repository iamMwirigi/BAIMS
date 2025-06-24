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