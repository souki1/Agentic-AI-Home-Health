"""Thin wrapper so 'uvicorn app:main' works. Prefer: uvicorn main:app --reload"""
from main import app as main

__all__ = ["main"]
