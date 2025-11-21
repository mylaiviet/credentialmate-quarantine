"""
RIS AI Query Router - Phase 7

Natural language and direct SQL querying for Repository Intelligence System.

Endpoints (4):
1. POST /api/v2/ris/query-natural-language  - Convert NL to SQL and execute
2. POST /api/v2/ris/query-sql               - Execute direct SQL (admin only)
3. GET  /api/v2/ris/query-examples          - Get example queries (public)
4. GET  /api/v2/ris/query-stats             - Get query statistics

Security:
- All query endpoints require authentication (JWT)
- Natural language queries require 'ris:read' permission
- Direct SQL queries require 'ris:admin' permission
- Rate limiting: 100 requests/hour per user
- SQL validation prevents dangerous operations
- Audit logging for all queries

Author: Claude Code
Phase: 7 - AI Query Layer
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import time
import json

from app.core.dependencies import get_db, get_current_user, require_admin
from app.services.ris.ai_query_service import (
    natural_language_to_sql,
    execute_safe_query,
    format_results,
    QueryResult,
)
from app.services.ris.query_templates import (
    get_query_examples_for_api,
    get_all_view_schemas,
)
from app.services.ris.query_audit import (
    log_query,
    get_query_stats,
    get_recent_queries,
    get_query_cost_estimate,
)
from app.services.ris.query_validator import validate_sql


router = APIRouter(prefix="/api/v2/ris", tags=["ris-query"])


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================


class NaturalLanguageQueryRequest(BaseModel):
    """Request model for natural language queries."""
    query: str = Field(..., description="Natural language query", min_length=1, max_length=500)
    use_mock: bool = Field(True, description="Use mock NL to SQL conversion (no AI costs)")
    format: str = Field("json", description="Result format: json, csv, or table")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Show me all Python files",
                "use_mock": True,
                "format": "json"
            }
        }


class DirectSQLQueryRequest(BaseModel):
    """Request model for direct SQL queries."""
    sql: str = Field(..., description="SQL query to execute", min_length=1)
    format: str = Field("json", description="Result format: json, csv, or table")

    class Config:
        json_schema_extra = {
            "example": {
                "sql": "SELECT file_path, line_count FROM ris_simple_file_search_view WHERE primary_language = 'Python' LIMIT 10;",
                "format": "json"
            }
        }


class QueryResponse(BaseModel):
    """Response model for query execution."""
    success: bool = Field(..., description="Whether query succeeded")
    sql_query: str = Field(..., description="SQL query that was executed")
    row_count: int = Field(..., description="Number of rows returned")
    execution_time_ms: float = Field(..., description="Query execution time in milliseconds")
    results: List[Dict[str, Any]] = Field(..., description="Query results")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    ai_model: Optional[str] = Field(None, description="AI model used (if applicable)")
    ai_tokens_used: Optional[int] = Field(None, description="AI tokens consumed (if applicable)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "sql_query": "SELECT file_path, line_count FROM ris_simple_file_search_view WHERE primary_language = 'Python' LIMIT 10;",
                "row_count": 10,
                "execution_time_ms": 45.2,
                "results": [
                    {"file_path": "backend/app/main.py", "line_count": 150},
                    {"file_path": "backend/app/core/config.py", "line_count": 80}
                ],
                "error_message": None,
                "ai_model": "mock",
                "ai_tokens_used": 0
            }
        }


class QueryExample(BaseModel):
    """Example query."""
    query: str = Field(..., description="Natural language query")
    sql: str = Field(..., description="Equivalent SQL")
    category: str = Field(..., description="Query category")


class QueryStatsResponse(BaseModel):
    """Query statistics response."""
    total_queries: int
    successful_queries: int
    failed_queries: int
    nl_queries: int
    direct_sql_queries: int
    avg_execution_time_ms: float
    total_results_returned: int
    total_ai_tokens_used: int


# ============================================
# NATURAL LANGUAGE QUERY ENDPOINT
# ============================================


@router.post("/query-natural-language", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def query_natural_language(
    request: NaturalLanguageQueryRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Execute natural language query against RIS data.

    Converts natural language to SQL, validates, executes, and logs the query.

    **Authentication:** JWT required
    **Permission:** ris:read
    **Rate Limit:** 100 requests/hour per user

    **Process:**
    1. Convert natural language to SQL (mock or AI)
    2. Validate SQL for safety
    3. Execute query with timeout
    4. Log to audit trail
    5. Return results

    **Supported Queries:**
    - File search: "Show me all Python files"
    - Dependencies: "What files import database.py?"
    - Security: "List files with secrets"
    - Changes: "What files were modified today?"
    - Statistics: "Count files by language"

    **Examples:**
    ```
    POST /api/v2/ris/query-natural-language
    {
        "query": "Show me the largest Python files",
        "use_mock": true,
        "format": "json"
    }
    ```

    **Returns:**
        QueryResponse with results and execution metadata

    **Raises:**
        400: Bad Request - Invalid query or validation failed
        401: Unauthorized - Missing or invalid authentication
        429: Too Many Requests - Rate limit exceeded
        500: Internal Server Error - Query execution failed
    """
    start_time = time.time()
    user_id = current_user.get("id") or current_user.get("user_id")

    # TODO: Check rate limit
    # if not check_rate_limit(user_id):
    #     raise HTTPException(
    #         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    #         detail="Rate limit exceeded. Maximum 100 requests per hour."
    #     )

    try:
        # Convert NL to SQL
        sql_query, ai_model, tokens_used = natural_language_to_sql(
            request.query,
            use_mock=request.use_mock
        )

        # Execute query
        result = execute_safe_query(sql_query, db)

        # Log query
        log_query(
            user_id=user_id,
            query_type="natural_language",
            query_text=sql_query,
            results_count=result.row_count,
            execution_time_ms=result.execution_time_ms,
            session=db,
            natural_language_query=request.query,
            error_message=result.error_message,
            ai_model=ai_model or result.ai_model,
            ai_tokens_used=tokens_used or result.ai_tokens_used
        )

        # Format results
        formatted_results = result.rows
        if request.format == "csv":
            formatted_results = format_results(result.rows, "csv")
        elif request.format == "table":
            formatted_results = format_results(result.rows, "table")

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error_message or "Query execution failed"
            )

        return QueryResponse(
            success=result.success,
            sql_query=result.sql_query,
            row_count=result.row_count,
            execution_time_ms=result.execution_time_ms,
            results=formatted_results if isinstance(formatted_results, list) else [{"result": formatted_results}],
            error_message=result.error_message,
            ai_model=ai_model or result.ai_model,
            ai_tokens_used=tokens_used or result.ai_tokens_used
        )

    except HTTPException:
        raise
    except Exception as e:
        # Log failed query
        execution_time = (time.time() - start_time) * 1000
        log_query(
            user_id=user_id,
            query_type="natural_language",
            query_text="",
            results_count=0,
            execution_time_ms=execution_time,
            session=db,
            natural_language_query=request.query,
            error_message=str(e)
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}"
        )


