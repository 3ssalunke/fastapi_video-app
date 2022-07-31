from starlette.exceptions import HTTPException

from app.main import app
from app.shortcuts import render, redirect
from .users.exceptions import LoginRequiredException


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    status_code = exc.status_code
    template_name = "errors/main.html"
    context = {"status_code": status_code}
    return render(request, template_name, context, status_code)


@app.exception_handler(LoginRequiredException)
async def http_exception_handler(request, exc):
    status_code = exc.status_code
    template_name = "errors/main.html"
    context = {"status_code": status_code}
    return redirect(f"/login?next={request.url}", remove_session=True)
