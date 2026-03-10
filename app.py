import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette_graphene3 import GraphQLApp, make_playground_handler

from database import db_session, init_db
from schema import schema

app = FastAPI(title="Fleet Tracking API")


@app.middleware("http")
async def db_session_middleware(request, call_next):
    try:
        response = await call_next(request)
    finally:
        db_session.remove()
    return response


@app.get("/", response_class=HTMLResponse)
async def index():
    return (
        "<h2>Fleet Tracking API</h2>"
        "<p>Visit <a href='/graphql'>/graphql</a> to open GraphiQL explorer.</p>"
    )


graphql_app = GraphQLApp(
    schema=schema,
    on_get=make_playground_handler()
)
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
    print("Starting Fleet Tracking API on http://127.0.0.1:8000")
    print("GraphiQL explorer: http://127.0.0.1:8000/graphql")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