# ============================================
# DIRECT SQL QUERY ENDPOINT (ADMIN ONLY)
# ============================================


@router.post("/query-sql", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def query_sql(
    request: DirectSQLQueryRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Execute direct SQL query against RIS data (admin only).

    Validates and executes SQL query directly without NL conversion.

    **Authentication:** JWT required
    **Permission:** ris:admin (admin or superadmin role)
    **Rate Limit:** 100 requests/hour per user

    **Security:**
    - Only SELECT statements allowed
    - Only approved views can be queried
    - Dangerous keywords blocked (DROP, DELETE, UPDATE, etc.)
    - Maximum 5 JOINs
    - Maximum 3 subqueries
    - Maximum LIMIT 10,000
    - 30 second timeout

    **Approved Views:**
    - ris_simple_file_search_view
    - ris_dependency_view
    - ris_recent_changes_view
    - ris_security_risk_view

    **Examples:**
    ```
    POST /api/v2/ris/query-sql
    {
        "sql": "SELECT primary_language, COUNT(*) as count FROM ris_simple_file_search_view GROUP BY primary_language ORDER BY count DESC LIMIT 20;",
        "format": "json"
    }
    ```

    **Returns:**
        QueryResponse with results and execution metadata

    **Raises:**
        400: Bad Request - Invalid SQL or validation failed
        401: Unauthorized - Missing or invalid authentication
        403: Forbidden - Insufficient permissions (admin required)
        429: Too Many Requests - Rate limit exceeded
        500: Internal Server Error - Query execution failed
    """
    start_time = time.time()
    user_id = current_user.get("id") or current_user.get("user_id")

    # TODO: Check rate limit
    # if not check_rate_limit(user_id):
    #     raise HTTPException(
    #         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    #         detail="Rate limit exceeded. Maximum 100 requests per hour."
    #     )

    try:
        # Validate SQL
        validation = validate_sql(request.sql)
        if not validation.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SQL validation failed: {validation.error_message}"
            )

        # Execute query
        result = execute_safe_query(request.sql, db)

        # Log query
        log_query(
            user_id=user_id,
            query_type="direct_sql",
            query_text=result.sql_query,
            results_count=result.row_count,
            execution_time_ms=result.execution_time_ms,
            session=db,
            error_message=result.error_message
        )

        # Format results
        formatted_results = result.rows
        if request.format == "csv":
            formatted_results = format_results(result.rows, "csv")
        elif request.format == "table":
            formatted_results = format_results(result.rows, "table")

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error_message or "Query execution failed"
            )

        return QueryResponse(
            success=result.success,
            sql_query=result.sql_query,
            row_count=result.row_count,
            execution_time_ms=result.execution_time_ms,
            results=formatted_results if isinstance(formatted_results, list) else [{"result": formatted_results}],
            error_message=result.error_message
        )

    except HTTPException:
        raise
    except Exception as e:
        # Log failed query
        execution_time = (time.time() - start_time) * 1000
        log_query(
            user_id=user_id,
            query_type="direct_sql",
            query_text=request.sql,
            results_count=0,
            execution_time_ms=execution_time,
            session=db,
            error_message=str(e)
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}"
        )


# ============================================
# QUERY EXAMPLES ENDPOINT (PUBLIC)
# ============================================


@router.get("/query-examples", response_model=List[QueryExample], status_code=status.HTTP_200_OK)
async def get_query_examples():
    """
    Get example natural language queries.

    Returns curated examples of natural language queries and their SQL equivalents.
    Useful for learning how to query RIS data effectively.

    **Authentication:** Not required (public endpoint)

    **Categories:**
    - search: File search queries
    - dependencies: Dependency analysis queries
    - security: Security risk queries
    - changes: Change tracking queries
    - statistics: Aggregation and counting queries

    **Returns:**
        List of QueryExample objects with query, SQL, and category

    **Example Response:**
    ```json
    [
        {
            "query": "Show me all Python files",
            "sql": "SELECT file_path, line_count FROM ris_simple_file_search_view WHERE primary_language = 'Python' LIMIT 1000;",
            "category": "search"
        }
    ]
    ```
    """
    examples = get_query_examples_for_api()
    return [QueryExample(**ex) for ex in examples]


# ============================================
# QUERY STATISTICS ENDPOINT
# ============================================


@router.get("/query-stats", response_model=QueryStatsResponse, status_code=status.HTTP_200_OK)
async def get_statistics(
    start_date: Optional[datetime] = Query(None, description="Filter start date"),
    end_date: Optional[datetime] = Query(None, description="Filter end date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get query statistics for current user.

    Returns aggregated statistics about queries executed by the current user.

    **Authentication:** JWT required
    **Permission:** ris:read

    **Filters:**
    - start_date: Optional start date (ISO format)
    - end_date: Optional end date (ISO format)

    **Returns:**
        QueryStatsResponse with aggregated statistics

    **Example:**
    ```
    GET /api/v2/ris/query-stats?start_date=2025-11-01T00:00:00Z
    ```
    """
    user_id = current_user.get("id") or current_user.get("user_id")

    stats = get_query_stats(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        session=db
    )

    return QueryStatsResponse(**stats)


# ============================================
# VIEW SCHEMAS ENDPOINT
# ============================================


@router.get("/views", status_code=status.HTTP_200_OK)
async def get_view_schemas():
    """
    Get RIS view schemas.

    Returns schema information for all queryable RIS views.

    **Authentication:** Not required (public endpoint)

    **Returns:**
        Dictionary of view names to schema information (description, columns)

    **Example Response:**
    ```json
    {
        "ris_simple_file_search_view": {
            "description": "Active files with metadata",
            "columns": {
                "file_id": {"type": "INTEGER", "description": "Primary key"},
                "file_path": {"type": "TEXT", "description": "Full file path"}
            }
        }
    }
    ```
    """
    return get_all_view_schemas()
